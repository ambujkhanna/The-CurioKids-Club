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
    if KIDS:
        _kids_room(c, t)
        K.logo(c, 540, 84, 0.95 * (1.0 + (0.18 * math.sin(min(1.0, max(0.0, (t - K.LOGO_T) / 0.5)) * math.pi) if t > K.LOGO_T else 0.0)), tcol="#1D1D1F")
        return
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
KIDS = os.environ.get("BG") == "kids"   # The CurioKids Club playroom


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


def _star(cx, cy, r1, r2, rot=0.0):
    p = skia.Path()
    for k in range(10):
        a = rot + k * math.pi / 5 - math.pi / 2; r = r1 if k % 2 == 0 else r2
        (p.moveTo if k == 0 else p.lineTo)(cx + math.cos(a) * r, cy + math.sin(a) * r)
    p.close(); return p


def _kids_room(c, t):
    """The CurioKids Club playroom: pastel wall, rainbow, bunting, window, toy shelf, teddy, rocket, foam play mat."""
    # wall: soft sky-blue with polka dots, mint wainscot
    c.drawRect(skia.Rect.MakeLTRB(-600, -600, W + 600, FLOOR), P("#DDF1FF"))
    for k in range(-2, 16):
        for j in range(0, 12):
            x = k * 90 + (45 if j % 2 else 0); y = 60 + j * 110
            if y < 1330: c.drawCircle(x, y, 7, P("#C6E6FF"))
    c.drawRect(skia.Rect.MakeLTRB(-600, 1330, W + 600, FLOOR), P("#CFF3E2"))
    c.drawLine(-600, 1330, W + 600, 1330, P(INK, 5))
    for k in range(-4, 30):
        c.drawLine(k * 48, 1340, k * 48, FLOOR - 6, P("#B5E8D1", 4))
    # floor: warm wood + foam play mat (coloured tiles)
    c.drawRect(skia.Rect.MakeLTRB(-600, FLOOR, W + 600, 2600), P("#F2DDB6"))
    for k in range(-6, 22):
        c.drawLine(k * 110, FLOOR, k * 110 - 140, 2400, P("#E3C998", 3))
    c.drawLine(-600, FLOOR, W + 600, FLOOR, P(INK, 6))
    mat = skia.Path(); mat.moveTo(120, 1630); mat.lineTo(960, 1630); mat.lineTo(1040, 1800); mat.lineTo(40, 1800); mat.close()
    c.save(); c.clipPath(mat, doAntiAlias=True)
    cols = ("#FF8FA3", "#FFD23F", "#7BD389", "#7CC6FF", "#C9A7FF")
    for i in range(10):
        for j in range(2):
            x0 = 40 + i * 100; y0 = 1630 + j * 85
            c.drawRect(skia.Rect.MakeXYWH(x0 - 20 + i * 2, y0, 104, 85), P(cols[(i + j * 2) % 5]))
    c.restore(); c.drawPath(mat, P(INK, 5))
    # painted rainbow on the wall (between the characters)
    for k, col in enumerate(("#FF6B6B", "#FF9F45", "#FFD23F", "#7BD389", "#4FC3F7", "#9B7BFF")):
        r = 190 - k * 22
        arc = skia.Path(); arc.addArc(skia.Rect.MakeLTRB(540 - r, 1250 - r, 540 + r, 1250 + r), 180, 180)
        c.drawPath(arc, P(col, 20, cap=False))
    for s_ in (-1, 1):  # little clouds at the rainbow ends
        for dx, dy, rr_ in ((-30, 0, 30), (0, -14, 36), (32, 0, 28)):
            c.drawCircle(540 + s_ * 170 + dx, 1255 + dy, rr_, P("#FFFFFF"))
        c.drawLine(540 + s_ * 170 - 60, 1268, 540 + s_ * 170 + 60, 1268, P("#E6F1FA", 6))
    # wall stars that twinkle
    for k, (x, y, r) in enumerate(((150, 870, 20), (930, 840, 18), (330, 960, 13), (740, 930, 15), (60, 1270, 12), (1030, 1250, 14))):
        tw = 0.75 + 0.25 * math.sin(t * 2.4 + k * 1.7)
        sp = _star(x, y, r * tw * 1.3, r * tw * 0.55, 0.2 * k)
        c.drawPath(sp, P("#FFD23F")); c.drawPath(sp, P(INK, 3))
    # bunting garland that sways
    pts = [(-20, 790), (270, 840), (540, 815), (810, 840), (1100, 790)]
    g = skia.Path(); g.moveTo(*pts[0])
    for a_, b_ in zip(pts[1::2], pts[2::2]):
        g.quadTo(a_[0], a_[1], b_[0], b_[1])
    c.drawPath(g, P(INK, 4))
    flags = ("#FF6B6B", "#FFD23F", "#4FC3F7", "#7BD389", "#C9A7FF", "#FF9F45")
    for k in range(13):
        x = 20 + k * 82; u = (x + 20) / 1120.0
        y = 790 + 50 * math.sin(math.pi * ((x % 540) / 540)) * (1 if True else 0) - 0
        y = 790 + (50 if 0 < x < 1080 else 0) * math.sin(math.pi * (x % 540) / 540)
        sw = math.sin(t * 2 + k) * 4
        f = skia.Path(); f.moveTo(x - 26, y); f.lineTo(x + 26, y); f.lineTo(x + sw, y + 58); f.close()
        c.drawPath(f, P(flags[k % 6])); c.drawPath(f, P(INK, 4))
    # window with sun + drifting clouds (right wall)
    wx, wy, ww, wh = 870, 930, 190, 250
    win = rrp(wx, wy, ww, wh, 12)
    sky = skia.Paint(AntiAlias=True)
    sky.setShader(skia.GradientShader.MakeLinear([skia.Point(0, wy), skia.Point(0, wy + wh)], [hexc("#7FD0FF"), hexc("#E3F6FF")]))
    c.save(); c.clipPath(win, doAntiAlias=True); c.drawPath(win, sky)
    c.drawCircle(wx + 140, wy + 60, 34 + math.sin(t * 2) * 2, P("#FFD23F"))
    for k, (y0, sp_, sz) in enumerate(((wy + 120, 8, 0.9), (wy + 200, 12, 0.7))):
        x0 = wx - 80 + ((t * sp_ + k * 120) % (ww + 160))
        for dx, dy, r in ((0, 0, 22), (22, -10, 26), (46, 0, 20)):
            c.drawCircle(x0 + dx * sz, y0 + dy * sz, r * sz, P("#FFFFFF"))
    c.restore()
    c.drawPath(win, P(INK, 7)); c.drawLine(wx + ww / 2, wy, wx + ww / 2, wy + wh, P(INK, 5)); c.drawLine(wx, wy + wh / 2, wx + ww, wy + wh / 2, P(INK, 5))
    for s_ in (-1, 1):  # curtains
        cp = skia.Path(); x0 = wx - 18 if s_ < 0 else wx + ww + 18
        cp.moveTo(x0, wy - 14); cp.quadTo(x0 - s_ * 50, wy + wh * 0.5, x0 - s_ * 10, wy + wh + 20); cp.lineTo(x0 + s_ * 20, wy + wh + 20); cp.lineTo(x0 + s_ * 20, wy - 14); cp.close()
        c.drawPath(cp, P("#FF9FB5")); c.drawPath(cp, P(INK, 5))
    ink(c, rrp(wx - 30, wy - 26, ww + 60, 14, 6), "#C98B5A", 4)
    # toy shelf (cubbies) behind the middle, with ABC blocks on top
    sx, sy, sw_, sh_ = 380, 1385, 320, 175
    ink(c, rrp(sx, sy, sw_, sh_, 10), "#FFFFFF", 6)
    c.drawLine(sx + sw_ / 2, sy, sx + sw_ / 2, sy + sh_, P(INK, 5)); c.drawLine(sx, sy + sh_ / 2, sx + sw_, sy + sh_ / 2, P(INK, 5))
    for k, (bx, by, col) in enumerate(((sx + 12, sy + 12, "#FF8FA3"), (sx + sw_ / 2 + 12, sy + 12, "#7CC6FF"),
                                       (sx + 12, sy + sh_ / 2 + 12, "#7BD389"), (sx + sw_ / 2 + 12, sy + sh_ / 2 + 12, "#FFD23F"))):
        ink(c, rrp(bx, by + 20, sw_ / 2 - 24, sh_ / 2 - 38, 8), col, 4)
    for k, (ch_, col) in enumerate((("A", "#FF6B6B"), ("B", "#4FC3F7"), ("C", "#7BD389"))):
        bx = sx + 40 + k * 86; by = sy - 70
        ink(c, rrp(bx, by, 70, 70, 8), col, 5)
        K.text(c, ch_, bx + 35, by + 37, 44, "#FFFFFF", K.FONT_XB)
    # teddy bear sitting on the floor (left corner), blinks
    tx, ty = 110, 1600
    for dx, dy, r, col in ((0, -40, 62, "#C8935F"), (0, -140, 50, "#C8935F")):
        b_ = skia.Path(); b_.addOval(ell(tx + dx, ty + dy, r, r * 0.95)); ink(c, b_, col, 5)
    for s_ in (-1, 1):
        e = skia.Path(); e.addOval(ell(tx + s_ * 38, ty - 182, 18, 18)); ink(c, e, "#C8935F", 4)
        c.drawCircle(tx + s_ * 38, ty - 182, 8, P("#E9B98A"))
        ft = skia.Path(); ft.addOval(ell(tx + s_ * 46, ty + 12, 24, 18)); ink(c, ft, "#C8935F", 4)
        arm = skia.Path(); arm.addOval(ell(tx + s_ * 60, ty - 56, 18, 32)); ink(c, arm, "#C8935F", 4)
    c.drawOval(ell(tx, ty - 34, 34, 30), P("#E9B98A"))
    c.drawOval(ell(tx, ty - 124, 22, 16), P("#E9B98A")); c.drawCircle(tx, ty - 130, 6, P(INK))
    blink = (t % 4.0) > 3.85
    for s_ in (-1, 1):
        if blink: c.drawLine(tx + s_ * 18 - 5, ty - 150, tx + s_ * 18 + 5, ty - 150, P(INK, 3))
        else: c.drawCircle(tx + s_ * 18, ty - 150, 5, P(INK))
    bow = skia.Path(); bow.moveTo(tx, ty - 92); bow.lineTo(tx - 22, ty - 104); bow.lineTo(tx - 22, ty - 80); bow.close()
    bow.moveTo(tx, ty - 92); bow.lineTo(tx + 22, ty - 104); bow.lineTo(tx + 22, ty - 80); bow.close()
    c.drawPath(bow, P("#FF6B6B")); c.drawPath(bow, P(INK, 3))
    # toy rocket (right floor corner) that gently wobbles
    c.save(); c.translate(1000, FLOOR + 30); c.rotate(math.sin(t * 1.5) * 2)
    body = skia.Path(); body.moveTo(0, -190); body.cubicTo(40, -150, 42, -60, 34, 0); body.lineTo(-34, 0); body.cubicTo(-42, -60, -40, -150, 0, -190); body.close()
    ink(c, body, "#FFFFFF", 5)
    c.drawCircle(0, -110, 16, P("#7CC6FF")); c.drawCircle(0, -110, 16, P(INK, 4))
    for s_ in (-1, 1):
        fin = skia.Path(); fin.moveTo(s_ * 32, -50); fin.lineTo(s_ * 62, 6); fin.lineTo(s_ * 30, 0); fin.close(); ink(c, fin, "#FF6B6B", 4)
    nose = skia.Path(); nose.moveTo(0, -190); nose.cubicTo(18, -175, 26, -160, 28, -150); nose.lineTo(-28, -150); nose.cubicTo(-26, -160, -18, -175, 0, -190); nose.close()
    ink(c, nose, "#FF6B6B", 4)
    c.restore()
    # a ball resting on the mat
    c.drawCircle(860, 1655, 34, P("#FFD23F")); c.drawCircle(860, 1655, 34, P(INK, 5))
    bp = skia.Path(); bp.addArc(ell(860, 1655, 34, 14), 0, 180); c.drawPath(bp, P("#FF6B6B", 6))


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
    c.drawRect(skia.Rect.MakeXYWH(BX, BY, BW, 66), P("#BDE3FF" if KIDS else "#FFE08A"))
    c.drawLine(BX, BY + 66, BX + BW, BY + 66, P(INK, 5))
    for i, col in enumerate(("#FF6B6B", "#FFD23F", "#7BD389")):
        c.drawCircle(BX + 46 + i * 30, BY + 34, 9, P(col)); c.drawCircle(BX + 46 + i * 30, BY + 34, 9, P(INK, 3))
    K.text(c, "FUN FACTS", BX + BW - 36, BY + 34, 24, "#1D1D1F", K.FONT_XB, "r")
