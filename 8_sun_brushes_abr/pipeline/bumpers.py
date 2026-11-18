"""Intro + outro around every video (owner, 2026-11-11). Same file in both channels.

  intro  (2.0 s): "Welcome to" + animated channel logo, light rays, sparkles, original music sting, white flash into the video
  outro  (3.5 s): "Find us online" card with the channel's YouTube / Facebook / Instagram links (readable, numbered rows)

    import bumpers; bumpers.wrap("out/video.mp4", long=False)     # adds both in place (re-encodes once)

Switch off with repo variables INTRO=off / OUTRO=off. Shorts stay under 180 s: if adding them would go over,
they are left out (logged). All drawing and music are generated here (no third-party assets); the kids logo is the
owner's own artwork (assets/brand/logo.png).
"""
import math, os, random, subprocess, sys, tempfile
import numpy as np
import skia

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import hashtags as HT

KIDS = HT.KIDS
FPS, SR = 24, 48000
INTRO_S, OUTRO_S = 2.0, 3.5
NAVY = "#1F2D44"
LINKS = HT.LINKS
HINDI = os.environ.get("TTS_LANG", "en") == "hi"


def _font(name):
    p = os.path.join(ROOT, "fonts", name)
    return skia.Typeface.MakeFromFile(p) if os.path.exists(p) else skia.Typeface("Arial", skia.FontStyle.Bold())


if KIDS:
    F_HEAD, F_BODY, F_LINK = _font("LilitaOne-Regular.ttf"), _font("Poppins-Bold.ttf"), _font("Poppins-Bold.ttf")
else:
    F_HEAD, F_BODY, F_LINK = _font("MPLUSU-ExtraBold.ttf"), _font("MPLUSU-Bold.ttf"), _font("MPLUSU-SemiBold.ttf")


def _c(h, a=1.0):
    h = h.lstrip("#"); return skia.Color(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(255 * max(0, min(1, a))))


def _p(col, a=1.0, stroke=None):
    p = skia.Paint(AntiAlias=True, Color=_c(col, a))
    if stroke: p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke)
    return p


def _ease(u):
    u = max(0.0, min(1.0, u)); return u * u * (3 - 2 * u)


def _back(u):  # ease-out with a little overshoot
    u = max(0.0, min(1.0, u)); s = 1.9; u -= 1; return u * u * ((s + 1) * u + s) + 1


def _elastic(u):
    if u <= 0: return 0.0
    if u >= 1.4: return 1.0
    return 1 - math.exp(-6.5 * u) * math.cos(11 * u)


def _text(c, s, x, y, size, col, tf, a=1.0, maxw=None, align="c"):
    """Text centred vertically on y; shrinks to fit maxw. Hindi goes through HarfBuzz (kids deva.py)."""
    if any("ऀ" <= ch <= "ॿ" for ch in s):
        try:
            import deva
            return deva.draw(c, s, x, y, size, _p(col, a), align)
        except Exception:
            pass
    f = skia.Font(tf, size)
    while maxw and f.measureText(s) > maxw and size > 16:
        size -= 1; f = skia.Font(tf, size)
    w = f.measureText(s); x0 = {"c": x - w / 2, "l": x, "r": x - w}[align]
    c.drawString(s, x0, y + size * 0.36, f, _p(col, a))
    return w


