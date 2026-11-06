"""Animated diagrams for The CurioKids Club board: body (with flows), cycle, journey, orbit.

Each builder adds board elements through the engine's helpers (passed in as `E`):
    E.el, E.cue_t, E.ico, E.big_text, E.pill, E.P, E.BX, E.BY, E.BW, E.BH, E.BCX, E.BCY, E.LN, E.K
Scene JSON (see episodes/README.md):
  {"type": "body", "title": "...", "show": ["heart","lungs","brain","stomach"], "flow": "blood|nerves|air|food",
   "cue": "word (flow starts)", "labels": [{"text": "Heart", "at": "heart", "cue": "word"}]}
  {"type": "cycle", "title": "...", "center": "🌍", "items": [{"icon": "☀️", "label": "Sun heats", "cue": "word"}, ...]}  (3-6)
  {"type": "journey", "title": "...", "traveler": "🔊", "items": [{"icon": "...", "label": "...", "cue": "word"}, ...]}  (2-5)
  {"type": "orbit", "title": "...", "center": "☀️", "items": [{"icon": "🌍", "label": "Earth", "cue": "word"}]}  (1-4)
"""
import math
import skia

NAVY = "#1F2D44"
SKIN = "#FFCDB8"
RED, BLUE, YELLOW, AIR, FOOD = "#E53935", "#1E88E5", "#FFC107", "#4FC3F7", "#FF8A65"


def _pp(E, col, stroke=None, a=1.0, cap=True):
    p = skia.Paint(AntiAlias=True, Color=E.K.hexc(col, a))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke)
        if cap: p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join)
    return p


def _title(E, i, t0, t1, sc):
    if sc.get("title"):
        E.el(t0, t1, lambda c, t, e: E.pill(c, E.BCX, E.BY + 62, sc["title"], sc.get("color", "#E91E63"), 42), (E.BCX + 200, E.BY + 62))
        return E.BY + 120
    return E.BY + 30


def _flow_dots(c, E, path, t, start, col, n=6, speed=0.45, r=9, reverse=False, arrows=True):
    """Moving dots/chevrons along a path; returns nothing. start: time the flow begins."""
    if t < start: return
    pm = skia.PathMeasure(path, False); L = pm.getLength()
    if L <= 0: return
    fade = min(1.0, (t - start) / 0.4)
    for k in range(n):
        f = ((t - start) * speed + k / n) % 1.0
        if reverse: f = 1 - f
        r_ = pm.getPosTan(f * L)
        if not r_: continue
        pos, tan = r_
        if arrows:
            ang = math.atan2(tan.y(), tan.x()) + (math.pi if reverse else 0)
            c.save(); c.translate(pos.x(), pos.y()); c.rotate(math.degrees(ang))
            ch = skia.Path(); ch.moveTo(-r, -r * 0.9); ch.lineTo(r * 0.9, 0); ch.lineTo(-r, r * 0.9); ch.close()
            c.drawPath(ch, _pp(E, col, a=fade)); c.drawPath(ch, _pp(E, "#FFFFFF", 2.5, a=0.8 * fade))
            c.restore()
        else:
            c.drawCircle(pos.x(), pos.y(), r, _pp(E, col, a=fade)); c.drawCircle(pos.x(), pos.y(), r * 0.45, _pp(E, "#FFFFFF", a=0.7 * fade))


# ------------------------------------------------------------------ body
ANCHORS = {"brain": (0, -258), "head": (0, -250), "eyes": (0, -248), "ears": (62, -246), "nose": (0, -232), "mouth": (0, -214),
           "lungs": (0, -112), "heart": (-10, -98), "stomach": (6, -18), "arm": (-150, -40), "hand": (-188, 22),
           "leg": (-52, 170), "foot": (-60, 292), "muscles": (150, -60), "skin": (88, -10), "bones": (52, 160)}


