"""The CurioKids Club — flat 2D vector animation renderer (skia). Original character designs.

Usage: python anim2d.py <out_dir> [frame_start frame_end] [--workers N]
"""
import json, math, os, sys
from multiprocessing import Pool
import skia
import doodle

HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(HERE, "build")
T = json.load(open(os.path.join(B, "timing.json")))
LN = T["lines"]
DUR = T["duration"]
FPS = 24
NF = int(math.ceil(DUR * FPS))
W, H = 1080, 1920
FONT_XB = skia.Typeface.MakeFromFile("/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf")
FONT_B = skia.Typeface.MakeFromFile("/usr/share/fonts/opentype/inter/Inter-Bold.otf")
FONT_SB = skia.Typeface.MakeFromFile("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf")
# Channel fonts (SIL Open Font License, shipped in fonts/): Fredoka (rounded, friendly) for The CurioKids Club
_FD = os.path.join(os.path.dirname(HERE), "fonts")


def _weight(tf, w):
    tag = lambda s: (ord(s[0]) << 24) | (ord(s[1]) << 16) | (ord(s[2]) << 8) | ord(s[3])
    coords = skia.FontArguments.VariationPosition.Coordinates([skia.FontArguments.VariationPosition.Coordinate(tag("wght"), w)])
    args = skia.FontArguments(); args.setVariationDesignPosition(skia.FontArguments.VariationPosition(coords))
    return tf.makeClone(args)


if os.path.exists(os.path.join(_FD, "Fredoka.ttf")):
    _fr = skia.Typeface.MakeFromFile(os.path.join(_FD, "Fredoka.ttf"))
    FONT_XB, FONT_B, FONT_SB = _weight(_fr, 700), _weight(_fr, 600), _weight(_fr, 600)
if doodle.ON:
    FONT_XB = doodle.typeface("title"); FONT_B = doodle.typeface("body"); FONT_SB = doodle.typeface("body")


def hexc(h, a=1.0):
    h = h.lstrip("#")
    return skia.Color(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(255 * a))


def P(color, stroke=None, cap=True, a=1.0):
    p = skia.Paint(AntiAlias=True, Color=hexc(color, a) if isinstance(color, str) else color)
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke)
        if cap:
            p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join)
    doodle.apply(p, bool(stroke))
    return p


def nofx(p):
    return skia.Paint(AntiAlias=True, Color=p.getColor())


def rr(x, y, w, h, r):
    return skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r)


def ell(cx, cy, rx, ry):
    return skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry)


ARROWS = ("→", "->", "➜", "➡", "➡️")


def text(c, s, x, y, size, color, tf=FONT_XB, align="c", a=1.0):
    if s.strip() in ARROWS:  # the brand fonts have no arrow glyph: draw a chunky arrow
        h = size * 0.30; L = size * 0.62; cx = x + {"c": 0, "l": L, "r": -L}[align]
        pa = skia.Path(); pa.moveTo(cx - L, y - h * 0.45); pa.lineTo(cx + L * 0.15, y - h * 0.45); pa.lineTo(cx + L * 0.15, y - h * 1.15)
        pa.lineTo(cx + L, y); pa.lineTo(cx + L * 0.15, y + h * 1.15); pa.lineTo(cx + L * 0.15, y + h * 0.45); pa.lineTo(cx - L, y + h * 0.45); pa.close()
        c.drawPath(pa, nofx(P(color, a=a))); return 2 * L
    miss = [ch for ch in s if ch.strip() and skia.Font(tf).unicharToGlyph(ord(ch)) == 0]
    if miss:  # missing glyph (e.g. a symbol): use a system font that has it
        tf = skia.FontMgr().matchFamilyStyleCharacter("", skia.FontStyle.Bold(), ["en"], ord(miss[0])) or tf
    f = skia.Font(tf, size)
    w = f.measureText(s)
    dx = {"c": -w / 2, "l": 0, "r": -w}[align]
    tp_ = nofx(P(color, a=a))
    c.drawString(s, x + dx, y + size * 0.36, f, tp_)
    return w


def smooth(u):
    u = min(1.0, max(0.0, u)); return u * u * (3 - 2 * u)


def back_out(u):
    u = min(1.0, max(0.0, u)); k = 1.70158
    return 1 + (k + 1) * (u - 1) ** 3 + k * (u - 1) ** 2


def wob(t, f, ph):  # smooth pseudo-noise in [-1, 1]
    return (math.sin(t * f + ph) * 0.6 + math.sin(t * f * 1.73 + ph * 2.1) * 0.3 + math.sin(t * f * 3.1 + ph * 0.7) * 0.1)


