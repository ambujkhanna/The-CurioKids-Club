"""Generate dialogue audio with Kokoro and exact per-phoneme timings."""
import json, os, re
import numpy as np, onnxruntime as ort, soundfile as sf
from kokoro_onnx import Kokoro

S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build"); os.makedirs(OUT, exist_ok=True)
SR, HOP = 24000, 600

VOICES = {"DAD": ("am_michael", 0.95), "TEEN": ("af_heart", 1.08)}
if os.environ.get("VARIANT") == "short":
    VOICES = {"DAD": ("am_michael", 1.02), "TEEN": ("af_heart", 1.14)}
VARIANT = os.environ.get("VARIANT", "full")
LOOP = "You got it! Follow AI Nation Studio for more. And next time someone asks... is an AI agent just a fancy chatbot?"
SCRIPTS = {
    "full": [
        ("DAD",  "Is an AI agent just a fancy chatbot?"),
        ("TEEN", "Not quite! A chatbot is like a smart helper you talk to. You ask a question, and it gives you an answer."),
        ("DAD",  "Like when I ask it for a pasta recipe?"),
        ("TEEN", "Exactly. It answers, and then it waits for your next message. You still do all the work."),
        ("DAD",  "So what does an agent do differently?"),
        ("TEEN", "An agent gets a goal, not just a question. It breaks the goal into steps, uses tools like search, calendars, or email, and then checks its own results."),
        ("DAD",  "Show me with a real example."),
        ("TEEN", "Say you want a weekend trip. A chatbot gives you a list of ideas. An agent checks the weather, compares train times, finds a hotel in your budget, and drafts the whole plan."),
        ("DAD",  "Wow. But I don't want it booking anything without asking me!"),
        ("TEEN", "And it shouldn't. Good agents ask your permission before important actions, like paying or sending emails. You stay in control."),
        ("DAD",  "Can agents make mistakes?"),
        ("TEEN", "Yes, they can. So always check their work, just like you would with a new assistant."),
        ("DAD",  "So, a chatbot answers. An agent acts."),
        ("TEEN", LOOP),
    ],
    "short": [
        ("DAD",  "Is an AI agent just a fancy chatbot?"),
        ("TEEN", "Not quite! A chatbot is a helper you talk to. You ask, it answers."),
        ("DAD",  "Like a pasta recipe?"),
        ("TEEN", "Exactly. It answers, then waits. You still do the work."),
        ("DAD",  "So what does an agent do differently?"),
        ("TEEN", "An agent gets a goal. It breaks it into steps, uses tools like search, calendars, or email, and checks its results."),
        ("DAD",  "Example?"),
        ("TEEN", "A weekend trip. A chatbot gives a list. An agent checks the weather, train times, a hotel in budget, and drafts the plan."),
        ("DAD",  "Wow. But I don't want it booking without asking me!"),
        ("TEEN", "It shouldn't. Good agents ask permission before paying or sending emails. You stay in control."),
        ("DAD",  "Can agents make mistakes?"),
        ("TEEN", "Yes. Always check their work, just like a new assistant's."),
        ("DAD",  "So, a chatbot answers. An agent acts."),
        ("TEEN", LOOP),
    ],
}
LINES = SCRIPTS[VARIANT]
EP_FILE = os.environ.get("EPISODE")
if EP_FILE:  # data-driven episode (episodes/<id>/episode.json)
    _ep = json.load(open(EP_FILE))
    LINES = [(l["who"], l["text"]) for l in _ep["lines"]]
    # Curio Kids Club voices: [kokoro voice, speed, pitch shift in semitones (optional)]. Override per episode with "voices".
    VOICES = {"MIA": ("af_heart", 1.05), "LEO": ("af_sky", 1.08, 2.5), "DAD": ("am_michael", 0.95), "TEEN": ("af_heart", 1.05)}
    VOICES.update({k: tuple(v) for k, v in _ep.get("voices", {}).items()})
GAP = 0.28  # seconds between lines
if EP_FILE:
    GAP = float(_ep.get("gap", 0.45))
LEAD = 0.25  # silence before first line