def _bg(c, W, H, t):
    if KIDS:
        g = skia.Paint(); g.setShader(skia.GradientShader.MakeLinear([(0, 0), (0, H)], [_c("#7FDBFF"), _c("#2F80ED")]))
    else:
        g = skia.Paint(); g.setShader(skia.GradientShader.MakeRadial((W / 2, H * 0.45), max(W, H) * 0.75, [_c("#2A4470"), _c("#0B1424")]))
    c.drawRect(skia.Rect.MakeWH(W, H), g)
    cx, cy = W / 2, H * (0.45 if H > W else 0.47)
    c.save(); c.translate(cx, cy); c.rotate(t * 22)  # slow light rays
    ray = skia.Path()
    R = max(W, H)
    for k in range(14):
        a0, a1 = math.radians(k * 360 / 14), math.radians(k * 360 / 14 + 9)
        ray.moveTo(0, 0); ray.lineTo(R * math.cos(a0), R * math.sin(a0)); ray.lineTo(R * math.cos(a1), R * math.sin(a1)); ray.close()
    c.drawPath(ray, _p("#FFFFFF", 0.10 if KIDS else 0.05))
    c.restore()
    if not KIDS:  # faint tech grid
        gp = _p("#5B8BD9", 0.10, 1.5); step = 90
        for x in range(0, W + 1, step): c.drawLine(x, 0, x, H, gp)
        for y in range(0, H + 1, step): c.drawLine(0, y, W, y, gp)
    rnd = random.Random(7)  # drifting confetti / particles
    cols = ["#FFD23F", "#FF6B9A", "#7CF29C", "#FFFFFF", "#B388FF"] if KIDS else ["#FFC93C", "#5AC8FA", "#FFFFFF"]
    for i in range(46):
        x = rnd.uniform(0, W); y = (rnd.uniform(0, H) + t * rnd.uniform(60, 180)) % H; r = rnd.uniform(4, 10)
        col = cols[i % len(cols)]
        if KIDS:
            c.save(); c.translate(x, y); c.rotate(t * 120 + i * 30)
            c.drawRect(skia.Rect.MakeXYWH(-r, -r / 2, 2 * r, r), _p(col, 0.85)); c.restore()
        else:
            c.drawCircle(x, y, r * 0.55, _p(col, 0.55))


def _sparkle(c, x, y, s, a, col="#FFFFFF"):
    p = skia.Path(); p.moveTo(x, y - s); p.quadTo(x, y, x + s, y); p.quadTo(x, y, x, y + s); p.quadTo(x, y, x - s, y); p.quadTo(x, y, x, y - s)
    c.drawPath(p, _p(col, a))


_LOGO = {}


def _logo_img():
    if "img" not in _LOGO:
        p = os.path.join(ROOT, "assets", "brand", "logo.png")
        _LOGO["img"] = skia.Image.MakeFromEncoded(skia.Data.MakeWithCopy(open(p, "rb").read())) if os.path.exists(p) else None
    return _LOGO["img"]


def _draw_logo(c, cx, cy, size, a=1.0):
    """Kids: the owner's round logo. AInation: big yellow 'AI' badge + wordmark."""
    img = _logo_img() if KIDS else None
    if img:
        r = size / 2
        sh = _p("#000000", 0.25 * a); sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 18))
        c.drawCircle(cx, cy + 14, r, sh)
        c.drawImageRect(img, skia.Rect.MakeXYWH(cx - r, cy - r, size, size), skia.SamplingOptions(skia.FilterMode.kLinear), _p("#FFFFFF", a))
        c.drawCircle(cx, cy, r, _p("#FFFFFF", a, 10))
        return
    b = size * 0.62
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(cx - b / 2, cy - b / 2, b, b), b * 0.24, b * 0.24)
    sh = _p("#000000", 0.35 * a); sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 22))
    c.save(); c.translate(0, 18); c.drawRRect(r, sh); c.restore()
    g = skia.Paint(AntiAlias=True)
    g.setShader(skia.GradientShader.MakeLinear([(0, cy - b / 2), (0, cy + b / 2)], [_c("#FFE07A", a), _c("#FFB800", a)]))
    c.drawRRect(r, g)
    _text(c, "AI", cx, cy + b * 0.02, b * 0.52, NAVY, F_HEAD, a)


