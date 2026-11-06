"""The CurioKids Club episode renderer: episode JSON -> PNG frames (cast of 1-2: LEO, MIA, DAD; living room, whiteboard).

    EPISODE=episodes/ep002/episode.json python pipeline/tts.py      # voices + build/timing.json
    EPISODE=... BG=v2 DOODLE=chars python pipeline/episode_engine.py <frames_dir> [frame ...]
    python pipeline/finish.py <frames_dir> 24 out.mp4

Episode JSON (see episodes/README.md):
  "cast": ["LEO", "MIA"] (left asks, right explains) or ["MIA"] (solo, centre)
  lines[i] = {"who": <cast code>, "text": "...", "board": {scene}?, "punch": "word"?}
  A line's "board" starts a new board scene that stays until the next line with a "board".
Scene types: title, big, gallery, poem, steps, compare, checklist, summary (+ legacy chat, permission).
Icons: one emoji ("🐙") or a legacy icon name.
Items inside scenes may carry "cue": a word of that line; the item pops in when the word is spoken.
"""
import json, math, os, random, sys
from multiprocessing import Pool
import skia
import kit2d as K
from kit2d import (P, rr, ell, text, smooth, wob, Track, Char, LN, DUR, NF, B, FONT_XB, FONT_B, FONT_SB,
                   appear, fade, scaled, shadow_rrect, bubble, card, icon_chat, icon_robot, icon_check, icon_sun,
                   icon_train, icon_doc, icon_lock, BX, BY, BW, BH, BCX, BCY)
import icons_extra as IX
import char_line, bg_line

EP = json.load(open(os.environ["EPISODE"]))
ELINES = EP["lines"]
assert len(ELINES) == len(LN), "timing.json does not match the episode: run tts.py with the same EPISODE first"

ICONS = {"chat": icon_chat, "robot": icon_robot, "check": icon_check, "sun": icon_sun, "train": icon_train,
         "doc": icon_doc, "lock": lambda c, x, y, k=1.0: icon_lock(c, x, y - 4 * k, k * 0.8), "target": IX.icon_target,
         "search": IX.icon_search, "calendar": IX.icon_cal, "mail": IX.icon_mail, "suitcase": IX.icon_suitcase,
         "warn": IX.icon_warn, "x": IX.icon_x, "user": IX.icon_user, "bulb": IX.icon_bulb, "shield": IX.icon_shield,
         "coin": IX.icon_coin, "eye": IX.icon_eye, "book": IX.icon_book, "globe": IX.icon_globe, "brain": IX.icon_brain,
         "phone": IX.icon_phone}


EMOJI_TF = skia.Typeface.MakeFromFile("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf")
_EMO = {}


def _emoji_drawer(s):
    s = s.replace("\ufe0f", "").replace("\ufe0e", "")
    f = skia.Font(EMOJI_TF, 100)
    if not s or EMOJI_TF is None or 0 in f.textToGlyphs(s):
        return None
    b = skia.Rect(); f.measureText(s, bounds=b)
    def draw(c, x, y, k=1.0, s=s, b=b):
        sz = 100 * 66 * k / max(b.width(), b.height(), 1)
        ff = skia.Font(EMOJI_TF, sz); sc = sz / 100
        c.drawString(s, x - (b.left() + b.width() / 2) * sc, y - (b.top() + b.height() / 2) * sc, ff, K.nofx(P("#000000")))
    return draw


_SVG = {}


def _svg_drawer(name):
    import re as _re, images
    path = images.resolve(name)
    if not path:
        print("warning: picture not found", name); return None
    txt = open(path, encoding="utf-8").read()
    m = _re.search(r'viewBox="([-\d.\s,]+)"', txt)
    vb = [float(x) for x in _re.split(r"[\s,]+", m.group(1).strip())] if m else [0, 0, 100, 100]
    dom = skia.SVGDOM.MakeFromStream(skia.Stream.MakeFromFile(path)); dom.setContainerSize(skia.Size(vb[2], vb[3]))
    def draw(c, x, y, k=1.0, dom=dom, vb=vb):
        box = 66 * k * 1.25  # real illustrations a bit larger than emoji
        s = box / max(vb[2], vb[3])
        c.save(); c.translate(x - vb[2] * s / 2, y - vb[3] * s / 2); c.scale(s, s); c.translate(-vb[0], -vb[1]); dom.render(c); c.restore()
    return draw


def ico(name):
    if not name: return None
    if name in ICONS: return ICONS[name]
    if isinstance(name, str) and name.startswith("img:"):
        if name not in _SVG: _SVG[name] = _svg_drawer(name)
        return _SVG[name] or ICONS["bulb"]
    if name not in _EMO:
        _EMO[name] = _emoji_drawer(name)
        if _EMO[name] is None: print("warning: no emoji glyph for", repr(name), "- using bulb")
    return _EMO[name] or ICONS["bulb"]


