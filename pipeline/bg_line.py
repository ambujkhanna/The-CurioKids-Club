"""Line-art room + board frame matching the line-art characters."""
import math
import skia
import kit2d as K
import doodle
import numpy as np
from char_line import ell, hexc, INK
from kit2d import P

W = K.W
BX, BY, BW, BH = K.BX, K.BY, K.BW, K.BH
FLOOR = 1560


def outline_rr(c, x, y, w, h, r, fill, lw=6):
    rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r)
    c.drawRRect(rr, P(fill)); c.drawRRect(rr, P(INK, lw))


_PAPER = None


def paper():
    """Subtle paper grain, generated once (deterministic)."""
    global _PAPER
    if _PAPER is None:
        rng = np.random.default_rng(4)
        n = rng.normal(0, 1, (480, 270)).astype(np.float32)
        n = (n - n.min()) / (n.max() - n.min())
        a = (n * 26).astype(np.uint8)
        img = np.zeros((480, 270, 4), np.uint8); img[..., 0:3] = 90; img[..., 3] = a
        _PAPER = skia.Image.fromarray(img, colorType=skia.kRGBA_8888_ColorType)
    return _PAPER


def draw_bg_doodle(c, t):
    c.drawRect(skia.Rect.MakeLTRB(-600, -600, W + 600, 2600), P("#FBF7EE"))
    c.drawImageRect(paper(), skia.Rect.MakeLTRB(-600, -600, W + 600, 2600), skia.SamplingOptions(skia.FilterMode.kLinear))
    # floor: pencil hatching instead of boards
    c.drawLine(-600, FLOOR, W + 600, FLOOR, P(INK, 6))
    for k in range(-30, 40):
        x0 = k * 46
        c.drawLine(x0, FLOOR + 14, x0 - 60, FLOOR + 74, P("#B9AE98", 3))
    # sketched rug
    c.drawOval(ell(540, 1690, 450, 62), P("#FFE08A", a=0.85)); c.drawOval(ell(540, 1690, 450, 62), P(INK, 5))
    for k in range(-8, 9):
        c.drawLine(540 + k * 50 - 14, 1650, 540 + k * 50 + 14, 1730, P("#F2B600", 4, a=0.7))


def draw_bg(c, t):
    if doodle.ON:
        draw_bg_doodle(c, t)
        _props(c, t)
        return
    # wall + floor
    c.drawRect(skia.Rect.MakeLTRB(-600, -600, W + 600, FLOOR), P("#FAF7F0"))
    for i in range(-6, 20):  # faint wallpaper stripes
        c.drawLine(i * 90, -600, i * 90, FLOOR, P("#EFE9DD", 3))
    c.drawRect(skia.Rect.MakeLTRB(-600, FLOOR, W + 600, 2600), P("#E9DFCC"))
    for k in range(-6, 22):  # floorboards
        c.drawLine(k * 110, FLOOR, k * 110 - 140, 2400, P("#DCCFB6", 3))
    c.drawLine(-600, FLOOR, W + 600, FLOOR, P(INK, 6))
    # rug
    c.drawOval(ell(540, 1690, 450, 62), P("#FFE08A")); c.drawOval(ell(540, 1690, 450, 62), P(INK, 5))
    c.drawOval(ell(540, 1690, 400, 46), P("#F2B600", 3))
    _props(c, t)


import os
V2 = os.environ.get("BG") == "v2"


def rrp(x, y, w, h, r):
    p = skia.Path(); p.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r)); return p


def ink(c, path, fill, lw=6):
    c.drawPath(path, P(fill)); c.drawPath(path, P(INK, lw))


