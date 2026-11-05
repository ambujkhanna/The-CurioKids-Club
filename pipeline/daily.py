"""Daily run: pick the next ready episode -> voices -> frames -> MP4 -> QC -> upload (publishes inside PUBLISH_WINDOW, IST).

    python pipeline/daily.py              # normal run (uploads only if YouTube secrets are set)
    python pipeline/daily.py --dry-run    # render + QC only
    python pipeline/daily.py --episode ep003   # force a specific episode
    python pipeline/daily.py --now             # publish immediately instead of scheduling

Publish time: a random 5-minute slot inside PUBLISH_WINDOW (IST, default "16:00-19:00"), today if there is still
time left in the window, otherwise tomorrow. Change the window via the repo variable PUBLISH_WINDOW.

State lives in episodes/state.json (committed back by the workflow). Fail-closed: any failed step
or QC check stops the run and nothing is uploaded.
"""
import datetime as dt, glob, json, os, random, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIPE = os.path.join(ROOT, "pipeline")
STATE = os.path.join(ROOT, "episodes", "state.json")
OUT = os.path.join(ROOT, "out")
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))


def sh(cmd, env=None, cwd=ROOT):
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True, cwd=cwd, env={**os.environ, **(env or {})})


def load_state():
    return json.load(open(STATE)) if os.path.exists(STATE) else {"episodes": {}}


def pick(state, forced=None):
    eps = []
    for f in sorted(glob.glob(os.path.join(ROOT, "episodes", "*", "episode.json"))):
        ep = json.load(open(f)); ep["_file"] = f
        eps.append(ep)
    if forced:
        return next(e for e in eps if e["id"] == forced)
    for ep in eps:
        st = state["episodes"].get(ep["id"], {}).get("status")
        if ep.get("status") == "ready" and st not in ("uploaded", "published", "manual"):
            return ep
    return None


def next_slot(now=None, window=None):
    """Random 5-minute slot inside the publish window (IST); today if possible, else tomorrow."""
    window = window or os.environ.get("PUBLISH_WINDOW") or "16:00-19:00"
    a, b = window.split("-")
    (ah, am), (bh, bm) = (map(int, a.split(":")), map(int, b.split(":")))
    now = now or dt.datetime.now(IST)
    earliest = now + dt.timedelta(minutes=45)  # YouTube needs publishAt comfortably in the future
    for add in (0, 1):
        day = (now + dt.timedelta(days=add)).date()
        start = dt.datetime(day.year, day.month, day.day, ah, am, tzinfo=IST)
        end = dt.datetime(day.year, day.month, day.day, bh, bm, tzinfo=IST)
        lo = max(start, earliest)
        if lo <= end - dt.timedelta(minutes=5):
            steps = int((end - lo).total_seconds() // 300)
            slot = lo + dt.timedelta(minutes=5 * random.randint(0, steps))
            return slot.replace(minute=slot.minute - slot.minute % 5, second=0, microsecond=0) if slot.minute % 5 else slot.replace(second=0, microsecond=0)
    raise RuntimeError("no slot found")


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height:format=duration",
                        "-of", "json", path], capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def qc(path, ep):
    """Automated quality gate. Returns list of problems (empty = pass)."""
    problems = []
    p = probe(path)
    dur = float(p["format"]["duration"])
    v = [s for s in p["streams"] if s["codec_type"] == "video"]
    a = [s for s in p["streams"] if s["codec_type"] == "audio"]
    if not (45 <= dur <= 180): problems.append(f"duration {dur:.1f}s outside 45-180s")
    if not v or (v[0]["width"], v[0]["height"]) != (1080, 1920): problems.append("video is not 1080x1920")
    if not a: problems.append("no audio stream")
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True)
    m = re.search(r"mean_volume: (-?[\d.]+) dB", r.stderr)
    if not m or float(m.group(1)) < -35: problems.append(f"audio too quiet ({m.group(1) if m else 'n/a'} dB)")
    cap = os.path.join(PIPE, "build", "captions.ass")
    if not os.path.exists(cap) or open(cap).read().count("Dialogue:") < 10: problems.append("captions missing")
    if not ep.get("title") or len(ep["title"]) > 100: problems.append("title missing or too long")
    if not ep.get("description"): problems.append("description missing")
    return problems


