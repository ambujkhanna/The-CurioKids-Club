"""Automatic trend Short (owner, 2026-11-22): one extra Short a day about what people search for right now. Same file in both repos.

    python pipeline/trend_short.py            # pick topic -> facts -> script -> checks -> render + upload (daily.py --script)
    python pipeline/trend_short.py --dry-run  # everything, but daily.py renders without uploading
    python pipeline/trend_short.py --script-only   # stop after writing + checking the script (local tests)

1. Topic: the FIRST search that fits the channel and isn't covered yet (owner's rule), in this order:
   today's Google Trends -> YouTube's trending charts -> the radar's most-searched YouTube questions.
2. Facts: Wikipedia's intro for the topic (Simple English Wikipedia for kids). The script may only use these facts.
3. Script: a free open model on the runner (Ollama, default qwen2.5:7b, Apache 2.0) writes it in the scripts/README.md format;
   script2episode + validate_episode check it (fixes fed back, 3 tries).
4. Checks: a second model pass compares the script with the facts; kid-safety block list. A topic that fails is dropped
   and the next topic is tried (max 4). Nothing is uploaded if all fail.
5. Video: daily.py --script (own queue in custom/, separate from the daily episodes), publish window PUBLISH_WINDOW (the
   workflow sets 12:00-14:00 IST), the record keeps "trend_topic" so a topic is never made twice.
Repo variables: TREND_SHORTS=on|off, TREND_MODEL (default qwen2.5:7b). No paid API anywhere.
"""
import datetime as dt, json, os, re, subprocess, sys, tempfile, urllib.error, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import radar, script2episode

KIDS = radar.KIDS
MODEL = os.environ.get("TREND_MODEL", "qwen2.5:7b")
OLLAMA = os.environ.get("OLLAMA_HOST", "127.0.0.1:11434")
UA = {"User-Agent": "studio-video-pipeline/1.0 (educational shorts; facts lookup)"}
OUT = os.path.join(ROOT, "out")

CHANNEL = ("The CurioKids Club: friendly science Shorts for kids aged 4-9. LEO (a curious little boy) asks short questions, "
           "his big sister MIA explains simply and warmly, with small jokes. Words a 6-year-old understands.") if KIDS else (
           "AInation Studio: AI explained simply for everyday adults. DAD asks practical questions, TEEN explains clearly, "
           "with everyday examples and one useful tip. No hype, no fear.")
ASK, EXPLAIN = ("LEO", "MIA") if KIDS else ("DAD", "TEEN")
EXAMPLE = os.path.join(ROOT, "scripts", "how-bees-make-honey.txt" if KIDS else "ai-concepts-01-tokens.txt")
CLOSER = ("LEO: What should we explore next? Ask a grown-up to drop a topic in the comment section!" if KIDS else
          "DAD: What should we explain next? Drop a topic in the comment section!")


# ------------------------------------------------------------------ 1. topic
def used_topics():
    p = os.path.join(ROOT, "custom", "state.json")
    try:
        recs = json.load(open(p, encoding="utf-8")).get("episodes", {})
    except Exception:
        recs = {}
    return {str(r.get("trend_topic", "")).lower() for r in recs.values() if isinstance(r, dict) and r.get("trend_topic")} | \
           {radar._clean(r.get("title", "")) for r in recs.values() if isinstance(r, dict)}


def candidates(limit=8):
    """[(source, question, subject)] in the owner's order: first relevant search first."""
    titles = radar.covered_titles() + list(used_topics())
    out, seen = [], set()
    def add(src, q, subj):
        q = radar._clean(q)
        if not q or q in seen or radar._covered(q, titles) or set(q.split()) & radar.BLOCK: return
        seen.add(q); out.append((src, q, subj))
    for g, term, traffic, head, fits in radar.google_trends():
        if fits:
            ang = radar.trend_angles(term)
            add(f"Google Trends {g} ({traffic})", ang[0] if ang else f"what is {term}", term)
    yt = radar.youtube()
    for g, cat, t, views, short, fits in (radar.youtube_trending(yt) if yt else []):
        if fits: add(f"YouTube trending {g}/{cat}", re.sub(r"#\w+", "", t), re.sub(r"#\w+", "", t))
    if len(out) < limit:  # evergreen: what people type into YouTube search most (the radar's demand list)
        for s, v in sorted(radar.demand().items(), key=lambda x: -x[1]):
            add(f"YouTube search (demand {v:.0f})", s, s)
            if len(out) >= limit: break
    return out


# ------------------------------------------------------------------ 2. facts
def _get(url):
    import time
    for attempt in range(4):  # Wikipedia asks bots to slow down (429): wait and retry
        try:
            time.sleep(0.4)
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == 3: raise
            time.sleep(5 * (attempt + 1))


