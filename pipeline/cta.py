"""Call-to-action graphics: animated Subscribe / Like / Share end card + a small mid-video Subscribe reminder.

Drawn by episode_engine.py:
  end card  - in a strip under the board, from the moment "subscribe"/"follow" is spoken in the last line
  reminder  - top-right corner, about 40% into the video, for ~3 s (AInation only)
Kids mode (The CurioKids Club): "Ask a grown-up to subscribe & like!" and no bell icon
(made-for-kids videos have no notification bell).
"""
import math
import skia

RED, NAVY, WHITE, GREY, BLUE = "#FF0033", "#1F2D44", "#FFFFFF", "#9AA4B2", "#0A84FF"
PAD = 30  # space between a button's text and its outline


def _btn_w(K, label, icon):
    return skia.Font(K.FONT_XB, 34).measureText(label) + (50 if icon else 0) + 2 * PAD


def _p(K, col, stroke=None, a=1.0):
    p = skia.Paint(AntiAlias=True, Color=K.hexc(col, a))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke)
        p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join)
    return p


def _ease(u):
    u = max(0.0, min(1.0, u)); return u * u * (3 - 2 * u)


def _text(c, K, s, x, y, size, col):
    f = skia.Font(K.FONT_XB, size); w = f.measureText(s)
    c.drawString(s, x - w / 2, y + size * 0.36, f, _p(K, col))


def _bell(c, K, x, y, k, col, shake=0.0):
    c.save(); c.translate(x, y - 14 * k); c.rotate(shake); c.translate(0, 14 * k)
    b = skia.Path(); b.moveTo(-16 * k, 10 * k); b.quadTo(-16 * k, -18 * k, 0, -18 * k); b.quadTo(16 * k, -18 * k, 16 * k, 10 * k)
    b.lineTo(20 * k, 14 * k); b.lineTo(-20 * k, 14 * k); b.close()
    c.drawPath(b, _p(K, col)); c.drawCircle(0, 19 * k, 5 * k, _p(K, col)); c.drawCircle(0, -20 * k, 3.5 * k, _p(K, col))
    c.restore()


def _thumb(c, K, x, y, k, col):
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 20 * k, y - 4 * k, 9 * k, 24 * k), 3 * k, 3 * k), _p(K, col))
    p = skia.Path(); p.moveTo(x - 8 * k, y - 2 * k); p.lineTo(x - 2 * k, y - 20 * k); p.quadTo(x + 4 * k, y - 26 * k, x + 6 * k, y - 16 * k)
    p.lineTo(x + 3 * k, y - 6 * k); p.lineTo(x + 18 * k, y - 6 * k); p.quadTo(x + 24 * k, y - 4 * k, x + 21 * k, y + 2 * k)
    p.lineTo(x + 16 * k, y + 18 * k); p.quadTo(x + 14 * k, y + 21 * k, x + 9 * k, y + 21 * k); p.lineTo(x - 8 * k, y + 21 * k); p.close()
    c.drawPath(p, _p(K, col))


def _share(c, K, x, y, k, col):
    p = skia.Path(); p.moveTo(x - 18 * k, y + 16 * k); p.quadTo(x - 16 * k, y - 8 * k, x + 8 * k, y - 8 * k)
    c.drawPath(p, _p(K, col, 6 * k))
    a = skia.Path(); a.moveTo(x + 4 * k, y - 20 * k); a.lineTo(x + 20 * k, y - 8 * k); a.lineTo(x + 4 * k, y + 4 * k); a.close()
    c.drawPath(a, _p(K, col))


def _cursor(c, K, x, y, press):
    s = 1.0 - 0.15 * press
    c.save(); c.translate(x, y); c.scale(s, s)
    p = skia.Path(); p.moveTo(0, 0); p.lineTo(0, 46); p.lineTo(12, 35); p.lineTo(21, 54); p.lineTo(29, 50); p.lineTo(20, 32); p.lineTo(36, 32); p.close()
    c.drawPath(p, _p(K, WHITE)); c.drawPath(p, _p(K, NAVY, 4))
    c.restore()


def _button(c, K, cx, cy, w, h, fill, label, tcol, icon=None, pressed=0.0, pop=0.0, border=None):
    s = 1.0 - 0.08 * pressed + 0.1 * pop
    c.save(); c.translate(cx, cy); c.scale(s, s)
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), h / 2, h / 2)
    sh = _p(K, "#000000", a=0.18); sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 6))
    c.save(); c.translate(0, 5); c.drawRRect(r, sh); c.restore()
    c.drawRRect(r, _p(K, fill))
    if border: c.drawRRect(r, _p(K, border, 4))
    fs = 34; f = skia.Font(K.FONT_XB, fs); iw = 50 if icon else 0
    while f.measureText(label) + iw > w - 2 * PAD and fs > 22: fs -= 1; f = skia.Font(K.FONT_XB, fs)
    tw = f.measureText(label)
    x0 = -(tw + iw) / 2
    if icon: icon(x0 + 18, 0)
    c.drawString(label, x0 + iw, fs * 0.36, f, _p(K, tcol))
    c.restore()


