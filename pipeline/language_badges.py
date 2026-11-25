"""Inline EN/HI/ES language badges for CurioKids thumbnails."""
import os
import skia

LABELS = {"en": "ENGLISH", "hi": "\u0939\u093f\u0928\u094d\u0926\u0940", "es": "ESPAÑOL"}
COLORS = {"en": "#1769AA", "hi": "#E87516", "es": "#16865A"}

def label_for(lang=None):
    key = (lang or os.environ.get("THUMB_LANG") or "en").lower()
    return LABELS.get(key, LABELS["en"])

def draw(c, K, lang, cx, cy, scale=1.0):
    key = (lang or os.environ.get("THUMB_LANG") or "en").lower()
    label, size = label_for(key), 36 * scale
    font = skia.Font(K.FONT_XB, size)
    try:
        import deva
        tw = deva.measure(label, size) if deva.has(label) else font.measureText(label)
    except Exception:
        tw = font.measureText(label)
    h, pad = size * 1.55, size * 0.55
    w, x, y = tw + 2 * pad, cx - (tw + 2 * pad) / 2, cy - h / 2
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), h / 2, h / 2),
                skia.Paint(AntiAlias=True, Color=K.hexc(COLORS.get(key, COLORS["en"]))))
    p, tx, baseline = skia.Paint(AntiAlias=True, Color=K.hexc("#FFFFFF")), cx - tw / 2, cy + size * 0.34
    try:
        import deva
        if deva.has(label):
            deva.draw(c, label, tx, baseline - size * 0.30, size, p, align="l")
        else:
            c.drawString(label, tx, baseline, font, p)
    except Exception:
        c.drawString(label, tx, baseline, font, p)
