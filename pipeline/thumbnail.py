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


def text3d(c, K, s, x, y, size, tf, align="c", depth=None, face=("#FFF27A", "#FFC21A", "#FF8F1F"), side="#1F2D44"):
    """Extruded 3D headline: stacked dark layers (depth), outline, gradient face, glossy top highlight."""
    f = skia.Font(tf, size); w = f.measureText(s); depth = depth or max(6, int(size * 0.11))
    x0 = x - w / 2 if align == "c" else x
    sh = _P(K, "#000000", a=0.35); sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, size * 0.08))
    c.drawString(s, x0 + depth + 6, y + depth + 10, f, sh)
    for d in range(depth, 0, -1):  # extrusion
        c.drawString(s, x0 + d * 0.8, y + d, f, _P(K, side))
        c.drawString(s, x0 + d * 0.8, y + d, f, _P(K, side, size * 0.09))
    c.drawString(s, x0, y, f, _P(K, side, size * 0.13))
    g = skia.Paint(AntiAlias=True)
    g.setShader(skia.GradientShader.MakeLinear([skia.Point(0, y - size * 0.75), skia.Point(0, y + size * 0.1)], [K.hexc(face[0]), K.hexc(face[1]), K.hexc(face[2])], [0, 0.55, 1]))
    c.drawString(s, x0, y, f, g)
    hl = skia.Paint(AntiAlias=True)
    hl.setShader(skia.GradientShader.MakeLinear([skia.Point(0, y - size * 0.75), skia.Point(0, y - size * 0.35)], [skia.Color(255, 255, 255, 150), skia.Color(255, 255, 255, 0)]))
    c.drawString(s, x0, y, f, hl)


def badge3d(c, K, x, y, r, fn=None, k=1.0):
    """Glossy 3D button for a picture: shadow, gold rim, domed face, specular highlight."""
    sh = _P(K, "#000000", a=0.35); sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, r * 0.18))
    c.drawCircle(x + r * 0.08, y + r * 0.16, r * 1.02, sh)
    rim = skia.Paint(AntiAlias=True)
    rim.setShader(skia.GradientShader.MakeLinear([skia.Point(x, y - r), skia.Point(x, y + r)], [K.hexc("#FFE58A"), K.hexc("#E0A82E"), K.hexc("#B8740E")], [0, 0.5, 1]))
    c.drawCircle(x, y, r, rim)
    face = skia.Paint(AntiAlias=True)
    face.setShader(skia.GradientShader.MakeRadial(skia.Point(x - r * 0.3, y - r * 0.35), r * 1.25, [K.hexc("#FFFFFF"), K.hexc("#F1F4FA"), K.hexc("#C9D3E3")], [0, 0.6, 1]))
    c.drawCircle(x, y, r * 0.86, face)
    if fn: fn(c, x, y + r * 0.04, k)
    gl = skia.Paint(AntiAlias=True)
    gl.setShader(skia.GradientShader.MakeLinear([skia.Point(x, y - r * 0.86), skia.Point(x, y - r * 0.1)], [skia.Color(255, 255, 255, 170), skia.Color(255, 255, 255, 0)]))
    c.drawOval(skia.Rect.MakeLTRB(x - r * 0.62, y - r * 0.8, x + r * 0.62, y - r * 0.12), gl)


def sunburst(c, K, cx, cy, R, n=18, col="#FFFFFF", a=0.10):
    p = skia.Path()
    for k in range(n):
        a0 = k * 2 * 3.14159265 / n; a1 = a0 + 3.14159265 / n
        import math as _m
        p.moveTo(cx, cy); p.lineTo(cx + _m.cos(a0) * R, cy + _m.sin(a0) * R); p.lineTo(cx + _m.cos(a1) * R, cy + _m.sin(a1) * R); p.close()
    c.drawPath(p, _P(K, col, a=a))


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
    if s.strip() in ("→", "->", "➜", "➡", "➡️"):  # brand fonts have no arrow glyph: draw a chunky arrow instead
        h = size * 0.30; L = size * 0.62; yy = y - size * 0.36
        pa = skia.Path(); pa.moveTo(x - L, yy - h * 0.45); pa.lineTo(x + L * 0.15, yy - h * 0.45); pa.lineTo(x + L * 0.15, yy - h * 1.15)
        pa.lineTo(x + L, yy); pa.lineTo(x + L * 0.15, yy + h * 1.15); pa.lineTo(x + L * 0.15, yy + h * 0.45)
        pa.lineTo(x - L, yy + h * 0.45); pa.close()
        if outline: c.drawPath(pa, _P(K, outline, ow))
        c.drawPath(pa, _P(K, col)); return
    if any(ch.strip() and skia.Font(tf).unicharToGlyph(ord(ch)) == 0 for ch in s):  # missing glyph: use a system font that has it
        m = skia.FontMgr().matchFamilyStyleCharacter("", skia.FontStyle.Bold(), ["en"], ord(next(ch for ch in s if ch.strip() and skia.Font(tf).unicharToGlyph(ord(ch)) == 0)))
        tf = m or tf
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