# ------------------------------------------------------------------ timing helpers
def wt(i, prefix, nth=0, end=False):
    if not prefix:
        return LN[i]["end"] if end else LN[i]["start"] + 0.1
    pre = prefix.lower().strip(".,!?")
    ws = [w for w in LN[i]["words"] if w[0].lower().strip(".,!?'\"").startswith(pre)]
    if len(ws) <= nth:
        return LN[i]["end"] if end else LN[i]["start"] + 0.1
    return ws[nth][2] if end else ws[nth][1]


def fit(c, s, x, y, size, color, maxw, tf=FONT_XB, align="c", a=1.0):
    f = skia.Font(tf, size)
    while f.measureText(s) > maxw and size > 14:
        size -= 1; f = skia.Font(tf, size)
    return text(c, s, x, y, size, color, tf, align, a)


# ------------------------------------------------------------------ characters + lip-sync
CAST = EP.get("cast", ["LEO", "MIA"])
XPOS = [540] if len(CAST) == 1 else [296, 784]
CH = {n: Char(n, x, 2.0 * k) for k, (n, x) in enumerate(zip(CAST, XPOS))}
ORDER = [CH[n] for n in CAST]
random.seed(5)
for c in ORDER:
    t = random.uniform(0.6, 1.5)
    while t < DUR:
        c.blinks.append(t); t += random.uniform(2.0, 4.0)
VIS = {}
for chars, ov in [("aɑ", (0.95, 1.0)), ("æ", (0.85, 1.05)), ("ʌɐ", (0.65, 0.92)), ("ɛe", (0.6, 1.05)),
                  ("ɪi", (0.4, 1.12)), ("ə", (0.42, 0.9)), ("ɚɝ", (0.42, 0.75)), ("oɔ", (0.72, 0.6)),
                  ("uʊ", (0.36, 0.5)), ("w", (0.24, 0.45)), ("ɹr", (0.36, 0.72)), ("l", (0.38, 0.95)),
                  ("mbp", (0.0, 0.85)), ("fv", (0.12, 0.98)), ("θð", (0.26, 0.98)), ("ʃʒ", (0.32, 0.62)),
                  ("sztdnkgŋhjɡɾʔç", (0.26, 0.97))]:
    for ch in chars: VIS[ch] = ov
for c in ORDER:
    c.mo.add(0, 0); c.mw.add(0, 1)
for ln in LN:
    c = CH[ln["speaker"]]
    c.mo.add(ln["start"] - 0.1, 0); c.mw.add(ln["start"] - 0.1, 1)
    for ch, a, b in ln["phonemes"]:
        if ch in VIS:
            o, w = VIS[ch]
            if ch in "mbp":
                c.mo.add(a + 0.01, 0); c.mo.add(b - 0.01, 0); c.mw.add((a + b) / 2, w)
            else:
                c.mo.add((a + b) / 2, o); c.mw.add((a + b) / 2, w)
        elif ch in " ,.!?;:" and b - a > 0.11:
            c.mo.add(a + 0.04, 0.04); c.mo.add(b - 0.03, 0.04)
    c.mo.add(ln["end"] + 0.08, 0); c.mw.add(ln["end"] + 0.08, 1)


# ------------------------------------------------------------------ board scenes -> elements
ELEMS = []  # (t_in, t_out, fn, anchor, pivot)


def el(t_in, t_out, fn, anchor=None, pivot=None):
    ELEMS.append((t_in, t_out, fn, anchor, pivot))


# ------------------------------------------------------------------ big, phone-readable scenes (The CurioKids Club)
# Everything is sized for a phone screen: text 52-96 px, pictures 2-4x bigger, at most a few words per item.
Y0 = BY + 70
scene_starts = [i for i, l in enumerate(ELINES) if l.get("board")]
CUES = []  # (time, line) of every cued item: drives pointing, looks and camera
NAVY = "#1F2D44"
last = len(LN) - 1
_cta_w = [w for w in LN[last]["words"] if w[0].lower().startswith(("subscrib", "follow"))]
T_FOLLOW = _cta_w[0][1] if _cta_w else None


def scene_window(k):
    i = scene_starts[k]
    t0 = LN[i]["start"] - 0.1 if i else 0.05
    t1 = (LN[scene_starts[k + 1]]["start"] - 0.1) if k + 1 < len(scene_starts) else DUR + 1
    if T_FOLLOW: t1 = min(t1, T_FOLLOW - 0.05)  # the panel clears for the Subscribe card
    return i, t0, t1


def cue_t(i, item, default):
    if item.get("cue"):
        t = wt(i, item["cue"]); CUES.append((t, i)); return t
    return default