def _body_shape(cx, cy, s):
    def pt(x, y): return cx + x * s, cy + y * s
    body = skia.Path()
    body.addCircle(*pt(0, -250), 66 * s)
    body.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(*pt(-88, -175), *pt(88, 48)), 52 * s, 52 * s))
    neck = skia.Path(); neck.addRect(skia.Rect.MakeLTRB(*pt(-22, -200), *pt(22, -165))); body = skia.Op(body, neck, skia.PathOp.kUnion_PathOp)
    for side in (-1, 1):
        for (x0, y0, x1, y1, w) in ((side * 80, -150, side * 185, 15, 34), (side * 46, 30, side * 58, 282, 46)):
            limb = skia.Path(); a = math.atan2(y1 - y0, x1 - x0); dx, dy = -math.sin(a) * w / 2, math.cos(a) * w / 2
            p0, p1 = pt(x0, y0), pt(x1, y1)
            limb.moveTo(p0[0] + dx * s, p0[1] + dy * s); limb.lineTo(p1[0] + dx * s, p1[1] + dy * s)
            limb.lineTo(p1[0] - dx * s, p1[1] - dy * s); limb.lineTo(p0[0] - dx * s, p0[1] - dy * s); limb.close()
            cap = skia.Path(); cap.addCircle(p1[0], p1[1], w / 2 * s)
            body = skia.Op(body, limb, skia.PathOp.kUnion_PathOp); body = skia.Op(body, cap, skia.PathOp.kUnion_PathOp)
        hand = skia.Path(); hand.addCircle(*pt(side * 192, 26), 24 * s); body = skia.Op(body, hand, skia.PathOp.kUnion_PathOp)
        foot = skia.Path(); foot.addOval(skia.Rect.MakeLTRB(*pt(side * 60 - 30, 280), *pt(side * 60 + 30 + side * 14, 306)))
        body = skia.Op(body, foot, skia.PathOp.kUnion_PathOp)
        ear = skia.Path(); ear.addCircle(*pt(side * 64, -246), 16 * s); body = skia.Op(body, ear, skia.PathOp.kUnion_PathOp)
    return body


def _vessel_paths(cx, cy, s, src, gap=0.0):
    """Routes from a source point to head, both hands and both feet (body coords -> screen)."""
    def pt(x, y): return skia.Point(cx + x * s, cy + y * s)
    sx, sy = src; out = []
    routes = [[(sx, sy), (0 + gap, -170), (0 + gap, -228)]]
    for side in (-1, 1):
        routes.append([(sx, sy), (side * 70, -150 + gap), (side * 130, -70 + gap), (side * 182, 12 + gap)])
        routes.append([(sx, sy), (side * 6 + gap, 10), (side * 42 + gap, 50), (side * 52 + gap, 170), (side * 58 + gap, 272)])
    for r in routes:
        p = skia.Path(); a = pt(*r[0]); p.moveTo(a)
        for k in range(1, len(r) - 1):
            b, c_ = pt(*r[k]), pt(*r[k + 1])
            p.quadTo(b, skia.Point((b.x() + c_.x()) / 2, (b.y() + c_.y()) / 2)) if k < len(r) - 2 else p.quadTo(b, c_)
        out.append(p)
    return out