def _intro_frame(c, W, H, t):
    _bg(c, W, H, t)
    tall = H > W
    cx, cy = W / 2, H * (0.45 if tall else 0.47)
    size = (560 if KIDS else 520) if tall else (430 if KIDS else 400)
    s = _elastic(t / 0.9)
    glow = 0.5 + 0.5 * math.sin(t * 6)
    halo = _p("#FFFFFF", 0.20 + 0.12 * glow); halo.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 40))
    c.drawCircle(cx, cy, size * 0.62 * max(0.01, s), halo)
    c.save(); c.translate(cx, cy); c.rotate(-14 * (1 - min(1.0, t / 0.6))); c.scale(max(0.01, s), max(0.01, s)); c.translate(-cx, -cy)
    _draw_logo(c, cx, cy, size)
    c.restore()
    for k in range(8):  # sparkle burst when the logo lands
        u = (t - 0.45) / 0.7
        if 0 < u < 1:
            ang = math.radians(k * 45 + 20); d = size * (0.55 + 0.45 * _ease(u))
            _sparkle(c, cx + d * math.cos(ang), cy + d * math.sin(ang), 26 * (1 - u) + 6, 1 - u, "#FFF3A0")
    hi = "आपका स्वागत है" if (KIDS and HINDI) else "Welcome to"
    a1 = _ease((t - 0.25) / 0.35); dy = 40 * (1 - _back((t - 0.25) / 0.45))
    head_y = cy - size * 0.5 - (150 if tall else 95)
    _text(c, hi, cx, head_y + dy, 84 if tall else 70, "#FFFFFF", F_HEAD, a1, W - 120)
    a2 = _ease((t - 0.55) / 0.35); sc = 0.6 + 0.4 * _back((t - 0.55) / 0.45)
    name_y = cy + size * 0.5 + (130 if tall else 85)
    c.save(); c.translate(cx, name_y); c.scale(sc, sc); c.translate(-cx, -name_y)
    pill_w = min(W - 100, (820 if tall else 900)); ph = 120 if tall else 104
    pr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(cx - pill_w / 2, name_y - ph / 2, pill_w, ph), ph / 2, ph / 2)
    c.drawRRect(pr, _p("#FFC93C" if not KIDS else "#FFFFFF", a2))
    _text(c, HT.NAME, cx, name_y, 74 if tall else 64, NAVY, F_HEAD, a2, pill_w - 80)
    c.restore()
    if t > INTRO_S - 0.22:  # white flash into the video
        c.drawRect(skia.Rect.MakeWH(W, H), _p("#FFFFFF", (t - (INTRO_S - 0.22)) / 0.22))


ROW_COLS = ["#FF0033", "#1877F2", "#C13584"]  # YouTube red, Facebook blue, Instagram magenta (plain colours, no logos)


def _outro_frame(c, W, H, t):
    _bg(c, W, H, t * 0.5)
    tall = H > W
    m = 60 if tall else 240
    top, bot = (220, H - 300) if tall else (50, H - 120)
    a0 = _ease(t / 0.3); lift = 60 * (1 - _back(t / 0.45))
    card = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(m, top + lift, W - m, bot + lift), 48, 48)
    sh = _p("#000000", 0.30 * a0); sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 26))
    c.save(); c.translate(0, 14); c.drawRRect(card, sh); c.restore()
    c.drawRRect(card, _p("#FFFFFF", a0))
    c.drawRRect(card, _p(NAVY, a0 * 0.15, 3))
    cx = W / 2; y = top + lift + (175 if tall else 95)
    _draw_logo(c, cx, y, (230 if KIDS else 250) if tall else 140, a0)
    y += 185 if tall else 112
    _text(c, "Find us online" if not (KIDS and HINDI) else "हमें यहाँ ढूँढें", cx, y, 80 if tall else 60, NAVY, F_HEAD, a0)
    y += 78 if tall else 56
    _text(c, f"Search \"{HT.NAME}\" or open:", cx, y, 38 if tall else 30, "#5B6B82", F_BODY, a0, W - 2 * m - 80)
    row_h = 250 if tall else 165; gap = 30 if tall else 18
    y += (70 if tall else 50) + row_h / 2
    inner_l, inner_r = m + 36, W - m - 36
    for i, (label, url) in enumerate(LINKS):
        u = (t - 0.35 - i * 0.22) / 0.4; a = _ease(u); dx = 80 * (1 - _back(u))
        if a <= 0: continue
        ry = y + i * (row_h + gap)
        box = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(inner_l + dx, ry - row_h / 2, inner_r + dx, ry + row_h / 2), 30, 30)
        c.drawRRect(box, _p("#F3F6FB", a))
        c.drawRRect(box, _p(ROW_COLS[i], a * 0.55, 3))
        nr = 36 if tall else 30; nx = inner_l + dx + 26 + nr
        c.drawCircle(nx, ry - (50 if tall else 34), nr, _p(ROW_COLS[i], a))
        _text(c, str(i + 1), nx, ry - (50 if tall else 34), 42 if tall else 36, "#FFFFFF", F_HEAD, a)
        tx = nx + nr + 22; tw = inner_r + dx - 26 - tx
        _text(c, label, tx, ry - (50 if tall else 34), 50 if tall else 40, NAVY, F_HEAD, a, tw, "l")
        lx = inner_l + dx + 34; lw = inner_r + dx - 34 - lx; ls = 38 if tall else 32
        if skia.Font(F_LINK, ls).measureText(url) <= lw:  # the link, full width under the label
            _text(c, url, lx, ry + (42 if tall else 30), ls, "#1456C8", F_LINK, a, lw, "l")
        else:  # too long for one line at a readable size: break after the domain
            k = url.find("/", 8) + 1
            _text(c, url[:k], lx, ry + (24 if tall else 18), ls, "#1456C8", F_LINK, a, lw, "l")
            _text(c, url[k:], lx, ry + (72 if tall else 52), ls, "#1456C8", F_LINK, a, lw, "l")
    c.drawRect(skia.Rect.MakeWH(W, H), _p("#000000", max(0.0, (t - (OUTRO_S - 0.35)) / 0.35)))  # fade to black