def big_text(c, s, x, y, size, color, maxw, tf=FONT_XB, min_size=46, lines=2, outline=None):
    """Fit text in maxw: shrink a little, then wrap to 2 lines, then shrink more. Centred on (x, y)."""
    words = s.split()
    for sz in range(size, min_size - 1, -2):
        f = skia.Font(tf, sz)
        if f.measureText(s) <= maxw:
            rows = [s]; break
        if lines >= 2 and len(words) > 1 and sz <= size * 0.9:
            best = min(range(1, len(words)), key=lambda k: max(f.measureText(" ".join(words[:k])), f.measureText(" ".join(words[k:]))))
            rows = [" ".join(words[:best]), " ".join(words[best:])]
            if max(f.measureText(r) for r in rows) <= maxw: break
    else:
        f = skia.Font(tf, min_size); rows = [s]; sz = min_size
    lh = sz * 1.08; y0 = y - lh * (len(rows) - 1) / 2
    for r_ in rows:
        if outline:
            p = skia.Paint(AntiAlias=True, Color=K.hexc(outline)); p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(sz * 0.16)
            p.setStrokeJoin(skia.Paint.kRound_Join)
            w_ = f.measureText(r_); c.drawString(r_, x - w_ / 2, y0 + sz * 0.36, f, p)
        text(c, r_, x, y0, sz, color, tf)
        y0 += lh


def pill(c, x, y, label, col, size=46):
    f = skia.Font(FONT_XB, size); w = f.measureText(label) + 70
    r = rr(x - w / 2, y - size * 0.8, w, size * 1.6, size * 0.8); shadow_rrect(c, r, 6, 4, 0.2); c.drawRRect(r, P(col))
    text(c, label, x, y, size, "#FFFFFF")


def card_bg(c, x, y, w, h, col, border="#1F2D44"):
    r = rr(x - w / 2, y - h / 2, w, h, 34); shadow_rrect(c, r, 8, 6, 0.18); c.drawRRect(r, P(col))
    pth = skia.Path(); pth.addRRect(r); c.drawPath(pth, char_line.shade_paint(pth, 0.6, fx=False))
    c.drawRRect(r, P(border, 5))


TINTS = ("#FFF1B8", "#DCEBFF", "#FFE0EC", "#DDF7E8", "#EFE3FF", "#FFE6D5")
COLS = ("#FF4D6D", "#0A84FF", "#8E44AD", "#2E9E5B", "#FF8C42")


def build_title(i, t0, t1, sc):
    L, R = sc.get("left", {}), sc.get("right", {})
    for side, S, col in ((-1, L, "#0A84FF"), (1, R, "#E91E63")):
        x = BCX + side * BW * 0.27
        def f(c, t, e, S=S, x=x, col=col, side=side):
            sl = 1 - smooth((t - t0) / 0.45); xx = x + side * sl * 300
            card_bg(c, xx, BCY - 40, BW * 0.44, 450, TINTS[0 if side < 0 else 2])
            (ico(S.get("icon")) or IX.icon_bulb)(c, xx, BCY - 120, 3.4)
            big_text(c, S.get("label", ""), xx, BCY + 100, 60, S.get("color", col), BW * 0.4)
        el(t0, t1, f, None, (x, BCY))
    el(t0 + 0.4, t1, lambda c, t, e: (c.drawCircle(BCX, BCY - 40, 74, P("#FFC93C")), c.drawCircle(BCX, BCY - 40, 74, P(NAVY, 6)),
                                      text(c, sc.get("mid", "?"), BCX, BCY - 40, 78 if len(sc.get("mid", "?")) < 3 else 48, NAVY)), (BCX, BCY - 40))
    if sc.get("subtitle"):
        el(t0 + 0.9, t1, lambda c, t, e: big_text(c, sc["subtitle"], BCX, BY + BH - 75, 52, NAVY, BW - 60, lines=1), pivot=(BCX, BY + BH - 75))


def build_big(i, t0, t1, sc):
    ic = ico(sc.get("icon", "bulb")) or IX.icon_bulb
    tin = cue_t(i, sc, t0 + 0.15)
    has_sub = bool(sc.get("sub"))
    el(tin, t1, lambda c, t, e: (ic(c, BCX, BCY - (140 if has_sub else 110) + math.sin(t * 3) * 6, 4.6),
                                 big_text(c, sc.get("text", ""), BCX, BCY + (80 if has_sub else 150), 90, NAVY, BW - 60)), (BCX + 200, BCY - 200), (BCX, BCY))
    if has_sub:
        ts = cue_t(i, {"cue": sc.get("sub_cue")}, tin + 0.8) if sc.get("sub_cue") else tin + 0.8
        el(ts, t1, lambda c, t, e: pill(c, BCX, BY + BH - 55, sc["sub"], sc.get("sub_color", "#0A84FF"), 48), pivot=(BCX, BY + BH - 55))


def build_gallery(i, t0, t1, sc):
    items = sc.get("items", [])[:6]; n = len(items)
    top = BY + 40
    if sc.get("title"):
        el(t0, t1, lambda c, t, e: pill(c, BCX, BY + 72, sc["title"], sc.get("color", "#FF8C42"), 46), (BCX + 200, BY + 72))
        top = BY + 140
    cols = n if n <= 3 else (2 if n == 4 else 3)
    rows = (n + cols - 1) // cols
    cw = (BW - 40) / cols; rh = (BY + BH - 30 - top) / rows
    for k, it in enumerate(items):
        r_, c_ = divmod(k, cols); in_row = min(cols, n - r_ * cols)
        x = BCX + (c_ - (in_row - 1) / 2) * cw; y = top + rh * (r_ + 0.5)
        ti = cue_t(i, it, t0 + 0.3 + k * 0.6)
        big = min(cw, rh) / 120
        def f(c, t, e, it=it, x=x, y=y, k=k, big=big):
            card_bg(c, x, y, cw - 22, rh - 22, TINTS[k % 6])
            (ico(it.get("icon")) or IX.icon_bulb)(c, x, y - rh * 0.14, big)
            big_text(c, it.get("label", ""), x, y + rh * 0.3, 56 if rows == 1 else 46, NAVY, cw - 50, lines=2, min_size=34)
        el(ti, t1, f, (x + cw / 2 - 30, y - rh / 2 + 30), (x, y))