def build_body(E, i, t0, t1, sc):
    top = _title(E, i, t0, t1, sc)
    cy = (top + E.BY + E.BH) / 2 + 12; s = min(1.1, (E.BY + E.BH - top + 10) / 620)
    cx = E.BCX - (60 if sc.get("labels") else 0)
    show = sc.get("show", ["heart"]); flow = sc.get("flow")
    t_flow = E.cue_t(i, sc, t0 + 0.8)
    def pt(x, y): return cx + x * s, cy + y * s
    shape = _body_shape(cx, cy, s)

    def body(c, t, e):
        sh = _pp(E, "#000000", a=0.12); sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 10))
        c.save(); c.translate(0, 10); c.drawPath(shape, sh); c.restore()
        g = skia.Paint(AntiAlias=True)
        b = shape.computeTightBounds()
        g.setShader(skia.GradientShader.MakeLinear([skia.Point(b.left(), b.top()), skia.Point(b.right(), b.bottom())], [E.K.hexc("#FFE1D3"), E.K.hexc(SKIN), E.K.hexc("#F4AE95")]))
        c.drawPath(shape, g); c.drawPath(shape, _pp(E, NAVY, 5))
        for side in (-1, 1):  # friendly face
            c.drawCircle(*pt(side * 22, -258), 7 * s, _pp(E, NAVY)); c.drawCircle(*pt(side * 40, -236), 11 * s, _pp(E, "#FF8A9A", a=0.5))
        sm = skia.Path(); sm.moveTo(*pt(-18, -228)); sm.quadTo(*pt(0, -214), *pt(18, -228)); c.drawPath(sm, _pp(E, NAVY, 4 * s))
        if flow == "blood":
            for k, p in enumerate(_vessel_paths(cx, cy, s, ANCHORS["heart"], 0)):
                c.drawPath(p, _pp(E, RED, 11 * s, a=0.85))
            for k, p in enumerate(_vessel_paths(cx, cy, s, ANCHORS["heart"], 9)):
                c.drawPath(p, _pp(E, BLUE, 11 * s, a=0.85))
        if flow == "nerves":
            for p in _vessel_paths(cx, cy, s, ANCHORS["brain"], 0):
                c.drawPath(p, _pp(E, "#FFB300", 9 * s, a=0.75))
        if flow in ("air", "food"):
            p = _air_food_path(cx, cy, s, flow); c.drawPath(p, _pp(E, AIR if flow == "air" else FOOD, 12 * s, a=0.45))
        organs = {"lungs": ("🫁", 1.9), "heart": ("🫀", 1.5), "brain": ("🧠", 1.45), "stomach": ("🟠", 0.0), "bones": ("🦴", 0.9),
                  "eyes": ("👀", 0.9), "ears": ("👂", 0.6), "muscles": ("💪", 0.9)}
        for name in sorted(show, key=lambda n_: {"lungs": 0, "heart": 2}.get(n_, 1)):  # heart on top of the lungs
            x, y = ANCHORS.get(name, (0, 0)); X, Y = pt(x, y)
            import images as _im
            if name in _im.BODY_IMG and _im.resolve(_im.BODY_IMG[name]):
                beat = 1.0 + (0.12 * max(0.0, math.sin(t * 7.5)) if name == "heart" and flow == "blood" and t > t_flow else 0.0)
                size = {"heart": 1.35, "lungs": 1.9, "brain": 1.25, "stomach": 0.9, "eyes": 0.6, "ears": 0.55, "muscles": 0.9}.get(name, 1.0)
                if name == "heart":
                    gl = _pp(E, "#FF5252", a=0.35 + 0.25 * max(0.0, math.sin(t * 7.5))); gl.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 14))
                    c.drawCircle(X, Y, 46 * s * beat, gl)
                E.ico(_im.BODY_IMG[name])(c, X, Y, size * s * beat); continue
            if name == "stomach":
                st = skia.Path(); st.addOval(skia.Rect.MakeLTRB(X - 40 * s, Y - 26 * s, X + 34 * s, Y + 26 * s))
                c.drawPath(st, _pp(E, "#F48FB1")); c.drawPath(st, _pp(E, NAVY, 3)); continue
            em, k_ = organs.get(name, (None, 0))
            if not em: continue
            beat = 1.0 + (0.12 * max(0.0, math.sin(t * 7.5)) if name == "heart" and flow == "blood" and t > t_flow else 0.0)
            if name == "heart":
                gl = _pp(E, "#FF5252", a=0.35 + 0.25 * max(0.0, math.sin(t * 7.5))); gl.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 14))
                c.drawCircle(X, Y, 46 * s * beat, gl)
            fn = E.ico(em)
            if fn: fn(c, X, Y, k_ * s * beat)

    E.el(t0, t1, body, None, (cx, cy))

    def flows(c, t, e):
        if flow == "blood":
            for p in _vessel_paths(cx, cy, s, ANCHORS["heart"], 0):
                _flow_dots(c, E, p, t, t_flow, RED, n=4, speed=0.42, r=15 * s)
            for p in _vessel_paths(cx, cy, s, ANCHORS["heart"], 9):
                _flow_dots(c, E, p, t, t_flow + 0.6, BLUE, n=4, speed=0.42, r=15 * s, reverse=True)
        elif flow == "nerves":
            for p in _vessel_paths(cx, cy, s, ANCHORS["brain"], 0):
                _flow_dots(c, E, p, t, t_flow, "#FFB300", n=3, speed=1.1, r=15 * s, arrows=False)
        elif flow in ("air", "food"):
            p = _air_food_path(cx, cy, s, flow)
            _flow_dots(c, E, p, t, t_flow, "#0288D1" if flow == "air" else "#E64A19", n=5, speed=0.55, r=15 * s,
                       reverse=(flow == "air" and int((t - t_flow) / 1.8) % 2 == 1))
    E.el(t_flow, t1, flows, None, (cx, cy))
    # labels with leader lines, spaced so they never overlap
    labs = []
    for k, lb in enumerate(sc.get("labels", [])[:5]):
        ax, ay = pt(*ANCHORS.get(lb.get("at", "heart"), (0, 0)))
        side = 1 if (k % 2 == 0) else -1
        lx = cx + side * 300 * max(0.8, s)
        lx = max(lx, E.BX + 120) if side < 0 else min(lx, E.BX + E.BW - 120)
        labs.append([lb, ax, ay, lx, min(max(ay, top + 40), E.BY + E.BH - 40), side])
    for side in (-1, 1):
        grp = sorted([L for L in labs if L[5] == side], key=lambda L: L[4])
        for j in range(1, len(grp)):
            if grp[j][4] - grp[j - 1][4] < 78: grp[j][4] = grp[j - 1][4] + 78
        over = (grp[-1][4] - (E.BY + E.BH - 40)) if grp else 0
        if over > 0:
            for L in grp: L[4] -= over
    for k, (lb, ax, ay, lx, ly, side) in enumerate(labs):
        tin = E.cue_t(i, lb, t0 + 0.6 + k * 0.7)
        def lab(c, t, e, lb=lb, ax=ax, ay=ay, lx=lx, ly=ly):
            d = math.hypot(lx - ax, ly - ay) or 1; sx_, sy_ = ax + (lx - ax) * 46 / d, ay + (ly - ay) * 46 / d
            c.drawLine(sx_, sy_, lx, ly, _pp(E, NAVY, 3, a=0.6)); c.drawCircle(sx_, sy_, 6, _pp(E, NAVY))
            E.pill(c, lx, ly, lb["text"], lb.get("color", "#8E44AD"), 36)
        E.el(tin, t1, lab, None, (lx, ly))


