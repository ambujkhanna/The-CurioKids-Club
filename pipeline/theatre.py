"""The CurioKids Club puppet theatre (2.5D look: shading, lighting, depth).

back(c, t)  - wooden frame, gold trim, spot-lit backdrop, perspective stage floor; then clips to the stage
front(c, t) - drawn AFTER the board content: velvet curtains (they open at the start), valance, footlights.
Board content (pictures and words) therefore appears BETWEEN the backdrop and the curtains, like puppets on a stage.
"""
import math
import skia
from char_line import hexc
from kit2d import P

SX0, SY0, SX1, SY1 = 22, 118, 1058, 918          # outer wooden frame
WX0, WY0, WX1, WY1 = 62, 156, 1018, 872          # stage opening (backdrop)
FLOOR_H = 70


def _lin(x0, y0, x1, y1, cols, pos=None):
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeLinear([skia.Point(x0, y0), skia.Point(x1, y1)], [hexc(c_) for c_ in cols], pos))
    return p


def back(c, t):
    outer = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(SX0, SY0, SX1, SY1), 28, 28)
    sh = P("#000000", a=0.28); sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 22))
    c.save(); c.translate(0, 22); c.drawRRect(outer, sh); c.restore()
    c.drawRRect(outer, _lin(0, SY0, 0, SY1, ["#C98A52", "#A5612F", "#7E4520"]))
    for k in range(7):  # wood grain
        y = SY0 + 20 + k * (SY1 - SY0 - 40) / 6
        c.drawLine(SX0 + 8, y, SX0 + 34, y + 30, P("#6B3A1A", 2, a=0.35)); c.drawLine(SX1 - 8, y + 10, SX1 - 34, y + 40, P("#6B3A1A", 2, a=0.35))
    c.drawRRect(outer, P("#FFE1B0", 4, a=0.55))  # bevel highlight
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(SX0 + 3, SY0 + 3, SX1 - 3, SY1 - 3), 26, 26), P("#4A2810", 3, a=0.6))
    gold = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(WX0 - 14, WY0 - 14, WX1 + 14, WY1 + 14), 20, 20)
    c.drawRRect(gold, _lin(0, WY0, 0, WY1, ["#FFE58A", "#E0A82E", "#FFE58A", "#C98B1E"], [0, 0.35, 0.6, 1]))
    win = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(WX0, WY0, WX1, WY1), 14, 14)
    c.drawRRect(win, _lin(0, WY0, 0, WY1, ["#FFF4D6", "#FFE6B5"]))
    c.save(); c.clipRRect(win, doAntiAlias=True)
    spot = skia.Paint(AntiAlias=True)
    spot.setShader(skia.GradientShader.MakeRadial(skia.Point(540, 470), 520, [skia.Color(255, 255, 245, 230), skia.Color(255, 250, 225, 90), skia.Color(255, 240, 200, 0)], [0, 0.55, 1]))
    c.drawRect(skia.Rect.MakeLTRB(WX0, WY0, WX1, WY1), spot)
    vig = skia.Paint(AntiAlias=True)
    vig.setShader(skia.GradientShader.MakeRadial(skia.Point(540, 500), 640, [skia.Color(0, 0, 0, 0), skia.Color(0, 0, 0, 0), skia.Color(90, 40, 10, 70)], [0, 0.7, 1]))
    c.drawRect(skia.Rect.MakeLTRB(WX0, WY0, WX1, WY1), vig)
    fy = WY1 - FLOOR_H  # perspective wooden stage floor
    fl = skia.Path(); fl.moveTo(WX0, WY1); fl.lineTo(WX0 + 70, fy); fl.lineTo(WX1 - 70, fy); fl.lineTo(WX1, WY1); fl.close()
    c.drawPath(fl, _lin(0, fy, 0, WY1, ["#B87842", "#8C5426"]))
    for k in range(1, 12):
        xa = WX0 + 70 + k * (WX1 - WX0 - 140) / 12; xb = WX0 + k * (WX1 - WX0) / 12
        c.drawLine(xa, fy, xb, WY1, P("#6B3A1A", 2, a=0.45))
    c.drawLine(WX0 + 70, fy, WX1 - 70, fy, P("#5A2F12", 3))
    c.restore()
    c.drawRRect(win, P("#5A2F12", 4))
    c.save(); c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(WX0, WY0, WX1, WY1), 14, 14), doAntiAlias=True)