def build_poem(i, t0, t1, sc):
    """Karaoke style: one verse line at a time, big, with its picture; the poem title stays on top."""
    vl = sc.get("lines", [])[:4]
    el(t0, t1, lambda c, t, e: pill(c, BCX, BY + 72, sc.get("title", "Poem"), "#8E44AD", 44), (BCX + 220, BY + 72))
    times = [cue_t(i, it, t0 + 0.3 + k * 1.6) for k, it in enumerate(vl)]
    for k, it in enumerate(vl):
        ti = times[k]; to = times[k + 1] if k + 1 < len(times) else t1
        def f(c, t, e, it=it, k=k):
            ic = ico(it.get("icon")) or ico(sc.get("icon"))
            if ic: ic(c, BCX, BCY - 50 + math.sin(t * 3.2) * 8, 3.6)
            big_text(c, it.get("text", ""), BCX, BCY + 200, 80, COLS[k % 5], BW - 60, outline="#FFFFFF")
        el(ti, to, f, None, (BCX, BCY + 60))


def _rows(i, t0, t1, items, key, title=None, marks=False):
    top = BY + 50
    if title:
        el(t0, t1, lambda c, t, e: pill(c, BCX, BY + 72, title, "#E91E63", 44), (BCX + 220, BY + 72))
        top = BY + 150
    n = max(1, len(items)); gap = min(150, (BY + BH - 30 - top) / n)
    for k, it in enumerate(items):
        y = top + gap * (k + 0.5)
        ti = cue_t(i, it, t0 + 0.3 + k * 0.7)
        def f(c, t, e, it=it, y=y, k=k, ti=ti):
            card_bg(c, BCX, y, BW - 60, gap - 18, TINTS[k % 6], COLS[k % 5])
            ic = ico(it.get("icon"))
            x0 = BX + 70
            if ic: ic(c, x0 + 20, y, min(1.6, (gap - 30) / 60)); x0 += 90
            maxw = BW - (x0 - BX) - (130 if marks else 60)
            f_ = skia.Font(FONT_XB, 56); s = it.get(key, ""); sz = 56
            while f_.measureText(s) > maxw and sz > 36: sz -= 2; f_ = skia.Font(FONT_XB, sz)
            text(c, s, x0, y, sz, NAVY, FONT_XB, "l")
            if marks and appear(t, ti + 0.3):
                (icon_check if it.get("ok", True) else IX.icon_x)(c, BX + BW - 90, y, 1.6)
        el(ti, t1, f, (BX + BW - 60, y - 30), (BCX, y))


def build_steps(i, t0, t1, sc): _rows(i, t0, t1, sc.get("items", []), "label", sc.get("title"))
def build_checklist(i, t0, t1, sc): _rows(i, t0, t1, sc.get("items", []), "text", sc.get("title"), marks=True)
def build_summary(i, t0, t1, sc): _rows(i, t0, t1, sc.get("rows", []), "text")


def build_compare(i, t0, t1, sc):
    for side, dc in ((-1, "#0A84FF"), (1, "#E91E63")):
        S = sc.get("left" if side < 0 else "right", {}); X = BCX + side * BW * 0.255
        el(t0, t1, lambda c, t, e, S=S, X=X, dc=dc: pill(c, X, BY + 72, S.get("label", ""), S.get("color", dc), 46), pivot=(X, BY + 72))
        items = S.get("items", []); n = max(1, len(items)); gap = min(170, (BY + BH - 180) / n)
        for k, it in enumerate(items):
            y = BY + 150 + gap * (k + 0.5)
            ti = cue_t(i, it, t0 + 0.3 + k * 0.6)
            def f(c, t, e, it=it, X=X, y=y, k=k):
                card_bg(c, X, y, BW * 0.48, gap - 18, it.get("bg", TINTS[(k + (0 if X < BCX else 2)) % 6]))
                ic = ico(it.get("icon"))
                if ic: ic(c, X - BW * 0.17, y, min(1.4, (gap - 30) / 60))
                big_text(c, it.get("text", ""), X + (40 if ic else 0), y, 48, NAVY, BW * (0.33 if ic else 0.43), lines=2, min_size=32)
                if it.get("tick") is not None:
                    (icon_check if it["tick"] else IX.icon_x)(c, X + BW * 0.21, y - gap / 2 + 26, 1.0)
            el(ti, t1, f, (X + 220, y - 30), (X, y))
    el(t0, t1, lambda c, t, e: c.drawLine(BCX, BY + 130, BCX, BY + BH - 30, P(NAVY, 3, a=0.15)), pivot=(BCX, BCY))