def word_t(line, prefix, nth=0, end=False):
    ws = [w for w in LN[line]["words"] if w[0].lower().strip(".,!?").startswith(prefix.lower())]
    return ws[nth][2] if end else ws[nth][1]


# ======================================================================= tracks
class Track:
    def __init__(self, default=0.0):
        self.k = []; self.d = default

    def add(self, t, v):
        self.k = [kv for kv in self.k if abs(kv[0] - t) > 1 / 60]
        self.k.append((t, v)); self.k.sort()

    def __call__(self, t):
        k = self.k
        if not k: return self.d
        if t <= k[0][0]: return k[0][1]
        if t >= k[-1][0]: return k[-1][1]
        lo, hi = 0, len(k) - 1
        while hi - lo > 1:
            m = (lo + hi) // 2
            if k[m][0] <= t: lo = m
            else: hi = m
        (t0, v0), (t1, v1) = k[lo], k[hi]
        return v0 + (v1 - v0) * smooth((t - t0) / (t1 - t0))


class LinTrack(Track):
    def __call__(self, t):
        k = self.k
        if not k: return self.d
        if t <= k[0][0]: return k[0][1]
        if t >= k[-1][0]: return k[-1][1]
        for i in range(1, len(k)):
            if k[i][0] >= t:
                (t0, v0), (t1, v1) = k[i - 1], k[i]
                u = (t - t0) / (t1 - t0); u = u * u * (3 - 2 * u) * 0.5 + u * 0.5
                return v0 + (v1 - v0) * u


POSES = {  # (upper-arm angle from down, + = outward), (forearm absolute angle), hand
    "rest": (9, 4, "rest"),
    "explain": (24, -112, "open"),
    "palms": (38, 96, "open"),
    "point": (112, 128, "point"),
    "point2": (122, 140, "point"),
    "fist": (38, 172, "fist"),
    "wave": (128, 168, "open"),
    "wag": (18, -168, "point"),
    "hip": (28, -40, "fist"),
    "chin": (12, -142, "fist"),
}


class Char:
    def __init__(self, name, x, phase):
        self.name, self.x, self.ph = name, x, phase
        self.yaw, self.pitch, self.roll = Track(), Track(), Track()
        self.brow_up, self.brow_tilt, self.smile = Track(), Track(), Track(0.35)
        self.mo, self.mw = LinTrack(0.0), LinTrack(1.0)
        self.arm = {s: (Track(POSES["rest"][0]), Track(POSES["rest"][1])) for s in (-1, 1)}
        self.hand = {s: [] for s in (-1, 1)}
        self.blinks = []
        self.bounce = Track()
        self.hop = Track()
        self.inner = 1 if x < W / 2 else -1

    def pose(self, s, name, t):
        a1, a2, hd = POSES[name]
        self.arm[s][0].add(t, a1); self.arm[s][1].add(t, a2)
        self.hand[s].append((t - 0.12, hd)); self.hand[s].sort()

    def gesture(self, s, name, t0, t1, blend=0.16):
        self.pose(s, "rest", t0 - blend); self.pose(s, name, t0); self.pose(s, name, t1)
        self.pose(s, "rest", t1 + blend + 0.06)

    def look(self, t, yaw=0, pitch=0, roll=0, hold=None):
        for tr, v in ((self.yaw, yaw), (self.pitch, pitch), (self.roll, roll)):
            tr.add(t, v)
            if hold: tr.add(t + hold, v)

    def brows(self, t, up=0.0, tilt=0.0):
        self.brow_up.add(t, up); self.brow_tilt.add(t, tilt)

    def nod(self, t, amt=7):
        for dt, p in ((0, 0), (0.13, amt), (0.3, -amt * 0.25), (0.45, 0)):
            self.bounce.add(t + dt, p)

    def hand_at(self, s, t):
        h = "rest"
        for tt, hd in self.hand[s]:
            if tt <= t: h = hd
        return h

    def blink_at(self, t):
        for b in self.blinks:
            if b - 0.02 <= t <= b + 0.16:
                u = (t - b) / 0.14
                return max(0.0, 1 - abs(u * 2 - 1)) if u >= 0 else 0.0
        return 0.0