def end_card(c, t, t0, K, kids=False, cx=540, cy=880):
    """Animated end card in its own strip under the board (stays visible to the last frame).
    t0 = when 'subscribe'/'follow' is spoken."""
    u = t - t0
    if u < -0.05: return
    pop = K.appear(t, t0 - 0.05)
    c.save(); c.translate(cx, cy - 30); c.scale(pop, pop); c.translate(-cx, -(cy - 30))
    panel = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(cx - 420, cy - 120, 840, 175), 40, 40)
    sh = _p(K, "#000000", a=0.16); sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 10))
    c.save(); c.translate(0, 8); c.drawRRect(panel, sh); c.restore()
    c.drawRRect(panel, _p(K, "#FFFDF5")); c.drawRRect(panel, _p(K, NAVY, 5))
    head = "Ask a grown-up to subscribe & like!" if kids else "Enjoyed it? Subscribe, like & share!"
    _text(c, K, head, cx, cy - 78, 32, NAVY)
    if u > 1.2:  # "drop a topic" bubble pops in under the card (owner, 2026-11-21)
        a_ = _ease((u - 1.2) / 0.35); bw, bh = 640, 70; by = cy + 92
        c.save(); c.translate(cx, by); c.scale(0.85 + 0.15 * a_, 0.85 + 0.15 * a_)
        bub = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-bw / 2, -bh / 2, bw, bh), bh / 2, bh / 2)
        tail = skia.Path(); tail.moveTo(-bw / 2 + 70, bh / 2 - 4); tail.lineTo(-bw / 2 + 60, bh / 2 + 22); tail.lineTo(-bw / 2 + 100, bh / 2 - 4); tail.close()
        c.drawRRect(bub, _p(K, BLUE, a=a_)); c.drawPath(tail, _p(K, BLUE, a=a_))
        _text(c, K, "Drop a topic in the comments!", 0, 0, 32, WHITE)
        c.restore()
    # widths from the widest label each button shows (SUBSCRIBED is longer than SUBSCRIBE), 22 px apart, centred
    ws = [_btn_w(K, "SUBSCRIBED", not kids), _btn_w(K, "LIKE", True), _btn_w(K, "SHARE", True)]
    k_ = min(1.0, 790 / (sum(ws) + 44)); ws = [w * k_ for w in ws]
    x_ = cx - (sum(ws) + 44) / 2; xs = []
    for w in ws: xs.append(x_ + w / 2); x_ += w + 22
    btns = [("sub", ws[0], xs[0]), ("like", ws[1], xs[1]), ("share", ws[2], xs[2])]
    taps = {name: 0.9 + k * 1.0 for k, (name, _, _) in enumerate(btns)}
    for name, w, x in btns:
        tp = taps[name]; pressed = max(0.0, 1 - abs(u - tp) / 0.12) if abs(u - tp) < 0.12 else 0.0
        done = u > tp + 0.08; pop = max(0.0, 1 - abs(u - tp - 0.2) / 0.18) if done else 0.0
        if name == "sub":
            shake = math.sin(u * 30) * 18 * max(0.0, 1 - (u - tp - 0.1) / 0.8) if done and not kids else 0.0
            icon = (lambda x_, y_, d=done, sh_=shake: _bell(c, K, x_, y_, 0.9, WHITE if not d else NAVY, sh_)) if not kids else None
            w = w if not kids else w
            _button(c, K, x, cy, w, 80, GREY if done else RED, "SUBSCRIBED" if done else "SUBSCRIBE", WHITE if not done else NAVY,
                    icon, pressed, pop)
        elif name == "like":
            col = BLUE if done else NAVY
            _button(c, K, x, cy, w, 80, WHITE, "LIKE", col, lambda x_, y_, col=col: _thumb(c, K, x_, y_, 1.0, col), pressed, pop, col)
        else:
            col = BLUE if done else NAVY
            _button(c, K, x, cy, w, 80, WHITE, "SHARE", col, lambda x_, y_, col=col: _share(c, K, x_, y_, 1.0, col), pressed, pop, col)
    # pointer travels to each button and taps it
    path = [(cx + 330, cy + 90)] + [(x - 10, cy + 6) for _, _, x in btns]
    times = [0.3] + [taps[n] for n, _, _ in btns]
    if u > 0.3:
        k = 0
        while k + 1 < len(times) and u > times[k + 1]: k += 1
        if k + 1 < len(times):
            a, b = times[k] + (0.15 if k else 0.0), times[k + 1] - 0.08
            e = _ease((u - a) / max(0.01, b - a))
            px = path[k][0] + (path[k + 1][0] - path[k][0]) * e; py = path[k][1] + (path[k + 1][1] - path[k][1]) * e
        else:
            px, py = path[-1]
        press = max(0.0, 1 - min(abs(u - tp) for tp in taps.values()) / 0.12)
        _cursor(c, K, px, py, press)
    c.restore()



