"""Weekly art run, step 1 (roadmap R7, built 2026-11-23): what pictures/icons are MISSING for the upcoming episodes?
Same file in both repos. Writes art_requests.json for the Kaggle job (tools/kaggle/auto/art_auto.py).

    python pipeline/art_queue.py --days 7 --out out/art_requests     # prints how many requests

Looks at the next N unposted episodes of every queue (English/Hindi order, Spanish, long videos) plus a WANTED list:
  * icons: a board icon that has neither our house icon nor a Fluent 3D emoji (it would fall back to a flat drawing),
           house-only names ("w_...") without a file, and the WANTED list below (e.g. w_grass);
  * pictures: "picture"/"photo" boards whose "art" name has no file in assets/art/.
Each request gets a prompt in the house style (same wording as the hand-run notebooks). Nothing is generated here.
"""
import argparse, glob, json, os, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
KIDS = os.path.isdir(os.path.join(ROOT, "library"))

# icons we know we want, even if no episode uses them yet (key -> what to draw)
WANTED = {
    "w_grass": "a small tuft of fresh green grass blades growing from a little clump of soil",
} if KIDS else {}

ICON_STYLE = ("photorealistic 3D product render, highly detailed realistic materials and textures, soft studio lighting, "
              "gentle reflections, crisp focus, clean and friendly, a single object centered with empty space around it, "
              "isolated on a plain solid {bg} background, no text, no letters, no numbers, no logos, no watermark, no people, no hands")
KID3D = ("realistic 3D render in the style of a modern animated family film, soft rounded shapes, bright cheerful colours, "
         "soft warm cinematic lighting, gentle depth of field, high detail, friendly and safe for children, "
         "no text, no letters, no numbers, no logos, no watermark")
AIN3D = ("realistic 3D render, clean modern white and soft blue studio look, soft daylight, gentle depth of field, high detail, "
         "people only as hands if needed, no faces, no text, no letters, no numbers, no logos, no brand names, no watermark")


def _eps(folder):
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, folder, "*", "episode.json"))):
        try:
            e = json.load(open(f, encoding="utf-8")); e["_file"] = f; out.append(e)
        except Exception:
            pass
    out.sort(key=lambda e: (0, float(e["order"])) if isinstance(e.get("order"), (int, float)) else (1, 0.0))
    return out


def _state(folder):
    try:
        return json.load(open(os.path.join(ROOT, folder, "state.json"), encoding="utf-8")).get("episodes", {})
    except Exception:
        return {}


def upcoming(days):
    """Episodes likely to be made in the next `days` days, across the queues."""
    picked = []
    st = _state("episodes"); eps = [e for e in _eps("episodes") if e.get("status") == "ready"]
    per_day = 2 if KIDS else 1  # kids: English/Hindi + Spanish a day; AInation: one Short a day
    todo = [e for e in eps if (st.get(e["id"], {}) or {}).get("status") not in ("uploaded", "published", "manual")]
    picked += todo[:days * per_day]
    if KIDS:  # the Spanish queue runs in the same order on its own record
        todo_es = [e for e in eps if os.path.exists(os.path.join(os.path.dirname(e["_file"]), "es.json"))
                   and ((st.get(e["id"], {}) or {}).get("es") or {}).get("status") not in ("uploaded", "published", "manual")]
        picked += todo_es[:days]
    st_l = _state("long")
    picked += [e for e in _eps("long") if (st_l.get(e["id"], {}) or {}).get("status") not in ("uploaded", "published", "manual")][:1]
    seen, out = set(), []
    for e in picked:
        if e["_file"] not in seen: seen.add(e["_file"]); out.append(e)
    return out


def _walk_icons(o, found):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ("icon", "left", "right") and isinstance(v, str) and 0 < len(v) <= 40: found.add(v)
            else: _walk_icons(v, found)
    elif isinstance(o, list):
        for v in o: _walk_icons(v, found)


def _icon_words(e):
    try:
        return unicodedata.name(e[0]).lower()
    except Exception:
        return e


def missing(days):
    import icons3d
    reqs, seen = [], set()
    art_dir = os.path.join(ROOT, "assets", "art")
    have_art = {f.rsplit("_", 1)[0] for f in os.listdir(art_dir)} if os.path.isdir(art_dir) else set()
    for key, what in WANTED.items():
        if not os.path.exists(os.path.join(ROOT, "assets", "icons_house", key + ".webp")):
            reqs.append({"kind": "icon", "key": key, "what": what, "bg": "soft pastel pink", "why": "wanted list"}); seen.add(key)
    for e in upcoming(days):
        boards = [l.get("board") for l in e.get("lines", []) if l.get("board")]
        icons = set(); _walk_icons(boards, icons)
        for ic in icons:
            name = ic[6:] if ic.startswith("house:") else ic
            if name.startswith(("img:",)): continue
            if name.startswith("w_"):
                key = name
                if os.path.exists(os.path.join(ROOT, "assets", "icons_house", key + ".webp")) or key in seen: continue
                what = name[2:].replace("_", " ")
            else:
                if icons3d.path(name) or name in icons3d.NAMED: continue  # house icon or Fluent 3D exists
                key = icons3d.key(name)
                if key in seen: continue
                what = _icon_words(name)
            seen.add(key)
            reqs.append({"kind": "icon", "key": key, "what": f"a {what}", "bg": "light grey", "why": f"{e['id']} board icon"})
        for b in boards:
            nm = b.get("art") if isinstance(b, dict) else None
            if b and b.get("type") in ("picture", "photo", "clip") and nm and nm not in have_art and nm not in seen:
                seen.add(nm)
                what = b.get("caption") or b.get("stock") or b.get("text") or e.get("title", "")
                topic = e.get("title", "").split("?")[0]
                reqs.append({"kind": "picture", "key": nm, "what": f"{what}, illustrating: {topic}",
                             "style": KID3D if KIDS else AIN3D, "why": f"{e['id']} picture board"})
    for r in reqs:
        if r["kind"] == "icon": r["prompt"] = r["what"] + ", " + ICON_STYLE.format(bg=r["bg"])
        else: r["prompt"] = r["what"] + ", " + r["style"]
    return reqs


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=int(os.environ.get("ART_DAYS", "7") or 7))
    ap.add_argument("--out", default=os.path.join(ROOT, "out", "art_requests"))
    ap.add_argument("--max", type=int, default=40, help="cap per run (Kaggle time)")
    a = ap.parse_args(argv)
    reqs = missing(a.days)[:a.max]
    os.makedirs(a.out, exist_ok=True)
    json.dump({"channel": "kids" if KIDS else "aination", "requests": reqs}, open(os.path.join(a.out, "art_requests.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"{len(reqs)} request(s) for the next {a.days} days")
    for r in reqs: print(f"  {r['kind']:7s} {r['key']:24s} {r['why']}")
    if os.environ.get("GITHUB_OUTPUT"):
        open(os.environ["GITHUB_OUTPUT"], "a").write(f"count={len(reqs)}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
