"""Doodle mode: hand-inked, boiling lines + marker fills. Enabled with env DOODLE=1."""
import os
import skia

MODE = os.environ.get("DOODLE", "")
ON = MODE == "1"                 # whole scene doodled
CHARS = MODE in ("1", "chars")   # characters doodled
SEED = 0            # set per frame (changes every 3 frames => gentle 'line boil')
FONTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts")


def apply_char(p, stroke):
    return _fx(p, stroke) if CHARS else p


def apply(p, stroke):
    return _fx(p, stroke) if ON else p


def _fx(p, stroke):
    if stroke:
        p.setPathEffect(skia.DiscretePathEffect.Make(9.0, 1.5, SEED))
    else:
        p.setPathEffect(skia.DiscretePathEffect.Make(16.0, 1.1, SEED + 101))
    return p


def typeface(kind):
    name = {"title": "Caveat-Bold.ttf", "body": "PatrickHand-Regular.ttf"}[kind]
    return skia.Typeface.MakeFromFile(os.path.join(FONTS, name))
