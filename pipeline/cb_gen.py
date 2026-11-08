"""Chatterbox voices (MIT, Resemble AI): runs inside its own Python environment (CB_PYTHON), called by tts.py.

    python cb_gen.py job.json     # job: {"lines": [{"who", "text", "ex", "cfg", "seed", "turbo"}], "refs": {...}, "out": dir}

Writes out/line_<i>.wav (24 kHz mono). Each character keeps their voice by cloning a short reference clip
(assets/voices/<name>.wav). "ex" is Chatterbox's exaggeration (0.5 natural .. 0.8 animated).
Items with "turbo": true use Chatterbox-Turbo, which performs tags like [laugh] [chuckle] [gasp] (used only for
short laughs/reactions - Turbo reads long lines too fast).
"""
import json, os, sys, time
import torch, torchaudio as ta

job = json.load(open(sys.argv[1], encoding="utf-8"))
torch.set_num_threads(os.cpu_count() or 4)
os.makedirs(job["out"], exist_ok=True)
_m = {}


def model(turbo):
    if turbo not in _m:
        if turbo:
            from chatterbox.tts_turbo import ChatterboxTurboTTS
            _m[turbo] = ChatterboxTurboTTS.from_pretrained(device="cpu")
        else:
            from chatterbox.tts import ChatterboxTTS
            _m[turbo] = ChatterboxTTS.from_pretrained(device="cpu")
    return _m[turbo]


for i, ln in enumerate(job["lines"]):
    t0 = time.time(); turbo = bool(ln.get("turbo"))
    torch.manual_seed(int(ln.get("seed", i)))
    m = model(turbo)
    if turbo:
        wav = m.generate(ln["text"], audio_prompt_path=job["refs"][ln["who"]])
    else:
        wav = m.generate(ln["text"], audio_prompt_path=job["refs"][ln["who"]],
                         exaggeration=float(ln.get("ex", 0.5)), cfg_weight=float(ln.get("cfg", 0.35)))
    if m.sr != 24000:
        wav = ta.functional.resample(wav, m.sr, 24000)
    ta.save(os.path.join(job["out"], f"line_{i}.wav"), wav.cpu(), 24000)
    print(f"chatterbox{' turbo' if turbo else ''} {i + 1}/{len(job['lines'])}: {time.time() - t0:.0f}s  {ln['text'][:60]}", flush=True)
