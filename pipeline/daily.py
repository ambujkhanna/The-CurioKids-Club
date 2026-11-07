"""Daily run: pick the next ready episode -> voices -> frames -> MP4 -> QC -> upload (publishes inside PUBLISH_WINDOW, IST).

    python pipeline/daily.py              # normal run (uploads only if YouTube secrets are set)
    python pipeline/daily.py --dry-run    # render + QC only
    python pipeline/daily.py --episode ep003   # force a specific episode
    python pipeline/daily.py --now             # publish immediately instead of scheduling
    python pipeline/daily.py --long            # weekly LONG video (16:9, 3-8 min) from long/<id>/episode.json
    python pipeline/daily.py --ig-test         # post a short test clip to Instagram only (diagnoses Instagram problems)
    python pipeline/daily.py --ig-test --episode ep004   # render ep004 and test versions of it on Instagram WITHOUT posting
    python pipeline/daily.py --social-backfill 3   # post up to 3 already-uploaded YouTube videos to Facebook/Instagram
    python pipeline/daily.py --fix-existing    # add already-uploaded videos to the playlist + apply MADE_FOR_KIDS
    python pipeline/daily.py --category quiz   # next episode of a category from library/<category>/<id>/episode.json
                                                 (comedy, quiz, knowledge, science, abc, counting, rhymes)

Publish time: a random 5-minute slot inside PUBLISH_WINDOW (IST, default "16:00-19:00"), today if there is still
time left in the window, otherwise tomorrow. Change the window via the repo variable PUBLISH_WINDOW.

State lives in episodes/state.json (committed back by the workflow). Fail-closed: any failed step
or QC check stops the run and nothing is uploaded.
"""
import datetime as dt, glob, json, os, random, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIPE = os.path.join(ROOT, "pipeline")
LONG = "--long" in sys.argv
CATEGORIES = ("comedy", "quiz", "knowledge", "science", "abc", "counting", "rhymes")
CATEGORY = sys.argv[sys.argv.index("--category") + 1] if "--category" in sys.argv else ""
CATEGORY = CATEGORY if CATEGORY in CATEGORIES else ""
EPDIR = os.path.join(ROOT, "long" if LONG else os.path.join("library", CATEGORY) if CATEGORY else "episodes")
STATE = os.path.join(EPDIR, "state.json")
OUT = os.path.join(ROOT, "out")
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
# Chatterbox voice style per category (exaggeration: 0.5 natural, 0.8 animated); an episode can set "exaggeration".
# cfg: lower = slower, more deliberate delivery (Chatterbox's advice for high exaggeration); gap: pause between lines (s)
EXAGGERATION = {"comedy": 0.8, "quiz": 0.8}
VOICE_CFG = {"comedy": 0.25, "quiz": 0.3}
LINE_GAP = {"comedy": 0.75, "quiz": 0.6}
VOICE_EX = str(EXAGGERATION.get(CATEGORY, 0.5))
VOICE_ENV = {"CB_EXAGGERATION": VOICE_EX, "CB_CFG": str(VOICE_CFG.get(CATEGORY, 0.35))}
if CATEGORY in LINE_GAP: VOICE_ENV["TTS_GAP"] = str(LINE_GAP[CATEGORY])
BRAND_LINE = "🌈 More fun science for curious kids: search The CurioKids Club on YouTube"


def sh(cmd, env=None, cwd=ROOT):
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True, cwd=cwd, env={**os.environ, **(env or {})})


def load_state():
    return json.load(open(STATE)) if os.path.exists(STATE) else {"episodes": {}}


def pick(state, forced=None):
    eps = []
    for f in sorted(glob.glob(os.path.join(EPDIR, "*", "episode.json"))):
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
    lo, hi, size = (90, 900, (1920, 1080)) if LONG else (20, 180, (1080, 1920))
    if not (lo <= dur <= hi): problems.append(f"duration {dur:.1f}s outside {lo}-{hi}s")
    if not v or (v[0]["width"], v[0]["height"]) != size: problems.append(f"video is not {size[0]}x{size[1]}")
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


