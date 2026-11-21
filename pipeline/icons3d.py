"""Icons for the boards: our own realistic house icons first (assets/icons_house/, made with FLUX.1-schnell + rembg on
Kaggle, see assets/icons_house/manifest.json), then Microsoft Fluent Emoji 3D (MIT licence, https://github.com/microsoft/fluentui-emoji).
Repo variable ICON_STYLE: house (default: curated mix, see PREFER_EMOJI) | house_all | 3d (Fluent only) | flat (old flat icons). A board icon can also name a
house-only picture with no emoji, e.g. "w_soil_block", "w_ai_chip" (list: assets/icons_house/*.webp).

    import icons3d
    draw = icons3d.drawer("🌱")      # or a board icon name: icons3d.drawer("robot")
    if draw: draw(canvas, x, y, k)  # same size convention as the old flat icons (66 px * k)

Pictures are downloaded once from GitHub (raw.githubusercontent.com) into assets/icons3d/ and reused;
`fluent3d_index.json` maps each emoji to its file (1,594 icons). If a picture can't be found or downloaded,
drawer() returns None and the engine draws the old flat icon, so a missing icon never breaks a video.
Repo variable ICON_STYLE=flat switches back to the old flat icons.
"""
import json, os, urllib.parse, urllib.request
import skia

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
CACHE = os.path.join(ROOT, "assets", "icons3d")
BASE = "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/"
STYLE = os.environ.get("ICON_STYLE", "house").strip().lower()
ON = STYLE != "flat"
HOUSE = STYLE not in ("3d", "flat")      # our own realistic icons first (assets/icons_house/), then Fluent 3D
HOUSE_ALL = STYLE == "house_all"         # use every house icon (no curated list)
HOUSE_DIR = os.path.join(ROOT, "assets", "icons_house")
# Curated mix (owner, 2026-11-21): for these the emoji (Fluent 3D) reads better on a white card or at small size -
# weather and symbols, mostly-white objects, the small robot. Their house icons stay in the repo: force one with
# "house:<emoji>" on a board (e.g. "house:☀️"), or use ICON_STYLE=house_all.
PREFER_EMOJI = set("""☀️ ☁️ ❄️ 🌀 ✅ ❌ ⚠️ 🚫 🛑 💬 📄 ✉️ 📅 📝 📖 🤖 🧼 🦴 🪶 🥛 🥚 🎲 🥤 🧴 🩹""".split())

# the boards' named icons -> the emoji whose 3D picture replaces them
NAMED = {"book": "📖", "brain": "🧠", "bulb": "💡", "calendar": "📅", "chat": "💬", "check": "✅", "coin": "🪙",
         "doc": "📄", "eye": "👁️", "globe": "🌍", "lock": "🔒", "mail": "✉️", "phone": "📱", "robot": "🤖",
         "search": "🔍", "shield": "🛡️", "suitcase": "💼", "sun": "☀️", "target": "🎯", "train": "🚆", "user": "🧑",
         "warn": "⚠️", "x": "❌", "star": "⭐", "heart": "❤️", "clock": "⏰", "camera": "📷", "music": "🎵"}

_IDX = None
_IMG = {}


def _index():
    global _IDX
    if _IDX is None:
        try: _IDX = json.load(open(os.path.join(HERE, "fluent3d_index.json"), encoding="utf-8"))
        except Exception: _IDX = {}
    return _IDX


def key(s):
    """'🌱' -> '1f331'; variation selectors are ignored."""
    return "-".join(f"{ord(ch):x}" for ch in s if ord(ch) not in (0xFE0F, 0xFE0E))


def house(s):
    """Our own icon for an emoji / board name / 'w_...' / 'house:<emoji>' name, or None (curated: see PREFER_EMOJI)."""
    if not HOUSE or not isinstance(s, str): return None
    forced = s.startswith("house:")
    if forced: s = s[6:]
    e = NAMED.get(s, s)
    if not (forced or HOUSE_ALL or s.startswith("w_")) and (e in PREFER_EMOJI or e.replace("\ufe0f", "") in {x.replace("\ufe0f", "") for x in PREFER_EMOJI}):
        return None
    k = s if s.startswith("w_") else key(e)
    p = os.path.join(HOUSE_DIR, k + ".webp")
    return p if os.path.exists(p) else None


def path(s):
    """Local picture for an emoji: our house icon if there is one, else the Fluent 3D PNG (downloaded the first time).
    None if unknown or offline."""
    h = house(s)
    if h: return h
    if isinstance(s, str) and s.startswith("w_"): return None
    if isinstance(s, str) and s.startswith("house:"): s = s[6:]  # forced house icon missing: fall back to the emoji
    s = NAMED.get(s, s)
    k = key(s); rel = _index().get(k)
    if not rel: return None
    local = os.path.join(CACHE, k + ".png")
    if os.path.exists(local) and os.path.getsize(local) > 500: return local
    try:
        os.makedirs(CACHE, exist_ok=True)
        with urllib.request.urlopen(BASE + urllib.parse.quote(rel), timeout=20) as r: data = r.read()
        if data[:8] != b"\x89PNG\r\n\x1a\n": return None
        tmp = local + ".part"; open(tmp, "wb").write(data); os.replace(tmp, local)
        return local
    except Exception as e:
        print("note: 3D icon not available for", repr(s), "-", str(e)[:80])
        return None


def image(s):
    if s not in _IMG:
        p = path(s) if ON else None
        _IMG[s] = skia.Image.MakeFromEncoded(skia.Data.MakeWithCopy(open(p, "rb").read())) if p else None
    return _IMG[s]


def drawer(s, scale=1.18, shadow=True):
    """Draw function (c, x, y, k) for an emoji or named icon, or None (then use the flat icon)."""
    if not ON or not isinstance(s, str) or not s: return None
    img = image(s)
    if img is None: return None
    tight = house(s) is not None
    def draw(c, x, y, k=1.0, a=1.0, img=img):
        box = 66 * k * scale * (0.9 if tight else 1.0)
        r = skia.Rect.MakeXYWH(x - box / 2, y - box / 2, box, box)
        if shadow:  # soft contact shadow under the icon
            p = skia.Paint(AntiAlias=True, Color=skia.Color(0, 0, 0, int(60 * a)))
            p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, box * 0.06))
            c.drawOval(skia.Rect.MakeXYWH(x - box * 0.34, y + box * 0.36, box * 0.68, box * 0.13), p)
        p = skia.Paint(AntiAlias=True); p.setAlphaf(a)
        c.drawImageRect(img, r, skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear), p)
    return draw
