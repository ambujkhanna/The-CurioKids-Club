"""Generate dialogue audio and exact per-phoneme timings (build/dialogue.wav + build/timing.json).

Voices: Kokoro (default), or Chatterbox when TTS_ENGINE=chatterbox and CB_PYTHON points to a Python that has
chatterbox-tts installed (see the workflow). With Chatterbox, each line is also read by Kokoro and the two are
matched (DTW on MFCC features) so lip-sync, captions and board cues stay on the right words. If Chatterbox fails
for any reason, the whole episode falls back to Kokoro.
Chatterbox exaggeration: CB_EXAGGERATION (0.5 natural .. 0.8 animated), or "exaggeration" in episode.json.
"""
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


def strip_tags(t):
    return re.sub(r"\s{2,}", " ", re.sub(r"\[[a-z_ ]+\]", "", t)).strip()


RAW = LINES
EP_FILE = os.environ.get("EPISODE")
if EP_FILE:  # data-driven episode (episodes/<id>/episode.json)
    _ep = json.load(open(EP_FILE))
    RAW = [(l["who"], l["text"]) for l in _ep["lines"]]  # may contain Chatterbox-Turbo tags like [laugh] [gasp]
    LINES = [(w, strip_tags(t)) for w, t in RAW]  # tags are performed, never shown or read by Kokoro
    # The CurioKids Club voices: [kokoro voice, speed, pitch shift in semitones (optional)]. Override per episode with "voices".
    VOICES = {"MIA": ("af_heart", 1.05), "LEO": ("af_sky", 1.08, 2.5), "DAD": ("am_michael", 0.95), "TEEN": ("af_heart", 1.05)}
    VOICES.update({k: tuple(v) for k, v in _ep.get("voices", {}).items()})
GAP = 0.28  # seconds between lines
if EP_FILE:
    GAP = float(_ep.get("gap") or os.environ.get("TTS_GAP") or 0.45)
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


def kokoro_line(spk, text):
    """Kokoro audio for one line + phonemes/words with times relative to the start of the clip."""
    voice, speed, semis = (tuple(VOICES[spk]) + (0,))[:3]
    ph = k.tokenizer.phonemize(text, "en-us")
    chars = [c for c in ph if c in vocab]
    toks = [vocab[c] for c in chars]
    style = k.get_voice_style(voice)[len(toks)]
    wav, dur = sess.run(None, {"input_ids": np.array([[0, *toks, 0]], np.int64),
                               "style": style, "speed": np.array([speed], np.float32)})
    wav = wav.ravel().astype(np.float32); dur = np.array(dur).ravel()
    assert abs(wav.size - dur.sum() * HOP) < HOP, (wav.size, dur.sum())
    edges = np.concatenate([[0], np.cumsum(dur)]) * HOP / SR
    phon = [(chars[i], edges[i + 1], edges[i + 2]) for i in range(len(chars))]
    words_txt = text.split()
    groups, cur = [], []
    for c, a, b in phon:
        if c == " ":
            if cur: groups.append(cur); cur = []
        else:
            cur.append((c, a, b))
    if cur: groups.append(cur)
    groups = [g for g in groups if any(re.match(r"\w", c) or c not in ".,!?;:…—\"'" for c, _, _ in g)]
    if len(groups) != len(words_txt):
        print("note: word timing via weighted fallback for:", text[:50])
        a0, b0 = phon[0][1], phon[-1][2]
        wts = [max(1, len([c for c in k.tokenizer.phonemize(w, "en-us") if c in vocab and c not in " .,!?"])) for w in words_txt]
        tot = sum(wts); acc = 0; words = []
        for w, n_ in zip(words_txt, wts):
            words.append((w, a0 + (b0 - a0) * acc / tot, a0 + (b0 - a0) * (acc + n_) / tot)); acc += n_
    else:
        words = [(w, g[0][1], g[-1][2]) for w, g in zip(words_txt, groups)]
    return wav, phon, words, edges[1], edges[-2], ph, semis


