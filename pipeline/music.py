"""Original background music, different for every episode (synthesised here; no third-party audio, no licence issues).

    music = make_music(duration_s, seed="ep012", sr=48000)

The seed (normally the episode id) picks a style, chord progression, key, tempo, instruments, drum groove and a
small melody, so each episode gets its own track but the same episode always sounds the same when re-rendered.

Optional: put your own royalty-free tracks (.wav / .mp3 / .ogg, e.g. from the YouTube Audio Library) in
music/ at the repo root. If that folder has tracks, one is picked per episode instead of the synthesised one.
"""
import glob, hashlib, os, subprocess
import numpy as np

STYLES = {
    #        bpm range   pad           lead          bass     drums       swing
    "sunny":  ((100, 116), "organ",     "marimba",    "sine",  "pop",      0.0),
    "bouncy": ((108, 124), "soft",      "pluck",      "tri",   "bounce",   0.0),
    "chill":  ((82, 94),   "soft",      "bell",       "sine",  "halftime", 0.0),
    "playful": ((96, 110), "none",      "marimba",    "tri",   "shaker",   0.12),
    "dreamy": ((76, 88),   "organ",     "bell",       "sine",  "none",     0.0),
    "groovy": ((92, 104),  "soft",      "pluck",      "tri",   "funk",     0.1),
    "march":  ((104, 116), "none",      "pluck",      "sine",  "march",    0.0),
    "lofi":   ((80, 90),   "organ",     "pluck",      "sine",  "halftime", 0.14),
}
PROGS = [[1, 5, 6, 4], [1, 6, 4, 5], [6, 4, 1, 5], [1, 4, 5, 4], [2, 5, 1, 6], [1, 3, 4, 5], [4, 1, 5, 6], [1, 5, 4, 5],
         [1, 4, 6, 5], [6, 5, 4, 5]]
MAJOR = [0, 2, 4, 5, 7, 9, 11]
PENTA = [0, 2, 4, 7, 9]
hz = lambda m: 440.0 * 2 ** ((m - 69) / 12)


def _chord(root_midi, degree, seventh):
    notes = []
    for k in (0, 2, 4, 6) if seventh else (0, 2, 4):
        d = degree - 1 + k
        notes.append(root_midi + MAJOR[d % 7] + 12 * (d // 7))
    return notes


def _tone(kind, f, L, sr):
    tt = np.arange(L) / sr
    if kind == "marimba":
        return (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(2 * np.pi * 4 * f * tt) * np.exp(-tt * 30)) * np.exp(-tt * 7)
    if kind == "bell":
        return sum(a * np.sin(2 * np.pi * f * r * tt) * np.exp(-tt * d) for r, a, d in ((1, 1, 3.2), (2.76, 0.35, 6), (5.4, 0.15, 11)))
    if kind == "pluck":
        return sum(np.sin(2 * np.pi * f * h * tt) / h * np.exp(-tt * (6 + 5 * h)) for h in range(1, 7))
    return np.sin(2 * np.pi * f * tt) * np.exp(-tt * 5)


def _pad(kind, f, tt):
    if kind == "organ":
        return (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * 2 * f * tt) + 0.15 * np.sin(2 * np.pi * 3 * f * tt)) * 0.045
    return (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * 2 * f * tt + 0.5)) * 0.055


def _add(buf, s0, seg):
    if s0 >= buf.size or s0 < 0: return
    n = min(seg.size, buf.size - s0); buf[s0:s0 + n] += seg[:n]


def _drums(music, style, beat, N, sr, rng, swing):
    nb = int(N / sr / beat) + 1
    def kick(s0, a=0.22):
        L = int(0.25 * sr); tt = np.arange(L) / sr
        _add(music, s0, np.sin(2 * np.pi * (50 + 80 * np.exp(-tt * 25)) * tt) * np.exp(-tt * 12) * a)
    def hat(s0, a=0.03, dec=80):
        L = int(0.06 * sr); h = rng.standard_normal(L) * np.exp(-np.arange(L) / sr * dec) * a
        _add(music, s0, np.diff(np.concatenate([[0], h])))
    def clap(s0, a=0.07):
        L = int(0.15 * sr); n = rng.standard_normal(L) * np.exp(-np.arange(L) / sr * 22) * a
        _add(music, s0, np.convolve(n, np.ones(6) / 6, mode="same"))
    for k in range(nb):
        s = int(k * beat * sr); off = int((k + 0.5 + swing) * beat * sr)
        if style == "pop":
            kick(s); hat(off)
            if k % 2: clap(s)
        elif style == "bounce":
            kick(s); hat(off); hat(s, 0.015)
            if k % 4 == 3: kick(off, 0.15)
        elif style == "halftime":
            if k % 4 == 0: kick(s)
            if k % 4 == 2: clap(s, 0.06)
            hat(off, 0.022)
        elif style == "shaker":
            for q in range(4): hat(int((k + q / 4 + (swing if q % 2 else 0)) * beat * sr), 0.014, 120)
            if k % 4 == 0: kick(s, 0.15)
        elif style == "funk":
            if k % 4 in (0, 2): kick(s)
            if k % 4 == 3: kick(off, 0.16)
            if k % 2: clap(s, 0.06)
            hat(off, 0.025); hat(s, 0.012)
        elif style == "march":
            kick(s, 0.18); hat(off, 0.02)
            if k % 2: clap(s, 0.05); clap(int((k + 0.25) * beat * sr), 0.03)


