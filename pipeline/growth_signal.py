"""What already works on OUR channel, as a topic signal (owner, 2026-11-23: "growth brief -> topic picking"). Same file in both repos.

Reads the latest YouTube Analytics table the daily/radar workflows download into out/analytics/ (made by
youtube-analytics.yml -> analytics.py; one row per video: views, engaged views, average % viewed ...).
For every word in our Shorts' titles it scores how those Shorts did compared with the channel's other Shorts:
    performance = half "engaged views" rank + half "average % viewed" rank (0 = worst, 1 = best), centred on 0
    word score  = average performance of the Shorts whose title has the word, shrunk when only 1-2 Shorts have it
Then:
    boost("why do cats knead")  -> -0.5 .. +0.5 (0 = no evidence)   used by radar.py and trend_short.py to rank topics
    summary_md()                 -> a short "what works for us" section for the weekly topic report
Advisory only: it re-orders candidates, it never blocks one. No data (first weeks, no analytics token) = no effect.
"""
import glob, os, re

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
STOP = set("""a an the of to for in on and or is are do does did why how what when where who can you your we our it its with from by be
this that these those make makes made fun facts fact kids kid explained explain simply shorts short video science learn
ai vs into out up about will would should could has have had not no yes more most very just really part""".split())
MIN_SHORTS = 6  # below this the channel has too little data to learn from
# subject groups: a whole area can earn credit ("dogs bark" profits from cats/bees doing well = animals)
GROUPS = {
    "animals": "animal cat dog bee bird fish whale shark zebra giraffe elephant owl penguin snake spider frog butterfly caterpillar flamingo chameleon ant insect octopus dolphin tiger lion bear monkey horse cow duck puppy kitten pet",
    "space": "space moon sun star planet mars earth galaxy astronaut rocket comet eclipse orbit sky supermoon saturn jupiter",
    "body": "body heart blood brain bone muscle teeth tooth eye ear nose tongue skin hair sleep sneeze yawn hiccup blink goosebump shiver tummy stomach fingerprint",
    "weather": "rain rainbow cloud snow snowflake wind storm thunder lightning weather season winter summer autumn spring ice fog",
    "plants": "plant tree leaf leave flower seed soil grass fruit apple honey",
    "earth": "volcano earthquake ocean sea river wave rock mountain salt water",
    "everyday": "magnet mirror shadow bubble balloon soap popcorn onion metal straw echo airplane",
    "chatbots": "chatgpt gemini claude copilot chatbot prompt llm gpt chat",
    "privacy_safety": "privacy secret safe safety scam fake deepfake voice password upload data remember",
    "work_money": "job work money business office career",
    "images_video": "image picture photo video camera art",
    "phones_apps": "phone app apps android iphone camera",
}
_GROUP_OF = {w: g for g, ws in GROUPS.items() for w in ws.split()}

_CACHE = {}


def _words(t):
    w = set(re.findall(r"[a-z][a-z']{2,}", (t or "").lower()))
    w = {x.replace("'", "") for x in w}
    w |= {x[:-1] for x in w if x.endswith("s") and not x.endswith("ss") and len(x) > 3}  # plurals count as the singular too
    return w - STOP


def _ranks(vals):
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    r = [0.0] * len(vals)
    for pos, i in enumerate(order): r[i] = pos / max(1, len(vals) - 1)
    return r


def _latest_csv():
    files = [f for f in glob.glob(os.path.join(ROOT, "out", "analytics", "**", "*.csv"), recursive=True)]
    return max(files, key=os.path.getmtime) if files else None


def load():
    """{'n': shorts used, 'words': {word: (score, count, [example titles])}} or None when there's not enough data."""
    if "sig" in _CACHE: return _CACHE["sig"]
    sig = None
    try:
        import growth
        f = _latest_csv()
        if f:
            rows = growth.read_rows(__import__("pathlib").Path(f))
            shorts = []
            for r in rows:
                try:
                    if str(r.get("content_type", "")).lower() == "short" and float(r.get("views") or 0) > 0 and (r.get("title") or "").strip():
                        shorts.append((r["title"].strip(), float(r.get("engaged_views") or 0), float(r.get("average_view_percentage") or 0)))
                except (TypeError, ValueError):
                    continue
            if len(shorts) >= MIN_SHORTS:
                re_, rp = _ranks([s[1] for s in shorts]), _ranks([s[2] for s in shorts])
                perf = [0.5 * a + 0.5 * b - 0.5 for a, b in zip(re_, rp)]
                acc = {}
                for (title, _, _), p in zip(shorts, perf):
                    ws = _words(title)
                    for w in ws:
                        acc.setdefault(w, []).append((p, title))
                    for gname in {_GROUP_OF[w] for w in ws if w in _GROUP_OF}:
                        acc.setdefault("#" + gname, []).append((p, title))
                words = {w: (sum(p for p, _ in v) / len(v) * len(v) / (len(v) + 2), len(v), [t for _, t in sorted(v, reverse=True)[:2]])
                         for w, v in acc.items()}
                sig = {"n": len(shorts), "words": words, "file": os.path.relpath(f, ROOT)}
    except Exception as e:
        print("note: growth signal unavailable:", str(e)[:100])
    _CACHE["sig"] = sig
    return sig


def boost(text):
    """How well Shorts with these words did on our channel: -0.5 .. +0.5 (0 = no evidence)."""
    sig = load()
    if not sig: return 0.0
    ws = _words(text)
    keys = [w for w in ws] + ["#" + _GROUP_OF[w] for w in ws if w in _GROUP_OF]
    hits = [sig["words"][k][0] for k in dict.fromkeys(keys) if k in sig["words"] and sig["words"][k][1] >= 2]
    return round(sum(hits) / len(hits), 3) if hits else 0.0


def mark(b):
    return "★ works for us" if b >= 0.08 else ("▼ weak for us" if b <= -0.08 else "")


def summary_md():
    sig = load()
    if not sig:
        return ["", "## What works on our channel", "",
                f"_Not enough analytics yet (needs the daily YouTube analytics run and at least {MIN_SHORTS} Shorts with views). Topics are ranked by search demand only._"]
    W = sig["words"]
    ws = [(w.replace("#", "subject: ").replace("_", " "), s, n, ex) for w, (s, n, ex) in W.items()
          if n >= 2 and not (w.endswith("s") and w[:-1] in W and W[w[:-1]][1] == n)]  # 'cats' = 'cat': list it once
    good = sorted(ws, key=lambda x: -x[1])[:8]
    weak = sorted(ws, key=lambda x: x[1])[:5]
    md = ["", "## What works on our channel", "",
          f"From {sig['n']} of our Shorts (engaged views + average % viewed, latest analytics). Topics with these words are ranked higher (★); weak ones lower (▼). Advisory only.", "",
          "| Works well | Shorts | Best example | | Works less | Shorts |", "|---|---:|---|---|---|---:|"]
    for i in range(max(len(good), len(weak))):
        g = good[i] if i < len(good) and good[i][1] > 0.02 else None
        k = weak[i] if i < len(weak) and weak[i][1] < -0.02 else None
        if g or k:
            md.append(f"| {g[0] if g else ''} | {g[2] if g else ''} | {(g[3][0][:60].replace('|', '/') if g else '')} | | {k[0] if k else ''} | {k[2] if k else ''} |")
    return md