# ------------------------------------------------------------------ Chatterbox + alignment
def _mfcc(wav, hop=480, win=960, n_mel=40, n_cep=13):
    """MFCC features, 20 ms hop (numpy only)."""
    if wav.size < win: wav = np.pad(wav, (0, win - wav.size))
    n = 1 + (wav.size - win) // hop
    fr = np.lib.stride_tricks.as_strided(wav, (n, win), (wav.strides[0] * hop, wav.strides[0])) * np.hanning(win)
    spec = np.abs(np.fft.rfft(fr, 1024)) ** 2
    mel = lambda f: 2595 * np.log10(1 + f / 700)
    pts = 700 * (10 ** (np.linspace(mel(60), mel(7600), n_mel + 2) / 2595) - 1)
    bins = np.floor((1024 + 1) * pts / SR).astype(int)
    fb = np.zeros((n_mel, spec.shape[1]))
    for m in range(1, n_mel + 1):
        a, b, c = bins[m - 1], bins[m], bins[m + 1]
        if b > a: fb[m - 1, a:b] = (np.arange(a, b) - a) / (b - a)
        if c > b: fb[m - 1, b:c] = (c - np.arange(b, c)) / (c - b)
    lm = np.log(spec @ fb.T + 1e-8)
    dct = np.cos(np.pi / n_mel * (np.arange(n_mel) + 0.5)[None, :] * np.arange(n_cep)[:, None])
    cep = lm @ dct.T
    cep = cep[:, 1:]  # drop c0 (voices differ in loudness)
    cep = (cep - cep.mean(0)) / (cep.std(0) + 1e-6)
    # speech/silence feature so pauses line up with pauses (expressive readers pause longer)
    e = np.log((fr ** 2).mean(1) + 1e-10); e = (e - e.max()) / 10
    vad = (e > -0.45).astype(float)  # ~ -45 dB below the loudest frame
    cep = cep * vad[:, None]  # silence frames all look alike
    return np.hstack([cep, 4.0 * vad[:, None]])


def _dtw(A, B):
    """Monotonic alignment of feature sequences A (n) and B (m). Returns a time map: A frame -> B frame (float)."""
    n, m = len(A), len(B)
    C = np.sqrt(((A[:, None, :] - B[None, :, :]) ** 2).sum(-1))
    band = max(int(0.25 * max(n, m)), abs(n - m) + 10)
    D = np.full((n + 1, m + 1), np.inf); D[0, 0] = 0
    for i in range(1, n + 1):
        jc = i * m / n; lo, hi = max(1, int(jc - band)), min(m, int(jc + band))
        prev, row, ci = D[i - 1], D[i], C[i - 1]
        for j in range(lo, hi + 1):
            row[j] = ci[j - 1] + min(prev[j], prev[j - 1], row[j - 1])
    i, j, path = n, m, []
    while i > 0 and j > 0:
        path.append((i - 1, j - 1))
        k_ = int(np.argmin([D[i - 1, j - 1], D[i - 1, j], D[i, j - 1]]))
        i, j = (i - 1, j - 1) if k_ == 0 else (i - 1, j) if k_ == 1 else (i, j - 1)
    path.reverse()
    mp = np.zeros(n)
    for a in range(n):
        js = [b for x, b in path if x == a]
        mp[a] = np.mean(js) if js else (mp[a - 1] if a else 0)
    return np.maximum.accumulate(mp)


