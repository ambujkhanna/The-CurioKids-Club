"""Validate a The CurioKids Club episode JSON: schema, cast, scene types, icons, and that every cue word is in its line.

    python pipeline/validate_episode.py episodes/*/episode.json
"""
import json, sys

TYPES = {"title", "big", "steps", "compare", "checklist", "summary", "poem", "gallery", "body", "cycle", "journey", "orbit"}
CAST = {"MIA", "LEO", "DAD"}
LEGACY_ICONS = {"chat", "robot", "check", "sun", "train", "doc", "lock", "target", "search", "calendar", "mail", "suitcase",
                "warn", "x", "user", "bulb", "shield", "coin", "eye", "book", "globe", "brain", "phone"}
LIMITS = {"steps": 5, "compare": 4, "checklist": 4, "summary": 4, "poem": 4, "gallery": 6, "cycle": 6, "journey": 5, "orbit": 4}


def cues(sc):
    out = [sc.get("cue"), sc.get("sub_cue")]
    for key in ("items", "rows", "lines", "labels"):
        out += [it.get("cue") for it in sc.get(key, []) if isinstance(it, dict)]
    for side in ("left", "right"):
        if isinstance(sc.get(side), dict):
            out += [it.get("cue") for it in sc[side].get("items", [])]
    return [c for c in out if c]


def icons(sc):
    out = [sc.get("icon"), sc.get("center"), sc.get("traveler")]
    for key in ("items", "rows", "lines"):
        out += [it.get("icon") for it in sc.get(key, []) if isinstance(it, dict)]
    for side in ("left", "right"):
        if isinstance(sc.get(side), dict):
            out.append(sc[side].get("icon"))
            out += [it.get("icon") for it in sc[side].get("items", [])]
    return [i for i in out if i]


def bad_icon(i):
    if i in LEGACY_ICONS: return False
    if i.startswith("img:"):  # real illustration: must be in assets/IMAGE_INDEX.txt
        return i not in _INDEX()
    return i.isascii() or "\u200d" in i or len(i.replace("\ufe0f", "")) > 2  # one plain emoji; no joined (ZWJ) sequences


_IDX = None


def _INDEX():
    global _IDX
    if _IDX is None:
        import os
        f = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "IMAGE_INDEX.txt")
        _IDX = {l.split()[0] for l in open(f, encoding="utf-8") if l.strip()} if os.path.exists(f) else set()
    return _IDX


BODY_PARTS = {"brain", "head", "eyes", "ears", "nose", "mouth", "lungs", "heart", "stomach", "arm", "hand", "leg", "foot", "muscles", "skin", "bones"}


def check(path):
    ep = json.load(open(path, encoding="utf-8")); errs = []
    for k in ("id", "title", "description", "hashtags", "lines", "cast"):
        if not ep.get(k): errs.append(f"missing {k}")
    if errs: return errs
    if len(ep["title"]) > 70: errs.append("title > 70 chars")
    cast = ep["cast"]
    if not (1 <= len(cast) <= 2) or any(c not in CAST for c in cast) or len(set(cast)) != len(cast):
        errs.append(f"cast must be 1-2 of {sorted(CAST)}")
    long_ = "/long/" in "/" + path.replace("\\", "/")
    lo, hi = (25, 120) if long_ else (9, 16)
    if not lo <= len(ep["lines"]) <= hi: errs.append(f"{len(ep['lines'])} lines (aim for {'40-80' if long_ else '11-14'})")
    if long_ and sum(1 for l in ep["lines"] if l.get("chapter")) < 3: errs.append("long video needs at least 3 lines with a \"chapter\" title")
    if not ep["lines"][0].get("board"): errs.append("line 0 must start a board scene")
    for i, l in enumerate(ep["lines"]):
        if l.get("who") not in cast: errs.append(f"line {i}: who '{l.get('who')}' is not in cast {cast}")
        if len(l.get("text", "")) > 230: errs.append(f"line {i}: text too long (> 230 chars)")
        words = [w.lower().strip(".,!?'\"…;:") for w in l["text"].split()]
        sc = l.get("board")
        if sc:
            if sc.get("type") not in TYPES: errs.append(f"line {i}: unknown board type {sc.get('type')}")
            for key, n in LIMITS.items():
                if sc.get("type") == key:
                    for fld in ("items", "rows", "lines"):
                        if len(sc.get(fld, [])) > n: errs.append(f"line {i}: {key} has more than {n} {fld}")
            if sc.get("type") == "body":
                for part in sc.get("show", []) + [lb.get("at") for lb in sc.get("labels", [])]:
                    if part not in BODY_PARTS: errs.append(f"line {i}: body part '{part}' unknown (use {sorted(BODY_PARTS)})")
                if sc.get("flow") not in (None, "blood", "nerves", "air", "food"): errs.append(f"line {i}: flow must be blood, nerves, air or food")
            for ic in icons(sc):
                if bad_icon(ic): errs.append(f"line {i}: icon '{ic}' is not an emoji or known icon")
        for c in (cues(sc) if sc else []) + ([l["punch"]] if l.get("punch") else []):
            if not any(w.startswith(c.lower()) for w in words): errs.append(f"line {i}: cue '{c}' not in text")
    last = ep["lines"][-1]["text"].lower()
    if "follow" not in last and "subscribe" not in last: errs.append("last line has no Subscribe/Follow call-to-action")
    lc = ep.get("loop_card")
    if lc:
        if lc.get("cue", "next") not in last: errs.append("loop cue not in last line")
        for k in ("left", "right"):
            if lc.get(k) and bad_icon(lc[k]): errs.append(f"loop_card {k} icon is not an emoji")
    return errs


if __name__ == "__main__":
    bad = 0
    for p in sys.argv[1:]:
        e = check(p); bad += bool(e)
        print(("OK   " if not e else "FAIL ") + p + ("" if not e else "\n  - " + "\n  - ".join(e)))
    sys.exit(1 if bad else 0)
