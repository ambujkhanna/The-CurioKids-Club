"""Line-art 'basic' characters (original designs): DAD (40-45, learner) and TEEN (15-16, teacher).
Bold ink lines, round heads, stick limbs, a few flat colour accents.
Same draw() signature as char2d.draw so episodes can switch styles."""
import math
import skia
import doodle

INK = "#1D1D1F"
LW = 8.0  # main line weight (character units)


def hexc(h, a=1.0):
    h = h.lstrip("#")
    return skia.Color(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(255 * a))


def P(color, stroke=None, a=1.0, cap=True):
    p = skia.Paint(AntiAlias=True, Color=hexc(color, a))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke)
        if cap:
            p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join)
    doodle.apply_char(p, bool(stroke))
    return p


def ell(cx, cy, rx, ry):
    return skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry)


def oval_p(cx, cy, rx, ry):
    p = skia.Path(); p.addOval(ell(cx, cy, rx, ry)); return p


def F(c, path, col, lw=LW, a=1.0):
    if doodle.CHARS:  # marker fill slightly off the ink line + a second sketchy pass
        c.save(); c.translate(3.5, 2.5); c.drawPath(path, P(col, a=a)); c.restore()
        if lw:
            c.drawPath(path, P(INK, lw))
            seed = doodle.SEED; doodle.SEED = seed + 57
            c.drawPath(path, P(INK, max(1.5, lw * 0.35), a=0.7))
            doodle.SEED = seed
        return
    c.drawPath(path, P(col, a=a))
    if lw:
        c.drawPath(path, P(INK, lw))


def wob(t, f, ph):
    return math.sin(t * f + ph) * 0.6 + math.sin(t * f * 1.73 + ph * 2.1) * 0.3 + math.sin(t * f * 3.1 + ph * 0.7) * 0.1


SPEC = {
    "DAD": dict(scale=1.0, skin="#FFE0C8", head=(118, 128), shirt="#FF6B6B", shirt_sh="#E85555", tie="#3A86FF",
                hair="#6B5544", torso_h=300, torso_w=96, hip_w=84, leg=330, L1=150, L2=140, shoe="#5A3A26"),
    "TEEN": dict(scale=0.92, skin="#FFE4D2", head=(120, 120), shirt="#FFD23F", shirt_sh="#F2B600", band="#FF4D8D",
                 hair="#7A4428", torso_h=270, torso_w=84, hip_w=78, leg=320, L1=138, L2=128, shoe="#FFFFFF"),
    # Curio Kids Club cast: big sister Mia (girl drawing, own colours) and little brother Leo
    "MIA": dict(scale=0.92, skin="#FFE4D2", head=(120, 120), shirt="#3DDC97", shirt_sh="#21B57A", band="#FF8C42",
                hair="#4A2C1D", torso_h=270, torso_w=84, hip_w=78, leg=320, L1=138, L2=128, shoe="#FFFFFF"),
    "LEO": dict(scale=0.78, skin="#FFE2CC", head=(124, 118), shirt="#4FC3F7", shirt_sh="#2BA6DE", stripe="#FFD23F",
                hair="#3B2A20", torso_h=190, torso_w=76, hip_w=68, leg=215, L1=106, L2=98, shoe="#FF6B6B", shorts="#3A5BA0"),
}
GIRLS = ("TEEN", "MIA")


# ------------------------------------------------------------------ face
def back_hair(c, ch, t, sp, vals):
    RX, RY = sp["head"]; hc = -RY; roll = vals[2]
    sw = wob(t, 1.8, ch.ph) * 4 - roll * 0.6
    bk = skia.Path(); bk.moveTo(-RX - 10, hc)
    bk.cubicTo(-RX - 22, hc + 80, -RX - 14 + sw, hc + 140, -RX + 4 + sw, hc + 172)
    for k_ in range(4):  # wavy ends
        x0 = -RX + 4 + k_ * (2 * RX - 8) / 4 + sw
        bk.quadTo(x0 + (2 * RX - 8) / 8, hc + 196, x0 + (2 * RX - 8) / 4, hc + 172)
    bk.cubicTo(RX + 14 + sw, hc + 140, RX + 22, hc + 80, RX + 10, hc)
    bk.arcTo(ell(0, hc, RX + 10, RY + 10), 0, -180, False); bk.close()
    F(c, bk, sp["hair"])
    for s_ in (-1, 1):
        p = skia.Path(); p.moveTo(s_ * (RX - 4), hc + 60); p.quadTo(s_ * (RX + 6) + sw, hc + 120, s_ * (RX - 10) + sw, hc + 165)
        c.drawPath(p, P(INK, 4))


