"""Self-check: listen to the finished video and compare the speech with the script (roadmap R6, 2026-11-22).
Same file in both channels. Uses faster-whisper (MIT, runs on the CPU, no key). It only WARNS: it never blocks an upload.

    python pipeline/selfcheck.py out/video.mp4 episodes/ep081-.../episode.json

Result: share of the script's words heard in the right order (intro / outro music and extra words don't count
against it) and the first places where words went missing. English only for now (Hindi recognition is not reliable
enough to judge). Repo variable SELFCHECK=off turns it off; it is skipped quietly if faster-whisper isn't installed.
"""
import difflib, json, os, re, sys

WARN_BELOW = 0.85   # heard < 85 % of the script -> warning in the run summary (and an alert)


def _words(s):
    s = re.sub(r"\[[^\]]*\]", " ", s.lower())            # [laugh] style tags are not spoken words
    s = s.replace("’", "'")
    return re.findall(r"[a-z0-9']+", s)


def check(mp4, ep, model_name="base.en"):
    if os.environ.get("SELFCHECK", "on").strip().lower() in ("off", "0", "no", "false"): return None
    try:
        from faster_whisper import WhisperModel
    except Exception:
        print("note: self-check skipped (faster-whisper not installed)"); return None
    import subprocess, numpy as np
    # decode with ffmpeg (already used everywhere) instead of PyAV, whose newer versions broke faster-whisper's reader
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", mp4, "-f", "s16le", "-ac", "1", "-ar", "16000", "-"],
                         capture_output=True, check=True, timeout=300).stdout
    audio = np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0
    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    segs, _ = model.transcribe(audio, language="en", vad_filter=True, beam_size=1)
    heard = _words(" ".join(s.text for s in segs))
    script = _words(" ".join(l.get("text", "") for l in ep.get("lines", [])))
    if not script: return None
    sm = difflib.SequenceMatcher(None, script, heard, autojunk=False)
    matched = sum(b.size for b in sm.get_matching_blocks())
    missing = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "replace" and "".join(script[i1:i2]) == "".join(heard[j1:j2]):  # "grown up" heard as "grownup"
            matched += i2 - i1; continue
        if tag in ("delete", "replace") and i2 - i1 >= 2:
            missing.append(" ".join(script[i1:i2])[:60] + (f'  → heard "{" ".join(heard[j1:j2])[:40]}"' if tag == "replace" else "  → not heard"))
    score = matched / len(script)
    return {"heard": round(score, 3), "ok": score >= WARN_BELOW, "missing": missing[:5], "words": len(script)}


def markdown(r):
    if not r: return ""
    head = f"- Self-check: heard **{r['heard']:.0%}** of the script's {r['words']} words" + ("" if r["ok"] else " ⚠️ (below 85 %: listen to this one before it goes public)")
    return head + "".join(f"\n  - {m}" for m in r["missing"][:3])


if __name__ == "__main__":
    r = check(sys.argv[1], json.load(open(sys.argv[2], encoding="utf-8")))
    print(json.dumps(r, indent=1, ensure_ascii=False)); print(markdown(r))
