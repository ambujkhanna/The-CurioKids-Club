"""Animated explanation scenes (same file in both channels). Characters stay 2D; the board comes alive.

Board types (in episode.json "board"):
  lifecycle     {"title", "items": [{"icon","label","cue"}...]}             stages: a big 3D hero changes stage by stage
  flow          {"title", "items": [nodes 2-4], "packet": "💬"}             things travel between nodes along curved paths
  transform     {"title", "from": {"icon","label"}, "to": {"icon","label","cue"}}   A shakes, bursts, becomes B
  water_cycle   {"title", "items": 4 x {"label","cue"}}   evaporation, condensation, precipitation, collection
  plant_growth  {"title", "items": 3-5 x {"label","cue"}} seed cracks, roots, shoot, leaves, tree

Every scene draws only inside the board and uses the episode's cue words for timing.
If anything inside a scene fails, the scene is skipped for that frame (the video still renders).
"""
import math, random
import skia

NAVY = "#1F2D44"


def _c(h, a=1.0):
    h = h.lstrip("#"); return skia.Color(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(255 * max(0.0, min(1.0, a))))


def _p(col, a=1.0, stroke=None, blur=None):
    p = skia.Paint(AntiAlias=True, Color=_c(col, a))
    if stroke: p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke); p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur: p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


def _cl(u): return max(0.0, min(1.0, u))
def _smooth(u): u = _cl(u); return u * u * (3 - 2 * u)
def _back(u, s=1.7): u = _cl(u) - 1; return u * u * ((s + 1) * u + s) + 1
def _elastic(u):
    if u <= 0: return 0.0
    if u >= 1.2: return 1.0
    return 1 - math.exp(-6 * u) * math.cos(10 * u)


def _icon(E, c, name, x, y, k, a=1.0, rot=0.0):
    fn = E.ico(name)
    if not fn or k <= 0.01 or a <= 0.01: return
    if a < 0.999: c.saveLayerAlpha(None, int(255 * a))
    else: c.save()
    c.translate(x, y); c.rotate(rot); fn(c, 0, 0, k); c.restore()


def _safe(fn):
    def run(c, t, e):
        try:
            fn(c, t, e)
        except Exception as ex:  # a scene problem must never stop the video
            if not getattr(run, "_warned", False):
                print("note: scene frame skipped:", str(ex)[:120]); run._warned = True
    return run


def _times(E, i, t0, items, gap=1.0):
    return [E.cue_t(i, it, t0 + 0.5 + k * gap) for k, it in enumerate(items)]


def _title(E, i, t0, t1, sc):
    """Optional pill title; returns the y where the scene area starts."""
    if not sc.get("title"): return E.BY + 30
    E.el(t0, t1, _safe(lambda c, t, e: E.pill(c, E.BCX, E.BY + 70, sc["title"], sc.get("color", "#FF6F61"), 44)), None, (E.BCX, E.BY + 70))
    return E.BY + 120


def _sparkles(c, x, y, t, t_burst, n=10, r=120, col="#FFD54F"):
    u = (t - t_burst) / 0.7
    if not 0 <= u <= 1: return
    for k in range(n):
        a = k * 2 * math.pi / n + 0.3
        d = r * _smooth(u); s = 16 * (1 - u) + 3
        x_, y_ = x + math.cos(a) * d, y + math.sin(a) * d
        st = skia.Path(); st.moveTo(x_, y_ - s); st.quadTo(x_, y_, x_ + s, y_); st.quadTo(x_, y_, x_, y_ + s); st.quadTo(x_, y_, x_ - s, y_); st.quadTo(x_, y_, x_, y_ - s)
        c.drawPath(st, _p(col, 1 - u))


