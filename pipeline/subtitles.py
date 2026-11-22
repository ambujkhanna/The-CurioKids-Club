"""Subtitles + translated titles on YouTube (roadmap R4, built 2026-11-22). Same file in both channels.

After an upload, daily.py calls add(). It never fails a run (returns a short status text).
  * Exact caption tracks from OUR script + word timing (pipeline/build/timing.json), not speech recognition:
      English video -> English track (word-timed)
      Spanish video -> Spanish track (word-timed) + English track (line-timed, from episode.json)
      Hindi video   -> Hindi track (line-timed, from hi.json) + English track (word-timed)
    Viewers in other languages use YouTube's own "Auto-translate" on these tracks.
  * Localizations (title + description shown to viewers whose YouTube is set to that language) from the files we already
    have: kids es.json / hi.json, and the English episode for the Spanish/Hindi versions. 50 quota units, no translator.
Quota (one Google Cloud project, 10,000 units/day for both channels): each caption track 400 units, so SUBS_TRACKS (default 2)
caps the tracks per video. Needs a YouTube login with the youtube.force-ssl scope (owner renewed both, 2026-11-22).
Repo variables: SUBS=on|off (default on), SUBS_TRACKS (default 2).
"""
import json, os, re, tempfile

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
LANG_NAMES = {"en": "English", "es": "Español", "hi": "हिन्दी", "pt": "Português"}
MAX_CHARS, MAX_SECS = 42, 3.2