REVEALS = []  # answer reveal times (confetti)


def build_guess(i, t0, t1, sc):
    """Guessing game: clues pop in on the left, a big '?' card flips to the answer when its cue word is spoken."""
    clues = sc.get("clues", [])[:3]; ans = sc.get("answer", {})
    top = BY + 40
    if sc.get("title"):
        el(t0, t1, lambda c, t, e: pill(c, BCX, BY + 62, sc["title"], sc.get("color", "#FF8C42"), 44), (BCX + 200, BY + 62))
        top = BY + 130
    n = max(1, len(clues)); gap = (BY + BH - 30 - top) / n
    cx_l, cw = BX + BW * 0.29, BW * 0.52
    for k, it in enumerate(clues):
        y = top + gap * (k + 0.5)
        ti = cue_t(i, it, t0 + 0.4 + k * 0.9)
        def f(c, t, e, it=it, y=y, k=k):
            card_bg(c, cx_l, y, cw, gap - 18, TINTS[k % 6], COLS[k % 5])
            ic = ico(it.get("icon"))
            if ic: ic(c, cx_l - cw / 2 + 60, y, min(1.4, (gap - 30) / 60))
            big_text(c, it.get("label", ""), cx_l + 40, y, 44, NAVY, cw - 150, lines=2, min_size=30)
        el(ti, t1, f, None, (cx_l, y))
    ta = t1 - 0.6
    if ans.get("cue"):  # the answer is usually said a line or two later: search this line and the following ones in this scene
        nxt = min([j for j in scene_starts if j > i] or [len(LN)])
        for j in range(i, nxt):
            if any(w[0].lower().strip(".,!?'\"").startswith(ans["cue"].lower()) for w in LN[j]["words"]):
                ta = wt(j, ans["cue"]); CUES.append((ta, j)); break
    REVEALS.append(ta)
    cx_r, cy_r = BX + BW * 0.78, (top + BY + BH) / 2
    w, h = BW * 0.36, min(BH - 60, (BY + BH - top) - 10)
    def card(c, t, e):
        u = max(0.0, min(1.0, (t - ta) / 0.5)); flip = abs(math.cos(u * math.pi))  # 1 -> 0 -> 1
        shown = u >= 0.5
        c.save(); c.translate(cx_r, cy_r); c.scale(max(0.02, flip), 1.0 + 0.06 * math.sin(u * math.pi)); c.translate(-cx_r, -cy_r)
        if not shown:
            card_bg(c, cx_r, cy_r, w, h, "#8E44AD", "#5B2C83")
            wob_ = math.sin(t * 5) * 6
            text(c, "?", cx_r, cy_r + wob_, 220, "#FFFFFF")
        else:
            card_bg(c, cx_r, cy_r, w, h, "#FFF6CC", "#F2B600")
            ic = ico(ans.get("icon"))
            if ic: ic(c, cx_r, cy_r - h * 0.12, min(3.0, w / 110))
            big_text(c, ans.get("label", ""), cx_r, cy_r + h * 0.33, 52, NAVY, w - 30, lines=2, min_size=30)
        c.restore()
    el(t0 + 0.2, t1, card, None, (cx_r, cy_r))


def build_letter(i, t0, t1, sc):
    """ABC learning: a giant 'A a' with picture words popping around it."""
    L = sc.get("letter", "A")[:1]
    words = sc.get("items", [])[:4]
    cols = ("#FF4D6D", "#0A84FF", "#2E9E5B", "#FF8C42", "#8E44AD")
    col = cols[(ord(L.upper()) - 65) % 5] if L.isalpha() else "#FF4D6D"
    ty = BY + BH * (0.40 if words else 0.48)
    def big(c, t, e):
        bob = math.sin(t * 2.4) * 8
        f = skia.Font(FONT_XB, 300); s_ = f"{L.upper()} {L.lower()}"; w = f.measureText(s_)
        sh = P("#000000", a=0.18); sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 10))
        c.drawString(s_, BCX - w / 2 + 8, ty + 100 + bob + 10, f, sh)
        c.drawString(s_, BCX - w / 2, ty + 100 + bob, f, P(col))
        p_ = P("#FFFFFF", 10, a=0.9); c.drawString(s_, BCX - w / 2, ty + 100 + bob, f, p_); c.drawString(s_, BCX - w / 2, ty + 100 + bob, f, P(col))
    tin = cue_t(i, sc, t0 + 0.15)
    el(tin, t1, big, None, (BCX, ty))
    n = len(words)
    for k, it in enumerate(words):
        IW = BW - 90; x = BX + 45 + IW * (k + 0.5) / max(1, n); y = BY + BH - 120  # inset so cards clear the curtains
        ti = cue_t(i, it, tin + 0.6 + k * 0.7)
        def f(c, t, e, it=it, x=x, y=y, k=k, IW=IW):
            card_bg(c, x, y, IW / max(1, n) - 18, 200, TINTS[k % 6])
            ic = ico(it.get("icon"))
            if ic: ic(c, x, y - 30, 1.5)
            big_text(c, it.get("label", ""), x, y + 62, 40, NAVY, IW / max(1, n) - 36, lines=1, min_size=24)
        el(ti, t1, f, None, (x, y))