# ------------------------------------------------------------------ lifecycle: one hero changes stage by stage
def build_lifecycle(E, i, t0, t1, sc):
    items = sc.get("items", [])[:6]; n = len(items)
    if not n: return
    top = _title(E, i, t0, t1, sc)
    times = _times(E, i, t0, items, 1.1)
    hx, hy = E.BCX, top + (E.BY + E.BH - top) * 0.36
    ty = E.BY + E.BH - 72  # timeline row
    xs = [E.BX + E.BW * (0.5 + (k - (n - 1) / 2) * min(0.2, 0.86 / max(1, n - 1)) if n > 1 else 0.5) for k in range(n)]

    def draw(c, t, e):
        cur = max([k for k in range(n) if t >= times[k]] or [-1])
        # glowing floor disc under the hero
        c.drawOval(skia.Rect.MakeXYWH(hx - 170, hy + 115, 340, 50), _p("#000000", 0.10, blur=14))
        halo = 0.5 + 0.5 * math.sin(t * 3)
        c.drawCircle(hx, hy, 150 + 6 * halo, _p("#FFF3B0", 0.55, blur=30))
        # hero: previous stage shrinks away while the new one pops in
        for k in (cur - 1, cur):
            if k < 0: continue
            if k == cur:
                u = (t - times[k]) / 0.55
                sc_ = 3.2 * _elastic(u); a = 1.0
            else:
                u = (t - times[cur]) / 0.35
                sc_ = 3.2 * (1 - _smooth(u)); a = 1 - _smooth(u)
            bob = 6 * math.sin(t * 2.2 + k)
            _icon(E, c, items[k].get("icon", "bulb"), hx, hy + bob, sc_, a, rot=2.5 * math.sin(t * 1.7))
        if cur >= 0:
            _sparkles(c, hx, hy, t, times[cur], n=12, r=190)
            lab = items[cur].get("label", "")
            a = _smooth((t - times[cur]) / 0.3)
            c.saveLayerAlpha(None, int(255 * a)); E.big_text(c, lab, hx, hy + 168, 50, NAVY, E.BW - 200, lines=1, min_size=32); c.restore()
        # timeline: path that fills as the stages arrive, small icons that light up
        x0, x1 = xs[0], xs[-1]
        c.drawLine(x0, ty, x1, ty, _p("#C9D3E3", 1, 12))
        if cur >= 0 and n > 1:
            seg = (x1 - x0) / (n - 1)
            fill = x0 + seg * cur + seg * _smooth((t - times[cur]) / 0.6) * (1 if cur < n - 1 else 0)
            c.drawLine(x0, ty, min(fill, x1), ty, _p("#2ECC71", 1, 12))
        for k in range(n):
            on = t >= times[k]
            r = 40
            c.drawCircle(xs[k], ty, r, _p("#FFFFFF")); c.drawCircle(xs[k], ty, r, _p("#2ECC71" if on else "#C9D3E3", 1, 6))
            _icon(E, c, items[k].get("icon", "bulb"), xs[k], ty, 0.95 if on else 0.8, 1.0 if on else 0.35)
    E.el(t0, t1, _safe(draw), None, (hx, hy))


# ------------------------------------------------------------------ flow: packets travel between nodes
def build_flow(E, i, t0, t1, sc):
    items = sc.get("items", [])[:4]; n = len(items)
    if n < 2: return
    top = _title(E, i, t0, t1, sc)
    times = _times(E, i, t0, items, 0.9)
    cy = top + (E.BY + E.BH - top) * 0.47
    xs = [E.BX + E.BW * (0.5 + (k - (n - 1) / 2) * ((0.62 if n > 2 else 0.5) / (n - 1))) for k in range(n)]
    packet = sc.get("packet", "💬")

    def arc(k, u):  # point on the curved path from node k to k+1
        x0, x1 = xs[k], xs[k + 1]; xm = (x0 + x1) / 2; lift = 120 if k % 2 == 0 else -120
        x = (1 - u) ** 2 * x0 + 2 * (1 - u) * u * xm + u * u * x1
        y = (1 - u) ** 2 * cy + 2 * (1 - u) * u * (cy - lift) + u * u * cy
        return x, y

    def draw(c, t, e):
        for k in range(n - 1):  # paths appear when the next node arrives
            if t < times[k + 1] - 0.3: continue
            grow = _smooth((t - times[k + 1] + 0.3) / 0.5)
            pth = skia.Path(); pth.moveTo(*arc(k, 0))
            for s in range(1, 31):
                u = s / 30 * grow; pth.lineTo(*arc(k, u))
            c.drawPath(pth, _p("#B0BED6", 1, 8))
            # dashes moving along the path = direction
            for d in range(6):
                u = ((t * 0.5 + d / 6) % 1.0) * grow
                x, y = arc(k, u); c.drawCircle(x, y, 6, _p("#7E8FB0"))
        for k in range(n):  # nodes
            if t < times[k]: continue
            a = _back((t - times[k]) / 0.4)
            pulse = 0
            for j in range(k):  # a packet arriving makes the node pulse
                pass
            last_arrival = None
            if k > 0 and t > times[k] + 0.6:
                ph = ((t - times[k] - 0.6) * 0.55) % 1.0
                if ph > 0.92: last_arrival = (ph - 0.92) / 0.08
            pulse = 1 + (0.12 * math.sin(last_arrival * math.pi) if last_arrival is not None else 0)
            r = 78 * a * pulse
            c.drawCircle(xs[k], cy + 8, r, _p("#000000", 0.12, blur=8))
            c.drawCircle(xs[k], cy, r, _p("#FFFFFF")); c.drawCircle(xs[k], cy, r, _p("#2F6BFF" if _studio() else ["#0A84FF", "#E91E63", "#2ECC71", "#FF9F0A"][k % 4], 1, 7))
            _icon(E, c, items[k].get("icon", "bulb"), xs[k], cy, 1.6 * a)
            E.big_text(c, items[k].get("label", ""), xs[k], cy + 128, 36, NAVY, E.BW * 0.28, lines=2, min_size=26)
        if t > times[-1] + 0.6:  # packets keep travelling once everything is shown
            for k in range(n - 1):
                u = ((t - times[-1] - 0.6) * 0.55 - k * 0.5) % 1.0
                x, y = arc(k, _smooth(u))
                _icon(E, c, packet, x, y, 0.9, 1.0, rot=10 * math.sin(t * 4))
    E.el(t0, t1, _safe(draw), None, (E.BCX, cy))