def _ts(t):
    t = max(0.0, t); h, r = divmod(int(round(t * 1000)), 3600000); m, r = divmod(r, 60000); s, ms = divmod(r, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _clean(s):
    return re.sub(r"\s+", " ", re.sub(r"\[[a-z_ ]+\]", "", s or "")).strip()


def cues_from_words(lines, offset=0.0):
    """Word-timed cues: short phrases (≤ 42 chars, ≤ 3.2 s), never across two speakers."""
    out = []
    for ln in lines:
        cur, a = [], None
        for w, s, e in ln.get("words", []):
            w = _clean(w)
            if not w: continue
            if cur and (len(" ".join(cur + [w])) > MAX_CHARS or e - a > MAX_SECS):
                out.append((a, prev_e, " ".join(cur))); cur, a = [], None
            if a is None: a = s
            cur.append(w); prev_e = e
            if re.search(r"[.!?…]$", w) and len(" ".join(cur)) > 18:  # end of a sentence: start a new cue
                out.append((a, e, " ".join(cur))); cur, a = [], None
        if cur: out.append((a, prev_e, " ".join(cur)))
    return [(a + offset, b + offset, t) for a, b, t in out]


def cues_from_lines(lines, texts, offset=0.0):
    """Line-timed cues for a language that is not the one spoken: each line's text over that line's time, split by length."""
    out = []
    for ln, txt in zip(lines, texts):
        txt = _clean(txt)
        if not txt: continue
        parts = [p for p in re.split(r"(?<=[.!?…।])\s+", txt) if p]
        merged = []
        for p in parts:  # join tiny sentences, keep each cue readable
            if merged and len(merged[-1]) + len(p) < MAX_CHARS * 1.6: merged[-1] += " " + p
            else: merged.append(p)
        a, b = ln["start"], ln["end"]; tot = sum(len(p) for p in merged) or 1; acc = 0
        for p in merged:
            s = a + (b - a) * acc / tot; acc += len(p); e = a + (b - a) * acc / tot
            out.append((s + offset, e + offset, p))
    return out


def srt(cues):
    return "\n".join(f"{i}\n{_ts(a)} --> {_ts(max(b, a + 0.4))}\n{t}\n" for i, (a, b, t) in enumerate(cues, 1))


def _side(epf, name):
    p = os.path.join(os.path.dirname(epf), name)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def plan(epf, lang, timing, offset=0.0):
    """(tracks, localizations) for this video. tracks = [(lang, srt_text)], localizations = {lang: {title, description}}."""
    ep = json.load(open(epf, encoding="utf-8")); lines = timing["lines"]
    en_text = [_clean(l.get("text", "")) for l in ep.get("lines", [])]
    tracks, loc = [], {}
    if lang == "es":
        tracks.append(("es", srt(cues_from_words(lines, offset))))
        if len(en_text) == len(lines): tracks.append(("en", srt(cues_from_lines(lines, en_text, offset))))
        loc["en"] = {"title": ep["title"][:100], "description": ep.get("description", "")[:4900]}
    elif lang == "hi":
        hi = _side(epf, "hi.json")
        if hi and len(hi.get("lines", [])) == len(lines): tracks.append(("hi", srt(cues_from_lines(lines, hi["lines"], offset))))
        tracks.append(("en", srt(cues_from_words(lines, offset))))  # the Hindi timing carries the English words
        loc["en"] = {"title": ep["title"][:100], "description": ep.get("description", "")[:4900]}
    else:
        tracks.append(("en", srt(cues_from_words(lines, offset))))
        es, hi = _side(epf, "es.json"), _side(epf, "hi.json")
        if es: loc["es"] = {"title": es["title_es"][:100], "description": (es["description_es"].strip() + "\n\n" + ep.get("description", ""))[:4900]}
        if hi: loc["hi"] = {"title": hi["title_hi"][:100], "description": (hi["description_hi"].strip() + "\n\n" + ep.get("description", ""))[:4900]}
    return tracks, loc


def add(video_id, epf, lang="en", offset=0.0, timing_path=None):
    """Upload the caption tracks + localizations for one video. Returns a status text; never raises."""
    if os.environ.get("SUBS", "on").strip().lower() in ("off", "0", "no", "false"):
        return "off (SUBS=off)"
    try:
        timing = json.load(open(timing_path or os.path.join(HERE, "build", "timing.json"), encoding="utf-8"))
        tracks, loc = plan(epf, lang, timing, offset)
        tracks = tracks[:max(0, int(os.environ.get("SUBS_TRACKS", "2") or 2))]
        from upload_youtube import _service
        from googleapiclient.http import MediaFileUpload
        yt = _service(); done = []
        for lg, text in tracks:
            if not text.strip(): continue
            f = os.path.join(tempfile.mkdtemp(), f"{lg}.srt"); open(f, "w", encoding="utf-8").write(text)
            try:
                yt.captions().insert(part="snippet", body={"snippet": {"videoId": video_id, "language": lg,
                                                                      "name": LANG_NAMES.get(lg, lg), "isDraft": False}},
                                     media_body=MediaFileUpload(f, mimetype="application/octet-stream", resumable=False)).execute()
                done.append(lg)
            except Exception as e:
                done.append(f"{lg} failed ({_why(e)})")
        if loc:
            try:
                yt.videos().update(part="localizations", body={"id": video_id, "localizations": loc}).execute()
                done.append("titles: " + ", ".join(loc))
            except Exception as e:
                done.append(f"titles failed ({_why(e)})")
        return "; ".join(done) or "nothing to add"
    except Exception as e:
        return "skipped: " + _why(e)


def _why(e):
    m = str(e)
    if "insufficient" in m.lower() or "forbidden" in m.lower() or "403" in m:
        return "the YouTube login needs the youtube.force-ssl scope (docs/SETUP.md)"
    if "quota" in m.lower():
        return "daily YouTube API quota used up"
    return m[:120]


def intro_offset(extras):
    """Seconds the logo intro adds in front of the video (bumpers.wrap's result text)."""
    if isinstance(extras, str) and extras.startswith("added") and "intro" in extras:
        try:
            import bumpers; return float(bumpers.INTRO_S)
        except Exception:
            return 2.0
    return 0.0


if __name__ == "__main__":  # local check: python pipeline/subtitles.py episodes/<id>/episode.json [en|es|hi]
    import sys
    tr, lc = plan(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "en", json.load(open(os.path.join(HERE, "build", "timing.json"), encoding="utf-8")))
    for lg, t in tr: print(f"=== {lg}\n" + t[:900])
    print("localizations:", {k: v["title"] for k, v in lc.items()})