def mouth(c, mx, my, op, wd, sm):
    w = 26 * wd; o = op * 34; lift = sm * 9
    if o < 3.5:
        p = skia.Path(); p.moveTo(mx - w, my - lift); p.quadTo(mx, my + 6 + lift * 1.2, mx + w, my - lift)
        c.drawPath(p, P(INK, 6.5)); return
    p = skia.Path(); p.moveTo(mx - w, my - lift * 0.8)
    p.cubicTo(mx - w * 0.5, my - o * 0.22 - lift * 0.3, mx + w * 0.5, my - o * 0.22 - lift * 0.3, mx + w, my - lift * 0.8)
    p.cubicTo(mx + w * 0.85, my + o, mx - w * 0.85, my + o, mx - w, my - lift * 0.8); p.close()
    c.drawPath(p, P("#5B1720"))
    c.save(); c.clipPath(p, doAntiAlias=True)
    if o > 8: c.drawRect(skia.Rect.MakeLTRB(mx - w, my - o, mx + w, my - o * 0.22 + min(10, o * 0.26)), P("#FFFFFF"))
    if o > 14: c.drawOval(ell(mx, my + o * 0.8, w * 0.6, o * 0.38), P("#FF7A85"))
    c.restore()
    c.drawPath(p, P(INK, 5.5))