# ------------------------------------------------------------------ newer end-card designs (CTA_STYLE = card | bar | pop)
def _ico3(name):
    try:
        import icons3d
        return icons3d.drawer(name)
    except Exception:
        return None


def _icon_or(c, K, name, x, y, k, fallback, a=1.0):
    d = _ico3(name)
    if a < 0.999: c.saveLayerAlpha(None, int(255 * a))
    else: c.save()
    if d: d(c, x, y, k)
    else: fallback(x, y)
    c.restore()


def _topic_bubble(c, K, cx, y, u):
    if u <= 0: return
    a_ = _ease(u / 0.35); bw, bh = 640, 70
    c.save(); c.translate(cx, y); c.scale(0.85 + 0.15 * a_, 0.85 + 0.15 * a_)
    bub = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-bw / 2, -bh / 2, bw, bh), bh / 2, bh / 2)
    tail = skia.Path(); tail.moveTo(-bw / 2 + 70, bh / 2 - 4); tail.lineTo(-bw / 2 + 60, bh / 2 + 22); tail.lineTo(-bw / 2 + 100, bh / 2 - 4); tail.close()
    c.drawRRect(bub, _p(K, BLUE, a=a_)); c.drawPath(tail, _p(K, BLUE, a=a_))
    _text(c, K, "Drop a topic in the comments!", 0, 0, 32, WHITE)
    c.restore()


def end_bar(c, t, t0, K, kids=False, cx=540, cy=880):
    """A: one slim floating action bar, three big round 3D buttons; a finger taps each in turn."""
    u = t - t0
    if u < -0.05: return
    pop = K.appear(t, t0 - 0.05)
    c.save(); c.translate(cx, cy); c.scale(pop, pop); c.translate(-cx, -cy)
    bw, bh = 780, 190
    bar = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(cx - bw / 2, cy - bh / 2, bw, bh), 60, 60)
    sh = _p(K, "#000000", a=0.16); sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 18))
    c.save(); c.translate(0, 10); c.drawRRect(bar, sh); c.restore()
    c.drawRRect(bar, _p(K, "#FFFFFF"))
    if kids:  # kids channel: a grown-up does the subscribing
        _text(c, K, "Ask a grown-up to subscribe & like!", cx, cy - bh / 2 - 34, 32, NAVY)
    names = [("SUBSCRIBE", "SUBSCRIBED", "🔔", RED), ("LIKE", "LIKED", "👍", BLUE), ("SHARE", "SHARED", "📤", "#2ECC71")]
    taps = [0.6 + k * 0.9 for k in range(3)]
    xs = [cx - 250, cx, cx + 250]
    for k, (lab, done_lab, ico, col) in enumerate(names):
        x = xs[k]; y = cy - 22; tp = taps[k]; done = u > tp
        press = max(0.0, 1 - abs(u - tp) / 0.12) if abs(u - tp) < 0.12 else 0.0
        bounce = 1 + 0.18 * max(0.0, 1 - abs(u - tp - 0.18) / 0.18) if done else 1.0
        r = 62 * (1 - 0.08 * press) * bounce
        c.drawCircle(x, y, r, _p(K, col if not (done and k == 0) else GREY))
        if done:  # ripple
            ru = (u - tp) / 0.6
            if ru < 1: c.drawCircle(x, y, r + 40 * ru, _p(K, col, 6, a=1 - ru))
        shake = math.sin(u * 30) * 14 * max(0.0, 1 - (u - tp - 0.1) / 0.7) if (done and k == 0) else 0.0
        c.save(); c.translate(x, y); c.rotate(shake)
        _icon_or(c, K, ico, 0, 0, 1.25, lambda x_, y_, k=k: (_bell if k == 0 else _thumb if k == 1 else _share)(c, K, x_, y_, 1.4, WHITE))
        c.restore()
        if done and k == 1 and u - tp < 1.0:  # +1 floats up
            fu = (u - tp) / 1.0; _text(c, K, "+1", x + 50, y - 60 - 60 * fu, 36, BLUE)
        _text(c, K, done_lab if done else lab, x, cy + 68, 30, NAVY)
    # finger that taps each button
    if 0.2 < u < taps[-1] + 0.5:
        k = min(2, max(0, int((u - 0.2) / 0.9)))
        tx, ty = xs[k] + 52, cy + 2
        e = _ease((u - 0.2 - k * 0.9) / 0.35)
        px = (xs[k - 1] + 52 if k else cx + 330) + (tx - (xs[k - 1] + 52 if k else cx + 330)) * e
        press = max(0.0, 1 - abs(u - taps[k]) / 0.12)
        _icon_or(c, K, "👆", px, ty + 40 + 8 * press, 1.25, lambda x_, y_: _cursor(c, K, x_, y_, press))
    c.restore()
    _topic_bubble(c, K, cx, cy + bh / 2 + 55, u - 3.0)