NUM_WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve",
             "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty"]


def build_count(i, t0, t1, sc):
    """Counting: objects appear one by one as the numbers are spoken; a big number shows the count so far."""
    n = max(1, min(20, int(sc.get("count", 5)))); icon = sc.get("icon", "⭐")
    start = int(sc.get("start", 1)); step = int(sc.get("step", 1))
    times = []
    words = [w for w in LN[i]["words"]]
    for k in range(n):
        val = start + k * step
        name = NUM_WORDS[val] if 0 <= val < len(NUM_WORDS) else str(val)
        hit = [w for w in words if w[0].lower().strip(".,!?'\"…").startswith(name) and w[1] > (times[-1] if times else 0)]
        times.append(hit[0][1] if hit else (times[-1] + 0.6 if times else t0 + 0.4))
        CUES.append((times[-1], i))
    cols = 5 if n > 12 else 4 if n > 6 else 3
    rows = (n + cols - 1) // cols
    gx0, gx1 = BX + 50, BX + BW * 0.64; gy0, gy1 = BY + 70, BY + BH - 40
    cw, rh = (gx1 - gx0) / cols, (gy1 - gy0) / rows
    k_ = min(cw, rh) / 80
    for k in range(n):
        r_, c_ = divmod(k, cols); x = gx0 + cw * (c_ + 0.5); y = gy0 + rh * (r_ + 0.5)
        el(times[k], t1, lambda c, t, e, x=x, y=y: (ico(icon) or IX.icon_bulb)(c, x, y, k_), None, (x, y))
    def num(c, t, e):
        shown = sum(1 for tt in times if tt <= t)
        if shown == 0: return
        val = start + (shown - 1) * step
        x = BX + BW * 0.83; y = BCY
        pop = 1 + 0.15 * max(0.0, 1 - (t - times[shown - 1]) / 0.25)
        c.save(); c.translate(x, y); c.scale(pop, pop)
        c.drawCircle(0, 0, 100, P("#FFD23F")); c.drawCircle(0, 0, 100, P(NAVY, 8))
        text(c, str(val), 0, 0, 130 if val < 100 else 95, NAVY)
        c.restore()
    el(t0, t1, num, None, (BX + BW * 0.83, BCY))


BUILD = {"letter": build_letter, "count": build_count, "guess": build_guess, "gallery": build_gallery, "poem": build_poem, "title": build_title, "steps": build_steps, "compare": build_compare,
         "checklist": build_checklist, "big": build_big, "summary": build_summary}
import types, diagrams
_E = types.SimpleNamespace(el=el, cue_t=cue_t, ico=ico, big_text=big_text, pill=pill, BX=BX, BY=BY, BW=BW, BH=BH,
                           BCX=BCX, BCY=BCY, LN=LN, K=K)
for _name, _fn in diagrams.BUILDERS.items():
    BUILD[_name] = (lambda f: (lambda i, t0, t1, sc: f(_E, i, t0, t1, sc)))(_fn)
for k in range(len(scene_starts)):
    i, t0, t1 = scene_window(k)
    sc = ELINES[i]["board"]
    BUILD.get(sc["type"], build_big)(i, t0, t1, sc)

import cta
KIDS_CTA = True
if T_FOLLOW:
    for k_ in range(3):  # tap sounds (the card itself is drawn on the top layer)
        el(T_FOLLOW + 0.9 + k_ * 1.0, T_FOLLOW + 1.0 + k_ * 1.0, lambda c, t, e: None)
LOOP = EP.get("loop_card")
if LOOP:
    tl = wt(last, LOOP.get("cue", "next"))
    def loopcard(c, t, e):  # top part of the panel; the Subscribe card sits underneath
        (ico(LOOP.get("left")) or IX.icon_bulb)(c, BCX - 260, BY + 170, 2.8); (ico(LOOP.get("right")) or IX.icon_bulb)(c, BCX + 260, BY + 170, 2.8)
        c.drawCircle(BCX, BY + 170, 62, P("#FFC93C")); c.drawCircle(BCX, BY + 170, 62, P(NAVY, 6)); text(c, "?", BCX, BY + 170, 76, NAVY)
        big_text(c, LOOP["text"], BCX, BY + 330, 72, NAVY, BW - 60, lines=2)
    el(tl, DUR + 1, loopcard, (BCX + 300, BY + 150), (BCX, BY + 260))