def head(c, ch, t, sp, vals):
    dad = ch.name == "DAD"; kid = ch.name == "LEO"
    yaw, pitch, roll, op, wd, bl, bu, btl, sm = vals
    fx, fy = yaw * 1.3, pitch * 1.0
    RX, RY = sp["head"]
    hc = -RY  # head centre above the neck point
    # ears
    for s in (-1, 1):
        F(c, oval_p(s * (RX - 2) - fx * 0.3, hc + 14, 18, 24), sp["skin"], 6)
    # head
    F(c, oval_p(0, hc, RX, RY), sp["skin"])
    # hair front
    if dad:
        q = skia.Path(); q.moveTo(-RX + 4, hc - 22)
        q.cubicTo(-RX - 6, hc - 92, -74 + fx * 0.3, hc - RY - 8, -24 + fx * 0.4, hc - RY - 34)   # rises at the front
        q.cubicTo(18 + fx * 0.4, hc - RY - 46, 74 + fx * 0.4, hc - RY - 30, 66 + fx * 0.4, hc - RY - 8)  # curls over
        q.cubicTo(RX + 6, hc - RY + 4, RX + 10, hc - 70, RX - 4, hc - 22)
        q.cubicTo(RX - 22, hc - 56, 46 + fx, hc - 70, 14 + fx, hc - 64)                             # hairline
        q.cubicTo(-20 + fx, hc - 60, -RX + 30, hc - 58, -RX + 4, hc - 22); q.close()
        F(c, q, sp["hair"])
        for (x0, y0, x1, y1, x2, y2) in ((-46, hc - 70, -52, hc - 120, -20, hc - RY - 24), (-12, hc - 66, -14, hc - 122, 26, hc - RY - 30),
                                         (24, hc - 68, 30, hc - 110, 60, hc - RY - 10)):
            p = skia.Path(); p.moveTo(x0 + fx * 0.3, y0); p.quadTo(x1 + fx * 0.35, y1, x2 + fx * 0.4, y2)
            c.drawPath(p, P(INK, 4))
        for s in (-1, 1):  # grey temples
            c.drawLine(s * (RX - 10) - fx * 0.3, hc - 44, s * (RX - 6) - fx * 0.3, hc - 4, P("#A7ADB4", 10))
    elif kid:  # short messy hair with tufts and a cowlick
        q = skia.Path(); q.moveTo(-RX - 4, hc + 4)
        q.cubicTo(-RX - 10, hc - 80, -50, hc - RY - 26, fx * 0.4, hc - RY - 22)
        q.cubicTo(50, hc - RY - 26, RX + 10, hc - 80, RX + 4, hc + 4)
        q.quadTo(RX - 8, hc - 36, RX - 30, hc - 44)
        for k_ in range(5):  # jagged fringe
            x1 = RX - 30 - (k_ + 0.5) * (2 * RX - 60) / 5; x2 = RX - 30 - (k_ + 1) * (2 * RX - 60) / 5
            q.lineTo(x1 + fx * 0.8, hc - 30 - (k_ % 2) * 8); q.lineTo(x2 + fx * 0.8, hc - 58)
        q.quadTo(-RX + 8, hc - 36, -RX - 4, hc + 4); q.close()
        F(c, q, sp["hair"])
        for x0, x1, y1 in ((-6, -26, -48), (6, 24, -52)):  # cowlick
            p = skia.Path(); p.moveTo(x0 + fx * 0.4, hc - RY - 20); p.quadTo(x0 + fx * 0.4, hc - RY + y1, x1 + fx * 0.4, hc - RY + y1 + 6)
            c.drawPath(p, P(INK, 6))
    else:
        bang = skia.Path(); bang.moveTo(-RX - 6, hc + 10)
        bang.cubicTo(-RX - 8, hc - 90, -40, hc - RY - 22, fx * 0.4, hc - RY - 10)
        bang.cubicTo(40, hc - RY - 22, RX + 8, hc - 90, RX + 6, hc + 10)
        bang.cubicTo(RX - 12, hc - 40, 60 + fx, hc - 56, 18 + fx, hc - 66)
        bang.quadTo(fx * 0.4, hc - 40, -20 + fx, hc - 66)
        bang.cubicTo(-60 + fx, hc - 56, -RX + 12, hc - 40, -RX - 6, hc + 10); bang.close()
        F(c, bang, sp["hair"])
        hb = skia.Path(); hb.addArc(ell(0, hc - 4, RX + 6, RY + 6), 205, 130)
        c.drawPath(hb, P(INK, 22)); c.drawPath(hb, P(sp["band"], 13))
    # eyes
    gx, gy = yaw * 0.35, pitch * 0.35
    for s in (-1, 1):
        ex, ey = s * 40 + fx, hc + 8 + fy
        if sm > 0.85 and bl < 0.5:
            p = skia.Path(); p.moveTo(ex - 15, ey + 4); p.quadTo(ex, ey - 14, ex + 15, ey + 4)
            c.drawPath(p, P(INK, 7))
        elif bl > 0.7:
            c.drawLine(ex - 14, ey + 2, ex + 14, ey + 2, P(INK, 6.5))
        else:
            k = 1 - bl; big = 1.2 if kid else 1.0
            c.drawOval(ell(ex + gx, ey + gy, 10 * big, 14 * k * big), P(INK))
            c.drawCircle(ex + gx + 3.5, ey + gy - 5 * k, 3.5 * big, P("#FFFFFF"))
            if not dad and not kid:  # lashes
                c.drawLine(ex + s * 9, ey - 10 * k, ex + s * 17, ey - 16 * k, P(INK, 4))
        by = hc - 30 + fy - bu * 12
        p = skia.Path(); p.moveTo(ex - s * 14, by - btl * 7); p.quadTo(ex, by - 6 - bu * 2, ex + s * 16, by + 3)
        c.drawPath(p, P(INK, 9 if dad else 6.5))
    # nose
    p = skia.Path(); p.moveTo(fx * 1.2 - 2, hc + 26 + fy); p.quadTo(fx * 1.2 + 12, hc + 40 + fy, fx * 1.2 - 2, hc + 48 + fy)
    c.drawPath(p, P(INK, 5))
    if dad:  # light stubble along the jaw
        import random as _r
        rg = _r.Random(7)
        for _ in range(70):
            a = rg.uniform(0.15, math.pi - 0.15); rr_ = rg.uniform(0.78, 0.95)
            c.drawCircle(math.cos(a) * RX * rr_ * 0.95 + fx * 0.4, hc + math.sin(a) * RY * rr_, 1.6, P(INK, a=0.55))
    else:
        for s in (-1, 1):
            c.drawOval(ell(s * 64 + fx, hc + 46 + fy, 16, 9), P("#FF8A9A", a=0.38 if kid else 0.5))
    mouth(c, fx * 1.1, hc + 74 + fy, op, wd, sm)