# ------------------------------------------------------------------ transform: A becomes B
def build_transform(E, i, t0, t1, sc):
    A, B = sc.get("from", {}), sc.get("to", {})
    top = _title(E, i, t0, t1, sc)
    tA = E.cue_t(i, A, t0 + 0.3); tB = E.cue_t(i, B, tA + 1.6)
    cx, cy = E.BCX, top + (E.BY + E.BH - top) * 0.45
    rnd = random.Random(7)
    bits = [(rnd.uniform(0, 2 * math.pi), rnd.uniform(80, 240), rnd.choice(["#FFD54F", "#FF6F61", "#4FC3F7", "#2ECC71"])) for _ in range(22)]

    def draw(c, t, e):
        if t < tB:  # A: appears, then shakes more and more just before the change
            a = _back((t - tA) / 0.45)
            shake = max(0.0, 1 - (tB - t) / 0.8) * 9 * math.sin(t * 55)
            _icon(E, c, A.get("icon", "bulb"), cx + shake, cy, 3.4 * a, 1.0, rot=shake)
            E.big_text(c, A.get("label", ""), cx, cy + 180, 46, NAVY, E.BW - 220, lines=1, min_size=30)
        else:
            u = (t - tB) / 0.6
            for ang, d, col in bits:  # burst
                if u < 1:
                    r = d * _smooth(u); c.drawCircle(cx + math.cos(ang) * r, cy + math.sin(ang) * r, 12 * (1 - u) + 2, _p(col, 1 - u))
            _icon(E, c, B.get("icon", "bulb"), cx, cy + 5 * math.sin(t * 2), 3.4 * _elastic((t - tB) / 0.6), 1.0)
            a = _smooth((t - tB - 0.2) / 0.3)
            c.saveLayerAlpha(None, int(255 * a)); E.big_text(c, B.get("label", ""), cx, cy + 180, 50, "#E91E63", E.BW - 220, lines=1, min_size=30); c.restore()
            _sparkles(c, cx, cy, t, tB + 0.1, n=10, r=200)
    E.el(tA, t1, _safe(draw), None, (cx, cy))