def draw_char(c, ch, t):
    mod = CHARMOD
    if mod is None:  # legacy flat-vector characters (not shipped in the repo)
        import char2d as mod
    op, wd = ch.mo(t), ch.mw(t)
    env = max(ch.mo(t - 0.04), op, ch.mo(t + 0.04))  # syllable envelope
    yaw = ch.yaw(t) + wob(t, 1.9, ch.ph + 4) * 3
    pitch = ch.pitch(t) + ch.bounce(t) * 0.9 + env * 7
    roll = ch.roll(t) + wob(t, 1.6, ch.ph) * 2.6 + env * 2.5 * math.sin(t * 9 + ch.ph)
    vals = (yaw, pitch, roll, op, wd, ch.blink_at(t), ch.brow_up(t) + env * 0.35, ch.brow_tilt(t), ch.smile(t))
    arms = {}
    for s in (-1, 1):
        hd = ch.hand_at(s, t)
        act = 0.0 if hd == "rest" else 1.0
        a1 = ch.arm[s][0](t) + wob(t, 2.2, ch.ph + s) * 4 + env * 7 * act
        a2 = ch.arm[s][1](t) + wob(t, 2.6, ch.ph + 2 * s) * 5 + env * 16 * act
        arms[s] = (a1, a2, hd)
    delay = 0.05 if ch.name == "DAD" else 0.18
    ip = back_out((t - delay) / 0.35) if t < 0.6 else 1.0
    mod.draw(c, ch, t, {"bounce": ch.bounce(t) * 1.2, "roll": roll, "vals": vals, "bob": env * 9, "hop": ch.hop(t)}, arms,
                max(0.001, min(ip, 1.06)), ch.x, 1765)


def logo(c, x, y, k=1.0, a=1.0, tcol="#FFFFFF"):
    """The CurioKids Club wordmark: 'The' + rainbow-letter 'Curio' badge + 'Kids Club'."""
    c.save(); c.translate(x, y); c.scale(k, k)
    f0 = skia.Font(FONT_XB, 30); f1 = skia.Font(FONT_XB, 42); f2 = skia.Font(FONT_XB, 40)
    w0 = f0.measureText("The"); w1 = f1.measureText("Curio"); w2 = f2.measureText("Kids Club"); pad = 18; gap = 10; wb = w1 + 2 * pad
    x0 = -(w0 + gap + wb + gap + w2) / 2
    c.drawString("The", x0, 12, f0, nofx(P(tcol, a=a)))
    xb = x0 + w0 + gap
    c.drawRRect(rr(xb, -30, wb, 60, 20), P("#FFFFFF", a=a)); c.drawRRect(rr(xb, -30, wb, 60, 20), P("#1F2D44", 4, a=a))
    xx = xb + pad
    for ch_, col in zip("Curio", ("#FF4D6D", "#FF8C42", "#F2B600", "#2ECC71", "#0A84FF")):
        c.drawString(ch_, xx, 15, f1, nofx(P(col, a=a))); xx += f1.measureText(ch_)
    c.drawString("Kids Club", xb + wb + gap, 14, f2, nofx(P(tcol, a=a)))
    c.restore()


# ======================================================================= board content
BX, BY, BW, BH = (105, 205, 870, 640) if os.environ.get("BG") == "kids" else (70, 150, 940, 600)  # kids: content area inside the puppet theatre
BCX, BCY = BX + BW / 2, BY + BH / 2


def appear(t, t_in, t_out=None, dur=0.32):
    if t < t_in: return 0.0
    s = back_out((t - t_in) / dur)
    if t_out is not None and t > t_out - 0.22:
        s *= max(0.0, (t_out - t) / 0.22)
    return max(0.0, s)


def fade(t, t_in, t_out=None):
    if t < t_in: return 0.0
    a = min(1.0, (t - t_in) / 0.18)
    if t_out is not None and t > t_out - 0.22:
        a *= max(0.0, (t_out - t) / 0.22)
    return a


def shadow_rrect(c, r, blur=14, dy=8, a=0.28):
    p = P("#000000", a=a); p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    c.save(); c.translate(0, dy); c.drawRRect(r, p); c.restore()


def scaled(c, cx, cy, s):
    c.save(); c.translate(cx, cy); c.scale(s, s); c.translate(-cx, -cy)


def icon_chat(c, x, y, k=1.0, col="#4FC3F7"):
    c.drawRRect(rr(x - 34 * k, y - 26 * k, 68 * k, 48 * k, 16 * k), P(col))
    p = skia.Path(); p.moveTo(x - 18 * k, y + 18 * k); p.lineTo(x - 26 * k, y + 34 * k); p.lineTo(x - 4 * k, y + 20 * k); p.close()
    c.drawPath(p, P(col))
    for i in (-1, 0, 1):
        c.drawCircle(x + i * 15 * k, y - 2 * k, 5 * k, P("#FFFFFF"))


def icon_robot(c, x, y, k=1.0, col="#F06292"):
    c.drawLine(x, y - 34 * k, x, y - 46 * k, P(col, 5 * k)); c.drawCircle(x, y - 48 * k, 7 * k, P(col))
    c.drawRRect(rr(x - 34 * k, y - 30 * k, 68 * k, 56 * k, 16 * k), P(col))
    c.drawRRect(rr(x - 24 * k, y - 18 * k, 48 * k, 26 * k, 10 * k), P("#1F2D44"))
    for s in (-1, 1): c.drawCircle(x + s * 11 * k, y - 5 * k, 5.5 * k, P("#7CF5FF"))