def _air_food_path(cx, cy, s, kind):
    def pt(x, y): return skia.Point(cx + x * s, cy + y * s)
    p = skia.Path()
    if kind == "air":
        p.moveTo(pt(0, -232)); p.quadTo(pt(0, -200), pt(0, -165)); p.quadTo(pt(0, -140), pt(-30, -110))
    else:
        p.moveTo(pt(0, -214)); p.quadTo(pt(0, -170), pt(0, -120)); p.quadTo(pt(4, -60), pt(6, -22))
    return p


# ------------------------------------------------------------------ cycle
def build_cycle(E, i, t0, t1, sc):
    top = _title(E, i, t0, t1, sc)
    items = sc.get("items", [])[:6]; n = max(1, len(items))
    cx, cy = E.BCX, (top + E.BY + E.BH) / 2 + 10
    R = min(E.BW * 0.30, (E.BY + E.BH - top) * 0.32)
    start = -3 * math.pi / 4 if n == 4 else -math.pi / 2  # 4 steps: diagonal layout so no label collides
    ang = [start + k * 2 * math.pi / n for k in range(n)]
    RX = min(E.BW * 0.36, R * 1.65)  # oval: wider than tall, so labels have room
    pos = [(cx + math.cos(a) * RX, cy + math.sin(a) * R) for a in ang]
    times = [E.cue_t(i, it, t0 + 0.4 + k * 0.9) for k, it in enumerate(items)]
    def ring(c, t, e):
        circ = skia.Path(); circ.addOval(skia.Rect.MakeLTRB(cx - RX, cy - R, cx + RX, cy + R))
        c.drawPath(circ, _pp(E, "#B39DDB", 10, a=0.35))
        for k in range(n):  # arrow heads between stops
            a = ang[k] + math.pi / n
            x, y = cx + math.cos(a) * RX, cy + math.sin(a) * R
            c.save(); c.translate(x, y); c.rotate(math.degrees(math.atan2(math.cos(a) * R, -math.sin(a) * RX)))
            ah = skia.Path(); ah.moveTo(-16, -14); ah.lineTo(16, 0); ah.lineTo(-16, 14); ah.close()
            c.drawPath(ah, _pp(E, "#7E57C2")); c.restore()
        if sc.get("center") and E.ico(sc["center"]):
            E.ico(sc["center"])(c, cx, cy, 2.0 + 0.08 * math.sin(t * 2))
        if t > times[-1] + 0.3:  # glowing dot travelling around once everything is shown
            a = start + ((t - times[-1]) * 1.4) % (2 * math.pi)
            g = _pp(E, "#FFD54F", a=0.9); g.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 6))
            c.drawCircle(cx + math.cos(a) * RX, cy + math.sin(a) * R, 18, g)
    E.el(t0, t1, ring, None, (cx, cy))
    for k, it in enumerate(items):
        x, y = pos[k]
        def node(c, t, e, it=it, x=x, y=y, k=k):
            r = 74 if n <= 4 else 62
            c.drawCircle(x, y + 5, r, _pp(E, "#000000", a=0.12)); c.drawCircle(x, y, r, _pp(E, "#FFFFFF")); c.drawCircle(x, y, r, _pp(E, "#7E57C2", 6))
            fn = E.ico(it.get("icon"))
            if fn: fn(c, x, y - 2, r / 40)
            if abs(x - cx) < 10:  # top / bottom node: label to the side, away from the title and the stage edge
                sd = 1 if k % 2 == 0 else -1
                E.big_text(c, it.get("label", ""), x + sd * (r + 120), y, 40, NAVY, 220, lines=2, min_size=28)
            elif y < cy - 5:
                E.big_text(c, it.get("label", ""), x, y - r - 30, 40, NAVY, 300, lines=1, min_size=28)
            else:
                E.big_text(c, it.get("label", ""), x, y + r + 32, 40, NAVY, 300, lines=1, min_size=28)
        E.el(times[k], t1, node, None, (x, y))


