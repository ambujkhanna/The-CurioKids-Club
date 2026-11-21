"""HD backdrops and picture boards (pilot, 2026-11-21). Same file in both channels.

Pictures are made once on a free Kaggle GPU with FLUX.1-schnell (Apache 2.0) and committed to assets/art/:
    assets/art/<name>_portrait.jpg    1080x1920  (Shorts)
    assets/art/<name>_landscape.jpg   1920x1080  (long videos, picture boards)
    assets/art/manifest.json          prompt, model, seed, licence and date for every picture

Use in episode.json:
    "backdrop": "garden"                                  whole video: the picture replaces the drawn room
    "board": {"type": "picture", "art": "sprout", "caption": "A tiny sprout", "cue": "sprout"}

Moves gently: slow zoom (Ken Burns), a little parallax with the camera, drifting sparkles / soft light dots.
If a picture is missing, the video keeps today's drawn room and the picture board falls back to a big icon board,
so nothing breaks. Repo variable ART=off turns every picture off; BACKDROP=<name> forces one backdrop (tests).
"""
import math, os, random
import skia

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DIR = os.environ.get("ART_DIR") or os.path.join(ROOT, "assets", "art")
ON = os.environ.get("ART", "on").strip().lower() not in ("off", "0", "no", "false")
KIDS = os.environ.get("BG") == "kids"
NAME = None          # this video's backdrop (set by use())
DUR = 60.0           # video length, for the slow zoom (set by use())
_IMG = {}


def image(name, orient="portrait"):
    """skia.Image for assets/art/<name>_<orient>.jpg (or .png; falls back to the other orientation), or None."""
    if not ON or not name or not isinstance(name, str): return None
    key = (name, orient)
    if key not in _IMG:
        _IMG[key] = None
        cands = [os.path.join(DIR, f"{os.path.basename(name)}_{o}.{ext}")
                 for o in (orient, "landscape" if orient == "portrait" else "portrait") for ext in ("jpg", "png")]
        for p in cands:
            if os.path.exists(p):
                try:
                    _IMG[key] = skia.Image.MakeFromEncoded(skia.Data.MakeWithCopy(open(p, "rb").read())); break
                except Exception as e:
                    print("note: art picture unreadable", p, str(e)[:80])
        if _IMG[key] is None: print(f"note: no art picture '{name}' ({orient}) - using the drawn look")
    return _IMG[key]


# Automatic choice by topic (for episodes and scripts without a "backdrop"): the background whose words appear
# most in the title (x5) and the dialogue (x1).
# Nothing matches -> the playroom. Order matters only for ties (earlier wins).
TOPICS = [
    ("night_sky",    "star stars twinkle twinkling night nighttime sleep sleeping dream dreams dark owl owls nocturnal constellation"),
    ("space",        "space planet planets astronaut astronauts rocket rockets orbit galaxy solar spinning saturn mars jupiter gravity"),
    ("bathroom",     "teeth tooth brush brushing toothbrush toothpaste bath bathtub soap wash washing germs shower wrinkly plaque"),
    ("kitchen",      "food eat eating tummy stomach apple apples fruit fruits cook cooking kitchen milk taste tongue sugar spoon "
                     "metal straw glass bread vegetables juice hungry"),
    ("ocean",        "sea seas ocean oceans wave waves fish whale whales shark sharks beach shell shells salty tide coral dolphin"),
    ("river_valley", "river rivers mountain mountains valley volcano volcanoes rock rocks stream waterfall lake"),
    ("reading_nook", "word words letter letters alphabet spell spelling read reading book books vowel vowels silent grammar "
                     "english sentence rhyme pronounce sound sounds"),
    ("windy_hills",  "wind windy cloud clouds kite air weather rainbow storm breeze blow blows thunder lightning"),
    ("garden",       "plant plants seed seeds tree trees flower flowers bee bees butterfly insect insects soil leaf leaves "
                     "garden worm worms bird birds grass sunlight shadow shadows ant ants"),
]
DEFAULT = "playroom"
AUTO = os.environ.get("ART_AUTO", "on").strip().lower() not in ("off", "0", "no", "false")


def auto_pick(title="", text=""):
    """Background name for a topic (always returns one; DEFAULT when nothing matches)."""
    import re
    tw = re.findall(r"[a-z]+", (title or "").lower()); dw = re.findall(r"[a-z]+", (text or "").lower())
    best, score = DEFAULT, 0
    for name, words in TOPICS:
        ws = set(words.split())
        sc = 5 * sum(w in ws for w in tw) + sum(w in ws for w in dw)
        if sc > score: best, score = name, sc
    return best if score >= 3 else DEFAULT


def use(episode_value=None, duration=60.0, title="", text=""):
    """Pick this video's backdrop: BACKDROP variable > the episode's "backdrop" field ("none" = the drawn room)
    > automatic choice by topic (ART_AUTO=off turns that off). Returns True if a picture is on."""
    global NAME, DUR
    v = os.environ.get("BACKDROP", "").strip() or (episode_value or "").strip()
    if v.lower() in ("none", "room", "off"): v = ""
    elif not v and AUTO and KIDS: v = auto_pick(title, text)
    NAME = v or None
    DUR = max(1.0, float(duration or 60.0))
    if NAME and image(NAME, "portrait") is None and image(NAME, "landscape") is None: NAME = None
    return NAME is not None


def active():
    return NAME is not None


_SAMP = skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear)