def icon_check(c, x, y, k=1.0):
    c.drawCircle(x, y, 20 * k, P("#2ECC71"))
    p = skia.Path(); p.moveTo(x - 9 * k, y); p.lineTo(x - 2 * k, y + 8 * k); p.lineTo(x + 10 * k, y - 8 * k)
    c.drawPath(p, P("#FFFFFF", 5 * k))


def icon_sun(c, x, y, k=1.0):
    for i in range(8):
        a = i * math.pi / 4
        c.drawLine(x + math.cos(a) * 22 * k, y + math.sin(a) * 22 * k, x + math.cos(a) * 31 * k, y + math.sin(a) * 31 * k, P("#FFC93C", 5 * k))
    c.drawCircle(x, y, 16 * k, P("#FFC93C"))


def icon_train(c, x, y, k=1.0):
    c.drawRRect(rr(x - 22 * k, y - 28 * k, 44 * k, 50 * k, 12 * k), P("#64B5F6"))
    c.drawRRect(rr(x - 15 * k, y - 20 * k, 30 * k, 18 * k, 5 * k), P("#E3F2FD"))
    for s in (-1, 1): c.drawCircle(x + s * 11 * k, y + 10 * k, 4.5 * k, P("#FFF59D"))
    for s in (-1, 1): c.drawLine(x + s * 12 * k, y + 22 * k, x + s * 20 * k, y + 32 * k, P("#90A4AE", 4 * k))


def icon_doc(c, x, y, k=1.0, lines=4):
    c.drawRRect(rr(x - 26 * k, y - 32 * k, 52 * k, 64 * k, 8 * k), P("#FFF1B8"))
    for i in range(lines):
        c.drawLine(x - 15 * k, y - 18 * k + i * 12 * k, x + 15 * k, y - 18 * k + i * 12 * k, P("#90A4AE", 4 * k))


def icon_lock(c, x, y, k=1.0, open_=0.0):
    p = skia.Path(); p.addArc(ell(x, y - 18 * k - open_ * 12 * k, 20 * k, 22 * k), 180, 180)
    c.drawPath(p, P("#B0BEC5", 8 * k, cap=False))
    for s in (-1, 1):
        c.drawLine(x + s * 20 * k, y - 18 * k - open_ * 12 * k, x + s * 20 * k, y - 4 * k, P("#B0BEC5", 8 * k, cap=False) if s > 0 or open_ < 0.5 else P("#B0BEC5", 8 * k, cap=False))
    c.drawRRect(rr(x - 32 * k, y - 8 * k, 64 * k, 50 * k, 12 * k), P("#FFC93C"))
    c.drawCircle(x, y + 12 * k, 7 * k, P("#8D6E00")); c.drawLine(x, y + 14 * k, x, y + 26 * k, P("#8D6E00", 5 * k))


def bubble(c, x, y, w, h, txt, size, col="#FFF1B8", tcol="#1F2D44", tail="l"):
    r = rr(x - w / 2, y - h / 2, w, h, h * 0.35 if h < 140 else 40)
    shadow_rrect(c, r, 10, 6, 0.25)
    c.drawRRect(r, P(col))
    p = skia.Path(); tx = x - w * 0.3 if tail == "l" else x + w * 0.3
    p.moveTo(tx - 16, y + h / 2 - 4); p.lineTo(tx - 22 if tail == "l" else tx + 22, y + h / 2 + 26); p.lineTo(tx + 14, y + h / 2 - 4); p.close()
    c.drawPath(p, P(col))
    text(c, txt, x, y, size, tcol, FONT_B)


def card(c, x, y, w, h, label, size, icon=None, col="#DCEBFF", tcol="#1F2D44", accent=None, align_icon=True):
    r = rr(x - w / 2, y - h / 2, w, h, 22)
    shadow_rrect(c, r, 8, 5, 0.3)
    c.drawRRect(r, P(col))
    if accent:
        c.save(); c.clipRRect(r, doAntiAlias=True); c.drawRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, 10, h), P(accent)); c.restore()
    if icon:
        icon(c, x - w / 2 + 52, y, 0.8)
        text(c, label, x - w / 2 + 96, y, size, tcol, FONT_XB, "l")
    else:
        text(c, label, x, y, size, tcol, FONT_XB)