def chapters(ep):
    """YouTube chapters (m:ss Title) from lines that carry "chapter"; needs >= 3, first at 0:00."""
    T = json.load(open(os.path.join(PIPE, "build", "timing.json")))
    marks = [(0.0 if i == 0 else T["lines"][i]["start"], l["chapter"]) for i, l in enumerate(ep["lines"]) if l.get("chapter")]
    if not marks or marks[0][0] > 0.5: marks.insert(0, (0.0, "Intro"))
    marks = [m for k, m in enumerate(marks) if k == 0 or m[0] - marks[k - 1][0] >= 10]
    if len(marks) < 3: return ""
    return "\n".join(f"{int(t // 60)}:{int(t % 60):02d} {name}" for t, name in [(0.0, marks[0][1])] + marks[1:])


def refresh_thumbnails():
    """Re-design and upload the thumbnail of every video already uploaded (e.g. after a thumbnail redesign)."""
    from upload_youtube import have_credentials, set_thumbnail
    if not have_credentials():
        print("No YouTube credentials - nothing to do."); return 0
    state = load_state(); eps = {}
    for f in glob.glob(os.path.join(EPDIR, "*", "episode.json")):
        e = json.load(open(f, encoding="utf-8")); eps[e["id"]] = f
    done = []
    for eid, rec in sorted(state["episodes"].items()):
        if rec.get("status") != "uploaded" or not rec.get("video_id") or eid not in eps: continue
        env = {"EPISODE": eps[eid], "BG": "kids", "DOODLE": "chars", "FORMAT": "long" if LONG else "short", "THUMB_ONLY": "1"}
        try:
            sh([sys.executable, os.path.join(PIPE, "tts.py")], {"EPISODE": eps[eid], "TTS_ENGINE": "kokoro"})  # thumbnail only: fast voices
            sh([sys.executable, os.path.join(PIPE, "episode_engine.py"), "x"], env, cwd=PIPE)
            os.makedirs(OUT, exist_ok=True)
            import shutil; dst = os.path.join(OUT, f"{eid}_thumbnail.jpg"); shutil.copy(os.path.join(PIPE, "build", "thumbnail.jpg"), dst)
            rec["thumbnail"] = set_thumbnail(rec["video_id"], dst)
        except Exception as e:
            rec["thumbnail"] = f"refresh failed: {e}"[:200]
        done.append(f"- {eid}: {rec['thumbnail']}")
        print(eid, rec["thumbnail"])
    json.dump(state, open(STATE, "w"), indent=2)
    summary("### 🖼️ Thumbnails refreshed\n\n" + ("\n".join(done) or "- no uploaded videos found"))
    return 0


def ig_test():
    """Post an 8-second test clip (made by ffmpeg) to Instagram only, plus account checks, to tell an account
    problem from a video problem. If it succeeds, delete the test Reel from Instagram afterwards."""
    import meta_post
    if not meta_post.have_ig():
        summary("### 🧪 Instagram test\n\n- META_PAGE_ID / META_PAGE_TOKEN / META_IG_USER_ID secrets are not all set"); return 0
    lines = []
    ig, tok = os.environ["META_IG_USER_ID"], os.environ["META_PAGE_TOKEN"]
    import urllib.parse
    q = urllib.parse.quote(tok)
    for label, url in (("Account", f"{meta_post.GRAPH}/{ig}?fields=username,name,media_count&access_token={q}"),
                       ("Publishing limit (24 h)", f"{meta_post.GRAPH}/{ig}/content_publishing_limit?fields=config,quota_usage&access_token={q}")):
        try:
            lines.append(f"- {label}: `{json.dumps(meta_post._req(url))[:300]}`")
        except Exception as e:
            lines.append(f"- {label}: failed: {e}"[:300])
    os.makedirs(OUT, exist_ok=True); clip = os.path.join(OUT, "ig_test.mp4")
    sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "testsrc2=size=1080x1920:rate=30:duration=8",
        "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=44100:duration=8",
        "-c:v", "libx264", "-profile:v", "high", "-level:v", "4.1", "-pix_fmt", "yuv420p", "-b:v", "4M",
        "-c:a", "aac", "-ar", "44100", "-ac", "2", "-b:a", "128k", "-shortest", "-movflags", "+faststart", clip])
    st = meta_post.post_instagram(clip, "Test post from The CurioKids Club automation (safe to delete).")
    lines.append(f"- Test clip (8 s, 1080x1920, H.264 + AAC): {st}")
    verdict = ("**The test clip posted, so the account and token work: the problem is in our episode videos.** "
               "Delete the test Reel from Instagram.") if st.startswith("posted") else \
              ("**Even a plain 8-second test clip failed, so the problem is the Instagram account, app or token, "
               "not our videos.** Post a Reel by hand in the Instagram app and check Settings > Account status.")
    summary("### 🧪 Instagram test\n\n" + "\n".join(lines) + "\n\n" + verdict)
    print("\n".join(lines)); return 0