def make_wide(path, K, chars, ep, ico, t_pose=None):
    """16:9 thumbnail (1280x720) for long videos: big headline + pictures on the left, characters in their room on the right."""
    W, H = 1280, 720
    surf = skia.Surface(W, H); c = surf.getCanvas(); c.clear(K.hexc("#4FAEA3"))
    t = t_pose if t_pose is not None else (K.LN[0]["start"] + K.LN[0]["end"]) / 2
    c.save(); c.translate(560, -560); c.scale(0.68, 0.68); K.draw_bg(c, t)
    for ch in chars: K.draw_char(c, ch, t)
    c.restore()
    g = skia.GradientShader.MakeLinear([(0, 0), (900, 0)], [skia.Color(24, 34, 60, 245), skia.Color(24, 34, 60, 225), skia.Color(24, 34, 60, 0)], [0, 0.62, 1])
    c.drawRect(skia.Rect.MakeLTRB(0, 0, 900, H), skia.Paint(Shader=g))
    tf = K.FONT_XB
    K.logo(c, 250, 58, 0.95, tcol=WHITE)
    head = _clean(K, (ep.get("cover_text") or _subtitle(ep)).upper(), tf)
    lines, size = _wrap(head, tf, 110, 640, 2)
    sunburst(c, K, 300, 240, 700, a=0.07)
    y = 175
    for ln in lines:
        text3d(c, K, ln, 40, y + size * 0.35, size, tf, align="l"); y += size * 1.04
    sub = _clean(K, _subtitle(ep), tf); sl, ss = _wrap(sub, tf, 48, 640, 2)
    y += 10
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(30, y - 10, 680, len(sl) * ss * 1.2 + 30), 28, 28); c.drawRRect(r, _P(K, WHITE))
    yy = y + 5 + ss * 0.95
    for ln in sl:
        f = skia.Font(tf, ss); c.drawString(ln, 55, yy, f, _P(K, NAVY)); yy += ss * 1.2
    icons, mid = _icons(ep, ico)
    box_bottom = y - 10 + len(sl) * ss * 1.2 + 30
    rad = max(48, min(78, (H - 12 - box_bottom) / 2 - 6)); cy = box_bottom + 8 + rad
    for k_, fn in enumerate(icons):
        x = 40 + rad + k_ * (rad * 2 + 40)
        badge3d(c, K, x, cy, rad, fn, rad / 50)
    tag = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(W - 300, H - 90, 270, 60), 30, 30)
    c.drawRRect(tag, _P(K, "#FF0033")); f = skia.Font(tf, 32); c.drawString("FULL VIDEO", W - 270, H - 48, f, _P(K, WHITE))
    img = surf.makeImageSnapshot()
    if hasattr(K, "grade"): img = K.grade(img)
    img.save(path, skia.kJPEG, 90)
    return path


def make(path, K, chars, ep, ico, t_pose=None):
    if getattr(K, "LANDSCAPE", False):
        return make_wide(path, K, chars, ep, ico, t_pose)
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
    lines, size = _wrap(head, tf, 150, 940, 2)
    sunburst(c, K, 540, 300, 900, a=0.08)
    c.save(); c.rotate(-3, 540, 300)
    y = 270 if len(lines) == 1 else 230
    for ln in lines:
        text3d(c, K, ln, 540, y + size * 0.35, size, tf); y += size * 1.05
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
    cy = y0 + pill_h + 136
    xs = [540] if len(icons) == 1 else [300, 780]
    for fn, x in zip(icons, xs):
        badge3d(c, K, x, cy, 116, fn, 2.3)
    if len(icons) == 2:
        c.drawCircle(540, cy, 62, _P(K, YELLOW)); c.drawCircle(540, cy, 62, _P(K, NAVY, 8))
        _text(c, K, mid or "?", 540, cy + 26, 72 if len(mid or "?") < 3 else 48, NAVY, tf)
    img = surf.makeImageSnapshot()
    if hasattr(K, "grade"): img = K.grade(img)
    img.save(path, skia.kJPEG, 90)
    return path
