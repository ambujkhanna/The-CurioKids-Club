"""Hindi (Devanagari) text on boards: Poppins Bold (OFL, owner's choice) + HarfBuzz shaping (uharfbuzz, Apache-2.0).

skia's plain drawString can't join conjuncts (क्ष, ज्ञ, त्र) or place the ि vowel sign, so Devanagari text is shaped
with HarfBuzz first and drawn as positioned glyphs. Used automatically by kit2d.text / episode_engine.big_text.
"""
import os, re
import skia

_FD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts")
_FONT = next((os.path.join(_FD, f) for f in ("Poppins-Bold.ttf", "Baloo2.ttf") if os.path.exists(os.path.join(_FD, f))), "")
_RE = re.compile(r"[ऀ-ॿ]")
_hb = {}


def has(s):
    return bool(s) and bool(_RE.search(s)) and os.path.exists(_FONT)


def _setup(weight):
    if weight not in _hb:
        import uharfbuzz as hb
        face = hb.Face(hb.Blob.from_file_path(_FONT)); font = hb.Font(face)
        if "[" not in _FONT and not _FONT.endswith("Baloo2.ttf"):  # static font (Poppins Bold): no weight axis
            _hb[weight] = (hb, font, skia.Typeface.MakeFromFile(_FONT)); return _hb[weight]
        font.set_variations({"wght": weight})
        tag = lambda s: (ord(s[0]) << 24) | (ord(s[1]) << 16) | (ord(s[2]) << 8) | ord(s[3])
        coords = skia.FontArguments.VariationPosition.Coordinates([skia.FontArguments.VariationPosition.Coordinate(tag("wght"), weight)])
        args = skia.FontArguments(); args.setVariationDesignPosition(skia.FontArguments.VariationPosition(coords))
        _hb[weight] = (hb, font, skia.Typeface.MakeFromFile(_FONT).makeClone(args))
    return _hb[weight]


def _shape(s, size, weight):
    hb, font, tf = _setup(weight)
    font.scale = (int(size * 64), int(size * 64))
    buf = hb.Buffer(); buf.add_str(s); buf.guess_segment_properties()
    hb.shape(font, buf, {})
    return buf, tf


def measure(s, size, weight=700):
    buf, _ = _shape(s, size, weight)
    return sum(p.x_advance for p in buf.glyph_positions) / 64


def draw(c, s, x, y, size, paint, align="c", weight=700):
    """Draw s with its vertical centre at y (like kit2d.text). Returns the width."""
    buf, tf = _shape(s, size, weight)
    w = sum(p.x_advance for p in buf.glyph_positions) / 64
    x0 = x - {"c": w / 2, "l": 0, "r": w}[align]; base = y + size * 0.30
    glyphs, pos, px = [], [], 0
    for info, p in zip(buf.glyph_infos, buf.glyph_positions):
        glyphs.append(info.codepoint); pos.append(skia.Point(x0 + (px + p.x_offset) / 64, base - p.y_offset / 64)); px += p.x_advance
    if glyphs:
        b = skia.TextBlobBuilder(); b.allocRunPos(skia.Font(tf, size), glyphs, pos); c.drawTextBlob(b.make(), 0, 0, paint)
    return w