# ------------------------------------------------------------------ water cycle (illustrated)
def build_water_cycle(E, i, t0, t1, sc):
    items = (sc.get("items") or [{"label": "Evaporation"}, {"label": "Condensation"}, {"label": "Precipitation"}, {"label": "Collection"}])[:4]
    top = _title(E, i, t0, t1, sc)
    times = _times(E, i, t0, items, 1.4)
    L, R, T, B = E.BX + 20, E.BX + E.BW - 20, top + 10, E.BY + E.BH - 20
    W, H = R - L, B - T
    sea_y = T + H * 0.72
    sx, sy = L + W * 0.16, T + H * 0.18           # sun
    cx_, cy_ = L + W * 0.64, T + H * 0.20         # cloud
    rnd = random.Random(3)
    vap = [(rnd.uniform(L + W * 0.25, L + W * 0.55), rnd.uniform(0, 1)) for _ in range(14)]
    drops = [(rnd.uniform(cx_ - 120, cx_ + 120), rnd.uniform(0, 1)) for _ in range(18)]
    lab_pos = [(L + W * 0.40, T + H * 0.46), (cx_, cy_ - 105), (cx_ + 175, T + H * 0.47), (L + W * 0.80, sea_y + 70)]

    def draw(c, t, e):
        shown = [t >= tt for tt in times]
        c.save(); c.clipRect(skia.Rect.MakeLTRB(L, T, R, B))
        sky = skia.Paint(AntiAlias=True)
        sky.setShader(skia.GradientShader.MakeLinear([(0, T), (0, sea_y)], [_c("#BFE6FF"), _c("#EAF7FF")]))
        c.drawRect(skia.Rect.MakeLTRB(L, T, R, sea_y), sky)
        # mountain + river on the right
        m = skia.Path(); m.moveTo(L + W * 0.55, sea_y); m.lineTo(L + W * 0.78, T + H * 0.40); m.lineTo(R + 40, sea_y); m.close()
        c.drawPath(m, _p("#8BC34A")); s_ = skia.Path(); s_.moveTo(L + W * 0.72, T + H * 0.47); s_.lineTo(L + W * 0.78, T + H * 0.40); s_.lineTo(L + W * 0.84, T + H * 0.47); s_.close(); c.drawPath(s_, _p("#FFFFFF"))
        riv = skia.Path(); riv.moveTo(L + W * 0.80, T + H * 0.50); riv.cubicTo(L + W * 0.70, T + H * 0.58, L + W * 0.78, T + H * 0.64, L + W * 0.58, sea_y + 4)
        c.drawPath(riv, _p("#4FC3F7", 1, 16))
        if shown[3]:  # water flows back down the river
            for d in range(5):
                u = (t * 0.45 + d / 5) % 1
                mx = skia.PathMeasure(riv, False); pos, _ = mx.getPosTan(mx.getLength() * u)
                c.drawCircle(pos.x(), pos.y(), 7, _p("#FFFFFF", 0.9))
        # sea with moving waves
        sea = skia.Path(); sea.moveTo(L, sea_y)
        for k in range(0, int(W) + 20, 20):
            sea.lineTo(L + k, sea_y + 8 * math.sin(k / 40 + t * 2.5))
        sea.lineTo(R, B); sea.lineTo(L, B); sea.close()
        sp = skia.Paint(AntiAlias=True); sp.setShader(skia.GradientShader.MakeLinear([(0, sea_y), (0, B)], [_c("#29B6F6"), _c("#0277BD")]))
        c.drawPath(sea, sp)
        # sun (heat rays pulse while evaporating)
        glow = 0.5 + 0.5 * math.sin(t * 3)
        c.drawCircle(sx, sy, 95 + 10 * glow, _p("#FFE082", 0.6, blur=25))
        _icon(E, c, "☀️", sx, sy, 2.3, 1.0, rot=t * 8)
        if shown[0]:  # vapour rises from the sea
            for x0, ph in vap:
                u = (t * 0.35 + ph) % 1.0
                x = x0 + 18 * math.sin(u * 6 + ph * 6); y = sea_y - u * (sea_y - cy_ - 40)
                c.drawCircle(x, y, 10 + 8 * u, _p("#FFFFFF", 0.75 * (1 - u)))
        # cloud gathers during condensation, darkens before rain
        if shown[1]:
            g = _smooth((t - times[1]) / 1.2)
            dark = _smooth((t - times[2]) / 0.6) if shown[2] else 0
            _icon(E, c, "☁️" if not dark else "🌧️", cx_ + 10 * math.sin(t * 0.8), cy_, 1.2 + 1.8 * g, 0.4 + 0.6 * g)
        if shown[2]:  # rain falls on the mountain
            for x0, ph in drops:
                u = (t * 1.1 + ph) % 1.0
                y = cy_ + 70 + u * (sea_y - cy_ - 60); x = x0 - 25 * u
                c.drawLine(x, y, x - 6, y + 22, _p("#0288D1", 0.85, 5))
        c.restore()
        for k, it in enumerate(items):  # stage labels appear on cue, the newest one bounces
            if not shown[k]: continue
            a = _back((t - times[k]) / 0.4)
            x, y = lab_pos[k]
            c.save(); c.translate(x, y); c.scale(a, a)
            E.pill(c, 0, 0, f"{k + 1}  {it.get('label', '')}", ["#FF7043", "#7E57C2", "#0288D1", "#2E7D32"][k], 30)
            c.restore()
    E.el(t0, t1, _safe(draw), None, (E.BCX, E.BCY))