def _stem(w):
    return re.sub(r"(ing|es|s|ed)$", "", w) if len(w) > 4 else w


def facts(subject):
    """Facts for the topic from Wikipedia (Simple English first for kids). The article must mention the topic's key words;
    from long articles only the intro + the paragraphs about the topic are used. Returns (source, text) or (None, '')."""
    qw = {"why", "how", "what", "when", "where", "who", "is", "are", "do", "does", "did", "can", "the", "a", "an", "we", "you",
          "our", "your", "it", "they", "their", "make", "makes", "happen", "work", "works", "for", "kids", "of", "to", "in", "on", "so"}
    keys = [w for w in re.findall(r"[a-z0-9]+", subject.lower()) if w not in qw]
    if not keys: return None, ""
    stems = {_stem(k) for k in keys}
    query = " ".join(keys)
    for wiki in (["simple", "en"] if KIDS else ["en"]):
        try:
            s_ = _get(f"https://{wiki}.wikipedia.org/w/api.php?" + urllib.parse.urlencode(
                {"action": "query", "list": "search", "srsearch": query, "srlimit": 5, "format": "json"}))
            for hit in s_.get("query", {}).get("search", []):
                q = _get(f"https://{wiki}.wikipedia.org/w/api.php?" + urllib.parse.urlencode(
                    {"action": "query", "prop": "extracts", "explaintext": 1, "titles": hit["title"], "format": "json", "redirects": 1}))
                for pg in q.get("query", {}).get("pages", {}).values():
                    full = (pg.get("extract") or "").strip()
                    if len(full) < 300 or "may refer to" in full[:300]: continue
                    paras = [x.strip() for x in full.split("\n") if len(x.strip()) > 60 and not x.startswith("==")]
                    hits = lambda t: sum(1 for st in stems if st in t.lower())
                    if hits(pg["title"] + " " + full) < len(stems) or not hits(pg["title"]):  # all key words in the article,
                        continue                                                               # and the title names the subject
                    pick = paras[:2] + [x for x in paras[2:] if hits(x)]
                    text = "\n".join(pick)[:3500]
                    if hits(text) < len(stems): continue
                    return f"{pg['title']} ({wiki}.wikipedia.org)", text
        except Exception as e:
            print("note: Wikipedia lookup failed:", str(e)[:80])
    return None, ""


