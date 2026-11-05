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
    f = skia.Font(K.FONT_XB, 34); tw = f.measureText(label); iw = 54 if icon else 0
    x0 = -(tw + iw) / 2
    if icon: icon(x0 + 18, 0)
    c.drawString(label, x0 + iw, 12, f, _p(K, tcol))
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
    btns = [("sub", 290, cx - 255), ("like", 190, cx + 7), ("share", 200, cx + 225)]
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