# ------------------------------------------------------------------ plant growth (soil cross-section)
def build_plant_growth(E, i, t0, t1, sc):
    items = (sc.get("items") or [{"label": "Seed"}, {"label": "Roots"}, {"label": "Shoot"}, {"label": "Leaves"}, {"label": "Tree"}])[:5]
    n = len(items)
    top = _title(E, i, t0, t1, sc)
    times = _times(E, i, t0, items, 1.3)
    L, R, T, B = E.BX + 20, E.BX + E.BW - 20, top + 10, E.BY + E.BH - 20
    W, H = R - L, B - T
    gy = T + H * 0.58  # ground line
    px = L + W * 0.5

    def stage(k): return _smooth((t_now[0] - times[k]) / 1.1) if k < n and t_now[0] >= times[k] else 0.0
    t_now = [0.0]

    def draw(c, t, e):
        t_now[0] = t
        c.save(); c.clipRect(skia.Rect.MakeLTRB(L, T, R, B))
        sky = skia.Paint(AntiAlias=True); sky.setShader(skia.GradientShader.MakeLinear([(0, T), (0, gy)], [_c("#C8ECFF"), _c("#F2FBFF")]))
        c.drawRect(skia.Rect.MakeLTRB(L, T, R, gy), sky)
        soil = skia.Paint(AntiAlias=True); soil.setShader(skia.GradientShader.MakeLinear([(0, gy), (0, B)], [_c("#8D6E63"), _c("#5D4037")]))
        c.drawRect(skia.Rect.MakeLTRB(L, gy, R, B), soil)
        c.drawRect(skia.Rect.MakeLTRB(L, gy - 8, R, gy + 6), _p("#7CB342"))
        rnd = random.Random(5)
        for _ in range(26): c.drawCircle(rnd.uniform(L, R), rnd.uniform(gy + 20, B), rnd.uniform(3, 7), _p("#4E342E", 0.6))
        _icon(E, c, "☀️", R - 110, T + 90, 1.8, 1.0, rot=t * 6)
        s0, s1, s2, s3, s4 = (stage(k) for k in range(5))
        sy = gy + 70
        # 1 seed: wobbles, then cracks
        seed_a = 1.0 - 0.6 * s2
        _icon(E, c, "🌰", px, sy, 2.0 * (0.6 + 0.4 * _back((t - times[0]) / 0.5)) if t >= times[0] else 0, seed_a, rot=6 * math.sin(t * 4) * (1 - s1))
        # 2 roots grow down and sideways
        if s1 > 0:
            for ang, ln in ((-25, 170), (0, 210), (25, 170), (-55, 110), (55, 110)):
                a = math.radians(90 + ang)
                ex, ey = px + math.cos(a) * ln * s1, sy + math.sin(a) * ln * s1
                pth = skia.Path(); pth.moveTo(px, sy + 10); pth.quadTo(px + math.cos(a) * ln * 0.4 * s1 + 12, sy + math.sin(a) * ln * 0.5 * s1, ex, ey)
                c.drawPath(pth, _p("#F5E6C8", 1, 7))
        # 3 shoot grows up, 4 leaves open
        stem_top = sy - (sy - (gy - H * 0.36)) * s2 - (H * 0.10) * s4
        if s2 > 0:
            stem = skia.Path(); stem.moveTo(px, sy - 10); stem.cubicTo(px - 18, sy - 80, px + 18, (sy + stem_top) / 2, px, stem_top)
            c.drawPath(stem, _p("#43A047", 1, 14 + 22 * s4))
        if s3 > 0:
            for side in (-1, 1):
                for j, f in enumerate((0.55, 0.85)):
                    yy = sy - (sy - stem_top) * f
                    c.save(); c.translate(px, yy); c.rotate(side * (55 - 25 * s3) + 5 * math.sin(t * 2 + j)); c.scale(side * s3 * 1.45, s3 * 1.45)
                    leaf = skia.Path(); leaf.moveTo(0, 0); leaf.quadTo(40, -38, 95, -8); leaf.quadTo(45, 18, 0, 0)
                    c.drawPath(leaf, _p("#66BB6A")); c.drawPath(leaf, _p("#2E7D32", 1, 3)); c.restore()
        if s4 > 0:  # 5 tree crown appears
            _icon(E, c, "🌳", px, stem_top - 40, 4.2 * _elastic((t - times[4]) / 0.9) if n > 4 else 0, 1.0, rot=2 * math.sin(t * 1.5))
        c.restore()
        cur = max([k for k in range(n) if t >= times[k]] or [-1])
        if cur >= 0:  # current stage name, big and clear
            a = _back((t - times[cur]) / 0.4)
            c.save(); c.translate(L + 190, T + 70); c.scale(a, a)
            E.pill(c, 0, 0, f"{cur + 1}. {items[cur].get('label', '')}", "#2E7D32", 36); c.restore()
            _sparkles(c, px, stem_top if cur >= 2 else sy, t, times[cur], n=8, r=110, col="#FFF59D")
    E.el(t0, t1, _safe(draw), None, (px, gy))


