"""Punchy thumbnails (2026-11-21, same file in both channels). Repo variables: THUMB_STYLE punch (default) | classic;
THUMB_MARK sticker (default, owner's pick: a "WHY?/HOW?/WHAT?" speech bubble on the answer picture) | glow | mystery | circle.

Built for curiosity at a glance (Shorts shelf, search, suggested videos):
  * 1-3 HUGE words (cover_text) - no small subtitle box
  * the characters BIG with a "wow!" face (raised brows, open mouth, hands up)
  * the topic pictures big, "A -> B" with a red arrow, the answer marked by THUMB_MARK (the curiosity gap)
  * strong contrast: the background is darkened at the edges, sunburst behind the picture
Kids: the episode's HD background picture (if any). AInation: its studio look, blue headline.
Called by thumbnail.make / make_wide; falls back to the classic design if anything fails.
"""
import math, os
import skia
import thumbnail as T

KIDS = os.environ.get("BG") == "kids"
HEAD = {"DAD": 1090, "TEEN": 1150, "MIA": 1150, "LEO": 1320}
RED = "#FF2D3D"
MARK = os.environ.get("THUMB_MARK", "sticker").strip().lower()  # how the answer picture is highlighted
FACE = ("#FFF27A", "#FFC21A", "#FF8F1F") if KIDS else ("#7FB0FF", "#2F6BFF", "#1D4FD8")
SIDE = "#1F2D44" if KIDS else "#0B1530"
_FW, _FH = 1080, 1920  # size of the thumbnail being drawn (set by make / make_wide)


def _wow(chars, t):
    """Give every character a surprised, delighted face at time t (after the video ends, so nothing else changes)."""
    for k, ch in enumerate(chars):
        for tr, v in ((ch.mo, 0.85), (ch.mw, 0.7), (ch.brow_up, 1.0), (ch.brow_tilt, 0.0), (ch.smile, 0.6),
                      (ch.yaw, 10 if k == 0 else -10), (ch.pitch, -5), (ch.roll, 4 if k == 0 else -4)):
            try: tr.add(t, v)
            except Exception: pass
        for s in (-1, 1):  # the one explaining (2nd) points up at the answer picture; the asker throws hands up
            try: ch.pose(s, "point2" if (k == 1 and s == -1) else "palms", t)
            except Exception: pass


def _char(c, K, ch, t, x, y, s):
    """Draw a character with its head centre at (x, y), scaled s."""
    c.save(); c.translate(x, y); c.scale(s, s); c.translate(-ch.x, -HEAD.get(ch.name, 1150) + 40)
    K.draw_char(c, ch, t); c.restore()


def _vignette(c, K, W, H, cx, cy, a=0.55):
    v = skia.Paint(AntiAlias=True)
    v.setShader(skia.GradientShader.MakeRadial(skia.Point(cx, cy), max(W, H) * 0.75,
                [K.hexc("#000000", 0.0), K.hexc("#000000", 0.05), K.hexc("#0B1020", a)], [0.0, 0.45, 1.0]))
    c.drawRect(skia.Rect.MakeWH(W, H), v)


def _glow(c, K, x, y, r, col):
    g = skia.Paint(AntiAlias=True, Color=K.hexc(col, 0.55)); g.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, r * 0.35))
    c.drawCircle(x, y, r * 1.15, g)


def _red_circle(c, K, x, y, r):
    """Hand-drawn red loop around (x, y): slightly tilted, not quite closed."""
    p = skia.Path(); n = 40
    for i in range(n + 6):
        a = -0.6 + i * 2 * math.pi / n; rr = r * (1.0 + 0.05 * math.sin(i * 0.9))
        pt = (x + math.cos(a) * rr * 1.08, y + math.sin(a) * rr * 0.95)
        p.moveTo(*pt) if i == 0 else p.lineTo(*pt)
    pa = T._P(K, RED, max(10, r * 0.07)); pa.setStrokeCap(skia.Paint.kRound_Cap)
    sh = T._P(K, "#000000", max(10, r * 0.07), a=0.35); sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 6))
    c.save(); c.translate(4, 6); c.drawPath(p, sh); c.restore(); c.drawPath(p, pa)