def draw_board_frame(c):
    # board frame
    r = rr(BX, BY, BW, BH, 40)
    shadow_rrect(c, r, 24, 16, 0.35)
    c.drawRRect(r, P("#FFC300"))
    inner = rr(BX + 16, BY + 16, BW - 32, BH - 32, 28)
    p = P("#1C2A40"); p.setShader(skia.GradientShader.MakeLinear([skia.Point(0, BY), skia.Point(0, BY + BH)], [hexc("#FFFFFF"), hexc("#EAF4FF")]))
    c.drawRRect(inner, p)
    c.save(); c.clipRRect(inner, doAntiAlias=True)
    # subtle grid
    for gx in range(BX + 16, BX + BW, 48):
        c.drawLine(gx, BY, gx, BY + BH, P("#3A86FF", 1, a=0.08))
    for gy in range(BY + 16, BY + BH, 48):
        c.drawLine(BX, gy, BX + BW, gy, P("#3A86FF", 1, a=0.08))
    # header bar
    c.drawRect(skia.Rect.MakeXYWH(BX, BY + 16, BW, 58), P("#3A86FF", a=0.10))
    for i, col in enumerate(("#FF6B6B", "#FFC93C", "#2ECC71")):
        c.drawCircle(BX + 52 + i * 26, BY + 45, 8, P(col))
    text(c, "FUN FACTS", BX + BW - 40, BY + 45, 24, "#5B6B80", FONT_B, "r")


def draw_bit(c, t):
    x = BITX(t) + wob(t, 1.7, 3) * 8; y = BITY(t) + math.sin(t * 4.2) * 7
    vx = BITX(t + 0.05) - BITX(t)
    c.save(); c.translate(x, y); c.rotate(max(-14, min(14, vx * 0.6)))
    # "Buzz" the helper bee (flies to each new board item)
    p = P("#000000", a=0.12); p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 6))
    c.drawOval(ell(0, 62, 26, 5), p)
    flap = abs(math.sin(t * 34))
    for s_ in (-1, 1):  # wings
        c.save(); c.translate(s_ * 6, -24); c.rotate(s_ * (20 + 25 * flap))
        c.drawOval(ell(s_ * 14, -10, 18, 11), P("#E8F6FF", a=0.92)); c.drawOval(ell(s_ * 14, -10, 18, 11), P("#1F2D44", 3))
        c.restore()
    body = ell(0, 0, 36, 27)
    c.drawOval(body, P("#FFD23F"))
    c.save(); c.clipRect(body)
    for xx in (-8, 10):
        c.drawRect(skia.Rect.MakeLTRB(xx - 5, -30, xx + 5, 30), P("#1F2D44"))
    c.restore()
    c.drawOval(body, P("#1F2D44", 3.5))
    c.drawPath(skia.Path().moveTo(-36, 0).lineTo(-48, -4).lineTo(-36, 6), P("#1F2D44"))  # stinger (tail)
    blink = 0.15 if (t % 3.3) < 0.12 else 1.0
    c.drawOval(ell(24, -6, 4.5, 6 * blink), P("#1F2D44"))
    c.drawPath(skia.Path().moveTo(16, 8).quadTo(24, 14, 31, 7), P("#1F2D44", 3))
    for s_ in (-1, 1):  # antennae
        c.drawLine(18, -22, 22 + s_ * 6, -40, P("#1F2D44", 3)); c.drawCircle(22 + s_ * 6, -41, 4, P("#1F2D44"))
    c.restore()


