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


def ico(name):
    if not name: return None
    if name in ICONS: return ICONS[name]
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


Y0 = BY + 130
scene_starts = [i for i, l in enumerate(ELINES) if l.get("board")]
CUES = []  # (time, line) of every cued item: drives pointing, looks and camera


def scene_window(k):
    i = scene_starts[k]
    t0 = LN[i]["start"] - 0.1 if i else 0.05
    t1 = (LN[scene_starts[k + 1]]["start"] - 0.1) if k + 1 < len(scene_starts) else DUR + 1
    return i, t0, t1


def cue_t(i, item, default):
    if item.get("cue"):
        t = wt(i, item["cue"]); CUES.append((t, i)); return t
    return default


def build_title(i, t0, t1, sc):
    L, R = sc.get("left", {}), sc.get("right", {})
    def f(c, t, e, L=L, R=R):
        sl = 1 - smooth((t - t0) / 0.45)
        li, ri = ico(L.get("icon", "chat")), ico(R.get("icon", "robot"))
        li = li or IX.icon_bulb; ri = ri or IX.icon_bulb
        li(c, BCX - 250 - sl * 300, BCY - 40, 2.0); fit(c, L.get("label", ""), BCX - 250 - sl * 300, BCY + 70, 40, L.get("color", "#0A84FF"), 330)
        ri(c, BCX + 250 + sl * 300, BCY - 30, 2.0); fit(c, R.get("label", ""), BCX + 250 + sl * 300, BCY + 70, 40, R.get("color", "#E91E63"), 330)
    el(t0, t1, f, pivot=(BCX, BCY))
    el(t0 + 0.4, t1, lambda c, t, e: (c.drawCircle(BCX, BCY + 10, 62, P("#FFC93C")), text(c, sc.get("mid", "?"), BCX, BCY + 10, 52, "#1F2D44")), (BCX, BCY + 10))
    if sc.get("subtitle"):
        el(t0 + 0.9, t1, lambda c, t, e: fit(c, sc["subtitle"], BCX, BCY + 180, 38, "#1F2D44", 820), pivot=(BCX, BCY + 180))


def build_chat(i, t0, t1, sc):
    if sc.get("title"):
        el(t0, t1, lambda c, t, e: IX.chip(c, BCX, Y0 - 20, sc["title"], sc.get("color", "#0A84FF"), None, 28), (BCX + 160, Y0 - 20))
    for k, it in enumerate(sc.get("items", [])):
        y = Y0 + 90 + k * 125
        ti = cue_t(i, it, t0 + 0.3 + k * 0.8)
        if it.get("who", "user") == "user":
            def f(c, t, e, it=it, y=y):
                IX.icon_user(c, BX + 100, y, 0.75)
                w = min(620, 60 + skia.Font(FONT_B, 32).measureText(it["text"]))
                bubble(c, BX + 160 + w / 2, y - 6, w, 92, it["text"], 32 if w < 620 else 26)
            el(ti, t1, f, (BX + 500, y - 40), (BX + 400, y))
        else:
            def f(c, t, e, it=it, y=y):
                w = min(620, 60 + skia.Font(FONT_B, 32).measureText(it["text"]))
                bubble(c, BX + BW - 160 - w / 2, y - 6, w, 92, it["text"], 32 if w < 620 else 26, col="#CDE7FF", tail="r")
                icon_chat(c, BX + BW - 90, y, 1.1)
            el(ti, t1, f, (BX + BW - 200, y - 40), (BX + BW - 400, y))


def build_steps(i, t0, t1, sc):
    if sc.get("title"):
        el(t0, t1, lambda c, t, e: IX.chip(c, BCX, Y0 - 20, sc["title"], sc.get("color", "#E91E63"), None, 28), (BCX + 180, Y0 - 20))
    items = sc.get("items", [])
    gap = min(104, 420 / max(1, len(items)))
    cols = ("#FF4D6D", "#0A84FF", "#8E44AD", "#2ECC71", "#FF8C5A")
    for k, it in enumerate(items):
        y = Y0 + 80 + k * gap
        ti = cue_t(i, it, t0 + 0.3 + k * 0.7)
        def f(c, t, e, it=it, y=y, k=k):
            r = rr(BCX - 360, y - 38, 720, 76, 24); shadow_rrect(c, r, 6, 4, 0.2); c.drawRRect(r, P("#FFFFFF")); c.drawRRect(r, P(cols[k % 5], 4))
            c.drawCircle(BCX - 318, y, 24, P(cols[k % 5])); text(c, str(k + 1), BCX - 318, y, 26, "#FFFFFF")
            ic = ico(it.get("icon"))
            if ic: ic(c, BCX - 255, y, 0.75)
            fit(c, it["label"], BCX - (210 if ic else 270), y, 32, "#1F2D44", 540, FONT_XB, "l")
        el(ti, t1, f, (BCX + 360, y - 30), (BCX, y))