def draw_board(c, t):
    K.draw_board_frame(c, t)
    for n_, (t_in, t_out, fn, anchor, pivot) in enumerate(ELEMS):
        e = appear(t, t_in, t_out)
        if not e: continue
        px, py = pivot or anchor or (BCX, BCY)
        # puppet entrance: slide in from the nearest wing (behind the curtains), then settle with a little bounce
        side = -1 if px < BCX - 40 else 1 if px > BCX + 40 else (-1 if n_ % 2 else 1)
        k_ = min(1.0, e); dx = (1 - k_) * 560 * side
        c.save(); c.translate(px + dx, py); c.scale(0.7 + 0.3 * e, 0.7 + 0.3 * e); c.translate(-px, -py)
        fn(c, t, e); c.restore()
    c.restore()
    bg_line.draw_board_front(c, t)  # curtains etc. in FRONT of the content


# ------------------------------------------------------------------ automatic acting
PARTNER = {n: (20 if c.x < 500 else -20 if c.x > 580 else 0) for n, c in CH.items()}
BOARD = {n: ((12, -12) if c.x < 500 else (-12, -12) if c.x > 580 else (0, -16)) for n, c in CH.items()}
cues_by_line = {}
for tc, i in sorted(CUES):
    cues_by_line.setdefault(i, []).append(tc)
for i, ln in enumerate(LN):
    sp = CH[ln["speaker"]]; others = [n for n in CAST if n != ln["speaker"]]
    lsn = others[0] if others else None; li = CH[lsn] if lsn else None
    a, b = ln["start"], ln["end"]; dur = b - a; txt = ln["text"].strip()
    sp.look(a - 0.25, 0, 0)
    if li: li.look(a - 0.1, PARTNER[lsn], 0, 3)
    q, ex = txt.endswith("?"), "!" in txt
    if q:
        sp.gesture(1, "palms", a + 0.1, min(b, a + 2.4)); sp.gesture(-1, "palms", a + 0.15, min(b, a + 2.45))
        sp.brows(a, 0.9, 0.5); sp.smile.add(a, 0.25)
    elif ex and dur < 3.5:
        sp.gesture(sp.inner, "fist", a + 0.05, a + 0.9); sp.brows(a, 0.8, 0.3); sp.smile.add(a, 0.85)
    else:
        sp.gesture(-sp.inner, "explain", a + 0.1, min(b, a + 2.6)); sp.brows(a, 0.35, 0.2); sp.smile.add(a, 0.6)
    for k, tc in enumerate(cues_by_line.get(i, [])):
        if k == 0 or tc - cues_by_line[i][k - 1] > 1.2:
            sp.gesture(sp.inner, "point" if k % 2 == 0 else "point2", tc - 0.12, min(b, tc + 1.2))
            sp.look(tc - 0.15, *BOARD[ln["speaker"]]); sp.look(min(b, tc + 1.1), 0, 0)
            if li: li.look(tc + 0.05, *BOARD[lsn]); li.look(tc + 1.3, PARTNER[lsn], 0, 3)
    if li and dur > 5 and lsn == CAST[0]:
        li.gesture(li.inner, "chin", a + 0.6, a + min(dur - 0.6, 3.5))
    sp.brows(b + 0.4, 0, 0)
    if li: li.nod(b - 0.1, 8)
    for c in ([sp, li] if li else [sp]):
        c.smile.add(b + 0.5, 0.45)

# finale: hop + wave + happy eyes
lastl = LN[last]
CH[lastl["speaker"]].hop.add(lastl["start"], 0)
for dt, v in ((0.12, 40), (0.3, 0), (0.36, -6), (0.44, 0)):
    CH[lastl["speaker"]].hop.add(lastl["start"] + dt, v)
if T_FOLLOW:
    tw_end = min(DUR - 0.2, (wt(last, LOOP.get("cue", "next")) - 0.2) if LOOP else DUR - 0.2)
    for c in ORDER:
        s = -c.inner
        c.pose(s, "rest", T_FOLLOW - 0.3); k = 0
        while T_FOLLOW + k * 0.27 < tw_end:
            c.arm[s][0].add(T_FOLLOW + k * 0.27, 128 + (8 if k % 2 else -4)); c.arm[s][1].add(T_FOLLOW + k * 0.27, 168 + (22 if k % 2 else -18)); k += 1
        c.hand[s].append((T_FOLLOW - 0.1, "open")); c.hand[s].sort(); c.pose(s, "rest", tw_end + 0.3)
        c.smile.add(T_FOLLOW, 0.92); c.brows(T_FOLLOW, 0.8, 0.3)

# ------------------------------------------------------------------ drone, camera, punches
bit_keys = [(0, (540, 60)), (0.6, (960, 860))]; idle = [(980, 860), (100, 860)]; lastt = 0.6
for (t_in, t_out, fn, anchor, pivot) in sorted(ELEMS, key=lambda e: e[0]):
    if anchor and t_in - lastt > 0.5:
        bit_keys.append((t_in + 0.2, (min(1000, anchor[0] + 40), max(200, anchor[1] - 40)))); lastt = t_in
for i in range(len(LN)):
    bit_keys.append((LN[i]["end"] + 0.2, idle[i % 2]))
for tt, (x, y) in sorted(bit_keys):
    K.BITX.add(tt, x); K.BITY.add(tt, y)