def summary(md):
    """Write a short report to the GitHub Actions run page (no-op locally)."""
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a") as fh:
            fh.write(md + "\n")


def main():
    args = sys.argv[1:]
    dry = "--dry-run" in args
    forced = args[args.index("--episode") + 1] if "--episode" in args else None
    now_mode = "--now" in args
    state = load_state()
    ep = pick(state, forced)
    if not ep:
        print("No ready episode left in the backlog. Add episodes/<id>/episode.json files."); return 0
    eid = ep["id"]; epf = ep["_file"]
    print(f"== {eid}: {ep['title']}")
    from validate_episode import check
    errs = check(epf)
    if errs:
        rec = state["episodes"].setdefault(eid, {}); rec.update({"status": "invalid", "problems": errs})
        json.dump(state, open(STATE, "w"), indent=2)
        print("Episode file invalid - not rendering:", errs); return 1
    os.makedirs(OUT, exist_ok=True)
    frames = os.path.join(OUT, f"{eid}_frames"); mp4 = os.path.join(OUT, f"CurioKids_{eid}.mp4")
    sh([sys.executable, os.path.join(PIPE, "tts.py")], {"EPISODE": epf})
    sh([sys.executable, os.path.join(PIPE, "episode_engine.py"), frames], {"EPISODE": epf, "BG": "v2", "DOODLE": "chars"}, cwd=PIPE)
    sh([sys.executable, os.path.join(PIPE, "finish.py"), frames, "24", mp4])
    problems = qc(mp4, ep)
    rec = state["episodes"].setdefault(eid, {})
    rec.update({"title": ep["title"], "rendered_at": dt.datetime.now(IST).isoformat(timespec="seconds"),
                "duration_s": round(float(probe(mp4)["format"]["duration"]), 2)})
    if problems:
        rec.update({"status": "qc_failed", "problems": problems})
        json.dump(state, open(STATE, "w"), indent=2)
        print("QC FAILED - not uploading:", problems)
        summary(f"### ❌ QC failed for {eid} — nothing uploaded\n\n" + "\n".join(f"- {p}" for p in problems)); return 1
    from upload_youtube import have_credentials, upload
    if dry or not have_credentials():
        rec.update({"status": "rendered", "note": "dry run" if dry else "no YouTube credentials configured"})
        json.dump(state, open(STATE, "w"), indent=2)
        print("Rendered + QC passed (not uploaded):", mp4)
        summary(f"### 🎬 Rendered {eid} (not uploaded: {rec['note']})\n\n- {ep['title']} — {rec['duration_s']} s, QC passed\n- Download it from this run's **Artifacts**.")
        return 0
    if now_mode:
        vid = upload(mp4, ep, None); when = "immediately (public now, if the API project is audited)"
        rec["publish_at_ist"] = dt.datetime.now(IST).isoformat(timespec="minutes")
    else:
        slot = next_slot()
        vid = upload(mp4, ep, slot.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
        when = slot.strftime("%d %b %Y, %H:%M IST"); rec["publish_at_ist"] = slot.isoformat(timespec="minutes")
    rec.pop("note", None)
    rec.update({"status": "uploaded", "video_id": vid, "url": f"https://www.youtube.com/shorts/{vid}",
                "uploaded_at": dt.datetime.now(IST).isoformat(timespec="seconds")})
    json.dump(state, open(STATE, "w"), indent=2)
    print("Uploaded:", rec["url"], "publish:", when)
    summary(f"### ✅ Uploaded {eid}: {ep['title']}\n\n- Link: {rec['url']}\n- Publish: {when}\n- Length: {rec['duration_s']} s\n"
            "- Note: until the YouTube API audit is approved, YouTube keeps API uploads **Private** — "
            "set it to Public (or Schedule) in YouTube Studio → Content.")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, PIPE)
    sys.exit(main())