def ig_episode_test(mp4, eid):
    import meta_post
    if not meta_post.have_ig():
        summary("### 🧪 Instagram test\n\n- META secrets are not all set"); return 0
    base = meta_post.ig_safe(mp4); dur = float(probe(base)["format"]["duration"])
    def cut(name, extra):
        out = os.path.join(OUT, f"igt_{name}.mp4")
        sh(["ffmpeg", "-y", "-loglevel", "error", "-i", base] + extra + ["-movflags", "+faststart", out]); return out
    enc = ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", "-b:v", "5M", "-c:a", "aac", "-ar", "44100", "-ac", "2"]
    tests = [(f"Full episode ({dur:.0f} s, Instagram copy)", base),
             ("First 30 s", cut("30", ["-t", "30"] + enc)),
             ("First 60 s", cut("60", ["-t", "60"] + enc)),
             ("First 89 s", cut("89", ["-t", "89"] + enc)) if dur > 89 else None,
             ("Full length, no audio", cut("mute", ["-an", "-c:v", "copy"])),
             ("Full length, 720x1280, 3 Mbps", cut("720", ["-vf", "scale=720:1280", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                                                         "-b:v", "3M", "-c:a", "aac", "-ar", "44100", "-ac", "2"]))]
    lines = []
    for t in [t for t in tests if t]:
        r = meta_post.ig_check(t[1]); lines.append(f"- {t[0]}: **{r}**"); print(lines[-1])
    summary(f"### 🧪 Instagram test with {eid} (nothing was posted)\n\n" + "\n".join(lines) +
            "\n\nSend this list to Claude: the versions Instagram accepts show what to change.")
    return 0


def social_backfill(n):
    """Post already-uploaded YouTube videos that are not on Facebook/Instagram yet (oldest first, n per run).
    Uses the Kokoro voices so the posted video matches the YouTube version. Shorts only (daily + categories)."""
    import meta_post
    if not meta_post.have_meta():
        summary("### 📣 Social backfill\n\n- META secrets are not set"); return 0
    todo = []
    for cat in ("",) + CATEGORIES:
        st_file = os.path.join(ROOT, "library", cat, "state.json") if cat else os.path.join(ROOT, "episodes", "state.json")
        if not os.path.exists(st_file): continue
        for eid, rec in json.load(open(st_file)).get("episodes", {}).items():
            if rec.get("status") != "uploaded": continue
            need = not str(rec.get("facebook", "")).startswith("posted") or \
                   (meta_post.have_ig() and not str(rec.get("instagram", "")).startswith("posted"))
            if need: todo.append((rec.get("uploaded_at", ""), eid, cat))
    todo.sort(); done = []
    for _, eid, cat in todo[:n]:
        cmd = [sys.executable, os.path.join(PIPE, "daily.py"), "--social-only", "--episode", eid] + (["--category", cat] if cat else [])
        r = subprocess.run(cmd, cwd=ROOT, env={**os.environ, "TTS_ENGINE": "kokoro", "GITHUB_STEP_SUMMARY": ""})
        st_file = os.path.join(ROOT, "library", cat, "state.json") if cat else os.path.join(ROOT, "episodes", "state.json")
        rec = json.load(open(st_file))["episodes"].get(eid, {})
        done.append(f"- {eid}: Facebook {rec.get('facebook', '-')} | Instagram {rec.get('instagram', '-')}" + ("" if r.returncode == 0 else " (render failed)"))
        print(done[-1])
    left = max(0, len(todo) - n)
    summary("### 📣 Social backfill\n\n" + ("\n".join(done) or "- nothing left to post: every uploaded video is on Facebook/Instagram") +
            (f"\n\n{left} more to go: run it again (or tomorrow)." if left else ""))
    return 0