def _arrow(c, K, x0, y0, x1, y1, w=16, bend=0.25):
    """Chunky curved red arrow from (x0, y0) to (x1, y1) with a white outline."""
    mx, my = (x0 + x1) / 2 - (y1 - y0) * bend, (y0 + y1) / 2 + (x1 - x0) * bend
    p = skia.Path(); p.moveTo(x0, y0); p.quadTo(mx, my, x1, y1)
    ang = math.atan2(y1 - my, x1 - mx); L = w * 3.2
    head = skia.Path(); head.moveTo(x1 + math.cos(ang) * w * 0.8, y1 + math.sin(ang) * w * 0.8)
    for da in (2.55, -2.55):
        head.lineTo(x1 + math.cos(ang + da) * L, y1 + math.sin(ang + da) * L)
    head.close()
    for col, extra in (("#FFFFFF", w * 0.6), (RED, 0)):
        pa = T._P(K, col, w + extra); pa.setStrokeCap(skia.Paint.kRound_Cap); c.drawPath(p, pa)
        c.drawPath(head, T._P(K, col, extra) if extra else T._P(K, col))
    c.drawPath(head, T._P(K, RED))


def _star(c, K, x, y, r, col="#FFFFFF", a=1.0):
    p = skia.Path()
    for i in range(8):
        rr = r if i % 2 == 0 else r * 0.28; ang = i * math.pi / 4 - math.pi / 2
        pt = (x + math.cos(ang) * rr, y + math.sin(ang) * rr)
        p.moveTo(*pt) if i == 0 else p.lineTo(*pt)
    p.close(); c.drawPath(p, T._P(K, col, a=a))


def _hero(c, K, x, y, r, fn, tf, ep, answer=True):
    """Draw the (answer) picture with the chosen highlight. Returns nothing."""
    m = MARK if answer else "plain"
    if m == "glow":  # warm light burst + sparkles behind the picture
        T.sunburst(c, K, x, y, r * 1.65, n=16, col="#FFE27A", a=0.5)
        g = skia.Paint(AntiAlias=True, Color=K.hexc("#FFE27A", 0.9)); g.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, r * 0.45))
        c.drawCircle(x, y, r * 1.2, g)
        T.badge3d(c, K, x, y, r, fn, r / 50)
        for dx, dy, s_ in ((-1.05, -0.95, 0.30), (1.1, -0.7, 0.22), (0.95, 0.95, 0.26), (-1.15, 0.6, 0.18)):
            _star(c, K, x + dx * r, y + dy * r, r * s_, "#FFFFFF")
        return
    _glow(c, K, x, y, r, "#FFFFFF")
    if m == "mystery":  # the answer is a dark silhouette with a big "?" - you have to watch to see it
        T.badge3d(c, K, x, y, r, None, r / 50)
        lp = skia.Paint(); lp.setColorFilter(skia.ColorFilters.Blend(K.hexc(SIDE), skia.BlendMode.kSrcIn))
        c.saveLayer(None, lp)
        if fn: fn(c, x, y + r * 0.04, r / 50)
        c.restore()
        T._text(c, K, "?", x, y + r * 0.42, r * 1.25, "#FFFFFF", tf, outline=SIDE, ow=r * 0.08)
        return
    T.badge3d(c, K, x, y, r, fn, r / 50)
    if m == "circle":
        _red_circle(c, K, x, y, r * 1.18)
    elif m == "sticker":  # tilted speech-bubble sticker with the question word (WHY? / HOW? / WHAT?)
        import re as _re
        w = (_re.findall(r"[A-Za-z]+", ep.get("title", "")) or ["WHY"])[0].upper()
        w = w if w in ("WHY", "HOW", "WHAT", "WHERE", "WHO", "CAN", "DO", "DOES", "IS", "ARE") else "WHY"
        w = {"DO": "WHY", "DOES": "HOW", "IS": "WHY", "ARE": "WHY", "CAN": "HOW"}.get(w, w) + "?"
        f = skia.Font(tf, r * 0.42); tw = f.measureText(w); bw, bh = tw + r * 0.5, r * 0.62
        # centred under the picture (kept inside the frame); the tail always points straight up at the picture's centre
        # fully below the picture's ring (small gap), inside the frame; only the pointer touches the ring
        bx, by = max(35.0, min(x - bw / 2, _FW - 35 - bw)), min(y + r * 1.16, _FH - bh - 14)
        tx = max(bx + bh * 0.6, min(x, bx + bw - bh * 0.6))  # tail base: under the picture, inside the bubble
        tip = y + r * 0.97  # bottom edge of the ring, straight below the picture's centre
        tail = skia.Path(); tail.moveTo(tx - r * 0.15, by + bh * 0.4); tail.lineTo(x, tip); tail.lineTo(tx + r * 0.15, by + bh * 0.4); tail.close()
        rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(bx, by, bw, bh), bh / 2, bh / 2)
        sh = T._P(K, "#000000", a=0.3); sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 10))
        c.save(); c.translate(6, 10); c.drawRRect(rr, sh); c.restore()
        c.drawPath(tail, T._P(K, SIDE, r * 0.07)); c.drawRRect(rr, T._P(K, SIDE, r * 0.07))  # outlines
        c.drawPath(tail, T._P(K, "#FF4D6D")); c.drawRRect(rr, T._P(K, "#FF4D6D"))  # fills (hide the seam)
        T._text(c, K, w, bx + bw / 2, by + bh * 0.72, r * 0.42, "#FFFFFF", tf)