def _file_track(dur, seed, sr):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files = sorted(f for e in ("wav", "mp3", "ogg", "flac") for f in glob.glob(os.path.join(root, "music", "*." + e)))
    if not files: return None
    f = files[int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(files)]
    try:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                             capture_output=True, check=True).stdout
        x = np.frombuffer(raw, np.float32).astype(np.float64)
        if x.size < sr: return None
        reps = int(np.ceil(dur * sr / x.size)); x = np.tile(x, reps)[: int(dur * sr)]
        print("music: using", os.path.basename(f))
        return x / max(1e-6, np.abs(x).max()) * 0.5
    except Exception as e:
        print("music: could not read", f, e); return None


def make_music(dur, seed="ep", sr=48000):
    own = _file_track(dur, seed, sr)
    if own is not None: return own
    rng = np.random.default_rng(int(hashlib.md5(seed.encode()).hexdigest()[:8], 16))
    name = list(STYLES)[rng.integers(len(STYLES))]
    (b0, b1), pad, lead, bass, drums, swing = STYLES[name]
    bpm = int(rng.integers(b0, b1 + 1)); beat = 60 / bpm; bar = beat * 4
    prog = PROGS[rng.integers(len(PROGS))]; key = 55 + int(rng.integers(0, 10))  # G3..E4
    seventh = bool(rng.integers(2)); arp = [[0, 2, 1, 3], [0, 1, 2, 1], [0, 2, 3, 2], [3, 2, 1, 0]][rng.integers(4)]
    print(f"music: {name}, {bpm} bpm, key {key}, progression {prog}")
    N = int(dur * sr); music = np.zeros(N)
    nbars = int(dur / bar) + 1
    for i in range(nbars):
        s0 = int(i * bar * sr); s1 = min(N, int((i + 1) * bar * sr))
        if s0 >= N: break
        tt = np.arange(s1 - s0) / sr
        env = np.minimum(1, tt / 0.25) * np.minimum(1, (bar - tt) / 0.3)
        ch = _chord(key, prog[i % 4], seventh)
        if pad != "none":
            for m in ch: music[s0:s1] += env * _pad(pad, hz(m), tt)
        bf = hz(ch[0] - 24)
        wave = np.sin(2 * np.pi * bf * tt) if bass == "sine" else 2 / np.pi * np.arcsin(np.sin(2 * np.pi * bf * tt))
        music[s0:s1] += env * wave * 0.11
    # arpeggio (lead instrument) on 8ths, with swing
    for k in range(int(dur / (beat / 2))):
        st = (k + (swing if k % 2 else 0)) * beat / 2
        ch = _chord(key, prog[int(st / bar) % 4], True)
        f = hz(ch[arp[k % 4]] + 12)
        _add(music, int(st * sr), _tone(lead, f, int(0.4 * sr), sr) * 0.045)
    # a short pentatonic melody every other bar pair (random walk, repeated so it feels like a tune)
    motif, step = [], int(rng.integers(0, 5))
    for _ in range(8):
        step = int(np.clip(step + rng.choice([-2, -1, 1, 1, 2]), 0, 9)); motif.append(step)
    rhythm = [0, 1, 1.5, 2, 3, 3.5, 4.5, 6][: len(motif)]
    for b in range(0, nbars, 4):
        for n_, r in zip(motif, rhythm):
            st = b * bar + r * beat
            if st >= dur: break
            m = key + 12 + PENTA[n_ % 5] + 12 * (n_ // 5)
            _add(music, int(st * sr), _tone("bell" if lead != "bell" else "marimba", hz(m), int(0.6 * sr), sr) * 0.04)
    _drums(music, drums, beat, N, sr, rng, swing)
    return music / max(1e-6, np.abs(music).max()) * 0.5