def fix_existing():
    """Add every uploaded video to the playlist and apply MADE_FOR_KIDS to it (daily, long and category videos)."""
    from upload_youtube import have_credentials, add_to_playlist, playlist_videos, set_made_for_kids
    if not have_credentials():
        print("No YouTube credentials - nothing to do."); return 0
    try:
        have = playlist_videos() if (os.environ.get("YT_PLAYLIST") or "").strip() else None
    except Exception as e:
        have = None; print("could not read the playlist:", e)
    done = []
    for st_file in [os.path.join(ROOT, "episodes", "state.json"), os.path.join(ROOT, "long", "state.json")] + \
                   sorted(glob.glob(os.path.join(ROOT, "library", "*", "state.json"))):
        if not os.path.exists(st_file): continue
        state = json.load(open(st_file))
        for eid, rec in sorted(state.get("episodes", {}).items()):
            if rec.get("status") != "uploaded" or not rec.get("video_id"): continue
            rec["playlist"] = add_to_playlist(rec["video_id"], have)
            rec["made_for_kids"] = set_made_for_kids(rec["video_id"])
            done.append(f"- {eid}: playlist {rec['playlist']}; {rec['made_for_kids']}"); print(done[-1])
        json.dump(state, open(st_file, "w"), indent=2)
    summary("### 🔧 Existing videos updated\n\n" + ("\n".join(done) or "- no uploaded videos found"))
    return 0