def _qbadge(c, K, x, y, r, tf, mid="?"):
    _glow(c, K, x, y, r, "#FFD23F")
    c.drawCircle(x, y, r, T._P(K, "#FFD23F")); c.drawCircle(x, y, r, T._P(K, SIDE, r * 0.12))
    T._text(c, K, mid or "?", x, y + r * 0.42, r * 1.2 if len(mid or "?") < 3 else r * 0.8, SIDE, tf)


def _headline(c, K, ep, tf, x, y, maxw, size0, align="c", rot=-4):
    head = T._clean(K, (ep.get("cover_text") or T._subtitle(ep)).upper(), tf)
    lines, size = T._wrap(head, tf, size0, maxw, 2)
    c.save(); c.rotate(rot, x if align == "c" else x + maxw / 2, y)
    yy = y - (len(lines) - 1) * size * 0.52
    for ln in lines:
        T.text3d(c, K, ln, x, yy + size * 0.35, size, tf, align=align, face=FACE, side=SIDE); yy += size * 1.04
    c.restore()
    return y + (len(lines) - 1) * size * 0.52 + size * 0.6


def _background(c, K, t, W, H, orient):
    try:
        import art
        if art.active():
            art.backdrop(c, t, W, H, orient); return True
    except Exception:
        pass
    return False


def _part_ribbon(c, K, ep, tf, x, y, size):
    """'PART 2' ribbon for a series episode (title contains 'Part N')."""
    import re as _re
    m = _re.search(r"\bPart\s*(\d+)", ep.get("title", ""), _re.I)
    if not m: return
    s = f"PART {m.group(1)}"; f = skia.Font(tf, size); tw = f.measureText(s); h = size * 1.45
    c.save(); c.rotate(-8, x, y)
    sh = T._P(K, "#000000", a=0.3); sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 8))
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, tw + size, h), 12, 12)
    c.save(); c.translate(5, 8); c.drawRRect(r, sh); c.restore()
    c.drawRRect(r, T._P(K, "#FFD23F")); c.drawRRect(r, T._P(K, SIDE, size * 0.1))
    c.drawString(s, x + size / 2, y + h * 0.72, f, T._P(K, SIDE))
    c.restore()


def _cast(chars, ep):
    first = (ep.get("lines") or [{}])[0].get("who")
    a = [ch for ch in chars if ch.name == first] or list(chars[:1])
    b = [ch for ch in chars if ch not in a]
    return a + b[:1]


