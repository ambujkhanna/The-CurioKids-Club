"""Shared icons and board widgets used by episode scenes."""
import math
import skia
from kit2d import P, rr, ell, text, shadow_rrect, FONT_XB, FONT_B, FONT_SB, hexc


def icon_target(c, x, y, k=1.0):
    for r_, col in ((30, "#FF4D6D"), (21, "#FFFFFF"), (12, "#FF4D6D")):
        c.drawCircle(x, y, r_ * k, P(col))
    c.drawLine(x, y, x + 26 * k, y - 26 * k, P("#1F2D44", 4 * k))


def icon_search(c, x, y, k=1.0):
    c.drawCircle(x - 5 * k, y - 5 * k, 15 * k, P("#0A84FF", 6 * k)); c.drawLine(x + 6 * k, y + 6 * k, x + 18 * k, y + 18 * k, P("#0A84FF", 8 * k))


def icon_cal(c, x, y, k=1.0):
    c.drawRRect(rr(x - 22 * k, y - 20 * k, 44 * k, 42 * k, 8 * k), P("#FFFFFF")); c.drawRRect(rr(x - 22 * k, y - 20 * k, 44 * k, 42 * k, 8 * k), P("#FF4D6D", 3 * k))
    c.drawRect(skia.Rect.MakeXYWH(x - 22 * k, y - 20 * k, 44 * k, 12 * k), P("#FF4D6D"))
    for i in range(3):
        for j in range(2):
            c.drawCircle(x - 12 * k + i * 12 * k, y + 2 * k + j * 10 * k, 3 * k, P("#5B6B80"))


def icon_mail(c, x, y, k=1.0):
    c.drawRRect(rr(x - 24 * k, y - 16 * k, 48 * k, 34 * k, 6 * k), P("#FFC300"))
    p = skia.Path(); p.moveTo(x - 24 * k, y - 14 * k); p.lineTo(x, y + 4 * k); p.lineTo(x + 24 * k, y - 14 * k)
    c.drawPath(p, P("#1F2D44", 3.5 * k))


def icon_suitcase(c, x, y, k=1.0):
    c.drawRRect(rr(x - 14 * k, y - 34 * k, 28 * k, 16 * k, 6 * k), P("#8B4A26", 5 * k))
    c.drawRRect(rr(x - 34 * k, y - 22 * k, 68 * k, 50 * k, 10 * k), P("#FF7A45"))
    c.drawLine(x - 34 * k, y - 2 * k, x + 34 * k, y - 2 * k, P("#E85D2A", 4 * k))


def icon_warn(c, x, y, k=1.0, col="#FFB703"):
    p = skia.Path(); p.moveTo(x, y - 34 * k); p.lineTo(x + 36 * k, y + 28 * k); p.lineTo(x - 36 * k, y + 28 * k); p.close()
    c.drawPath(p, P(col)); c.drawPath(p, P(col, 8 * k))
    c.drawLine(x, y - 10 * k, x, y + 8 * k, P("#1F2D44", 7 * k)); c.drawCircle(x, y + 18 * k, 4 * k, P("#1F2D44"))


def icon_x(c, x, y, k=1.0):
    c.drawCircle(x, y, 20 * k, P("#FF4D6D"))
    c.drawLine(x - 8 * k, y - 8 * k, x + 8 * k, y + 8 * k, P("#FFFFFF", 5 * k)); c.drawLine(x + 8 * k, y - 8 * k, x - 8 * k, y + 8 * k, P("#FFFFFF", 5 * k))


def icon_user(c, x, y, k=1.0):
    c.drawCircle(x, y, 40 * k, P("#FFC300")); c.drawCircle(x, y - 10 * k, 14 * k, P("#1F2D44"))
    c.drawOval(ell(x, y + 22 * k, 23 * k, 14 * k), P("#1F2D44"))


def chip(c, x, y, label, col, icon=None, size=30):
    f = skia.Font(FONT_XB, size); w = f.measureText(label) + (90 if icon else 50)
    r = rr(x - w / 2, y - 32, w, 64, 32); shadow_rrect(c, r, 6, 4, 0.2); c.drawRRect(r, P(col))
    if icon:
        icon(c, x - w / 2 + 40, y, 0.6); text(c, label, x - w / 2 + 74, y, size, "#FFFFFF", FONT_XB, "l")
    else:
        text(c, label, x, y, size, "#FFFFFF")


