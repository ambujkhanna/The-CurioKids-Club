"""Chatterbox voices (MIT, Resemble AI): runs inside its own Python environment (CB_PYTHON), called by tts.py.

    python cb_gen.py job.json     # job: {"lines": [{"who", "text", "ex", "seed"}], "refs": {"MIA": wav, ...}, "out": dir}

Writes out/line_<i>.wav (24 kHz mono). Each character keeps their voice by cloning a short reference clip
(assets/voices/<name>.wav). "ex" is Chatterbox's exaggeration: 0.5 = natural, 0.8 = very animated.
"""
import json, os, sys, time
import torch, torchaudio as ta
from chatterbox.tts import ChatterboxTTS

job = json.load(open(sys.argv[1], encoding="utf-8"))
torch.set_num_threads(os.cpu_count() or 4)
model = ChatterboxTTS.from_pretrained(device="cpu")
os.makedirs(job["out"], exist_ok=True)
for i, ln in enumerate(job["lines"]):
    t0 = time.time()
    torch.manual_seed(int(ln.get("seed", i)))
    wav = model.generate(ln["text"], audio_prompt_path=job["refs"][ln["who"]],
                         exaggeration=float(ln.get("ex", 0.5)), cfg_weight=float(ln.get("cfg", 0.35)))
    if model.sr != 24000:
        wav = ta.functional.resample(wav, model.sr, 24000)
    ta.save(os.path.join(job["out"], f"line_{i}.wav"), wav.cpu(), 24000)
    print(f"chatterbox line {i + 1}/{len(job['lines'])}: {time.time() - t0:.0f}s", flush=True)
