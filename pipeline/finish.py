"""Mix audio (dialogue + original music bed + SFX), build word-highlight captions, encode MP4.

Usage: python finish.py <frames_dir> <fps_of_frames> <out.mp4>
"""
import json, os, subprocess, sys
import numpy as np, soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(HERE, "build")
frames, ffps, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
T = json.load(open(os.path.join(B, "timing.json")))
SH = json.load(open(os.path.join(B, "shots.json")))
SR = 48000
DUR = T["duration"]
N = int(DUR * SR)
rng = np.random.default_rng(3)

# ---------------------------------------------------------------- dialogue
d, sr = sf.read(os.path.join(B, "dialogue.wav"))
d = np.interp(np.arange(N) / SR, np.arange(d.size) / sr, d)

# ---------------------------------------------------------------- original music bed: a different track per episode (music.py)
from music import make_music
t = np.arange(N) / SR
_ep = os.environ.get("EPISODE")
SEED = json.load(open(_ep, encoding="utf-8"))["id"] if _ep and os.path.exists(_ep) else T["lines"][0]["text"]
music = make_music(DUR, SEED, SR)[:N]
music = np.pad(music, (0, N - music.size))
# fade in/out and duck under speech
fade = np.minimum(1, t / 1.0) * np.minimum(1, (DUR - t) / 1.2)
duck = np.ones(N)
for ln in T["lines"]:
    a, b = int((ln["start"] - 0.15) * SR), int((ln["end"] + 0.15) * SR)
    duck[max(0, a):min(N, b)] = 0.35
k = int(0.12 * SR); duck = np.convolve(duck, np.ones(k) / k, mode="same")
music *= fade * duck * 0.55

# ---------------------------------------------------------------- SFX: pops on holo elements, whoosh on cuts
sfx = np.zeros(N)
for p in SH["pops"]:
    s0 = int(p * SR); L = int(0.12 * SR); tt = np.arange(L) / SR
    blip = np.sin(2 * np.pi * (500 + 900 * tt / 0.12) * tt) * np.exp(-tt * 35) * 0.16
    sfx[s0:s0 + L] += blip[: max(0, min(L, N - s0))]
for tc, _ in SH["shots"][1:]:
    s0 = int((tc - 0.12) * SR); L = int(0.3 * SR)
    w = rng.standard_normal(L); w = np.convolve(w, np.ones(40) / 40, mode="same")
    env = np.sin(np.linspace(0, np.pi, L)) ** 2 * 0.05
    sfx[s0:s0 + L] += (w * env)[: max(0, min(L, N - s0))]

mix = d * 0.95 + music + sfx
mix = mix / max(1.0, np.abs(mix).max() / 0.95)
wav = os.path.join(B, "mix.wav"); sf.write(wav, np.stack([mix, mix], 1), SR)

# ---------------------------------------------------------------- captions (ASS, word highlight)
def ts(x):
    x = max(0, x); h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f"{h}:{m:02d}:{s:05.2f}"

ass = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "WrapStyle: 2", "",
       "[V4+ Styles]",
       "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
       "Style: Cap,Inter ExtraBold,82,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,7,3,2,60,60,330,1",
       "Style: Who,Inter ExtraBold,40,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,2,0,1,5,0,2,60,60,450,1",
       "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
HL = {"DAD": "&H00FFC04F&", "TEEN": "&H0000D6FF&", "MIA": "&H0097DC3D&", "LEO": "&H0000D6FF&"}  # BGR
for ln in T["lines"]:
    words = []
    for w in ln["words"]:
        if words and words[-1][0] == "Curio" and w[0].lower().startswith("kids"):
            words[-1] = ["CurioKids", words[-1][1], w[2]]
        else:
            words.append(list(w))
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) == 3 or w[0][-1] in ".,!?" :
            chunks.append(cur); cur = []
    if cur: chunks.append(cur)
    for ci, ch in enumerate(chunks):
        c_end = chunks[ci + 1][0][1] if ci + 1 < len(chunks) else ln["end"] + 0.25
        for wi, w in enumerate(ch):
            a = w[1] if wi else (ch[0][1] if ci else ch[0][1] - 0.05)
            b = ch[wi + 1][1] if wi + 1 < len(ch) else c_end
            parts = []
            for wj, w2 in enumerate(ch):
                txt = w2[0] if w2[0] == "CurioKids" else w2[0].upper()
                if wj == wi:
                    parts.append(f"{{\\c{HL.get(ln['speaker'], '&H0000D6FF&')}\\fscx108\\fscy108}}{txt}{{\\c&H00FFFFFF&\\fscx100\\fscy100}}")
                else:
                    parts.append(txt)
            pop = "{\\fad(40,0)}" if wi == 0 else ""
            ass.append(f"Dialogue: 0,{ts(a)},{ts(b)},Cap,,0,0,0,,{pop}{' '.join(parts)}")
if os.environ.get("DOODLE") == "1":
    ass = [l.replace("Style: Cap,Inter ExtraBold,82,", "Style: Cap,Patrick Hand,96,") for l in ass]
assf = os.path.join(B, "captions.ass"); open(assf, "w").write("\n".join(ass) + "\n")

# ---------------------------------------------------------------- encode
cmd = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(ffps), "-pattern_type", "glob", "-i", os.path.join(frames, "f*.png"),
       "-i", wav, "-vf", f"scale=1080:1920:flags=lanczos,fps=24,ass={assf}:fontsdir={os.path.join(os.path.dirname(HERE), 'fonts')}",
       "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-profile:v", "high",
       "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", out]
subprocess.run(cmd, check=True)
print("OK", out)