def row(c, x, y, w, label, icon=None, size=28, col="#DCEBFF"):
    r = rr(x - w / 2, y - 38, w, 76, 22); shadow_rrect(c, r, 6, 4, 0.22); c.drawRRect(r, P(col))
    if icon:
        icon(c, x - w / 2 + 46, y, 0.8); text(c, label, x - w / 2 + 88, y, size, "#1F2D44", FONT_B, "l")
    else:
        text(c, label, x, y, size, "#1F2D44", FONT_B)



def icon_bulb(c, x, y, k=1.0):
    c.drawCircle(x, y - 6 * k, 22 * k, P("#FFD23F")); c.drawCircle(x, y - 6 * k, 22 * k, P("#1F2D44", 3 * k))
    c.drawRRect(rr(x - 10 * k, y + 14 * k, 20 * k, 14 * k, 4 * k), P("#90A4AE"))
    for a in (-0.9, -0.3, 0.3, 0.9):
        c.drawLine(x + math.sin(a) * 30 * k, y - 6 * k - math.cos(a) * 30 * k, x + math.sin(a) * 38 * k, y - 6 * k - math.cos(a) * 38 * k, P("#FFB703", 4 * k))


def icon_shield(c, x, y, k=1.0):
    p = skia.Path(); p.moveTo(x, y - 30 * k); p.lineTo(x + 26 * k, y - 20 * k); p.quadTo(x + 24 * k, y + 16 * k, x, y + 30 * k)
    p.quadTo(x - 24 * k, y + 16 * k, x - 26 * k, y - 20 * k); p.close()
    c.drawPath(p, P("#2ECC71")); c.drawPath(p, P("#1F2D44", 3 * k))
    q = skia.Path(); q.moveTo(x - 10 * k, y); q.lineTo(x - 2 * k, y + 8 * k); q.lineTo(x + 12 * k, y - 8 * k)
    c.drawPath(q, P("#FFFFFF", 5 * k))


def icon_coin(c, x, y, k=1.0):
    c.drawCircle(x, y, 26 * k, P("#FFC93C")); c.drawCircle(x, y, 26 * k, P("#B8860B", 4 * k))
    text(c, "$", x, y, 30 * k, "#8D6E00", FONT_XB)


def icon_eye(c, x, y, k=1.0):
    p = skia.Path(); p.moveTo(x - 30 * k, y); p.quadTo(x, y - 26 * k, x + 30 * k, y); p.quadTo(x, y + 26 * k, x - 30 * k, y); p.close()
    c.drawPath(p, P("#FFFFFF")); c.drawPath(p, P("#1F2D44", 3.5 * k))
    c.drawCircle(x, y, 10 * k, P("#0A84FF")); c.drawCircle(x, y, 4.5 * k, P("#1F2D44"))


def icon_book(c, x, y, k=1.0):
    for s in (-1, 1):
        p = skia.Path(); p.moveTo(x, y - 20 * k); p.quadTo(x + s * 16 * k, y - 28 * k, x + s * 32 * k, y - 22 * k)
        p.lineTo(x + s * 32 * k, y + 22 * k); p.quadTo(x + s * 16 * k, y + 16 * k, x, y + 24 * k); p.close()
        c.drawPath(p, P("#CDE7FF")); c.drawPath(p, P("#1F2D44", 3 * k))


def icon_globe(c, x, y, k=1.0):
    c.drawCircle(x, y, 26 * k, P("#7BD389")); c.drawCircle(x, y, 26 * k, P("#1F2D44", 3 * k))
    c.drawOval(ell(x, y, 11 * k, 26 * k), P("#1F2D44", 2.5 * k)); c.drawLine(x - 26 * k, y, x + 26 * k, y, P("#1F2D44", 2.5 * k))


def icon_brain(c, x, y, k=1.0):
    for dx, dy, r in ((-12, -8, 16), (10, -10, 16), (-14, 10, 14), (12, 10, 14), (0, 0, 14)):
        c.drawCircle(x + dx * k, y + dy * k, r * k, P("#FF9AB5"))
    c.drawCircle(x, y, 28 * k, P("#1F2D44", 3 * k)); c.drawLine(x, y - 26 * k, x, y + 26 * k, P("#C2185B", 2.5 * k))


def icon_phone(c, x, y, k=1.0):
    c.drawRRect(rr(x - 18 * k, y - 30 * k, 36 * k, 60 * k, 8 * k), P("#1F2D44"))
    c.drawRRect(rr(x - 14 * k, y - 24 * k, 28 * k, 44 * k, 4 * k), P("#7CF5FF"))


def icon_lock_small(c, x, y, k=1.0):
    from kit2d import icon_lock
    icon_lock(c, x, y - 4 * k, k * 0.8)