def _curtain(c, side, t, open_k):
    xo = WX0 if side < 0 else WX1
    full = (WX1 - WX0) / 2 + 8
    top_w = full + (92 - full) * open_k; tie_w = full + (40 - full) * open_k; bot_w = full + (72 - full) * open_k
    tie_y = WY0 + (WY1 - WY0) * (0.58 + 0.1 * (1 - open_k))
    sway = math.sin(t * 1.3 + side) * 3
    s_ = 1 if side < 0 else -1
    p = skia.Path()
    p.moveTo(xo, WY0 - 4); p.lineTo(xo + s_ * (top_w + sway), WY0 - 4)
    p.cubicTo(xo + s_ * (top_w * 0.9), WY0 + 160, xo + s_ * (tie_w + 20), tie_y - 120, xo + s_ * tie_w, tie_y)
    p.cubicTo(xo + s_ * (tie_w + 6), tie_y + 80, xo + s_ * (bot_w + 8), WY1 - 120, xo + s_ * (bot_w + sway), WY1 + 2)
    p.lineTo(xo, WY1 + 2); p.close()
    sh = P("#000000", a=0.28); sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 10))
    c.save(); c.translate(s_ * 9, 6); c.drawPath(p, sh); c.restore()
    n = 6 if open_k > 0.5 else 14
    stops = [k / n for k in range(n + 1)]; cols = ["#7A0F22" if k % 2 == 0 else "#E8384F" for k in range(n + 1)]
    xa, xb = sorted((xo, xo + s_ * top_w))
    fold = skia.Paint(AntiAlias=True)
    fold.setShader(skia.GradientShader.MakeLinear([skia.Point(xa, 0), skia.Point(xb, 0)], [hexc(x) for x in cols], stops))
    c.drawPath(p, fold)
    shade = skia.Paint(AntiAlias=True)
    shade.setShader(skia.GradientShader.MakeLinear([skia.Point(0, WY0), skia.Point(0, WY1)], [skia.Color(255, 255, 255, 45), skia.Color(0, 0, 0, 0), skia.Color(0, 0, 0, 70)]))
    c.drawPath(p, shade)
    c.drawPath(p, P("#4A0812", 4))
    if open_k > 0.6:  # gold rope + tassel
        tx = xo + s_ * (tie_w + 4)
        c.drawLine(xo, tie_y - 6, tx, tie_y, P("#B8860B", 12)); c.drawLine(xo, tie_y - 6, tx, tie_y, P("#FFD54A", 7))
        c.drawCircle(tx, tie_y, 15, _lin(tx, tie_y - 15, tx, tie_y + 15, ["#FFE58A", "#C98B1E"])); c.drawCircle(tx, tie_y, 15, P("#7A5200", 3))
        ts = skia.Path(); ts.moveTo(tx - 10, tie_y + 12); ts.lineTo(tx + 10, tie_y + 12); ts.lineTo(tx + 14, tie_y + 54); ts.lineTo(tx - 14, tie_y + 54); ts.close()
        c.drawPath(ts, _lin(0, tie_y + 12, 0, tie_y + 54, ["#FFD54A", "#C98B1E"])); c.drawPath(ts, P("#7A5200", 3))


def front(c, t):
    open_k = max(0.0, min(1.0, (t - 0.15) / 0.9)); open_k = open_k * open_k * (3 - 2 * open_k)
    c.save(); c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(WX0, WY0 - 2, WX1, WY1 + 4), 14, 14), doAntiAlias=True)
    _curtain(c, -1, t, open_k); _curtain(c, 1, t, open_k)
    n = 8; w = (WX1 - WX0) / n
    val = skia.Path(); val.moveTo(WX0, WY0 - 4)
    for k in range(n):
        val.quadTo(WX0 + (k + 0.5) * w, WY0 + 118, WX0 + (k + 1) * w, WY0 - 4)
    val.close()
    sh = P("#000000", a=0.3); sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 8))
    c.save(); c.translate(0, 8); c.drawPath(val, sh); c.restore()
    c.drawPath(val, _lin(0, WY0, 0, WY0 + 90, ["#E8384F", "#A3142B"]))
    fr = skia.Path(); fr.moveTo(WX0, WY0 - 4)
    for k in range(n):
        fr.quadTo(WX0 + (k + 0.5) * w, WY0 + 118, WX0 + (k + 1) * w, WY0 - 4)
    c.drawPath(fr, P("#FFD54A", 7)); c.drawPath(fr, P("#B8860B", 2))
    for k in range(n - 1):
        tx = WX0 + (k + 1) * w
        c.drawCircle(tx, WY0 + 6, 9, P("#FFD54A")); c.drawCircle(tx, WY0 + 6, 9, P("#7A5200", 2))
    c.restore()
    for k in range(7):  # footlights glowing on the frame
        x = WX0 + 80 + k * (WX1 - WX0 - 160) / 6; y = WY1 + 24
        g = P("#FFE58A", a=0.55 + 0.25 * math.sin(t * 4 + k)); g.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 12))
        c.drawCircle(x, y - 6, 22, g)
        c.drawCircle(x, y, 11, _lin(x, y - 11, x, y + 11, ["#FFFBE0", "#FFC93C"])); c.drawCircle(x, y, 11, P("#7A5200", 3))
