"""Validate a Curio Kids Club episode JSON: schema, cast, scene types, icons, and that every cue word is in its line.

    python pipeline/validate_episode.py episodes/*/episode.json
"""
import json, sys

TYPES = {"title", "big", "steps", "compare", "checklist", "summary", "poem", "gallery"}
CAST = {"MIA", "LEO", "DAD"}
LEGACY_ICONS = {"chat", "robot", "check", "sun", "train", "doc", "lock", "target", "search", "calendar", "mail", "suitcase",
                "warn", "x", "user", "bulb", "shield", "coin", "eye", "book", "globe", "brain", "phone"}
LIMITS = {"steps": 5, "compare": 4, "checklist": 4, "summary": 4, "poem": 4, "gallery": 6}


def cues(sc):
    out = [sc.get("cue"), sc.get("sub_cue")]
    for key in ("items", "rows", "lines"):
        out += [it.get("cue") for it in sc.get(key, []) if isinstance(it, dict)]
    for side in ("left", "right"):
        if isinstance(sc.get(side), dict):
            out += [it.get("cue") for it in sc[side].get("items", [])]
    return [c for c in out if c]


def icons(sc):
    out = [sc.get("icon")]
    for key in ("items", "rows", "lines"):
        out += [it.get("icon") for it in sc.get(key, []) if isinstance(it, dict)]
    for side in ("left", "right"):
        if isinstance(sc.get(side), dict):
            out.append(sc[side].get("icon"))
            out += [it.get("icon") for it in sc[side].get("items", [])]
    return [i for i in out if i]


def bad_icon(i):
    if i in LEGACY_ICONS: return False
    return i.isascii() or "\u200d" in i or len(i.replace("\ufe0f", "")) > 2  # one plain emoji; no joined (ZWJ) sequences


def check(path):
    ep = json.load(open(path, encoding="utf-8")); errs = []
    for k in ("id", "title", "description", "hashtags", "lines", "cast"):
        if not ep.get(k): errs.append(f"missing {k}")
    if errs: return errs
    if len(ep["title"]) > 70: errs.append("title > 70 chars")
    cast = ep["cast"]
    if not (1 <= len(cast) <= 2) or any(c not in CAST for c in cast) or len(set(cast)) != len(cast):
        errs.append(f"cast must be 1-2 of {sorted(CAST)}")
    if not 9 <= len(ep["lines"]) <= 16: errs.append(f"{len(ep['lines'])} lines (aim for 11-14)")
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
            for ic in icons(sc):
                if bad_icon(ic): errs.append(f"line {i}: icon '{ic}' is not an emoji or known icon")
        for c in (cues(sc) if sc else []) + ([l["punch"]] if l.get("punch") else []):
            if not any(w.startswith(c.lower()) for w in words): errs.append(f"line {i}: cue '{c}' not in text")
    last = ep["lines"][-1]["text"].lower()
    if "follow" not in last: errs.append("last line has no Follow call-to-action")
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