def end_pop(c, t, t0, K, kids=False, cx=540, cy=880):
    """B: one big button at a time in the centre (Subscribe -> Like -> Share), confetti on each tap."""
    u = t - t0
    if u < -0.05: return
    steps = [("SUBSCRIBE", "🔔", RED), ("LIKE", "👍", BLUE), ("SHARE", "📤", "#2ECC71")]
    k = min(2, max(0, int(u / 1.0))); lu = u - k * 1.0
    lab, ico, col = steps[k]
    a = _ease(lu / 0.25) if k < 2 or lu < 10 else 1.0
    s_ = 0.7 + 0.3 * _ease(lu / 0.3)
    press = max(0.0, 1 - abs(lu - 0.55) / 0.1) if abs(lu - 0.55) < 0.1 else 0.0
    w, h = 560, 150
    c.save(); c.translate(cx, cy); c.scale(s_ * (1 - 0.06 * press), s_ * (1 - 0.06 * press))
    sh = _p(K, "#000000", a=0.2); sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 16))
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), h / 2, h / 2)
    c.save(); c.translate(0, 10); c.drawRRect(r, sh); c.restore()
    c.drawRRect(r, _p(K, col))
    _icon_or(c, K, ico, -w / 2 + 90, 0, 1.4, lambda x_, y_: None)
    f = skia.Font(K.FONT_XB, 62); c.drawString(lab, -w / 2 + 160, 22, f, _p(K, WHITE))
    c.restore()
    if lu > 0.55:  # confetti burst on the tap
        cu = (lu - 0.55) / 0.5
        if cu < 1:
            for j in range(14):
                ang = j * 2 * math.pi / 14
                c.drawCircle(cx + math.cos(ang) * 320 * cu, cy + math.sin(ang) * 150 * cu, 9 * (1 - cu) + 2, _p(K, ["#FFD23F", RED, BLUE, "#2ECC71"][j % 4], a=1 - cu))
    _icon_or(c, K, "👆", cx + 170, cy + 70 + 10 * press, 1.3, lambda x_, y_: _cursor(c, K, x_, y_, press), a=1.0 if lu < 0.9 else 0.0)
    _topic_bubble(c, K, cx, cy + 140, u - 3.0)


_card_end = end_card


def end_card(c, t, t0, K, kids=False, cx=540, cy=880):  # noqa: F811  (dispatch on CTA_STYLE)
    import os
    # owner, 2026-11-21: kids = action bar, AInation = big pop; CTA_STYLE=card brings back the old card
    style = (os.environ.get("CTA_STYLE", "") or ("bar" if kids else "pop")).strip().lower()
    if style == "bar": return end_bar(c, t, t0, K, kids, cx, cy)
    if style == "pop": return end_pop(c, t, t0, K, kids, cx, cy)
    return _card_end(c, t, t0, K, kids, cx, cy)

def reminder(c, t, t_show, K, dur=3.2):
    """Small 'SUBSCRIBE' pill that slides in at the top right, rings its bell, and slides out."""
    u = t - t_show
    if u < 0 or u > dur: return
    slide = _ease(u / 0.35) * (1 - _ease((u - dur + 0.35) / 0.35))
    x = 1080 + 20 - 300 * slide; y = 150 + 760  # just under the board, right side
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y - 34, 270, 68), 34, 34)
    c.drawRRect(r, _p(K, RED))
    _bell(c, K, x + 40, y, 0.85, WHITE, math.sin(u * 28) * 16 * max(0.0, 1 - abs(u - 1.0) / 0.6))
    f = skia.Font(K.FONT_XB, 30); c.drawString("SUBSCRIBE", x + 72, y + 11, f, _p(K, WHITE))