def pitch_shift(wav, semis):
    """Raise/lower the pitch without changing timing (ffmpeg rubberband). Falls back to the original audio."""
    import subprocess, tempfile
    d = tempfile.mkdtemp(); a, b = os.path.join(d, "a.wav"), os.path.join(d, "b.wav")
    sf.write(a, wav, SR)
    try:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", a, "-af",
                        f"rubberband=pitch={2 ** (semis / 12):.5f}:formant=shifted:pitchq=quality", b], check=True)
        out, _ = sf.read(b, dtype="float32")
        out = out if out.ndim == 1 else out.mean(1)
        out = np.pad(out, (0, max(0, wav.size - out.size)))[:wav.size]  # keep exact length -> lip-sync timing stays valid
        return out.astype(np.float32)
    except Exception as e:
        print("note: pitch shift unavailable, using normal voice:", e)
        return wav


k = Kokoro(os.path.join(S, "kokoro-q8.onnx"), os.path.join(S, "voices.bin"))
sess = ort.InferenceSession(os.path.join(S, "kokoro-dur.onnx"))
vocab = k.tokenizer.vocab

audio = [np.zeros(int(LEAD * SR), np.float32)]
t = LEAD
lines = []
for spk, text in LINES:
    voice, speed, semis = (tuple(VOICES[spk]) + (0,))[:3]
    ph = k.tokenizer.phonemize(text, "en-us")
    chars = [c for c in ph if c in vocab]
    toks = [vocab[c] for c in chars]
    style = k.get_voice_style(voice)[len(toks)]
    wav, dur = sess.run(None, {"input_ids": np.array([[0, *toks, 0]], np.int64),
                               "style": style, "speed": np.array([speed], np.float32)})
    wav = wav.ravel().astype(np.float32); dur = np.array(dur).ravel()
    assert abs(wav.size - dur.sum() * HOP) < HOP, (wav.size, dur.sum())
    # trim: keep BOS silence partly, it's natural lead-in
    edges = np.concatenate([[0], np.cumsum(dur)]) * HOP / SR
    phon = [(chars[i], t + edges[i + 1], t + edges[i + 2]) for i in range(len(chars))]
    # words: split phoneme string on spaces, align with text words
    words_txt = text.split()
    groups, cur = [], []
    for c, a, b in phon:
        if c == " ":
            if cur: groups.append(cur); cur = []
        else:
            cur.append((c, a, b))
    if cur: groups.append(cur)
    # drop groups that are only punctuation
    groups = [g for g in groups if any(re.match(r"\w", c) or c not in ".,!?;:…—\"'" for c, _, _ in g)]
    if len(groups) != len(words_txt):
        print("note: word timing via weighted fallback for:", text[:50])
        # fallback: spread the spoken span over the words, weighted by each word's own phoneme count
        a0, b0 = phon[0][1], phon[-1][2]
        wts = [max(1, len([c for c in k.tokenizer.phonemize(w, "en-us") if c in vocab and c not in " .,!?"])) for w in words_txt]
        tot = sum(wts); acc = 0; words = []
        for w, n_ in zip(words_txt, wts):
            words.append((w, a0 + (b0 - a0) * acc / tot, a0 + (b0 - a0) * (acc + n_) / tot)); acc += n_
    else:
        words = [(w, g[0][1], g[-1][2]) for w, g in zip(words_txt, groups)]
    if semis:
        wav = pitch_shift(wav, semis)
    peak = np.abs(wav).max(); wav = wav / peak * 0.85
    start, end = t + edges[1], t + edges[-2]
    lines.append(dict(speaker=spk, text=text, start=start, end=end, phonemes=phon, words=words, ipa=ph))
    audio.append(wav); t += wav.size / SR
    audio.append(np.zeros(int(GAP * SR), np.float32)); t += GAP
    print(f"{spk:5s} {start:6.2f}-{end:6.2f} {text}")

audio.append(np.zeros(int(0.8 * SR), np.float32))
full = np.concatenate(audio)
sf.write(os.path.join(OUT, "dialogue.wav"), full, SR)
json.dump(dict(duration=full.size / SR, lines=lines), open(os.path.join(OUT, "timing.json"), "w"), indent=1)
print("total", full.size / SR)