BUILDERS = {"lifecycle": build_lifecycle, "flow": build_flow, "transform": build_transform,
            "water_cycle": build_water_cycle, "plant_growth": build_plant_growth}


# ------------------------------------------------------------------ list designs (lighter alternatives to the full-width rows)
TINTS = ["#FFF4CC", "#DFF3FF", "#FFE3EE", "#E3F7E8", "#EFE6FF"]
ACC = ["#F5A623", "#0A84FF", "#E91E63", "#2ECC71", "#7E57C2"]


def _rr(x, y, w, h, r): return skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r)


def _studio():
    import os
    return os.environ.get("THEME", "classic").strip().lower() in ("studio_light", "studio_dark", "studio_open")


def _card(c, x, y, w, h, fill, a=1.0, r=36):
    c.drawRRect(_rr(x, y + 10, w, h, r), _p("#1F2D44", 0.08 * a, blur=16))
    if _studio():  # clean look: white card, hairline border, no pastel fill
        c.drawRRect(_rr(x, y, w, h, r), _p("#FFFFFF", a)); c.drawRRect(_rr(x, y, w, h, r), _p("#E3E8F0", a, 3)); return
    c.drawRRect(_rr(x, y, w, h, r), _p(fill, a))


def _label(E, c, s, x, y, size, maxw, col=NAVY, a=1.0, lines=2):
    if a < 0.999: c.saveLayerAlpha(None, int(255 * a))
    else: c.save()
    E.big_text(c, s, x, y, size, col, maxw, tf=getattr(E.K, "FONT_SB", None) or E.K.FONT_XB, lines=lines, min_size=24)
    c.restore()


def build_tiles(E, i, t0, t1, sc, marks=False):
    """Airy tiles in a row (1-4): big 3D icon + short label; each pops in on its cue.
    Checklists: an item without its own icon shows a 3D tick/cross; with an icon it gets a tick/cross badge."""
    key = "rows" if sc.get("rows") else "items"
    items = sc.get(key, [])[:4]; n = len(items)
    if not n: return
    top = _title(E, i, t0, t1, sc) + 10
    times = _times(E, i, t0, items, 0.8)
    gap = 30; w = min(320, (E.BW - 90 - gap * (n - 1)) / n); h = min(440, E.BY + E.BH - top - 45)
    x0 = E.BCX - (n * w + (n - 1) * gap) / 2; y0 = top + (E.BY + E.BH - top - h) / 2
    for k, it in enumerate(items):
        x = x0 + k * (w + gap)
        ok = it.get("ok", True)
        icon = it.get("icon") or (("✅" if ok else "❌") if marks else "💡")
        def f(c, t, e, k=k, it=it, x=x, ok=ok, icon=icon):
            u = _back((t - times[k]) / 0.45); a = _smooth((t - times[k]) / 0.25)
            c.save(); c.translate(x + w / 2, y0 + h / 2 + 40 * (1 - u)); c.scale(0.9 + 0.1 * u, 0.9 + 0.1 * u); c.translate(-(x + w / 2), -(y0 + h / 2))
            _card(c, x, y0, w, h, TINTS[k % 5], a)
            _icon(E, c, icon, x + w / 2, y0 + h * 0.37 + 5 * math.sin(t * 2 + k), min(2.7, w / 95), a)
            if marks and it.get("icon"):  # tick / cross badge on the tile
                b = _back((t - times[k] - 0.25) / 0.35)
                _icon(E, c, "✅" if ok else "❌", x + w - 38, y0 + 38, 0.8 * b, a)
            _label(E, c, it.get("label") or it.get("text", ""), x + w / 2, y0 + h * 0.78, 42, w - 36, a=a)
            c.restore()
        E.el(times[k], t1, _safe(f), None, (x + w / 2, y0 + h / 2))