# ======================================================================= background
def draw_bg(c, t):
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeLinear([skia.Point(0, -400), skia.Point(0, 1560)], [hexc("#8BF5E8"), hexc("#3FD9C8")]))
    c.drawRect(skia.Rect.MakeLTRB(-600, -600, W + 600, 1560), p)
    # soft light behind board
    g = skia.Paint(AntiAlias=True)
    g.setShader(skia.GradientShader.MakeRadial(skia.Point(BCX, BCY), 700, [hexc("#FFFFFF", 0.22), hexc("#FFFFFF", 0.0)]))
    c.drawRect(skia.Rect.MakeLTRB(-600, -600, W + 600, 1560), g)
    # wall decor: dots pattern
    for i in range(-2, 14):
        for j in range(0, 4):
            x, y = 40 + i * 90 + (45 if j % 2 else 0), 860 + j * 90
            if 180 < x < 900: continue
            c.drawCircle(x, y, 5, P("#FFFFFF", a=0.18))
    # floating shapes
    for k, (x, y, r, col) in enumerate(((60, 40, 18, "#FFC93C"), (1010, 90, 14, "#F06292"), (90, 1300, 12, "#FFFFFF"), (1000, 1260, 16, "#FFC93C"))):
        c.drawCircle(x + math.sin(t * 0.8 + k) * 10, y + math.cos(t * 0.6 + k) * 12, r, P(col, 6, a=0.55))
    # ambient occlusion where wall meets floor
    ao = skia.Paint(AntiAlias=True)
    ao.setShader(skia.GradientShader.MakeLinear([skia.Point(0, 1380), skia.Point(0, 1556)], [hexc("#0B6F66", 0.0), hexc("#0B6F66", 0.35)]))
    c.drawRect(skia.Rect.MakeLTRB(-600, 1380, W + 600, 1556), ao)
    # floor
    fp = skia.Paint(AntiAlias=True)
    fp.setShader(skia.GradientShader.MakeLinear([skia.Point(0, 1560), skia.Point(0, 2100)], [hexc("#28C2B2"), hexc("#168F84")]))
    c.drawRect(skia.Rect.MakeLTRB(-600, 1560, W + 600, 2600), fp)
    c.drawRect(skia.Rect.MakeLTRB(-600, 1552, W + 600, 1568), P("#E6FFFB"))
    # rug
    c.drawOval(ell(540, 1690, 470, 70), P("#FFB703")); c.drawOval(ell(540, 1690, 430, 56), P("#FFD60A"))
    c.drawOval(ell(540, 1690, 430, 56), P("#E39F2A", 4, a=0.6))
    # wall shelf with books (left)
    c.drawRRect(rr(0, 1010, 210, 16, 6), P("#FFFFFF"))
    for i, (w_, h_, col) in enumerate(((26, 92, "#F06292"), (22, 78, "#4FC3F7"), (30, 100, "#FFC93C"), (20, 70, "#FFFFFF"))):
        bx = 22 + sum(v[0] + 4 for v in ((26, 0), (22, 0), (30, 0), (20, 0))[:i])
        c.drawRRect(rr(bx, 1010 - h_, w_, h_, 4), P(col))
    c.save(); c.translate(168, 978); c.rotate(-14); c.drawRRect(rr(-14, -40, 28, 72, 4), P("#7E57C2")); c.restore()
    # wall clock (right)
    c.drawCircle(990, 960, 52, P("#F7F3EA")); c.drawCircle(990, 960, 44, P("#FFFFFF"))
    for i in range(12):
        a_ = i * math.pi / 6; c.drawLine(990 + math.cos(a_) * 34, 960 + math.sin(a_) * 34, 990 + math.cos(a_) * 40, 960 + math.sin(a_) * 40, P("#90A4AE", 3))
    am = t * 0.6; ah = t * 0.05
    c.drawLine(990, 960, 990 + math.sin(am) * 32, 960 - math.cos(am) * 32, P("#1F2D44", 4))
    c.drawLine(990, 960, 990 + math.sin(ah + 1) * 22, 960 - math.cos(ah + 1) * 22, P("#1F2D44", 6))
    c.drawCircle(990, 960, 5, P("#F06292"))
    # plant (left)
    c.save(); c.translate(70, 1560)
    for k, (ang, ln, col) in enumerate(((-30, 260, "#16A34A"), (-8, 320, "#22C55E"), (14, 280, "#16A34A"), (36, 220, "#4ADE80"), (-50, 180, "#4ADE80"))):
        sw = math.sin(t * 1.3 + k) * 2.5
        c.save(); c.rotate(ang + sw)
        lp = skia.Path(); lp.moveTo(0, -60); lp.quadTo(-44, -60 - ln * 0.5, 0, -60 - ln); lp.quadTo(44, -60 - ln * 0.5, 0, -60); lp.close()
        c.drawPath(lp, P(col)); c.drawLine(0, -70, 0, -50 - ln * 0.9, P("#1E5C38", 3, a=0.5))
        c.restore()
    pot = skia.Path(); pot.moveTo(-62, -130); pot.lineTo(62, -130); pot.lineTo(48, 0); pot.lineTo(-48, 0); pot.close()
    c.drawPath(pot, P("#FF7A45")); c.drawRect(skia.Rect.MakeLTRB(-68, -138, 68, -112), P("#E85D2A"))
    c.restore()
    # lamp (right)
    c.save(); c.translate(1010, 1560)
    c.drawOval(ell(0, 0, 60, 12), P("#1F2D44")); c.drawLine(0, 0, 0, -520, P("#1F2D44", 10))
    shade = skia.Path(); shade.moveTo(-70, -520); shade.lineTo(70, -520); shade.lineTo(42, -620); shade.lineTo(-42, -620); shade.close()
    c.drawPath(shade, P("#FFD60A"))
    lg = skia.Paint(AntiAlias=True)
    lg.setShader(skia.GradientShader.MakeRadial(skia.Point(0, -500), 260, [hexc("#FFF3C4", 0.35), hexc("#FFF3C4", 0.0)]))
    c.drawCircle(0, -500, 260, lg)
    c.restore()
    # brand
    tf_ = LOGO_T
    k = 1.0 + (0.18 * math.sin(min(1.0, max(0.0, (t - tf_) / 0.5)) * math.pi) if t > tf_ else 0.0)
    logo(c, 540, 84, 0.95 * k)