def _speech_span(wav, thr=0.02):
    """First/last sample with speech (energy above thr x peak, 10 ms frames)."""
    fr = wav[: wav.size // 240 * 240].reshape(-1, 240)
    e = np.sqrt((fr ** 2).mean(1)); on = np.where(e > thr * (e.max() + 1e-9))[0]
    if not on.size: return 0, wav.size
    return max(0, on[0] * 240 - 480), min(wav.size, (on[-1] + 1) * 240 + 960)


def align(kwav, ka, kb, cwav):
    """Map Kokoro times (speech from ka..kb s) onto the Chatterbox clip. Returns (trimmed clip, f(t))."""
    c0, c1 = _speech_span(cwav); cwav = cwav[c0:c1]
    ks, ke = int(ka * SR), int(kb * SR)
    A, B = _mfcc(kwav[ks:ke]), _mfcc(cwav)
    mp = _dtw(A, B) * 0.02  # Kokoro frame (20 ms) -> Chatterbox seconds
    ta = np.arange(len(mp)) * 0.02
    def f(t):
        return float(np.interp(t - ka, ta, mp, left=0, right=mp[-1] + (t - kb if t > kb else 0)))
    return cwav, f


LAUGH = re.compile(r"^(?:(?:ha|hah|hee|he|ho|heh)[\s,-]*)+[!.,…]*$", re.I)
SNORE = re.compile(r"^z{2,}[!.,…]*$", re.I)  # "Zzz", "Zzzz!" -> a cartoon snore sound, never read out
PAUSE_BEFORE_LAUGH, PAUSE_AFTER_LAUGH, PAUSE_SFX, PAUSE_JOIN = 0.55, 0.3, 0.25, 0.12


def chunks(raw):
    """Split a line into [(kind, text)], kind = "speech" (normal Chatterbox), "turbo" (Chatterbox-Turbo: laughs like
    'Ha ha!' and sentences with [tags]) or "sfx" (sound effect, e.g. 'Zzzz!'). Neighbouring speech parts are joined."""
    out = []
    for p in re.findall(r"[^.!?…]+(?:[.!?…]+|$)", raw.strip()):
        p = p.strip()
        if not p: continue
        m = re.match(r"^((?:(?:ha|hah|hee|he|ho|heh)[\s-]*)+[,.…]+)\s*(.+)$", p, re.I)  # "Hee hee, that's fancy!"
        for q in ([m.group(1), m.group(2)] if m else [p]):
            if SNORE.match(q):
                out.append(("sfx", "snore"))
            elif LAUGH.match(q):
                big = len(re.findall(r"ha|hee|he|ho", q, re.I)) > 1
                out.append(("turbo", q.rstrip(",") + (" [laugh]" if big else " [chuckle]")))
            elif re.search(r"\[[a-z_ ]+\]", q):
                out.append(("turbo", q))
            elif out and out[-1][0] == "speech":
                out[-1] = ("speech", out[-1][1] + " " + q)
            else:
                out.append(("speech", q))
    return out or [("speech", raw)]


def is_laugh(kind, text):
    return kind == "turbo" and ("[laugh]" in text or "[chuckle]" in text)


def chatterbox_all():
    """Generate every line with Chatterbox (in its own Python). Returns (list of wavs, lead pauses), or None."""
    import subprocess, tempfile
    import sfx
    py = os.environ.get("CB_PYTHON")
    if os.environ.get("TTS_ENGINE", "kokoro") != "chatterbox" or not py:
        return None
    vdir = os.path.join(S, "assets", "voices")
    refs = {n: os.path.join(vdir, n.lower() + ".wav") for n in ("MIA", "LEO", "DAD", "TEEN")}
    for a, b in (("TEEN", "MIA"), ("MIA", "TEEN")):  # a character without its own clip borrows the closest voice
        if not os.path.exists(refs[a]): refs[a] = refs[b]
    ex = float((_ep.get("exaggeration") if EP_FILE else None) or os.environ.get("CB_EXAGGERATION") or 0.5)
    cfg = float((_ep.get("cfg") if EP_FILE else None) or os.environ.get("CB_CFG") or 0.35)
    use_turbo = os.environ.get("CB_TURBO_LAUGHS", "1") == "1"
    seed0 = sum(map(ord, _ep.get("id", "x"))) if EP_FILE else 7
    d = tempfile.mkdtemp(); job = os.path.join(d, "job.json")
    items, plan = [], []
    for i, (spk, raw) in enumerate(RAW):
        cs = chunks(raw) if use_turbo else [("speech", strip_tags(raw))]
        parts = []
        for k, (kind, txt) in enumerate(cs):
            if kind == "sfx":
                parts.append((kind, txt, None)); continue
            parts.append((kind, txt, len(items)))
            items.append({"who": spk, "text": txt, "ex": ex, "cfg": cfg, "seed": seed0 * 100 + i * 7 + k, "turbo": kind == "turbo"})
        plan.append(parts)
    json.dump({"out": d, "refs": refs, "lines": items}, open(job, "w"))
    try:
        subprocess.run([py, os.path.join(S, "pipeline", "cb_gen.py"), job], check=True, timeout=3 * 3600)
        out, leads = [], []
        for i, parts in enumerate(plan):
            seg = []
            for k, (kind, txt, j) in enumerate(parts):
                if kind == "sfx":
                    w = sfx.snore(seed=i * 10 + k) * 0.8
                else:
                    w, sr = sf.read(os.path.join(d, f"line_{j}.wav"), dtype="float32")
                    w = w if w.ndim == 1 else w.mean(1)
                    assert sr == SR and w.size > SR * 0.2, "bad chatterbox audio"
                    a, b = _speech_span(w); w = w[a:b]
                    w = w / (np.percentile(np.abs(w), 99.5) + 1e-6) * 0.7  # match loudness between the two models
                if seg:  # comic timing: a beat before a laugh, a breath after it
                    prev_kind, prev_txt = parts[k - 1][0], parts[k - 1][1]
                    gap = PAUSE_BEFORE_LAUGH if is_laugh(kind, txt) else PAUSE_AFTER_LAUGH if is_laugh(prev_kind, prev_txt) \
                        else PAUSE_SFX if "sfx" in (kind, prev_kind) else PAUSE_JOIN
                    seg.append(np.zeros(int(gap * SR), np.float32))
                seg.append(w.astype(np.float32))
            out.append(np.concatenate(seg))
            leads.append(PAUSE_BEFORE_LAUGH * 0.6 if i and parts and is_laugh(parts[0][0], parts[0][1]) else 0.0)
        n_t = sum(1 for it in items if it["turbo"]); n_s = sum(1 for ps in plan for p_ in ps if p_[0] == "sfx")
        print(f"voices: Chatterbox (exaggeration {ex}, cfg {cfg}, gap {GAP}; {n_t} laugh/reaction parts with Turbo, {n_s} sound effects)")
        return out, leads
    except Exception as e:
        print("note: Chatterbox failed, using Kokoro voices:", e)
        return None


_cb = chatterbox_all()
CB, LEADS = (_cb if _cb else (None, None))
ENGINE = "chatterbox" if CB else "kokoro"
audio = [np.zeros(int(LEAD * SR), np.float32)]
t = LEAD
lines = []
for li, (spk, text) in enumerate(LINES):
    kwav, phon, words, ka, kb, ph, semis = kokoro_line(spk, text)
    if CB:
        if LEADS[li]:  # a reaction that starts with a laugh waits a beat after the previous line's punchline
            audio.append(np.zeros(int(LEADS[li] * SR), np.float32)); t += LEADS[li]
        wav, f = align(kwav, ka, kb, CB[li])
        phon = [(c, f(a), max(f(a), f(b))) for c, a, b in phon]
        words = [(w, f(a), max(f(a) + 0.04, f(b))) for w, a, b in words]
        ka, kb = f(ka), f(kb)
    else:
        wav = kwav
        if semis: wav = pitch_shift(wav, semis)
    peak = np.abs(wav).max(); wav = wav / (peak + 1e-9) * 0.85
    phon = [(c, t + a, t + b) for c, a, b in phon]; words = [(w, t + a, t + b) for w, a, b in words]
    start, end = t + ka, t + kb
    lines.append(dict(speaker=spk, text=text, start=start, end=end, phonemes=phon, words=words, ipa=ph))
    audio.append(wav); t += wav.size / SR
    audio.append(np.zeros(int(GAP * SR), np.float32)); t += GAP
    print(f"{spk:5s} {start:6.2f}-{end:6.2f} {text}")

audio.append(np.zeros(int(0.8 * SR), np.float32))
full = np.concatenate(audio)
sf.write(os.path.join(OUT, "dialogue.wav"), full, SR)
json.dump(dict(duration=full.size / SR, engine=ENGINE, lines=lines), open(os.path.join(OUT, "timing.json"), "w"), indent=1)
print("total", full.size / SR, "voices:", ENGINE)