# ------------------------------------------------------------------------------------------- music (generated)
def _tone(f, dur, decay, amp=1.0, harm=(1.0, 0.45, 0.22, 0.1)):
    n = int(dur * SR); tt = np.arange(n) / SR
    w = sum(h * np.sin(2 * np.pi * f * (k + 1) * tt) for k, h in enumerate(harm))
    return (amp * w * np.exp(-tt / decay) * np.minimum(1, tt / 0.004)).astype(np.float32)


def _add(buf, sig, at):
    i = int(at * SR); j = min(buf.size, i + sig.size)
    if i < buf.size: buf[i:j] += sig[: j - i]


def _intro_audio():
    n = int(INTRO_S * SR); out = np.zeros(n, np.float32); rnd = np.random.default_rng(3)
    wl = int(0.55 * SR); noise = rnd.standard_normal(wl).astype(np.float32)  # whoosh: noise through a rising low-pass
    y = np.zeros(wl, np.float32); acc = 0.0
    for i in range(wl):
        a = 0.02 + 0.25 * (i / wl); acc += a * (noise[i] - acc); y[i] = acc
    out[:wl] += y * np.sin(np.linspace(0, np.pi, wl)) * 0.9
    notes = [523.25, 659.25, 783.99, 1046.5] if KIDS else [440.0, 554.37, 659.25, 880.0]
    for k, f in enumerate(notes):
        _add(out, _tone(f, 0.9, 0.35, 0.32), 0.32 + k * 0.12)
    for f in (notes[0] / 2, notes[1] / 2, notes[2] / 2, notes[3]):  # landing chord
        _add(out, _tone(f, INTRO_S - 0.85, 0.55, 0.22), 0.85)
    for k in range(5):  # sparkle pings
        _add(out, _tone(2093 + 300 * k, 0.25, 0.06, 0.08, (1.0,)), 0.5 + k * 0.07)
    return out


def _outro_audio():
    n = int(OUTRO_S * SR); out = np.zeros(n, np.float32); tt = np.arange(n) / SR
    chord = [261.63, 329.63, 392.0, 523.25] if KIDS else [220.0, 277.18, 329.63, 440.0]
    env = np.minimum(1, tt / 0.4) * np.clip((OUTRO_S - tt) / 0.6, 0, 1)
    for f in chord:
        out += (0.10 * np.sin(2 * np.pi * f * tt) + 0.03 * np.sin(4 * np.pi * f * tt)).astype(np.float32) * env.astype(np.float32)
    for i in range(len(LINKS)):
        _add(out, _tone(chord[-1] * (1.5 + 0.25 * i), 0.5, 0.12, 0.16), 0.35 + i * 0.22)
    return out