def build_compare(i, t0, t1, sc):
    LX, RX = BCX - 225, BCX + 225
    for side, X, dc in (("left", LX, "#0A84FF"), ("right", RX, "#E91E63")):
        S = sc.get(side, {})
        el(t0, t1, lambda c, t, e, S=S, X=X, dc=dc: IX.chip(c, X, Y0 - 20, S.get("label", ""), S.get("color", dc), None, 26), pivot=(X, Y0 - 20))
        for k, it in enumerate(S.get("items", [])):
            y = Y0 + 80 + k * 98
            ti = cue_t(i, it, t0 + 0.3 + k * 0.6)
            def f(c, t, e, it=it, X=X, y=y):
                r = rr(X - 205, y - 38, 410, 76, 22); shadow_rrect(c, r, 6, 4, 0.2); c.drawRRect(r, P(it.get("bg", "#EEF5FF")))
                ic = ico(it.get("icon"))
                if ic: ic(c, X - 160, y, 0.7)
                fit(c, it["text"], X - (118 if ic else 180), y, 27, "#1F2D44", (300 if ic else 360) - (55 if it.get("tick") is not None else 0), FONT_B, "l")
                if it.get("tick") is not None:
                    (icon_check if it["tick"] else IX.icon_x)(c, X + 175, y, 0.9)
            el(ti, t1, f, (X + 200, y - 30), (X, y))
    el(t0, t1, lambda c, t, e: c.drawLine(BCX, Y0 + 30, BCX, BY + BH - 40, P("#1F2D44", 2, a=0.15)), pivot=(BCX, BCY))


def build_checklist(i, t0, t1, sc):
    if sc.get("title"):
        ic = ico(sc.get("icon", "search"))
        el(t0, t1, lambda c, t, e: (ic(c, BCX - 300, Y0 + 10, 1.6), fit(c, sc["title"], BCX + 30, Y0 + 10, 44, "#1F2D44", 560)), (BCX + 300, Y0))
    for k, it in enumerate(sc.get("items", [])):
        y = Y0 + 120 + k * 92
        ti = cue_t(i, it, t0 + 0.4 + k * 0.7)
        def f(c, t, e, it=it, y=y, ti=ti):
            IX.row(c, BCX, y, 600, it["text"], ico(it.get("icon")), 30)
            ck = appear(t, ti + 0.3)
            if ck:
                scaled(c, BCX + 260, y, ck); (icon_check if it.get("ok", True) else IX.icon_x)(c, BCX + 260, y, 1.0); c.restore()
        el(ti, t1, f, (BCX + 300, y - 30), (BCX, y))


def build_big(i, t0, t1, sc):
    ic = ico(sc.get("icon", "bulb"))
    tin = cue_t(i, sc, t0 + 0.15)
    el(tin, t1, lambda c, t, e: (ic(c, BCX, BCY - 50, 2.8), fit(c, sc.get("text", ""), BCX, BCY + 130, 48, "#1F2D44", 820)), (BCX + 150, BCY - 120), (BCX, BCY))
    if sc.get("sub"):
        ts = cue_t(i, {"cue": sc.get("sub_cue")}, tin + 0.8) if sc.get("sub_cue") else tin + 0.8
        el(ts, t1, lambda c, t, e: fit(c, sc["sub"], BCX, BCY + 210, 32, sc.get("sub_color", "#0A84FF"), 820, FONT_B), pivot=(BCX, BCY + 210))