def build_timeline(E, i, t0, t1, sc):
    """C: slim numbered timeline; the item being spoken is highlighted, the others fade back."""
    items = sc.get("items", [])[:5]; n = len(items)
    if not n: return
    top = _title(E, i, t0, t1, sc) + 10
    times = _times(E, i, t0, items, 0.9)
    gy = (E.BY + E.BH - top - 40) / n; lx = E.BX + 150
    def draw(c, t, e):
        cur = max([k for k in range(n) if t >= times[k]] or [-1])
        y_first, y_last = top + gy * 0.5, top + gy * (n - 0.5)
        c.drawLine(lx, y_first, lx, y_last, _p("#DCE3EE", 1, 6))
        if cur >= 0: c.drawLine(lx, y_first, lx, top + gy * (cur + 0.5) * 1.0, _p(ACC[1], 1, 6))
        for k, it in enumerate(items):
            if t < times[k] - 0.05: continue
            y = top + gy * (k + 0.5); act = k == cur
            a = 1.0 if act else 0.45
            u = _back((t - times[k]) / 0.4)
            if act:
                c.drawRRect(_rr(lx + 60, y - gy * 0.40, E.BX + E.BW - 70 - lx - 60, gy * 0.80, 30), _p("#F3F7FF"))
            c.drawCircle(lx, y, 26 * u, _p(ACC[1] if t >= times[k] else "#DCE3EE"))
            E.big_text(c, str(k + 1), lx, y, 30, "#FFFFFF", 40, lines=1, min_size=20)
            _icon(E, c, it.get("icon", "bulb"), lx + 120, y, (1.35 if act else 1.1) * u, a)
            c.save(); c.translate(lx + 190, 0)
            if a < 1: c.saveLayerAlpha(None, int(255 * a))
            E.big_text(c, it.get("label") or it.get("text", ""), 0, y, 42 if act else 38, NAVY, E.BX + E.BW - lx - 290, align="l", lines=1, min_size=26) if "align" in E.big_text.__code__.co_varnames else E.K.text(c, it.get("label") or it.get("text", ""), 0, y, 42 if act else 38, NAVY, E.K.FONT_XB, "l")
            if a < 1: c.restore()
            c.restore()
    E.el(t0, t1, _safe(draw), None, (E.BCX, E.BCY))


BUILDERS.update({"tiles": build_tiles, "timeline": build_timeline})


def use_for_lists(BUILD, E):
    """Make list boards lighter (owner, 2026-11-21): steps / checklist / summary are drawn as tiles
    (a 5-item step list as a timeline). Repo variable LIST_STYLE=classic keeps the old full-width rows."""
    import os
    if os.environ.get("LIST_STYLE", "tiles").strip().lower() == "classic": return
    old = {k: BUILD.get(k) for k in ("steps", "checklist", "summary")}
    def steps(i, t0, t1, sc):
        n = len(sc.get("items", []))
        if n > 4: return build_timeline(E, i, t0, t1, sc)
        return build_tiles(E, i, t0, t1, sc)
    def checklist(i, t0, t1, sc):
        if len(sc.get("items", [])) > 4 and old["checklist"]: return old["checklist"](i, t0, t1, sc)
        return build_tiles(E, i, t0, t1, sc, marks=True)
    def summary(i, t0, t1, sc):
        if len(sc.get("rows", [])) > 4 and old["summary"]: return old["summary"](i, t0, t1, sc)
        return build_tiles(E, i, t0, t1, sc)
    BUILD.update({"steps": steps, "checklist": checklist, "summary": summary})
