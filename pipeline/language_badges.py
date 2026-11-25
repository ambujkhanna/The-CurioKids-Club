"""Inline language badges for CurioKids thumbnails."""
import os
import skia

LABELS = {"en": "ENGLISH", "hi": "\u0939\u093f\u0928\u094d\u0926\u0940", "es": "ESPAÑOL"}
COLORS = {"en": "#1769AA", "hi": "#E87516", "es": "#16865A"}

def label_for(lang=None):
    return LABELS.get((lang or os.environ.get("THUMB_LANG") or "en").lower(), LABELS["en"])

def _measure(font, text):
    try:
        import deva
        if deva.has(text):
            return deva.measure(text, font.getSize())
    except Exception:
        pass
    return font.measureText(text)

def draw(c, K, lang, cx, cy, scale=1.0):
    label = label_for(lang)
    size = 36 * scale
    font = skia.Font(K.FONT_XB, size)
    tw = _measure(font, label)
    h, pad = size * 1.55, size * 0.55
    w = tw + pad * 2
    x, y = cx - w / 2, cy - h / 2
    color = COLORS.get((lang or "en").lower(), COLORS["en"])
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), h / 2, h / 2),
                skia.Paint(AntiAlias=True, Color=K.hexc(color)))
    paint = skia.Paint(AntiAlias=True, Color=K.hexc("#FFFFFF"))
    tx, baseline = cx - tw / 2, cy + size * 0.34
    try:
        import deva
        if deva.has(label):
            deva.draw(c, label, tx, baseline - size * 0.30, size, paint, align="l")
        else:
            c.drawString(label, tx, baseline, font, paint)
    except Exception:
        c.drawString(label, tx, baseline, font, paint)
    return w, h

def beside(c, K, lang, lines, font, title_size, baseline, anchor_x, align, W, H):
    if not lines:
        return
    scale = min(W, H) / 1080
    bf = skia.Font(K.FONT_XB, 36 * scale)
    bw = _measure(bf, label_for(lang)) + 36 * scale * 1.1
    bh, gap = 36 * scale * 1.55, 18 * scale
    tw = _measure(skia.Font(font, title_size), lines[-1])
    if align == "left":
        cx = anchor_x + tw + gap + bw / 2
        cy = baseline - title_size * 0.28
        if cx + bw / 2 > W - 24 * scale:
            cx, cy = max(24 * scale + bw / 2, anchor_x + tw / 2), baseline + bh * 0.72
    else:
        left, right = anchor_x - tw / 2, anchor_x + tw / 2
        rc, lc = right + gap + bw / 2, left - gap - bw / 2
        if rc + bw / 2 <= W - 24 * scale:
            cx, cy = rc, baseline - title_size * 0.28
        elif lc - bw / 2 >= 24 * scale:
            cx, cy = lc, baseline - title_size * 0.28
        else:
            cx, cy = anchor_x, baseline + bh * 0.72
    draw(c, K, lang, cx, cy, scale)