def build_permission(i, t0, t1, sc):
    def box(c, t, e):
        r = rr(BCX - 360, Y0 - 50, 720, 410, 30); shadow_rrect(c, r, 12, 8, 0.3); c.drawRRect(r, P("#FFFFFF")); c.drawRRect(r, P("#0A84FF", 4))
        icon_lock(c, BCX - 290, Y0 + 10, 0.8); fit(c, sc.get("title", "Agent wants to:"), BCX - 240, Y0 + 12, 32, "#1F2D44", 540, FONT_XB, "l")
    el(t0, t1, box, (BCX + 300, Y0 - 40), (BCX, Y0 + 150))
    for k, it in enumerate(sc.get("items", [])):
        y = Y0 + 100 + k * 90
        ti = cue_t(i, it, t0 + 0.4 + k * 0.6)
        el(ti, t1, lambda c, t, e, it=it, y=y: IX.row(c, BCX, y, 600, it["text"], ico(it.get("icon")), 28, "#FFF1B8"), (BCX + 300, y - 20))
    ta = cue_t(i, {"cue": sc.get("allow_cue")}, t0 + 1.5)
    def allow(c, t, e):
        y = Y0 + 300; on = smooth((t - ta - 0.1) / 0.3)
        for k, (lab, col) in enumerate((("DENY", "#B0BEC5"), ("ALLOW", "#2ECC71"))):
            x = BCX - 130 + k * 260
            c.drawRRect(rr(x - 110, y - 34, 220, 68, 34), P(col, a=(0.35 + 0.65 * on) if lab == "ALLOW" else 0.6))
            text(c, lab, x, y, 28, "#1F2D44" if lab == "DENY" else "#FFFFFF")
    el(t0 + 0.3, t1, allow, None, (BCX, Y0 + 300))


def build_summary(i, t0, t1, sc):
    for k, it in enumerate(sc.get("rows", [])):
        y = Y0 + 50 + k * 112
        ti = cue_t(i, it, t0 + 0.2 + k * 0.8)
        el(ti, t1, lambda c, t, e, it=it, y=y: card(c, BCX, y, 760, 96, it["text"], 36,
                                                     (lambda c_, x, yy, kk, n=it.get("icon"): ico(n)(c_, x, yy, 0.85)) if ico(it.get("icon")) else None,
                                                     accent=it.get("color", "#0A84FF")), (BCX + 380, y - 40), (BCX, y))


def build_gallery(i, t0, t1, sc):
    items = sc.get("items", [])[:6]; n = len(items)
    if sc.get("title"):
        el(t0, t1, lambda c, t, e: IX.chip(c, BCX, Y0 - 20, sc["title"], sc.get("color", "#FF8C42"), None, 28), (BCX + 180, Y0 - 20))
    cols = 3 if n > 4 or n == 3 else max(1, n if n < 3 else 2)
    rows = (n + cols - 1) // cols
    cw = 280 if cols == 3 else 340; rh = 230 if rows > 1 else 300
    tints = ("#FFF1B8", "#DCEBFF", "#FFE0EC", "#DDF7E8", "#EFE3FF", "#FFE6D5")
    for k, it in enumerate(items):
        r_, c_ = divmod(k, cols); in_row = min(cols, n - r_ * cols)
        x = BCX + (c_ - (in_row - 1) / 2) * cw
        y = Y0 + 70 + (rh / 2 if rows > 1 else 150) + r_ * rh - (0 if rows > 1 else 0)
        ti = cue_t(i, it, t0 + 0.3 + k * 0.6)
        big = 1.55 if rows > 1 else 2.2
        def f(c, t, e, it=it, x=x, y=y, k=k, big=big):
            r = rr(x - cw / 2 + 14, y - rh / 2 + 10, cw - 28, rh - 20, 26); shadow_rrect(c, r, 6, 4, 0.18); c.drawRRect(r, P(tints[k % 6]))
            ic = ico(it.get("icon"))
            if ic: ic(c, x, y - 26 * big / 1.55, big)
            fit(c, it.get("label", ""), x, y + rh / 2 - 46, 30, "#1F2D44", cw - 50, FONT_XB)
        el(ti, t1, f, (x + cw / 2 - 30, y - rh / 2 + 30), (x, y))


def build_poem(i, t0, t1, sc):
    vl = sc.get("lines", [])[:4]
    def head_(c, t, e):
        r = rr(BX + 40, Y0 - 60, BW - 80, BH - 100, 30); c.drawRRect(r, P("#FFFBEA")); c.drawRRect(r, P("#FFC93C", 5))
        ic = ico(sc.get("icon"))
        if ic: ic(c, BX + 120, Y0 + 4, 1.0)
        fit(c, sc.get("title", ""), BCX + (30 if ic else 0), Y0 + 6, 38, "#8E44AD", 640, FONT_XB)
    el(t0, t1, head_, (BCX + 360, Y0 - 40), (BCX, BCY))
    cols = ("#E91E63", "#0A84FF", "#2E9E5B", "#FF8C42")
    for k, it in enumerate(vl):
        y = Y0 + 108 + k * 100
        ti = cue_t(i, it, t0 + 0.3 + k * 1.2)
        def f(c, t, e, it=it, y=y, k=k):
            ic = ico(it.get("icon"))
            if ic: ic(c, BX + 120, y, 0.85)
            fit(c, it.get("text", ""), BX + (170 if ic else 110), y, 40, cols[k % 4], BW - (260 if ic else 200), FONT_XB, "l")
        el(ti, t1, f, (BX + BW - 120, y - 30), (BCX, y))


