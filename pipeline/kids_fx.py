"""Attention effects for The CurioKids Club: sparkle bursts when pictures pop in, confetti on 'wow' words and on Subscribe.

    fx = KidsFX(K, bursts=[(t, x, y), ...], confetti=[t, ...]);  fx.draw(c, t)   # world coordinates, after the board
"""
import math, random
import skia

COLS = ("#FF4D6D", "#FFD23F", "#4FC3F7", "#7BD389", "#C9A7FF", "#FF9F45")


def _p(K, col, a=1.0):
    return skia.Paint(AntiAlias=True, Color=K.hexc(col, max(0.0, min(1.0, a))))


def _star(cx, cy, r, rot):
    p = skia.Path()
    for k in range(10):
        a = rot + k * math.pi / 5 - math.pi / 2; rr = r if k % 2 == 0 else r * 0.45
        (p.moveTo if k == 0 else p.lineTo)(cx + math.cos(a) * rr, cy + math.sin(a) * rr)
    p.close(); return p


class KidsFX:
    def __init__(self, K, bursts, confetti):
        self.K = K
        rg = random.Random(11)
        self.bursts = []
        for t0, x, y in bursts:
            parts = [(rg.uniform(0, 2 * math.pi), rg.uniform(90, 170), rg.choice(COLS), rg.uniform(9, 16), rg.random() < 0.5) for _ in range(10)]
            self.bursts.append((t0, x, y, parts))
        self.confetti = []
        for t0 in confetti:
            pieces = [(rg.uniform(-40, 1120), rg.uniform(-500, -40), rg.uniform(260, 520), rg.uniform(-60, 60), rg.choice(COLS),
                       rg.uniform(0, 6.28), rg.uniform(4, 10), rg.random() < 0.3) for _ in range(70)]
            self.confetti.append((t0, pieces))

    def draw(self, c, t):
        K = self.K
        for t0, x, y, parts in self.bursts:
            u = t - t0
            if not 0 <= u <= 0.65: continue
            e = 1 - (1 - u / 0.65) ** 3; a = 1 - u / 0.65
            for ang, dist, col, size, star in parts:
                px, py = x + math.cos(ang) * dist * e, y + math.sin(ang) * dist * e
                if star: c.drawPath(_star(px, py, size * (1.1 - 0.4 * e), u * 6), _p(K, col, a))
                else: c.drawCircle(px, py, size * 0.45 * (1 - 0.5 * e), _p(K, col, a))
        for t0, pieces in self.confetti:
            u = t - t0
            if not 0 <= u <= 2.4: continue
            a = min(1.0, (2.4 - u) / 0.5)
            for x0, y0, vy, vx, col, ph, spin, circ in pieces:
                px = x0 + vx * u + math.sin(u * 3 + ph) * 22; py = y0 + vy * u + 140 * u * u
                if circ: c.drawCircle(px, py, 8, _p(K, col, a)); continue
                c.save(); c.translate(px, py); c.rotate(math.degrees(ph + u * spin))
                c.scale(1.0, abs(math.cos(u * spin + ph)) + 0.2)
                c.drawRect(skia.Rect.MakeXYWH(-9, -5, 18, 10), _p(K, col, a)); c.restore()