def make(path, K, chars, ep, ico, t_pose=None):
    """1080x1920 Shorts thumbnail."""
    global _FW, _FH; _FW, _FH = 1080, 1920
    W, H = 1080, 1920
    surf = skia.Surface(W, H); c = surf.getCanvas(); c.clear(K.hexc("#4FAEA3"))
    t = max(l["end"] for l in K.LN) + 30.0
    _wow(chars, t)
    tf = K.FONT_XB
    if not _background(c, K, t, W, H, "portrait"):
        K.draw_bg(c, t)  # the drawn room / AInation studio (draws the logo too)
        own_logo = False
    else:
        own_logo = True
    icons, mid = T._icons(ep, ico)
    hy = 800
    T.sunburst(c, K, 540, hy, 1100, n=22, col="#FFFFFF", a=0.16)
    _vignette(c, K, W, H, 540, hy, 0.62)
    if own_logo or KIDS:
        c.drawRoundRect(skia.Rect.MakeXYWH(540 - 250, 92 - 44, 500, 88), 44, 44, T._P(K, "#FFFFFF", a=0.92))
        K.logo(c, 540, 92, 1.15, tcol="#1D1D1F")
    # pictures: one hero, or "A -> ? -> B"
    if len(icons) == 2:
        (xa, ra), (xb, rb) = (270, 170), (790, 205)
        _hero(c, K, xa, hy, ra, icons[0], tf, ep, answer=False)
        _hero(c, K, xb, hy, rb, icons[1], tf, ep)
        _arrow(c, K, xa + ra * 0.85, hy - ra * 0.15, xb - rb * 1.05, hy - rb * 0.1, w=18, bend=-0.3)
        if MARK in ("circle", "glow"): _qbadge(c, K, 540, hy + 150, 62, tf, mid)
    else:
        r = 250
        if icons: _hero(c, K, 540, hy, r, icons[0], tf, ep)
        if MARK in ("circle", "glow"): _qbadge(c, K, 540 + r * 0.95, hy - r * 0.8, 70, tf)
    # characters, big, with a wow face (bottom), the one asking in front
    cast = _cast(chars, ep)
    spots = [(300, 1400, 1.75), (800, 1440, 1.55)]
    for ch, (x, y, s) in reversed(list(zip(cast, spots))):
        _char(c, K, ch, t, x, y, s)
    # headline last, on top of everything
    _headline(c, K, ep, tf, 540, 350, 1000, 200)
    _part_ribbon(c, K, ep, tf, 40, 1020, 64)
    img = surf.makeImageSnapshot()
    if hasattr(K, "grade"): img = K.grade(img)
    img.save(path, skia.kJPEG, 90)
    return path


def make_wide(path, K, chars, ep, ico, t_pose=None):
    """1280x720 thumbnail for long videos."""
    global _FW, _FH; _FW, _FH = 1280, 720
    W, H = 1280, 720
    surf = skia.Surface(W, H); c = surf.getCanvas(); c.clear(K.hexc("#4FAEA3"))
    t = max(l["end"] for l in K.LN) + 30.0
    _wow(chars, t)
    tf = K.FONT_XB
    if not _background(c, K, t, W, H, "landscape"):
        c.save(); c.translate(560, -560); c.scale(0.68, 0.68); K.draw_bg(c, t); c.restore()
    icons, mid = T._icons(ep, ico)
    T.sunburst(c, K, 330, 470, 900, n=22, col="#FFFFFF", a=0.14)
    _vignette(c, K, W, H, 520, 380, 0.7)
    cast = _cast(chars, ep)
    for ch, (x, y, s) in reversed(list(zip(cast, [(930, 330, 0.95), (1170, 350, 0.82)]))):
        _char(c, K, ch, t, x, y, s)
    c.drawRoundRect(skia.Rect.MakeXYWH(30, 22, 330, 60), 30, 30, T._P(K, "#FFFFFF", a=0.92))
    K.logo(c, 195, 52, 0.72, tcol="#1D1D1F")
    _headline(c, K, ep, tf, 40, 200, 700, 118, align="l", rot=-3)
    _part_ribbon(c, K, ep, tf, 640, 400, 40)
    hy = 490
    if len(icons) == 2:
        _hero(c, K, 130, hy, 95, icons[0], tf, ep, answer=False)
        _hero(c, K, 470, hy, 115, icons[1], tf, ep)
        _arrow(c, K, 230, hy - 10, 345, hy - 10, w=12, bend=-0.35)
        if MARK in ("circle", "glow"): _qbadge(c, K, 300, hy + 95, 40, tf, mid)
    elif icons:
        _hero(c, K, 300, hy, 120, icons[0], tf, ep)
        if MARK in ("circle", "glow"): _qbadge(c, K, 430, hy - 100, 42, tf)
    tag = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(W - 300, H - 90, 270, 60), 30, 30)
    c.drawRRect(tag, T._P(K, "#FF0033")); T._ds(c, "FULL VIDEO", W - 270, H - 48, skia.Font(tf, 32), T._P(K, "#FFFFFF")) if hasattr(T, "_ds") \
        else c.drawString("FULL VIDEO", W - 270, H - 48, skia.Font(tf, 32), T._P(K, "#FFFFFF"))
    img = surf.makeImageSnapshot()
    if hasattr(K, "grade"): img = K.grade(img)
    img.save(path, skia.kJPEG, 90)
    return path