# ------------------------------------------------------------------ limbs
def stick_arm(c, x0, y0, a1, a2, s, sp, hand, sleeve):
    L1, L2 = sp["L1"], sp["L2"]
    r1, r2 = math.radians(a1), math.radians(a2)
    ex, ey = x0 + s * math.sin(r1) * L1, y0 + math.cos(r1) * L1
    hx, hy = ex + s * math.sin(r2) * L2, ey + math.cos(r2) * L2
    # sleeve on the upper arm (coloured, outlined), then ink stick to the hand
    sx, sy = x0 + (ex - x0) * 0.55, y0 + (ey - y0) * 0.55
    c.drawLine(x0, y0, sx, sy, P(INK, 34)); c.drawLine(x0, y0, sx, sy, P(sleeve, 22))
    c.drawLine(sx, sy, ex, ey, P(INK, LW)); c.drawLine(ex, ey, hx, hy, P(INK, LW))
    d = math.atan2(hy - ey, hx - ex)
    hx2, hy2 = hx + math.cos(d) * 14, hy + math.sin(d) * 14
    if hand == "point":
        c.drawLine(hx2, hy2, hx2 + math.cos(d) * 30, hy2 + math.sin(d) * 30, P(INK, 7))
        F(c, oval_p(hx2, hy2, 15, 15), sp["skin"], 6)
    elif hand == "fist":
        F(c, oval_p(hx2, hy2, 17, 16), sp["skin"], 6)
    else:
        F(c, oval_p(hx2, hy2, 17, 20), sp["skin"], 6)
        tx, ty = hx2 + math.cos(d - s * 1.6) * 16, hy2 + math.sin(d - s * 1.6) * 16
        c.drawLine(hx2, hy2, tx, ty, P(INK, 6))