BUILD = {"gallery": build_gallery, "poem": build_poem, "title": build_title, "chat": build_chat, "steps": build_steps, "compare": build_compare, "checklist": build_checklist,
         "big": build_big, "permission": build_permission, "summary": build_summary}
for k in range(len(scene_starts)):
    i, t0, t1 = scene_window(k)
    sc = ELINES[i]["board"]
    BUILD[sc["type"]](i, t0, t1, sc)

# follow pill + loop card on the last line
last = len(LN) - 1
_cta_w = [w for w in LN[last]["words"] if w[0].lower().startswith(("subscrib", "follow"))]
T_FOLLOW = _cta_w[0][1] if _cta_w else None
import cta
KIDS_CTA = True
if T_FOLLOW:
    for k_ in range(3):  # tap sounds (the card itself is drawn after the board, see below)
        el(T_FOLLOW + 0.9 + k_ * 1.0, T_FOLLOW + 1.0 + k_ * 1.0, lambda c, t, e: None)
LOOP = EP.get("loop_card")
if LOOP:
    tl = wt(last, LOOP.get("cue", "next"))
    def loopcard(c, t, e):
        c.drawRRect(rr(BX + 30, BY + 80, BW - 60, BH - 110, 26), P("#FFFFFF"))
        (ico(LOOP.get("left")) or IX.icon_bulb)(c, BCX - 250, BCY - 30, 2.0); (ico(LOOP.get("right")) or IX.icon_bulb)(c, BCX + 250, BCY - 20, 2.0)
        c.drawCircle(BCX, BCY, 60, P("#FFC93C")); text(c, "?", BCX, BCY, 70, "#1F2D44")
        fit(c, LOOP["text"], BCX, BCY + 170, 46, "#1F2D44", 820)
    el(tl, DUR + 1, loopcard, (BCX + 300, BCY - 100), (BCX, BCY))


def draw_board(c, t):
    K.draw_board_frame(c)
    for (t_in, t_out, fn, anchor, pivot) in ELEMS:
        e = appear(t, t_in, t_out)
        if not e: continue
        px, py = pivot or anchor or (BCX, BCY)
        scaled(c, px, py, e); fn(c, t, e); c.restore()
    c.restore()


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
CAMS = {"wide": (540, 960, 1.0, 1.05), "board": (540, 640, 1.08, 1.13)}
for n, c in CH.items():
    hy, z = HEADY[n]
    CAMS[n] = (c.x + (10 if c.x < 540 else -10 if c.x > 540 else 0), hy, z, z + 0.1)
PUNCH = [wt(i, l["punch"]) for i, l in enumerate(ELINES) if l.get("punch")]

import kids_fx
_bursts = [(e[0], (e[4] or e[3])[0], (e[4] or e[3])[1]) for e in ELEMS if e[0] > 0.3 and (e[4] or e[3]) and (T_FOLLOW is None or e[0] < T_FOLLOW - 0.1)]
_conf = sorted(set([round(p_, 2) for p_ in PUNCH] + ([T_FOLLOW + 0.95] if T_FOLLOW else [])))
FX = kids_fx.KidsFX(K, _bursts, _conf)
_top0fx = K.draw_top
K.draw_top = lambda c, t: (_top0fx(c, t), FX.draw(c, t))
_top1 = K.draw_top
K.draw_top = lambda c, t: (_top1(c, t), cta.end_card(c, t, T_FOLLOW, K, KIDS_CTA) if T_FOLLOW else None)
if not KIDS_CTA:
    T_REMIND = DUR * 0.42
    if T_FOLLOW is None or T_REMIND + 3.5 < T_FOLLOW:
        _top0 = K.draw_top
        K.draw_top = lambda c, t: (_top0(c, t), cta.reminder(c, t, T_REMIND, K))
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
