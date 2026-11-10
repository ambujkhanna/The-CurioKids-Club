"""Turn a simple text script (scripts/*.txt) into an episode (custom/<id>/episode.json, + hi.json for Hindi).

    python pipeline/script2episode.py scripts/bees.txt            # check + convert (prints problems, exit 1 if any)
    python pipeline/script2episode.py scripts/bees.txt --check    # check only

The format is explained in scripts/README.md (and docs/SCRIPT_GUIDE.md). Shared by both channels: the channel is
detected from the repo (kids: MIA/LEO/DAD, AInation: DAD/TEEN).
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KIDS = os.path.exists(os.path.join(ROOT, "library")) or "curio" in ROOT.lower()
CH = {
    True: dict(cast={"MIA", "LEO", "DAD"}, host="MIA",
               cta="Ask a grown-up to subscribe to The Curio Kids Club for more fun, and share this with a friend!",
               cta_hi="और मज़ेदार बातों के लिए किसी बड़े से द क्यूरियो किड्स क्लब को सब्सक्राइब करने और दोस्तों के साथ शेयर करने को कहो!",
               tagline="The CurioKids Club: short, curious answers to kids' big questions. Subscribe: https://www.youtube.com/@CurioKidsClub",
               hashtags=["#KidsLearning", "#FunFacts", "#Shorts"]),
    False: dict(cast={"DAD", "TEEN"}, host="TEEN",
                cta="Subscribe to AI Nation Studio, and share this with a friend!",
                cta_hi=None,
                tagline="AInation Studio — AI, explained simply. Subscribe: https://www.youtube.com/@AI.nationstudio",
                hashtags=["#AI", "#AIExplained", "#Shorts"]),
}[KIDS]
TAGS_OK = ("laugh", "chuckle", "gasp", "sigh", "cough")
EMOJI = {  # keyword -> picture, for boards the script didn't specify
    "cat": "🐱", "dog": "🐶", "bee": "🐝", "honey": "🍯", "flower": "🌸", "tree": "🌳", "leaf": "🍃", "seed": "🌱", "plant": "🌱",
    "sun": "☀️", "moon": "🌙", "star": "⭐", "planet": "🪐", "earth": "🌍", "rain": "🌧️", "cloud": "☁️", "snow": "❄️",
    "rainbow": "🌈", "water": "💧", "ocean": "🌊", "sea": "🌊", "fish": "🐟", "whale": "🐋", "shark": "🦈", "bird": "🐦",
    "owl": "🦉", "penguin": "🐧", "elephant": "🐘", "lion": "🦁", "tiger": "🐯", "giraffe": "🦒", "zebra": "🦓", "monkey": "🐒",
    "frog": "🐸", "snake": "🐍", "turtle": "🐢", "dinosaur": "🦕", "butterfly": "🦋", "spider": "🕷️", "ant": "🐜",
    "heart": "❤️", "brain": "🧠", "eye": "👀", "eyes": "👀", "ear": "👂", "ears": "👂", "nose": "👃", "mouth": "👄",
    "tooth": "🦷", "teeth": "🦷", "bone": "🦴", "bones": "🦴", "muscle": "💪", "muscles": "💪", "hand": "✋", "sleep": "😴",
    "food": "🍎", "apple": "🍎", "banana": "🍌", "milk": "🥛", "pizza": "🍕", "cookie": "🍪", "ice": "🧊", "fire": "🔥",
    "volcano": "🌋", "mountain": "⛰️", "rocket": "🚀", "space": "🚀", "astronaut": "🚀", "car": "🚗", "train": "🚂",
    "plane": "✈️", "airplane": "✈️", "boat": "⛵", "ship": "🚢", "bike": "🚲", "music": "🎵", "book": "📚", "school": "🏫",
    "clock": "⏰", "time": "⏰", "light": "💡", "idea": "💡", "magnet": "🧲", "science": "🔬", "germ": "🦠", "germs": "🦠",
    "soap": "🧼", "robot": "🤖", "ai": "🤖", "computer": "💻", "phone": "📱", "chat": "💬", "chatbot": "💬", "email": "📧",
    "money": "💰", "lock": "🔒", "password": "🔑", "data": "📊", "picture": "🖼️", "image": "🖼️", "video": "🎬",
    "game": "🎮", "ball": "⚽", "gift": "🎁", "party": "🎉", "smile": "😊", "happy": "😊", "sad": "😢", "laugh": "😂",
    "joke": "😂", "question": "❓", "search": "🔍", "map": "🗺️", "world": "🌍", "home": "🏠", "family": "🏠",
}


def parse(text):
    """-> (headers dict, lines list of dict(who, text, hint, hi, ln)), problems list"""
    head, lines, probs, body = {}, [], [], False
    for n, raw in enumerate(text.splitlines(), 1):
        s = raw.strip()
        if not s or s.startswith("#"): continue
        if s.startswith("---"): body = True; continue
        m = re.match(r"^([A-Za-z_ ]+?)\s*:\s*(.*)$", s)
        if not m:
            probs.append(f"line {n}: not understood - expected 'NAME: text' (e.g. 'MIA: Hello!'): {s[:60]}"); continue
        key, val = m.group(1).strip().upper().replace(" ", "_"), m.group(2).strip()
        if not body and key in ("TITLE", "COVER", "DESCRIPTION", "HASHTAGS", "TAGS", "TITLE_BOARD", "TITLE_HI", "DESCRIPTION_HI"):
            head[key] = val; continue
        body = True
        if key == "HI":
            if not lines: probs.append(f"line {n}: 'HI:' must come right after the English line it translates"); continue
            if lines[-1]["hi"]: probs.append(f"line {n}: two 'HI:' lines for one dialogue line"); continue
            lines[-1]["hi"] = val; continue
        if key not in CH["cast"]:
            probs.append(f"line {n}: speaker '{key}' is not a character of this channel (use {', '.join(sorted(CH['cast']))})"); continue
        txt, hint = (val.split("|", 1) + [""])[:2]
        lines.append(dict(who=key, text=txt.strip(), hint=hint.strip(), hi="", ln=n))
    return head, lines, probs


def icon_of(s):
    m = re.match(r"^(img:\S+|[^\w\s\"'(),.!?;:-]+)\s*(.*)$", s.strip())
    return (m.group(1), m.group(2).strip()) if m else (None, s.strip())


def auto_icon(text):
    for w in re.findall(r"[a-z]+", text.lower()):
        if w in EMOJI: return EMOJI[w], w
        if w.endswith("s") and w[:-1] in EMOJI: return EMOJI[w[:-1]], w
    return None, None


def cue_for(hint_text, line_text):
    words = [w.lower().strip(".,!?'\"…;:") for w in line_text.split()]
    for h in re.findall(r"[A-Za-z']{3,}", hint_text):
        if any(w.startswith(h.lower()) for w in words): return h.lower()
    return None


def build(path):
    head, lines, probs = parse(open(path, encoding="utf-8").read())
    title = head.get("TITLE", "")
    if not title: probs.append("TITLE: is missing (first line, e.g. 'TITLE: How Do Bees Make Honey? 🐝')")
    elif len(title) > 70: probs.append(f"TITLE is {len(title)} characters - keep it to 70")
    if not lines: probs.append("no dialogue lines found (after '---', lines like 'LEO: ...')")
    if probs: return None, None, probs
    cast = list(dict.fromkeys(l["who"] for l in lines))
    if len(cast) > 2: probs.append(f"use 1 or 2 characters per video (found {', '.join(cast)})")
    # call-to-action: added automatically if the last line has none
    if not re.search(r"subscrib|follow", lines[-1]["text"], re.I):
        who = CH["host"] if CH["host"] in cast else cast[-1]
        lines.append(dict(who=who, text=CH["cta"], hint="", hi=CH["cta_hi"] or "", ln=0, auto=True))
    if not 9 <= len(lines) <= 16:
        probs.append(f"{len(lines)} dialogue lines (incl. the Subscribe line) - use 9 to 16 (best 11-14)")
    use_hi = any(l["hi"] for l in lines if not l.get("auto"))
    for l in lines:
        t = l["text"]; where = f"line {l['ln']}" if l["ln"] else "Subscribe line"
        if not t: probs.append(f"{where}: empty text")
        if len(t) > 230: probs.append(f"{where}: {len(t)} characters - split it into two lines (max 230)")
        bad = [x for x in re.findall(r"\[([^\]]*)\]", t) if x.lower() not in TAGS_OK]
        if bad: probs.append(f"{where}: unknown sound tag [{bad[0]}] - use [laugh] [chuckle] [gasp] [sigh] [cough]")
        if l["hint"]:
            ic, ht = icon_of(l["hint"].split(";")[0])
            if not ic: probs.append(f"{where}: picture hint must start with an emoji, e.g. '| 🐝 Busy bees'")
            if len(ht) > 32: probs.append(f"{where}: board text '{ht[:20]}…' is {len(ht)} characters - max 32 (about 5 words)")
        if use_hi and not l["hi"]: probs.append(f"{where}: Hindi line missing - add 'HI: ...' after it (all lines need one, or none)")
    if use_hi and not KIDS: probs.append("Hindi (HI:) lines are only supported on the kids channel")
    if use_hi and not head.get("TITLE_HI"): probs.append("TITLE_HI: is missing (needed for the Hindi version)")
    words = sum(len(re.sub(r"\[[^\]]*\]", "", l["text"]).split()) for l in lines)
    est = words / 2.6 + len(lines) * 0.75 + 1.5
    if est > 170: probs.append(f"too long: about {words} words ≈ {est:.0f} s - keep under ~180 words (Shorts max 180 s)")
    if est < 22: probs.append(f"too short: about {words} words ≈ {est:.0f} s - write at least ~50 words")
    if probs: return None, None, probs
    # ---------------------------------------------------------------- episode
    q = re.sub(r"\s*(fun facts for kids|explained simply)\s*$", "", re.sub(r"[^\w\s?!',.:-]", "", title), flags=re.I).strip(" |-")
    if "?" in q: q = q[:q.index("?") + 1]  # the board shows just the question
    q = re.sub(r"\s{2,}", " ", q)
    eps = []; last_board = -9
    for i, l in enumerate(lines):
        e = {"who": l["who"], "text": l["text"]}
        if l["hint"] or i == 0:
            if l["hint"]:
                main, _, sub = l["hint"].partition(";"); ic, ht = icon_of(main)
            else:
                ic, ht, sub = None, q, ""
            if i == 0 and head.get("TITLE_BOARD") and "->" in head["TITLE_BOARD"]:
                a, b = [icon_of(x) for x in head["TITLE_BOARD"].split("->", 1)]
                e["board"] = {"type": "title", "left": {"icon": a[0] or "❓", "label": a[1].upper()[:12]},
                              "right": {"icon": b[0] or "💡", "label": b[1].upper()[:12]}, "subtitle": q[:40], "mid": "→"}
            else:
                ic = ic or auto_icon(l["text"] + " " + title)[0] or "❓"
                e["board"] = {"type": "big", "icon": ic, "text": ht or q}
                c = cue_for(ht, l["text"]) if ht else None
                if c: e["board"]["cue"] = c
                if sub.strip():
                    e["board"]["sub"] = sub.strip()[:32]; c2 = cue_for(sub, l["text"])
                    if c2: e["board"]["sub_cue"] = c2
            last_board = i
        elif i - last_board >= 3 and not l.get("auto"):  # keep the board lively: a picture for a keyword in this line
            ic, w = auto_icon(l["text"])
            if ic:
                e["board"] = {"type": "big", "icon": ic, "text": w.capitalize() + "!", "cue": w}; last_board = i
        eps.append(e)
    sid = "s-" + re.sub(r"[^a-z0-9]+", "-", os.path.splitext(os.path.basename(path))[0].lower()).strip("-")[:40]
    first_answer = next((l["text"] for l in lines[1:] if l["who"] != lines[0]["who"]), lines[0]["text"])
    tags = head.get("HASHTAGS", "").split() or [f"#{w.capitalize()}" for w in re.findall(r"[A-Za-z]{4,}", q)[:2]]
    ep = {"id": sid, "slug": sid[2:], "status": "ready", "source": os.path.relpath(path, ROOT), "title": title,
          "cover_text": head.get("COVER") or " ".join(re.findall(r"[A-Za-z']+", q)[-2:]).upper() + "?",
          "description": (head.get("DESCRIPTION") or first_answer) + "\n\n" + CH["tagline"],
          "hashtags": list(dict.fromkeys([h if h.startswith("#") else "#" + h for h in tags] + CH["hashtags"]))[:8],
          "tags": [t.strip() for t in head.get("TAGS", "").split(",") if t.strip()] or [q.lower()],
          "cast": cast, "lines": eps}
    hi = None
    if use_hi:
        hi = {"title_hi": head["TITLE_HI"], "description_hi": head.get("DESCRIPTION_HI") or lines[1]["hi"],
              "lines": [l["hi"] for l in lines]}
    return ep, hi, []


def convert(path, out_root=None):
    """Write custom/<id>/episode.json (+ hi.json). Returns (episode file, problems)."""
    ep, hi, probs = build(path)
    if probs: return None, probs
    d = os.path.join(out_root or os.path.join(ROOT, "custom"), ep["id"]); os.makedirs(d, exist_ok=True)
    f = os.path.join(d, "episode.json")
    json.dump(ep, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    hp = os.path.join(d, "hi.json")
    if hi: json.dump(hi, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    elif os.path.exists(hp): os.remove(hp)
    sys.path.insert(0, os.path.join(ROOT, "pipeline"))
    from validate_episode import check
    errs = check(f)
    if hi:
        from validate_episode import check_hi
        errs += check_hi(f)
    return f, ["episode check: " + e for e in errs]


if __name__ == "__main__":
    p = sys.argv[1]
    if "--check" in sys.argv:
        _, _, probs = build(p)
    else:
        f, probs = convert(p)
        if not probs: print("OK ->", os.path.relpath(f, ROOT))
    for x in probs: print("PROBLEM:", x)
    sys.exit(1 if probs else 0)