# ------------------------------------------------------------------ journey
def build_journey(E, i, t0, t1, sc):
    top = _title(E, i, t0, t1, sc)
    items = sc.get("items", [])[:5]; n = max(2, len(items))
    if n <= 3:
        ys = [(top + E.BY + E.BH) / 2] * n; xs = [E.BX + E.BW * (k + 0.5) / n for k in range(n)]
    else:
        h = E.BY + E.BH - top; xs, ys = [], []
        for k in range(n):
            row = 0 if k < (n + 1) // 2 else 1; col = k if row == 0 else (n - 1 - k)
            per = (n + 1) // 2
            xs.append(E.BX + E.BW * (col + 0.5) / per); ys.append(top + h * (0.3 if row == 0 else 0.75))
    times = [E.cue_t(i, it, t0 + 0.4 + k * 1.0) for k, it in enumerate(items)]
    path = skia.Path(); path.moveTo(xs[0], ys[0])
    for k in range(1, len(items)):
        mx = (xs[k - 1] + xs[k]) / 2; my = min(ys[k - 1], ys[k]) - 60
        path.quadTo(mx, my, xs[k], ys[k])
    seg = []
    pm = skia.PathMeasure(path, False); total = pm.getLength()
    acc = [0.0]
    for k in range(1, len(items)):
        sp = skia.Path(); sp.moveTo(xs[k - 1], ys[k - 1]); sp.quadTo((xs[k - 1] + xs[k]) / 2, min(ys[k - 1], ys[k]) - 60, xs[k], ys[k])
        acc.append(acc[-1] + skia.PathMeasure(sp, False).getLength())
    def road(c, t, e):
        dash = _pp(E, "#90A4AE", 8); dash.setPathEffect(skia.DashPathEffect.Make([22, 18], -t * 60))
        c.drawPath(path, dash)
        # traveler moves towards the stop that was most recently cued
        d = 0.0
        for k in range(1, len(items)):
            if t >= times[k] - 0.6:
                u = min(1.0, (t - (times[k] - 0.6)) / 0.6); d = acc[k - 1] + (acc[k] - acc[k - 1]) * (u * u * (3 - 2 * u))
        r_ = pm.getPosTan(min(d, total)); trav = E.ico(sc.get("traveler", "⭐"))
        if r_ and trav and t >= times[0]:
            p_ = r_[0]
            trav(c, p_.x(), p_.y() - 70 + math.sin(t * 6) * 6, 1.3)
    E.el(t0, t1, road, None, (E.BCX, (top + E.BY + E.BH) / 2))
    for k, it in enumerate(items):
        x, y = xs[k], ys[k]
        def stop(c, t, e, it=it, x=x, y=y):
            c.drawCircle(x, y + 5, 66, _pp(E, "#000000", a=0.12)); c.drawCircle(x, y, 66, _pp(E, "#FFFFFF")); c.drawCircle(x, y, 66, _pp(E, "#26A69A", 6))
            fn = E.ico(it.get("icon"))
            if fn: fn(c, x, y, 1.55)
            E.big_text(c, it.get("label", ""), x, y + 100, 40, NAVY, E.BW / min(n, 3) - 20, lines=2, min_size=28)
        E.el(times[k], t1, stop, None, (x, y))