def _living_room(c, t):
    # window with sky + drifting clouds (left wall, behind the plant)
    wx, wy, ww, wh = 18, 1060, 190, 270
    win = rrp(wx, wy, ww, wh, 10)
    sky = skia.Paint(AntiAlias=True)
    sky.setShader(skia.GradientShader.MakeLinear([skia.Point(0, wy), skia.Point(0, wy + wh)], [hexc("#9FD8FF"), hexc("#E3F4FF")]))
    c.save(); c.clipPath(win, doAntiAlias=True); c.drawPath(win, sky)
    for k, (y0, sp, sz) in enumerate(((wy + 60, 9, 1.0), (wy + 150, 6, 0.8), (wy + 220, 11, 0.6))):
        x0 = wx - 80 + ((t * sp + k * 90) % (ww + 160))
        for dx, dy, r in ((0, 0, 22), (22, -10, 26), (46, 0, 20)):
            c.drawCircle(x0 + dx * sz, y0 + dy * sz, r * sz, P("#FFFFFF"))
    c.restore()
    c.drawPath(win, P(INK, 7)); c.drawLine(wx + ww / 2, wy, wx + ww / 2, wy + wh, P(INK, 5)); c.drawLine(wx, wy + wh / 2, wx + ww, wy + wh / 2, P(INK, 5))
    ink(c, rrp(wx - 10, wy + wh - 4, ww + 20, 16, 6), "#FFFFFF", 5)
    # framed pictures between the characters' heads
    for (fx, fy, fw, fh, col, kind) in ((448, 905, 90, 110, "#FFE08A", "sun"), (552, 930, 80, 80, "#CDE7FF", "heart")):
        ink(c, rrp(fx, fy, fw, fh, 6), "#FFFFFF", 6)
        c.drawRect(skia.Rect.MakeXYWH(fx + 10, fy + 10, fw - 20, fh - 20), P(col))
        if kind == "sun":
            c.drawCircle(fx + fw / 2, fy + fh / 2 - 6, 14, P("#FF8C5A")); c.drawLine(fx + 14, fy + fh - 22, fx + fw - 14, fy + fh - 22, P("#7BD389", 6))
        else:
            hp = skia.Path(); cx, cy = fx + fw / 2, fy + fh / 2
            hp.moveTo(cx, cy + 14); hp.cubicTo(cx - 26, cy - 4, cx - 10, cy - 22, cx, cy - 8); hp.cubicTo(cx + 10, cy - 22, cx + 26, cy - 4, cx, cy + 14); hp.close()
            c.drawPath(hp, P("#FF6B6B"))
    # sofa behind the characters
    back = rrp(330, 1300, 420, 170, 40); ink(c, back, "#5BC0BE", 6)
    seat = rrp(320, 1420, 440, 90, 30); ink(c, seat, "#4AAFAD", 6)
    for ax in (300, 740):
        ink(c, rrp(ax, 1380, 60, 140, 28), "#5BC0BE", 6)
    for lx in (350, 730):
        c.drawLine(lx, 1510, lx, FLOOR, P(INK, 7))
    ink(c, rrp(372, 1330, 90, 80, 24), "#FF8C5A", 5)  # cushion
    # sleepy cat on the sofa (blinks, flicks its tail)
    cx, cy = 575, 1400
    tail = skia.Path(); sw = math.sin(t * 2.2) * 14
    tail.moveTo(cx + 46, cy + 10); tail.cubicTo(cx + 90, cy + 10, cx + 96 + sw, cy - 30, cx + 74 + sw, cy - 44)
    c.drawPath(tail, P(INK, 16)); c.drawPath(tail, P("#B0B6BE", 9))
    body = skia.Path(); body.addOval(ell(cx, cy, 58, 30)); ink(c, body, "#B0B6BE", 5)
    head = skia.Path(); head.addOval(ell(cx - 50, cy - 14, 28, 24)); ink(c, head, "#B0B6BE", 5)
    for s_ in (-1, 1):
        e = skia.Path(); e.moveTo(cx - 50 + s_ * 8, cy - 32); e.lineTo(cx - 50 + s_ * 24, cy - 52); e.lineTo(cx - 50 + s_ * 26, cy - 26); e.close()
        ink(c, e, "#B0B6BE", 4)
    awake = (t % 6.0) > 5.2
    for s_ in (-1, 1):
        ex = cx - 50 + s_ * 11
        if awake:
            c.drawCircle(ex, cy - 14, 4, P(INK))
        else:
            ep = skia.Path(); ep.moveTo(ex - 6, cy - 14); ep.quadTo(ex, cy - 9, ex + 6, cy - 14); c.drawPath(ep, P(INK, 3))
    if not awake:
        zz = (t * 0.8) % 1.0
        K.text(c, "z", cx - 10 + zz * 20, cy - 60 - zz * 40, 26 + zz * 10, "#5B6B80", K.FONT_XB, a=1 - zz)
    # side table with laptop (right, next to the lamp)
    tx = 860
    ink(c, rrp(tx, 1440, 130, 18, 6), "#C98B5A", 5)
    for lx in (tx + 14, tx + 116):
        c.drawLine(lx, 1458, lx, FLOOR, P(INK, 6))
    scr = rrp(tx + 22, 1366, 86, 62, 6); ink(c, scr, "#1F2D44", 5)
    glow = 0.55 + 0.25 * math.sin(t * 3)
    c.drawRect(skia.Rect.MakeXYWH(tx + 30, 1374, 70, 46), P("#7CF5FF", a=glow))
    ink(c, rrp(tx + 12, 1428, 106, 12, 4), "#C9CDD2", 4)