def draw(c, ch, t, get_face, arms, intro_k, x, floor_y):
    sp = SPEC[ch.name]; dad = ch.name == "DAD"; kid = ch.name == "LEO"; girl = ch.name in GIRLS
    sway = wob(t, 1.4, ch.ph) * 1.8
    breath = math.sin(t * 2 * math.pi / 2.6 + ch.ph) * 0.016
    k = sp["scale"] * intro_k
    hop = get_face.get("hop", 0.0); bob = get_face.get("bob", 0.0)
    leg = sp["leg"]; hip_y = -leg; tw, hw = sp["torso_w"], sp["hip_w"]
    top_y = hip_y - sp["torso_h"]; H_ = sp["torso_h"]
    c.save(); c.translate(x, floor_y); c.scale(k, k)
    sh = P("#000000", a=0.12); sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 8))
    c.drawOval(ell(0, 4, 110 * (1 - hop / 300), 20), sh)
    c.translate(0, -hop); c.rotate(sway)
    # legs: ink sticks + shoes
    for s in (-1, 1):
        fxp = s * 46
        c.drawLine(s * hw * 0.45, hip_y - 6, fxp, -26, P(INK, LW + 1))
        shp = skia.Path(); shp.moveTo(fxp - s * 18, -30); shp.cubicTo(fxp + s * 30, -40, fxp + s * 56, -18, fxp + s * 50, 0)
        shp.lineTo(fxp - s * 22, 0); shp.quadTo(fxp - s * 28, -16, fxp - s * 18, -30); shp.close()
        F(c, shp, sp["shoe"], 6)
        if girl:
            c.drawLine(fxp - s * 18, -8, fxp + s * 46, -8, P(sp.get("band", "#FF4D8D") if ch.name == "MIA" else "#FF4D8D", 5, cap=False))
        elif kid:
            c.drawLine(fxp - s * 16, -10, fxp + s * 44, -10, P("#FFFFFF", 5, cap=False))
    c.translate(0, -bob)
    if girl:
        c.save(); c.translate(0, top_y - 14 + get_face["bounce"]); c.rotate(get_face["roll"])
        back_hair(c, ch, t, sp, get_face["vals"]); c.restore()
    # torso
    c.save(); c.translate(0, hip_y); c.scale(1, 1 + breath); c.translate(0, -hip_y)
    tp = skia.Path()
    tp.moveTo(-tw + 26, top_y); tp.lineTo(tw - 26, top_y); tp.quadTo(tw + 6, top_y, tw + 6, top_y + 34)
    tp.lineTo(hw, hip_y - 10); tp.quadTo(hw, hip_y + 8, hw - 18, hip_y + 8); tp.lineTo(-hw + 18, hip_y + 8)
    tp.quadTo(-hw, hip_y + 8, -hw, hip_y - 10); tp.lineTo(-tw - 6, top_y + 34); tp.quadTo(-tw - 6, top_y, -tw + 26, top_y); tp.close()
    F(c, tp, sp["shirt"])
    c.save(); c.clipPath(tp, doAntiAlias=True)
    c.drawRect(skia.Rect.MakeLTRB(tw * 0.35, top_y, tw + 10, hip_y + 10), P(sp["shirt_sh"], a=0.55))
    c.restore(); c.drawPath(tp, P(INK, LW))
    if dad:  # open collar, tie, buttons
        tie = skia.Path(); tie.moveTo(-10, top_y + 8); tie.lineTo(10, top_y + 8); tie.lineTo(15, top_y + H_ * 0.5)
        tie.lineTo(0, top_y + H_ * 0.58); tie.lineTo(-15, top_y + H_ * 0.5); tie.close()
        F(c, tie, sp["tie"], 5.5)
        for s in (-1, 1):
            cl = skia.Path(); cl.moveTo(s * 6, top_y + 4); cl.lineTo(s * 40, top_y - 6); cl.lineTo(s * 30, top_y + 30); cl.close()
            F(c, cl, "#FFFFFF", 5.5)
        c.drawLine(-hw + 6, hip_y - 26, hw - 6, hip_y - 26, P(INK, 5))  # belt line
    elif kid:  # striped t-shirt + shorts
        c.save(); c.clipPath(tp, doAntiAlias=True)
        for yy in (top_y + H_ * 0.42, top_y + H_ * 0.62):
            c.drawRect(skia.Rect.MakeLTRB(-tw - 10, yy, tw + 10, yy + 16), P(sp["stripe"]))
        sh_ = skia.Path(); sh_.moveTo(-hw - 2, hip_y - 34); sh_.lineTo(hw + 2, hip_y - 34); sh_.lineTo(hw + 6, hip_y + 12); sh_.lineTo(-hw - 6, hip_y + 12); sh_.close()
        c.drawPath(sh_, P(sp["shorts"]))
        c.restore(); c.drawPath(tp, P(INK, LW))
        c.drawLine(-tw * 0.4, top_y + 2, 0, top_y + 26, P(INK, 5)); c.drawLine(tw * 0.4, top_y + 2, 0, top_y + 26, P(INK, 5))
    else:  # hoodie: hood, strings, pocket
        F(c, oval_p(0, top_y + 6, tw * 0.66, 26), sp["shirt_sh"], 5.5)
        for s in (-1, 1):
            c.drawLine(s * 16, top_y + 26, s * 18, top_y + H_ * 0.32, P(INK, 4.5))
            c.drawCircle(s * 18, top_y + H_ * 0.32 + 6, 5, P(INK))
        pk = skia.Path(); pk.moveTo(-hw * 0.6, hip_y - 26); pk.lineTo(-hw * 0.45, hip_y - H_ * 0.32)
        pk.lineTo(hw * 0.45, hip_y - H_ * 0.32); pk.lineTo(hw * 0.6, hip_y - 26)
        c.drawPath(pk, P(INK, 5.5))
    c.restore()
    # neck + head
    c.drawLine(0, top_y - 2, 0, top_y - 24, P(INK, LW))
    c.save(); c.translate(0, top_y - 14 + get_face["bounce"]); c.rotate(get_face["roll"])
    head(c, ch, t, sp, get_face["vals"])
    c.restore()
    # arms
    for s in (-1, 1):
        a1, a2, hd = arms[s]
        stick_arm(c, s * (tw - 4), top_y + 22, a1, a2, s, sp, hd, sp["shirt"])
    c.restore()