def camera(t):
    i = max(k for k in range(len(SHOTS)) if SHOTS[k][0] <= t + 1e-6)
    t0, kind = SHOTS[i]; t1 = SHOTS[i + 1][0] if i + 1 < len(SHOTS) else DUR
    cx, cy, z0, z1 = CAMS[kind]
    u = (t - t0) / max(0.1, t1 - t0)
    z = z0 + (z1 - z0) * u
    if i > 0:
        z *= 1 + 0.035 * max(0.0, 1 - (t - t0) / 0.3) ** 2  # settle after cut
    for tw in PUNCH:
        if tw <= t < tw + 0.45:
            z *= 1 + 0.045 * math.exp(-(t - tw) * 7) * min(1.0, (t - tw) / 0.05)
    cx += wob(t, 0.5, 1) * 4; cy += wob(t, 0.4, 2) * 4
    # keep inside world
    hw, hh = W / 2 / z, H / 2 / z
    cx = min(max(cx, hw - 60), W + 60 - hw); cy = min(max(cy, hh - 200), H + 40 - hh)
    return cx, cy, z


def draw_top(c, t):
    pass


# ---------------------------------------------------------------- 16:9 long-video layout (FORMAT=long)
# The scene is still built in the vertical "world" (1080x1920). For long videos the frame is recomposed:
# the board/stage goes big on the left, the room with the characters on the right, captions under the board.
LANDSCAPE = os.environ.get("FORMAT") == "long"
OW, OH = (1920, 1080) if LANDSCAPE else (W, H)


def _board_rect():
    if os.environ.get("BG") == "kids":
        return (12, 100, 1068, 945)                       # puppet theatre incl. frame + footlights
    return (BX - 24, BY - 24, BX + BW + 24, BY + BH + 30)  # whiteboard incl. shadow


def _fit(src, dst):
    sx0, sy0, sx1, sy1 = src; dx0, dy0, dx1, dy1 = dst
    s = min((dx1 - dx0) / (sx1 - sx0), (dy1 - dy0) / (sy1 - sy0))
    ox = dx0 + ((dx1 - dx0) - (sx1 - sx0) * s) / 2; oy = dy0 + ((dy1 - dy0) - (sy1 - sy0) * s) / 2
    return s, ox - sx0 * s, oy - sy0 * s


ROOM_SRC = (100, 820, 1080, 1900)   # world area with the characters and the room behind them
BOARD_DST = (34, 92, 1150, 1000)
ROOM_DST = (1160, 120, 1920, 1080)


def _wide_decor(c, t):
    """Full-width string of glowing lights across the top of the wide frame."""
    kids = os.environ.get("BG") == "kids"
    cols = ("#FF6B6B", "#FFD23F", "#4FC3F7", "#7BD389", "#C9A7FF") if kids else ("#FFE9A8",)
    for seg in range(2):
        x0, x1 = seg * OW / 2 - 40, (seg + 1) * OW / 2 + 40
        wire = skia.Path(); wire.moveTo(x0, 18); wire.quadTo((x0 + x1) / 2, 92, x1, 18)
        c.drawPath(wire, P("#3B3B3B", 3, a=0.7))
        pm = skia.PathMeasure(wire, False); L = pm.getLength()
        for k in range(1, 12):
            r_ = pm.getPosTan(L * k / 12)
            if not r_: continue
            pt = r_[0]; col = cols[(k + seg) % len(cols)]
            tw = 0.6 + 0.4 * math.sin(t * 3 + k * 1.7 + seg)
            g = P(col, a=0.45 * tw); g.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 10))
            c.drawCircle(pt.x(), pt.y() + 14, 18, g)
            c.drawOval(skia.Rect.MakeLTRB(pt.x() - 7, pt.y() + 4, pt.x() + 7, pt.y() + 24), P(col))
            c.drawRect(skia.Rect.MakeLTRB(pt.x() - 5, pt.y() - 2, pt.x() + 5, pt.y() + 5), P("#5A5A5A"))