# ------------------------------------------------------------------ 3. script
def chat(messages, temperature=0.4):
    body = json.dumps({"model": MODEL, "messages": messages, "stream": False,
                       "options": {"temperature": temperature, "num_ctx": 8192}}).encode()
    req = urllib.request.Request(f"http://{OLLAMA}/api/chat", data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as r:
        return json.loads(r.read())["message"]["content"]


def rules():
    kid = KIDS
    return f"""You write ONE script for a YouTube Short. Channel: {CHANNEL}
Write ONLY the script, in exactly this plain-text format (no markdown, no code fences, no notes):

TITLE: <the question as a title, max 60 characters, ends with one emoji{', then " Fun Facts for Kids"' if KIDS else ''}>
COVER: <1-3 BIG words for the thumbnail, capitals>
HASHTAGS: <3 hashtags, space-separated>
TITLE_BOARD: <emoji Word -> emoji Word>
---
{ASK}: <the opening question>
{EXPLAIN}: <answer> | <one emoji> <up to 5 words for the screen>
...

Rules:
- 10 to 12 dialogue lines in total (count them!), about 110-160 words. Only the speakers {ASK} and {EXPLAIN}, taking turns.
- Line 1: {ASK} asks the question. Every line max 200 characters, short sentences.
- On about every second {EXPLAIN} line, add "| emoji Short text" at the end (one simple, everyday emoji that shows the thing itself, max 5 words, max 30 characters; never 🌿 unless the line is about leaves or herbs).
- The FIRST answer gives the MAIN reason from the FACTS (the most interesting real fact), not a vague feeling.
- Then 2-3 more real facts from the FACTS, one per answer, each explained with one simple comparison {"a child knows" if KIDS else "from everyday life"}.
- No technical terms unless you explain them in plain words. Every answer must teach something new.
- Use ONLY facts from the FACTS section. No numbers, dates or names that are not in FACTS. If unsure, leave it out.
- {"Kid-safe and gentle: nothing scary, no brands, no violence." if KIDS else "Practical and honest: no hype, no brands praised, no financial or medical advice."}
- The second-to-last line {ASK} sums up the main idea in one sentence.
- The LAST line is exactly: {CLOSER}
Here is an example of a finished script in the right format and style:

{open(EXAMPLE, encoding="utf-8").read() if os.path.exists(EXAMPLE) else ''}"""


def clean_script(t):
    t = re.sub(r"```[a-z]*", "", t).replace("**", "").strip()
    keep = [l.rstrip() for l in t.split("\n") if re.match(r"^(TITLE|COVER|HASHTAGS|TITLE_BOARD|DESCRIPTION|TAGS|BACKDROP):|^---$|^(LEO|MIA|DAD|TEEN):", l.strip())]
    return "\n".join(keep) + "\n"


def trim(text, max_lines=13):
    """Small models can't count: drop whole question+answer pairs from the middle (pairs without a screen picture first),
    keeping the opening question + answer and the last two lines (summary + comment line). Subscribe is added later."""
    head, _, body = text.partition("---\n")
    lines = [l for l in body.split("\n") if l.strip() and not re.search(r"(?i)explore next|explain next|comment section|subscribe", l)]
    lines.append(CLOSER)  # always the channel's own closing line (models often forget it)
    while len(lines) > max_lines:
        mid = [i for i in range(2, len(lines) - 3) if lines[i].startswith(ASK + ":") and lines[i + 1].startswith(EXPLAIN + ":")]
        if not mid: break
        mid.sort(key=lambda i: ("|" in lines[i + 1], -i))  # no picture first, later pairs first
        i = mid[0]; del lines[i:i + 2]
    return head + "---\n" + "\n".join(lines) + "\n"


def fix_pictures(text):
    """The model often picks a near-miss emoji (🌿 herb for 'grass'). If a board's words name a thing we have a picture
    for (script2episode.EMOJI: grass, nest, milk, paw...), that picture wins."""
    out = []
    for l in text.split("\n"):
        m = re.match(r"^(.*\|\s*)(\S+)(\s+)(.+)$", l)
        if m and ":" in l.split("|")[0]:
            pic, _ = script2episode.auto_icon(m.group(4))
            if pic and pic != m.group(2): l = m.group(1) + pic + m.group(3) + m.group(4)
        out.append(l)
    return "\n".join(out)


def problems_of(text):
    """script2episode's own checks (the same as for the owner's scripts) + kid-safety words."""
    d = tempfile.mkdtemp(); p = os.path.join(d, "trend.txt"); open(p, "w", encoding="utf-8").write(text)
    try:
        _, _, probs = script2episode.build(p)
    except Exception as e:
        probs = [f"could not read the script: {e}"]
    bad = set(re.findall(r"[a-z']+", text.lower())) & radar.BLOCK
    if bad: probs = list(probs) + [f"remove these words (not for this channel): {', '.join(sorted(bad))}"]
    return list(probs)


def write_script(question, fact_title, fact_text):
    msgs = [{"role": "system", "content": rules()},
            {"role": "user", "content": f"TOPIC: {question}\n\nFACTS (from {fact_title}):\n{fact_text}\n\nWrite the script now."}]
    for attempt in range(3):
        text = fix_pictures(trim(clean_script(chat(msgs))))
        probs = problems_of(text)
        if not probs: return text, []
        print(f"  script try {attempt + 1}: {len(probs)} problem(s): {probs[:3]}")
        msgs += [{"role": "assistant", "content": text},
                 {"role": "user", "content": "Fix these problems and write the whole script again, same format:\n- " + "\n- ".join(probs[:8])}]
    return text, probs


# ------------------------------------------------------------------ 4. fact check
_NUMW = {"one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
         "hundred": "100", "thousand": "1000", "million": "million", "billion": "billion"}


def fact_check(text, fact_text):
    """Two checks on each explaining line (the opening question, summary and closing lines are not facts):
    1. in code: every number must appear in the facts (catches '13%' when the source says 14%);
    2. the model: does the source CONTRADICT the sentence? (small models judge contradictions far better than proof).
    Returns the problem lines ([] = all fine)."""
    body = text.partition("---\n")[2].split("\n")
    claims = [l.split(":", 1)[1].split("|")[0].strip() for l in body[:-2] if l.startswith(EXPLAIN + ":")]
    src = fact_text.lower().replace(",", "")
    bad = []
    for c in claims:
        nums = re.findall(r"\d+(?:\.\d+)?", c.replace(",", "")) + [v for k, v in _NUMW.items() if re.search(rf"\b{k}\b", c.lower()) and v.isdigit() and int(v) > 2]
        missing = [n for n in nums if n not in src and not (n in _NUMW.values() and any(k in src for k, v in _NUMW.items() if v == n))]
        if missing:
            bad.append(f"{c} (number {', '.join(missing)} is not in the source)"); continue
        ans = chat([{"role": "system", "content": "You check educational videos against a source text."},
                    {"role": "user", "content": f"SOURCE:\n{fact_text}\n\nSENTENCE: {c}\n\n"
                     "Does a sentence in the SOURCE clearly contradict the SENTENCE? Simple explanations, comparisons, jokes and "
                     "feelings are fine. If yes, answer: YES: \"<copy the contradicting SOURCE sentence word for word>\" - <why>. "
                     "If not, answer: NO."}], temperature=0.0).strip()
        if ans.upper().startswith("YES"):
            m = re.search(r'"([^"]{15,})"', ans)
            quote = set(re.findall(r"[a-z0-9]+", (m.group(1) if m else "").lower()))
            real = quote and max((len(quote & set(re.findall(r"[a-z0-9]+", sent.lower()))) / len(quote)
                                  for sent in re.split(r"(?<=[.!?])\s+", fact_text)), default=0) >= 0.7
            if real:  # only a contradiction backed by a real source sentence counts (small models invent objections)
                bad.append(f"{c} (source says: {m.group(1)[:160]})")
    return bad


def make_script(question, subject):
    ft, fx = facts(subject)
    if not fx:
        return None, f"no Wikipedia facts found for '{subject}'"
    print(f"  facts: {ft} ({len(fx)} chars)")
    text, probs = write_script(question, ft, fx)
    if probs:
        return None, "script still had problems after 3 tries: " + "; ".join(probs[:3])
    issues = fact_check(text, fx)
    for rnd in range(2):  # up to two rewrites with the checker's reasons, then give up on this topic
        if not issues: break
        print(f"  fact check {rnd + 1}:", issues)
        msgs = [{"role": "system", "content": rules()},
                {"role": "user", "content": f"TOPIC: {question}\n\nFACTS (from {ft}):\n{fx}\n\nHere is a script:\n{text}\n"
                 "A fact-checker found these problems. Rewrite the whole script without them (same format):\n- " + "\n- ".join(issues)}]
        text = fix_pictures(trim(clean_script(chat(msgs)))); probs = problems_of(text)
        issues = fact_check(text, fx) if not probs else ["format problems after the rewrite: " + "; ".join(probs[:2])]
    if issues:
        return None, "fact check failed: " + "; ".join(issues[:3])
    return text + f"# source: {ft}\n", None


# ------------------------------------------------------------------ 5. run
def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if os.environ.get("TREND_SHORTS", "on").strip().lower() in ("off", "0", "no", "false"):
        print("trend Shorts off (TREND_SHORTS=off)"); return 0
    cands = [("forced (--topic)", radar._clean(argv[argv.index("--topic") + 1]), radar._clean(argv[argv.index("--topic") + 1]))] \
        if "--topic" in argv else candidates()
    print("topics in order:", *[f"{i + 1}. {q}  [{src}]" for i, (src, q, _) in enumerate(cands)], sep="\n  ")
    os.makedirs(OUT, exist_ok=True)
    log = []
    import time; t0 = time.time()
    for src, q, subj in cands[:4]:
        if time.time() - t0 > 40 * 60:  # leave the render enough of the job's 120 minutes
            log.append("- stopped trying new topics after 40 minutes"); break
        print(f"== topic: {q} ({src})")
        try:
            text, why = make_script(q, subj)
        except Exception as e:
            text, why = None, f"script writer error: {str(e)[:120]}"
        if not text:
            print("  skipped:", why); log.append(f"- skipped **{q}** ({src}): {why}"); continue
        slug = re.sub(r"[^a-z0-9]+", "-", q)[:40].strip("-")
        path = os.path.join(OUT, f"trend-{dt.date.today().isoformat()}-{slug}.txt")
        open(path, "w", encoding="utf-8").write(text)
        print(text)
        _summary("### 🔥 Trend Short\n\n" + "\n".join(log + [f"- **Topic:** {q} ({src})", f"- **Script:** `{os.path.relpath(path, ROOT)}` (in this run's Artifacts)",
                                                         "", "```text", text.strip(), "```"]))
        if "--script-only" in argv: return 0
        try:  # free the model's memory before the render (the voices and video need it)
            urllib.request.urlopen(urllib.request.Request(f"http://{OLLAMA}/api/generate", data=json.dumps({"model": MODEL, "keep_alive": 0}).encode(),
                                                          headers={"Content-Type": "application/json"}), timeout=30).read()
        except Exception:
            pass
        args = [sys.executable, os.path.join(HERE, "daily.py"), "--script", path] + (["--dry-run"] if "--dry-run" in argv else [])
        return subprocess.run(args, cwd=ROOT, env={**os.environ, "TREND_TOPIC": q, "SCRIPT_IN": ""}).returncode
    _summary("### 🔥 Trend Short: nothing made today\n\n" + "\n".join(log or ["- no topic found"]))
    return 0


def _summary(md):
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8").write(md + "\n")


if __name__ == "__main__":
    sys.exit(main())