def _props(c, t):
    if V2:
        _living_room(c, t)
    # shelf + books (left)
    for i, (w_, h_, col) in enumerate(((28, 96, "#FF6B6B"), (24, 80, "#3A86FF"), (32, 104, "#FFD23F"), (22, 72, "#7BD389"))):
        bx = 26 + sum(v for v in (32, 28, 36, 26)[:i])
        outline_rr(c, bx, 1006 - h_, w_, h_, 4, col, 4)
    outline_rr(c, 6, 1006, 210, 16, 5, "#FFFFFF", 5)
    # clock (right)
    c.drawCircle(990, 960, 50, P("#FFFFFF")); c.drawCircle(990, 960, 50, P(INK, 6))
    for i in range(12):
        a = i * math.pi / 6
        c.drawLine(990 + math.cos(a) * 36, 960 + math.sin(a) * 36, 990 + math.cos(a) * 42, 960 + math.sin(a) * 42, P(INK, 3))
    c.drawLine(990, 960, 990 + math.sin(t * 0.6) * 32, 960 - math.cos(t * 0.6) * 32, P(INK, 4))
    c.drawLine(990, 960, 990 + math.sin(t * 0.05 + 1) * 22, 960 - math.cos(t * 0.05 + 1) * 22, P(INK, 6))
    # plant (left)
    c.save(); c.translate(80, FLOOR)
    for k, (ang, ln) in enumerate(((-30, 250), (-8, 300), (14, 270), (36, 210), (-50, 180))):
        c.save(); c.rotate(ang + math.sin(t * 1.3 + k) * 2.5)
        lp = skia.Path(); lp.moveTo(0, -70); lp.quadTo(-40, -70 - ln * 0.5, 0, -70 - ln); lp.quadTo(40, -70 - ln * 0.5, 0, -70); lp.close()
        c.drawPath(lp, P("#7BD389")); c.drawPath(lp, P(INK, 5)); c.drawLine(0, -80, 0, -60 - ln * 0.9, P(INK, 3))
        c.restore()
    pot = skia.Path(); pot.moveTo(-60, -130); pot.lineTo(60, -130); pot.lineTo(46, 0); pot.lineTo(-46, 0); pot.close()
    c.drawPath(pot, P("#FF8C5A")); c.drawPath(pot, P(INK, 6))
    c.restore()
    # lamp (right)
    c.save(); c.translate(1010, FLOOR)
    c.drawLine(0, 0, 0, -520, P(INK, 8)); c.drawOval(ell(0, 0, 56, 10), P(INK))
    sh = skia.Path(); sh.moveTo(-66, -520); sh.lineTo(66, -520); sh.lineTo(40, -616); sh.lineTo(-40, -616); sh.close()
    c.drawPath(sh, P("#FFD23F")); c.drawPath(sh, P(INK, 6))
    c.restore()
    K.logo(c, 540, 84, 0.95 * (1.0 + (0.18 * math.sin(min(1.0, max(0.0, (t - K.LOGO_T) / 0.5)) * math.pi) if t > K.LOGO_T else 0.0)), tcol="#1D1D1F")


def draw_board_frame(c):
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(BX, BY, BW, BH), 34, 34)
    sh = P("#000000", a=0.10); sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 14))
    c.save(); c.translate(8, 12); c.drawRRect(r, sh); c.restore()
    c.drawRRect(r, P("#FFFFFF")); c.drawRRect(r, P(INK, 8))
    inner = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(BX + 4, BY + 4, BW - 8, BH - 8), 30, 30)
    c.save(); c.clipRRect(inner, doAntiAlias=True)
    c.drawRect(skia.Rect.MakeXYWH(BX, BY, BW, 66), P("#FFE08A"))
    c.drawLine(BX, BY + 66, BX + BW, BY + 66, P(INK, 5))
    for i, col in enumerate(("#FF6B6B", "#FFD23F", "#7BD389")):
        c.drawCircle(BX + 46 + i * 30, BY + 34, 9, P(col)); c.drawCircle(BX + 46 + i * 30, BY + 34, 9, P(INK, 3))
    K.text(c, "FUN FACTS", BX + BW - 36, BY + 34, 24, "#1D1D1F", K.FONT_XB, "r")
