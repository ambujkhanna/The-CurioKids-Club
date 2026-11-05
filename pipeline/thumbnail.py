"""Designed thumbnail (1080x1920 JPEG): room + characters + the episode's pictures + big headline that says what it's about.

Called by episode_engine.py after the frames are rendered:
    thumbnail.make(out_path, K, chars, ep, ico)
Uses "cover_text" (2-4 big words) and "title" from episode.json, and the icons of the first board scene.
"""
import re
import skia

NAVY, YELLOW, WHITE = "#1F2D44", "#FFD23F", "#FFFFFF"


def _P(K, col, stroke=None, a=1.0):
    p = skia.Paint(AntiAlias=True, Color=K.hexc(col, a))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke); p.setStrokeJoin(skia.Paint.kRound_Join)
    return p


def _clean(K, s, tf):
    f = skia.Font(tf, 40)
    s = "".join(ch for ch in s if ch.isascii() or 0 not in f.textToGlyphs(ch))
    return re.sub(r"\s+", " ", s).strip()


def _subtitle(ep):
    t = ep.get("title", "")
    t = re.split(r"\s+[|–—-]\s+|(?<=[?!.])\s", t)[0]  # keep the question / main phrase
    for suf in (" Fun Facts for Kids", " for Kids", " Explained"):
        t = t.replace(suf, "")
    return t.strip(" .")


def _wrap(text, tf, size, maxw, max_lines):
    while size > 40:
        f = skia.Font(tf, size); words = text.split(); lines = [""]
        for w in words:
            trial = (lines[-1] + " " + w).strip()
            if f.measureText(trial) <= maxw: lines[-1] = trial
            else: lines.append(w)
        if len(lines) <= max_lines and all(f.measureText(l) <= maxw for l in lines):
            if len(lines) == 2:  # balance the two lines
                best = min(range(1, len(words)), key=lambda k: max(f.measureText(" ".join(words[:k])), f.measureText(" ".join(words[k:]))))
                lines = [" ".join(words[:best]), " ".join(words[best:])]
            return lines, size
        size -= 4
    return [text], size


def _text(c, K, s, x, y, size, col, tf, outline=None, ow=0):
    f = skia.Font(tf, size); w = f.measureText(s)
    if outline:
        c.drawString(s, x - w / 2, y, f, _P(K, outline, ow))
    c.drawString(s, x - w / 2, y, f, _P(K, col))


def _icons(ep, ico):
    b = (ep["lines"][0].get("board") or {})
    names = []
    if b.get("type") == "title": names = [b.get("left", {}).get("icon"), b.get("right", {}).get("icon")]
    elif b.get("icon"): names = [b["icon"]]
    elif b.get("items"): names = [it.get("icon") for it in b["items"][:2]]
    if not any(names) and ep.get("loop_card"): names = [ep["loop_card"].get("left"), ep["loop_card"].get("right")]
    return [ico(n) for n in names if n and ico(n)][:2], b.get("mid", "?") if b.get("type") == "title" else "?"


def make(path, K, chars, ep, ico, t_pose=None):
    W, H = 1080, 1920
    surf = skia.Surface(W, H); c = surf.getCanvas()
    t = t_pose if t_pose is not None else (K.LN[0]["start"] + K.LN[0]["end"]) / 2
    K.draw_bg(c, t)
    # characters, a bit bigger, anchored at the bottom
    c.save(); c.translate(540, 1920); c.scale(1.04, 1.04); c.translate(-540, -1775)
    for ch in chars: K.draw_char(c, ch, t)
    c.restore()
    # soft dark band behind the text area so it pops on any background
    g = skia.GradientShader.MakeLinear([(0, 0), (0, 1080)], [skia.Color(24, 34, 60, 255), skia.Color(24, 34, 60, 255), skia.Color(24, 34, 60, 170), skia.Color(24, 34, 60, 0)], [0, 0.16, 0.62, 1])
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, 1080), skia.Paint(Shader=g))
    tf = K.FONT_XB
    # brand
    K.logo(c, 540, 92, 1.15, tcol=WHITE)
    # headline (cover_text): huge, yellow on navy outline, slight tilt
    head = _clean(K, (ep.get("cover_text") or _subtitle(ep)).upper(), tf)
    lines, size = _wrap(head, tf, 150, 960, 2)
    c.save(); c.rotate(-3, 540, 300)
    y = 270 if len(lines) == 1 else 230
    for ln in lines:
        _text(c, K, ln, 540, y + size * 0.35, size, YELLOW, tf, NAVY, 26); y += size * 1.02
    c.restore()
    # subtitle: what the video is about (the question)
    sub = _clean(K, _subtitle(ep), tf)
    sl, ss = _wrap(sub, tf, 58, 900, 2)
    y0 = y - size * 0.55 + 50
    pill_h = len(sl) * ss * 1.2 + 40
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(60, y0, 960, pill_h), 36, 36)
    c.drawRRect(r, _P(K, WHITE))
    yy = y0 + 20 + ss * 0.95
    for ln in sl:
        _text(c, K, ln, 540, yy, ss, NAVY, tf); yy += ss * 1.2
    # the episode's pictures in white circles
    icons, mid = _icons(ep, ico)
    cy = min(y0 + pill_h + 150, 760)
    xs = [540] if len(icons) == 1 else [300, 780]
    for fn, x in zip(icons, xs):
        c.drawCircle(x, cy + 8, 122, _P(K, "#000000", a=0.25))
        c.drawCircle(x, cy, 122, _P(K, WHITE)); c.drawCircle(x, cy, 122, _P(K, YELLOW, 10))
        fn(c, x, cy, 2.6)
    if len(icons) == 2:
        c.drawCircle(540, cy, 62, _P(K, YELLOW)); c.drawCircle(540, cy, 62, _P(K, NAVY, 8))
        _text(c, K, mid or "?", 540, cy + 26, 72 if len(mid or "?") < 3 else 48, NAVY, tf)
    img = surf.makeImageSnapshot()
    img.save(path, skia.kJPEG, 90)
    return path