# ------------------------------------------------------------------ orbit
def build_orbit(E, i, t0, t1, sc):
    top = _title(E, i, t0, t1, sc)
    items = sc.get("items", [])[:4]
    cx, cy = E.BCX, (top + E.BY + E.BH) / 2 + 10
    Rmax = min(E.BW * 0.44, (E.BY + E.BH - top) * 0.44)
    times = [E.cue_t(i, it, t0 + 0.5 + k * 0.8) for k, it in enumerate(items)]
    def sun(c, t, e):
        for k in range(len(items)):
            R = Rmax * (k + 1) / max(1, len(items))
            c.drawOval(skia.Rect.MakeLTRB(cx - R, cy - R * 0.55, cx + R, cy + R * 0.55), _pp(E, "#B0BEC5", 3, a=0.7))
        g = _pp(E, "#FFD54F", a=0.5); g.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 20))
        c.drawCircle(cx, cy, 70 + 6 * math.sin(t * 3), g)
        fn = E.ico(sc.get("center", "☀️"))
        if fn: fn(c, cx, cy, 2.2)
    E.el(t0, t1, sun, None, (cx, cy))
    for k, it in enumerate(items):
        R = Rmax * (k + 1) / max(1, len(items)); sp = float(it.get("speed", 0.9 / (k + 1)))
        def planet(c, t, e, it=it, R=R, sp=sp, k=k):
            a = (t - times[k]) * sp + k * 1.3
            x, y = cx + math.cos(a) * R, cy + math.sin(a) * R * 0.55
            fn = E.ico(it.get("icon"))
            if fn: fn(c, x, y, 1.25)
            if it.get("label"): E.pill(c, x, y + 62, it["label"], "#5C6BC0", 30)
        E.el(times[k], t1, planet, None, (cx, cy))


BUILDERS = {"body": build_body, "cycle": build_cycle, "journey": build_journey, "orbit": build_orbit}