SHOTS = [(0.0, "wide")]
for i, ln in enumerate(LN):
    if i == 0:
        continue
    who = ln["speaker"] if len(CAST) > 1 else ("wide" if i % 3 else ln["speaker"])
    _sc_i = max([j for j in scene_starts if j <= i] or [0])
    if ELINES[_sc_i].get("board", {}).get("type") in list(diagrams.BUILDERS) + ["guess", "letter", "count"]:  # keep diagrams / guessing games on screen
        who = "board"
    SHOTS.append((ln["start"] - 0.05, "wide" if i % 4 == 0 or i == last else who))
    cl = cues_by_line.get(i, [])
    if cl and ln["end"] - ln["start"] > 2.5:
        SHOTS.append((cl[0] - 0.1, "board"))
        if ln["end"] - cl[0] > 4.5:
            SHOTS.append((cl[0] + 3.0, "wide"))
if T_FOLLOW:
    SHOTS.append((T_FOLLOW - 0.1, "wide"))
if LOOP:
    SHOTS.append((wt(last, LOOP.get("cue", "next")) - 0.1, "board"))
SHOTS.sort()
dedup = []
for t_, k in SHOTS:  # drop cuts closer than 1.2 s and repeated shots
    if dedup and (t_ - dedup[-1][0] < 1.2 or k == dedup[-1][1]):
        if t_ - dedup[-1][0] < 1.2 and len(dedup) > 1:
            dedup[-1] = (dedup[-1][0], k)
        continue
    dedup.append((t_, k))
SHOTS = dedup
HEADY = {"DAD": (1090, 1.95), "MIA": (1150, 1.95), "LEO": (1320, 2.2)}
CAMS = {"wide": (540, 960, 1.0, 1.05), "board": (540, 930, 1.03, 1.05)}
for n, c in CH.items():
    hy, z = HEADY[n]
    CAMS[n] = (c.x + (10 if c.x < 540 else -10 if c.x > 540 else 0), hy, z, z + 0.1)
PUNCH = [wt(i, l["punch"]) for i, l in enumerate(ELINES) if l.get("punch")]

import kids_fx
_bursts = [(e[0], (e[4] or e[3])[0], (e[4] or e[3])[1]) for e in ELEMS if e[0] > 0.3 and (e[4] or e[3]) and (T_FOLLOW is None or e[0] < T_FOLLOW - 0.1)]
_conf = sorted(set([round(p_, 2) for p_ in PUNCH] + [round(r_ + 0.25, 2) for r_ in REVEALS] + ([T_FOLLOW + 0.95] if T_FOLLOW else [])))
FX = kids_fx.KidsFX(K, _bursts, _conf)
_top0fx = K.draw_top
K.draw_top = lambda c, t: (_top0fx(c, t), FX.draw(c, t))
_top1 = K.draw_top
K.draw_top = lambda c, t: (_top1(c, t), cta.end_card(c, t, T_FOLLOW, K, KIDS_CTA, cy=BY + BH - 110) if T_FOLLOW else None)
if not KIDS_CTA:
    T_REMIND = DUR * 0.42
    if T_FOLLOW is None or T_REMIND + 3.5 < T_FOLLOW:
        _top0 = K.draw_top
        K.draw_top = lambda c, t: (_top0(c, t), cta.reminder(c, t, T_REMIND, K))
def _speaker_x(t):
    cur = LN[0]
    for ln in LN:
        if ln["start"] - 0.2 <= t: cur = ln
    return CH[cur["speaker"]].x
bg_line.SPEAKER_X = _speaker_x
K.CHARS = ORDER; K.SHOTS = SHOTS; K.CAMS = CAMS; K.PUNCH = PUNCH; K.LOGO_T = T_FOLLOW or DUR + 10
K.draw_board = draw_board; K.CHARMOD = char_line; K.draw_bg = bg_line.draw_bg; K.draw_board_frame = bg_line.draw_board_frame


def worker(args):
    out, fs = args
    for f in fs:
        K.render_frame(f).save(os.path.join(out, f"f{f + 1:04d}.png"), skia.kPNG)
    return len(fs)


def make_thumbnail():
    import thumbnail
    path = thumbnail.make(os.path.join(B, "thumbnail.jpg"), K, ORDER, EP, ico)
    print("thumbnail", path)


if __name__ == "__main__":
    if os.environ.get("THUMB_ONLY"):
        make_thumbnail(); sys.exit(0)
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    frames = [int(x) for x in sys.argv[2:]] or list(range(NF))
    n = int(os.environ.get("WORKERS", os.cpu_count() or 2))
    with Pool(n) as pool:
        print("rendered", sum(pool.map(worker, [(out, frames[j::n]) for j in range(n)])))
    pops = sorted(set(round(e[0], 3) for e in ELEMS if e[0] > 0.3))
    try:
        make_thumbnail()
    except Exception as e:  # a thumbnail problem must never block the video
        print("thumbnail failed:", e)
    json.dump({"frames": NF, "pops": pops, "shots": [(t_, k) for t_, k in SHOTS]}, open(os.path.join(B, "shots.json"), "w"))