def main():
    args = sys.argv[1:]
    if "--ig-test" in args and "--episode" not in args:
        return ig_test()
    if "--fix-existing" in args:
        return fix_existing()
    if "--social-backfill" in args:
        return social_backfill(int(args[args.index("--social-backfill") + 1]))
    if "--refresh-thumbnails" in args:
        return refresh_thumbnails()
    dry = "--dry-run" in args
    forced = args[args.index("--episode") + 1] if "--episode" in args else None
    now_mode = "--now" in args
    state = load_state()
    ep = pick(state, forced)
    if not ep:
        print(f"No ready episode left in the backlog. Add {os.path.relpath(EPDIR, ROOT)}/<id>/episode.json files."); return 0
    eid = ep["id"]; epf = ep["_file"]
    print(f"== {eid}: {ep['title']}")
    import images  # download any real illustrations this episode uses (from GitHub), before checking it
    try:
        images.fetch(images.used(json.load(open(ep["_file"], encoding="utf-8"))))
    except Exception as e:
        print("note: could not fetch pictures:", e)
    from validate_episode import check
    errs = check(epf)
    if errs:
        rec = state["episodes"].setdefault(eid, {}); rec.update({"status": "invalid", "problems": errs})
        json.dump(state, open(STATE, "w"), indent=2)
        print("Episode file invalid - not rendering:", errs); return 1
    os.makedirs(OUT, exist_ok=True)
    frames = os.path.join(OUT, f"{eid}_frames"); mp4 = os.path.join(OUT, f"CurioKids_{'long_' if LONG else ''}{eid}.mp4")
    def render(voice_env):
        import shutil; shutil.rmtree(frames, ignore_errors=True)
        sh([sys.executable, os.path.join(PIPE, "tts.py")], {"EPISODE": epf, **VOICE_ENV, **voice_env})
        sh([sys.executable, os.path.join(PIPE, "episode_engine.py"), frames], {"EPISODE": epf, "BG": "kids", "DOODLE": "chars", "FORMAT": "long" if LONG else "short"}, cwd=PIPE)
        sh([sys.executable, os.path.join(PIPE, "finish.py"), frames, "24", mp4], {"EPISODE": epf, "FORMAT": "long" if LONG else "short"})
    render({})
    if json.load(open(os.path.join(PIPE, "build", "timing.json"))).get("engine") == "chatterbox" and \
            float(probe(mp4)["format"]["duration"]) > (900 if LONG else 180):  # too long with the expressive voices
        print("note: video too long with Chatterbox voices - re-rendering with Kokoro voices")
        render({"TTS_ENGINE": "kokoro"})
    thumb = mp4[:-4] + "_thumbnail.jpg"
    if os.path.exists(os.path.join(PIPE, "build", "thumbnail.jpg")):
        import shutil; shutil.copy(os.path.join(PIPE, "build", "thumbnail.jpg"), thumb)
    else:
        thumb = None
    problems = qc(mp4, ep)
    rec = state["episodes"].setdefault(eid, {})
    rec["voices"] = json.load(open(os.path.join(PIPE, "build", "timing.json"))).get("engine", "kokoro")
    rec.update({"title": ep["title"], "rendered_at": dt.datetime.now(IST).isoformat(timespec="seconds"),
                "duration_s": round(float(probe(mp4)["format"]["duration"]), 2)})
    if problems:
        rec.update({"status": "qc_failed", "problems": problems})
        json.dump(state, open(STATE, "w"), indent=2)
        print("QC FAILED - not uploading:", problems)
        summary(f"### ❌ QC failed for {eid} — nothing uploaded\n\n" + "\n".join(f"- {p}" for p in problems)); return 1
    if LONG:  # chapters from the "chapter" markers + no #Shorts tag
        ch = chapters(ep)
        if ch: ep["description"] = ep["description"].rstrip() + "\n\nChapters:\n" + ch
        ep["hashtags"] = [h for h in ep.get("hashtags", []) if h.lower() != "#shorts"]
    from upload_youtube import have_credentials, upload, set_thumbnail, add_to_playlist, made_for_kids
    import meta_post
    if "--ig-test" in args:  # which version of this episode does Instagram accept? (nothing is posted)
        return ig_episode_test(mp4, eid)
    if "--social-only" in args and not dry:  # post this episode to Facebook / Instagram only (no YouTube)
        social = meta_post.post_all(mp4, ep, BRAND_LINE, LONG, rec) if meta_post.have_meta() else {"facebook": "no META secrets configured"}
        rec.update({k: v.replace(" (kept, not re-posted)", "") for k, v in social.items()}); json.dump(state, open(STATE, "w"), indent=2)
        print("Social only:", social)
        summary(f"### 📣 Social post for {eid}\n\n" + "\n".join(f"- {k.title()}: {v}" for k, v in social.items())); return 0
    if dry or not have_credentials():
        rec.update({"status": "rendered", "note": "dry run" if dry else "no YouTube credentials configured"})
        json.dump(state, open(STATE, "w"), indent=2)
        print("Rendered + QC passed (not uploaded):", mp4)
        summary(f"### 🎬 Rendered {eid} (not uploaded: {rec['note']})\n\n- {ep['title']} — {rec['duration_s']} s, QC passed, voices: {rec['voices']}\n- Download the video and its thumbnail from this run's **Artifacts**.")
        return 0
    if now_mode:
        vid = upload(mp4, ep, None); when = "immediately (public now, if the API project is audited)"
        rec["publish_at_ist"] = dt.datetime.now(IST).isoformat(timespec="minutes")
    else:
        slot = next_slot()
        vid = upload(mp4, ep, slot.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
        when = slot.strftime("%d %b %Y, %H:%M IST"); rec["publish_at_ist"] = slot.isoformat(timespec="minutes")
    rec.pop("note", None)
    rec["thumbnail"] = set_thumbnail(vid, thumb) if thumb else "not rendered"
    rec["playlist"] = add_to_playlist(vid)
    rec["made_for_kids"] = "yes" if made_for_kids() else "no"
    social = meta_post.post_all(mp4, ep, BRAND_LINE, LONG, rec)  # Facebook Page + Instagram (if META secrets are set)
    rec.update(social)
    rec.update({"status": "uploaded", "video_id": vid, "url": f"https://www.youtube.com/{'watch?v=' if LONG else 'shorts/'}{vid}",
                "uploaded_at": dt.datetime.now(IST).isoformat(timespec="seconds")})
    json.dump(state, open(STATE, "w"), indent=2)
    print("Uploaded:", rec["url"], "publish:", when)
    summary(f"### ✅ Uploaded {eid}: {ep['title']}\n\n- Link: {rec['url']}\n- Publish: {when}\n- Length: {rec['duration_s']} s\n- Voices: {rec['voices']}\n- Thumbnail: {rec['thumbnail']}\n- Playlist: {rec['playlist']}\n- Made for kids: {rec['made_for_kids']}\n" + "".join(f"- {k.title()}: {v}\n" for k, v in social.items()) +
            "- Note: until the YouTube API audit is approved, YouTube keeps API uploads **Private** — "
            "set it to Public (or Schedule) in YouTube Studio → Content.")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, PIPE)
    sys.exit(main())