def _landscape(c, t):
    z = 1.0
    for tw in PUNCH:  # keep the little "punch" zooms; no camera cuts in long videos
        if tw <= t < tw + 0.45:
            z *= 1 + 0.03 * math.exp(-(t - tw) * 7) * min(1.0, (t - tw) / 0.05)
    c.save(); c.translate(OW / 2, OH / 2); c.scale(z, z); c.translate(-OW / 2, -OH / 2)
    rs, rx, ry = _fit(ROOM_SRC, ROOM_DST); ry = ROOM_DST[3] - ROOM_SRC[3] * rs  # room stands on the bottom edge
    c.save(); c.translate(rx, ry); c.scale(rs, rs)
    draw_bg(c, t)
    for ch_ in CHARS:
        draw_char(c, ch_, t)
    c.restore()
    _wide_decor(c, t)
    bs, bx, by = _fit(_board_rect(), BOARD_DST)
    b0 = _board_rect(); bottom = by + b0[3] * bs; left = bx + b0[0] * bs; right = bx + b0[2] * bs
    sh = P("#000000", a=0.22); sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 22))
    c.drawOval(skia.Rect.MakeLTRB(left + 40, bottom - 16, right - 40, bottom + 34), sh)  # contact shadow on the floor
    c.save(); c.translate(bx, by); c.scale(bs, bs)
    draw_board(c, t); draw_bit(c, t); draw_top(c, t)
    c.restore()
    logo(c, 1530, 122, 1.1, tcol="#1D1D1F")
    c.restore()


def render_frame(f):
    t = f / FPS
    if LANDSCAPE:
        doodle.SEED = f // 3
        surf = skia.Surface(OW, OH); c = surf.getCanvas(); c.clear(hexc("#4FAEA3"))
        _landscape(c, t)
        vg = skia.Paint(AntiAlias=True)
        vg.setShader(skia.GradientShader.MakeRadial(skia.Point(OW / 2, OH * 0.5), 1300, [hexc("#000000", 0.0), hexc("#000000", 0.0), hexc("#0B1E24", 0.10)], [0.0, 0.6, 1.0]))
        c.drawRect(skia.Rect.MakeWH(OW, OH), vg)
        return grade(surf.makeImageSnapshot())
    doodle.SEED = f // 3
    surf = skia.Surface(W, H); c = surf.getCanvas(); c.clear(hexc("#4FAEA3"))
    cx, cy, z = camera(t)
    c.save(); c.translate(W / 2, H / 2); c.scale(z, z); c.translate(-cx, -cy)
    draw_bg(c, t); draw_board(c, t); draw_bit(c, t)
    for ch_ in CHARS:
        draw_char(c, ch_, t)
    draw_top(c, t)  # overlays above the characters (end card, reminders, effects)
    c.restore()
    vg = skia.Paint(AntiAlias=True)
    vg.setShader(skia.GradientShader.MakeRadial(skia.Point(W / 2, H * 0.48), 1250, [hexc("#000000", 0.0), hexc("#000000", 0.0), hexc("#0B1E24", 0.10)], [0.0, 0.55, 1.0]))
    c.drawRect(skia.Rect.MakeWH(W, H), vg)
    return grade(surf.makeImageSnapshot())


GRADE = dict(sat=1.22, contrast=1.07, bright=4.0)  # vibrant, fresh look; set sat=1, contrast=1, bright=0 for the plain look


def _grade_filter():
    s, k, b = GRADE["sat"], GRADE["contrast"], GRADE["bright"]
    lr, lg, lb = 0.2126, 0.7152, 0.0722
    m = [lr * (1 - s) + s, lg * (1 - s), lb * (1 - s),
         lr * (1 - s), lg * (1 - s) + s, lb * (1 - s),
         lr * (1 - s), lg * (1 - s), lb * (1 - s) + s]
    off = (1 - k) * 128 + b
    rows = []
    for r in range(3):
        rows += [m[r * 3] * k, m[r * 3 + 1] * k, m[r * 3 + 2] * k, 0, off / 255.0]
    rows += [0, 0, 0, 1, 0]
    return skia.ColorFilters.Matrix(rows)


_GF = None


def grade(img):
    global _GF
    if GRADE["sat"] == 1 and GRADE["contrast"] == 1 and not GRADE["bright"]:
        return img
    _GF = _GF or _grade_filter()
    s2 = skia.Surface(img.width(), img.height()); c2 = s2.getCanvas()
    c2.drawImage(img, 0, 0, skia.SamplingOptions(), skia.Paint(ColorFilter=_GF))
    return s2.makeImageSnapshot()


def worker(args):
    out, fs = args
    for f in fs:
        render_frame(f).save(os.path.join(out, f"f{f + 1:04d}.png"), skia.kPNG)
    return len(fs)



# episode-provided globals (set by the episode module)
CHARS, SHOTS, CAMS, PUNCH, LOGO_T = [], [(0.0, "wide")], {}, [], 1e9
BITX, BITY = Track(540), Track(80)
draw_board = None
CHARMOD = None