def _clip(path, W, H, dur, frame_fn, audio, gain=0.45):
    d = tempfile.mkdtemp(); wav = os.path.join(d, "a.wav")
    a = np.clip(audio * gain, -1, 1)  # matched to the videos' loudness (about -20 dB mean)
    import wave
    with wave.open(wav, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        st = (np.repeat(a[:, None], 2, axis=1) * 32767).astype("<i2"); w.writeframes(st.tobytes())
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                          "-c:a", "aac", "-b:a", "192k", "-ar", str(SR), "-ac", "2", "-shortest", path], stdin=subprocess.PIPE)
    surf = skia.Surface(W, H)
    for i in range(int(round(dur * FPS))):
        c = surf.getCanvas(); c.clear(skia.ColorWHITE)
        frame_fn(c, W, H, i / FPS)
        p.stdin.write(surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).tobytes())
    p.stdin.close(); p.wait()
    if p.returncode: raise RuntimeError("ffmpeg failed making " + os.path.basename(path))
    return path


def make_intro(path, long=False):
    W, H = (1920, 1080) if long else (1080, 1920)
    return _clip(path, W, H, INTRO_S, _intro_frame, _intro_audio(), 0.42)


def make_outro(path, long=False):
    W, H = (1920, 1080) if long else (1080, 1920)
    return _clip(path, W, H, OUTRO_S, _outro_frame, _outro_audio(), 0.60)


def _dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path], capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


def wrap(mp4, long=False):
    """Put the intro before and the outro after the finished video (in place). Returns a short status."""
    use_in = os.environ.get("INTRO", "on").strip().lower() not in ("off", "0", "false", "no")
    use_out = os.environ.get("OUTRO", "on").strip().lower() not in ("off", "0", "false", "no")
    if not (use_in or use_out): return "intro/outro off"
    if not long and _dur(mp4) + INTRO_S * use_in + OUTRO_S * use_out > 179:
        return "intro/outro skipped (the Short would go over 180 s)"
    try:
        d = tempfile.mkdtemp(); parts = []
        if use_in: parts.append(make_intro(os.path.join(d, "intro.mp4"), long))
        parts.append(mp4)
        if use_out: parts.append(make_outro(os.path.join(d, "outro.mp4"), long))
        W, H = (1920, 1080) if long else (1080, 1920)
        cmd = ["ffmpeg", "-y", "-loglevel", "error"]
        for p in parts: cmd += ["-i", p]
        fl = "".join(f"[{i}:v]scale={W}:{H},fps={FPS},setsar=1,format=yuv420p[v{i}];"
                     f"[{i}:a]aresample={SR},aformat=channel_layouts=stereo[a{i}];" for i in range(len(parts)))
        fl += "".join(f"[v{i}][a{i}]" for i in range(len(parts))) + f"concat=n={len(parts)}:v=1:a=1[v][a]"
        tmp = mp4[:-4] + "_wrapped.mp4"
        cmd += ["-filter_complex", fl, "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "slow", "-crf", "18",
                "-pix_fmt", "yuv420p", "-profile:v", "high", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", tmp]
        subprocess.run(cmd, check=True)
        os.replace(tmp, mp4)
        return "added " + " + ".join(x for x, on in (("intro", use_in), ("outro", use_out)) if on)
    except Exception as e:  # never lose the video because of the extras
        print("note: intro/outro not added:", e)
        return f"intro/outro not added: {e}"[:160]


if __name__ == "__main__":  # preview: python pipeline/bumpers.py out/ [--long]
    o = sys.argv[1] if len(sys.argv) > 1 else "."
    lg = "--long" in sys.argv
    print(make_intro(os.path.join(o, "intro_preview.mp4"), lg), make_outro(os.path.join(o, "outro_preview.mp4"), lg))