def _cover(c, img, x, y, w, h, zoom=1.0, fx=0.5, fy=0.5, a=1.0):
    """Draw img to fill the rect (x, y, w, h), cropped like CSS 'cover', zoomed around (fx, fy) of the rect."""
    s = max(w / img.width(), h / img.height()) * zoom
    iw, ih = img.width() * s, img.height() * s
    dx = x + (w - iw) * fx; dy = y + (h - ih) * fy
    p = skia.Paint(AntiAlias=True); p.setAlphaf(a)
    c.drawImageRect(img, skia.Rect.MakeXYWH(dx, dy, iw, ih), _SAMP, p)


def _col(h, a):
    h = h.lstrip("#"); return skia.Color(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(255 * max(0.0, min(1.0, a))))


_DOTS = [(random.Random(7 + k).random(), random.Random(99 + k).random(), random.Random(301 + k).random()) for k in range(28)]


def _particles(c, t, w, h):
    """Kids: twinkling sparkles drifting up. AInation: soft blue light dots drifting sideways."""
    for k, (u, v, r) in enumerate(_DOTS):
        if KIDS:
            x = (u * w + math.sin(t * 0.6 + k) * 18) % w
            y = (v * h - t * (14 + 22 * r)) % h
            tw = 0.5 + 0.5 * math.sin(t * (1.5 + r) + k * 1.3)
            size = 3 + 5 * r
            g = skia.Paint(AntiAlias=True, Color=_col("#FFFFFF", 0.35 * tw)); g.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, size * 1.6))
            c.drawCircle(x, y, size * 1.8, g)
            c.drawCircle(x, y, size * 0.55, skia.Paint(AntiAlias=True, Color=_col("#FFFDF0", 0.85 * tw)))
        else:
            x = (u * w + t * (8 + 14 * r)) % w
            y = v * h + math.sin(t * 0.4 + k) * 14
            size = 6 + 16 * r
            g = skia.Paint(AntiAlias=True, Color=_col("#2F6BFF" if k % 3 else "#FFFFFF", 0.10 + 0.10 * r)); g.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, size * 0.8))
            c.drawCircle(x, y, size, g)


def backdrop(c, t, w, h, orient="portrait", cam=None):
    """Full-frame picture in screen space (drawn before the camera), with slow zoom, camera parallax and particles.
    cam = (cx, cy, z) of the scene camera: the picture follows it at 30% so it feels deeper than the characters."""
    img = image(NAME, orient)
    if img is None: return False
    u = min(1.0, max(0.0, t / DUR))
    zoom = 1.04 + 0.06 * u                      # very slow push-in over the whole video
    fx, fy = 0.5 + 0.03 * math.sin(t * 0.07), 0.5
    if cam:
        cx, cy, z = cam
        zoom *= 1 + (z - 1) * 0.3
        fx = min(1.0, max(0.0, fx + (cx - w / 2) / w * 0.3)); fy = min(1.0, max(0.0, fy + (cy - h / 2) / h * 0.2))
    _cover(c, img, 0, 0, w, h, zoom, fx, fy)
    # soft light veil at the top half so the board and its text stay easy to read
    veil = skia.Paint(AntiAlias=True)
    veil.setShader(skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, h * 0.55)], [_col("#FFFFFF", 0.22), _col("#FFFFFF", 0.0)]))
    c.drawRect(skia.Rect.MakeWH(w, h * 0.55), veil)
    _particles(c, t, w, h)
    return True


def ground(c, xs, floor_y):
    """Soft contact shadows so the characters stand on the picture instead of floating (world coordinates)."""
    for x in xs:
        g = skia.Paint(AntiAlias=True, Color=_col("#000000", 0.22)); g.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 18))
        c.drawOval(skia.Rect.MakeLTRB(x - 150, floor_y + 110, x + 150, floor_y + 160), g)


def build_picture(E, i, t0, t1, sc):
    """Board type 'picture': an HD picture fills the board with a slow push-in; optional caption pill at the bottom."""
    img = image(sc.get("art"), "landscape")
    if img is None:  # missing picture: show a big icon board instead
        fb = {"type": "big", "icon": sc.get("icon", "bulb"), "text": sc.get("caption", ""), "cue": sc.get("cue")}
        return E.BUILD_BIG(i, t0, t1, fb)
    tin = E.cue_t(i, sc, t0 + 0.15)
    x, y, w, h = E.BX + 26, E.BY + 26, E.BW - 52, E.BH - 52
    cap = sc.get("caption")

    def draw(c, t, e, img=img):
        k = min(1.0, max(0.0, (t - tin) / max(0.5, t1 - tin)))
        rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), 30, 30)
        sh = skia.Paint(AntiAlias=True, Color=_col("#000000", 0.18)); sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 16))
        c.save(); c.translate(0, 10); c.drawRRect(rr, sh); c.restore()
        c.save(); c.clipRRect(rr, doAntiAlias=True)
        _cover(c, img, x, y, w, h, 1.0 + 0.10 * k, 0.5, 0.45)
        c.restore()
        st = skia.Paint(AntiAlias=True, Color=_col("#FFFFFF", 1.0)); st.setStyle(skia.Paint.kStroke_Style); st.setStrokeWidth(8)
        c.drawRRect(rr, st)
    E.el(tin, t1, draw, None, (E.BCX, E.BCY))
    if cap:
        E.el(max(tin + 0.6, E.cue_t(i, {"cue": sc.get("caption_cue")}, tin + 0.6)) if sc.get("caption_cue") else tin + 0.6, t1,
             lambda c, t, e: E.pill(c, E.BCX, y + h - 50, cap, sc.get("color", "#0A84FF"), 46), pivot=(E.BCX, y + h - 50))
