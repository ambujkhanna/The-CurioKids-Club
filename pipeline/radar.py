"""Weekly topic and keyword radar + viewers' topic requests (roadmap R2 + R3, 2026-11-22). Same file in both channels.

    python pipeline/radar.py                 # prints the report; in GitHub Actions also opens an issue
    python pipeline/radar.py --no-issue      # report only

What it combines (each part is skipped quietly if its login or network isn't available):
  1. YouTube search suggestions (free, no key): channel seed phrases + "seed a".."seed z"; a phrase that appears
     for many seeds and high in the lists = real demand.
  2. Competition (YouTube Data API: search.list + videos.list) for the top candidates: views and age of the top 10
     videos. Needs the upload login with the broad "youtube" scope (kids) or a YT_API_KEY secret (optional).
  3. Our own search terms (YouTube Analytics, YT_ANALYTICS_REFRESH_TOKEN): the searches that already bring viewers.
  4. Viewers' requests (R3): recent comments on our last 30 videos that ask for a topic. Only the request text is
     shown (no names, no links, no emails/phone numbers). Never replies.
Output: a markdown report (run summary + radar/latest.md artifact) and a GitHub issue "Topic radar YYYY-WW" with tick
boxes (needs GITHUB_TOKEN with issues: write). Read-only towards YouTube. Repo variable RADAR=off turns it off.
"""
import datetime as dt, json, math, os, re, string, sys, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
KIDS = os.path.exists(os.path.join(ROOT, "library")) or "curio" in ROOT.lower()
UA = {"User-Agent": "studio-video-pipeline/1.0 (topic research)"}

SEEDS = {
    True: ["why do animals", "why do plants", "why is the sky", "why does the moon", "how do plants", "how does the body",
           "why do we have", "why do birds", "how do bees", "fun facts for kids about", "science for kids", "why is the ocean",
           "how do fish", "why do leaves", "how does the sun", "why do we need", "what makes", "kids science experiment"],
    False: ["how to use chatgpt", "ai for", "is ai", "ai tools for", "chatgpt vs", "how does ai", "can ai",
            "ai explained", "how to use ai", "ai safety"],
}[KIDS]
# a phrase must be about a real subject: kids = science / nature / body / everyday-world words (+ our own title words);
# AInation = AI words. Keeps pop culture, celebrities and games out.
TOPIC = set(("""animal animals plant plants tree trees leaf leaves flower flowers seed seeds bee bees bird birds fish whale
shark dog dogs cat cats insect insects ant ants butterfly spider frog snake dinosaur dinosaurs elephant lion owl penguin
body brain heart blood bones bone teeth tooth eyes eye ears ear nose tongue skin hair muscles stomach lungs sleep dream
dreams sneeze hiccups yawn blink sweat cough germs space sun moon earth planet planets star stars mars saturn galaxy
astronaut rocket sky ocean sea water rain rainbow cloud clouds snow ice wind weather thunder lightning volcano
earthquake rock rocks soil sand mountain river rivers magnet magnets light sound shadow shadows color colors colour
colours air fire gravity energy electricity machine machines robot robots science experiment experiments
seasons winter summer autumn spring day night food fruit vegetables milk egg eggs honey slime bubbles""").split()) if KIDS else set(
"""ai chatgpt gemini claude copilot llm llms gpt openai prompt prompts agent agents robot robots deepfake deepfakes
machine learning neural automation chatbot chatbots algorithm data model models""".split())
# kids: never suggest these (scary, adult, brand-led or not for children)
BLOCK = set("""sex sexy porn nude kill killed killing death die dies dying dead murder blood gore gun guns war drug drugs
alcohol beer rum weed vape smoke smoking suicide horror scary creepy fear 3am dating girlfriend boyfriend kiss hickey mate
mating tiktok roblox minecraft fortnite gta skibidi mrbeast batman marvel trump biden election religion god woman stock
market money crypto bitcoin juggalo goodbye rabies""".split()) if KIDS else set("porn nude sex onlyfans".split())
NOISE = set("song lyrics meme tiktok reaction asmr prank challenge live stream download free apk mod hack crack".split())
# Reject unrelated finance/news topics on BOTH channels, even if a trend headline contains an AI brand.
OFF_CHANNEL = set("""gold price prices stock stocks market markets share shares crypto bitcoin ethereum forex currency currencies
exchange trading trader economy economic inflation recession interest rates bond bonds commodity commodities
politics politician election celebrity celebrities gossip breaking news war conflict""".split())


def _get(url, timeout=15):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def suggestions(q, lang="en"):
    try:
        d = _get("https://suggestqueries.google.com/complete/search?" + urllib.parse.urlencode(
            {"client": "firefox", "ds": "yt", "hl": lang, "q": q}))
        return [s.strip().lower() for s in d[1] if isinstance(s, str)]
    except Exception:
        return []


def _clean(s):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9' ]", " ", s.lower())).strip()


_TITLE_WORDS = None


def _ok(s):
    global _TITLE_WORDS
    if _TITLE_WORDS is None:  # our own episode title words count as topic words too
        _TITLE_WORDS = {w for t in covered_titles() for w in t.split() if len(w) > 3} - STOP
    w = set(s.split())
    return len(s) >= 8 and len(w) >= 3 and not (w & BLOCK) and not (w & NOISE) and not (w & OFF_CHANNEL) and bool(w & (TOPIC | _TITLE_WORDS))


def demand():
    """{phrase: score} from YouTube search suggestions."""
    score, hits = {}, {}
    queries = [(sd, sd) for sd in SEEDS] + [(sd, f"{sd} {c}") for sd in SEEDS for c in string.ascii_lowercase]
    for seed, q in queries:
        for pos, s in enumerate(suggestions(q)):
            s = _clean(s)
            if not _ok(s) or s == seed: continue
            score[s] = score.get(s, 0) + (10 - min(pos, 9))
            hits.setdefault(s, set()).add(q)
        time.sleep(0.15)
    return {s: v * (1 + 0.15 * (len(hits[s]) - 1)) for s, v in score.items()}


def covered_titles():
    out = []
    for d in ("episodes", "long", "custom"):
        p = os.path.join(ROOT, d)
        if not os.path.isdir(p): continue
        for e in os.listdir(p):
            f = os.path.join(p, e, "episode.json")
            if os.path.exists(f):
                try: out.append(_clean(json.load(open(f, encoding="utf-8")).get("title", "")))
                except Exception: pass
    try:  # videos made from scripts (incl. the automatic trend Shorts): only their state is kept in the repo
        for r in json.load(open(os.path.join(ROOT, "custom", "state.json"), encoding="utf-8")).get("episodes", {}).values():
            if isinstance(r, dict) and r.get("title"): out.append(_clean(r["title"]))
            if isinstance(r, dict) and r.get("trend_topic"): out.append(_clean(r["trend_topic"]))
    except Exception:
        pass
    return out


STOP = set("a an the of to for in on and or is are do does why how what can you your we our it its with from by be "
           "kids facts fun science explained video".split())


def _covered(s, titles):
    w = set(s.split()) - STOP
    if not w: return False
    for t in titles:
        tw = set(t.split()) - STOP
        if tw and len(w & tw) / len(w) >= 0.6: return True
    return False


# ------------------------------------------------------------------ YouTube logins (all optional)
def youtube():
    """Data API client: API key if given, else the upload login (works when it has the broad 'youtube' scope)."""
    try:
        from googleapiclient.discovery import build
        if os.environ.get("YT_API_KEY"):
            return build("youtube", "v3", developerKey=os.environ["YT_API_KEY"], cache_discovery=False)
        from google.oauth2.credentials import Credentials
        if not os.environ.get("YT_REFRESH_TOKEN"): return None
        creds = Credentials(None, refresh_token=os.environ["YT_REFRESH_TOKEN"], token_uri="https://oauth2.googleapis.com/token",
                            client_id=os.environ.get("YT_CLIENT_ID"), client_secret=os.environ.get("YT_CLIENT_SECRET"))
        return build("youtube", "v3", credentials=creds, cache_discovery=False)
    except Exception as e:
        print("note: no YouTube Data API access:", str(e)[:100]); return None


def competition(yt, phrase):
    """(median views, top views, share of top 10 older than a year) or None."""
    try:
        r = yt.search().list(q=phrase, part="id", type="video", maxResults=10, relevanceLanguage="en", safeSearch="strict").execute()
        ids = [i["id"]["videoId"] for i in r.get("items", [])]
        if not ids: return (0, 0, 0.0)
        v = yt.videos().list(id=",".join(ids), part="statistics,snippet").execute()
        views = sorted(int(x["statistics"].get("viewCount", 0)) for x in v.get("items", []))
        now = dt.datetime.now(dt.timezone.utc)
        old = sum(1 for x in v.get("items", []) if (now - dt.datetime.fromisoformat(x["snippet"]["publishedAt"].replace("Z", "+00:00"))).days > 365)
        return (views[len(views) // 2] if views else 0, views[-1] if views else 0, old / max(1, len(views)))
    except Exception as e:
        print("note: competition check skipped:", str(e)[:120]); return None


def our_search_terms(days=90):
    try:
        sys.path.insert(0, HERE); import analytics
        svc = analytics.analytics_service()
        end = dt.date.today(); start = end - dt.timedelta(days=days)
        r = svc.reports().query(ids="channel==MINE", startDate=str(start), endDate=str(end), metrics="views",
                                dimensions="insightTrafficSourceDetail", filters="insightTrafficSourceType==YT_SEARCH",
                                maxResults=25, sort="-views").execute()
        return [(row[0], int(row[1])) for row in r.get("rows", [])]
    except BaseException as e:  # analytics_service() exits when the login is missing
        print("note: our search terms skipped:", str(e)[:120]); return []


REQ = re.compile(r"(video (on|about)|make (a|one|more)|please (make|do|explain)|can you (make|do|explain)|next (video|topic|one)|"
                 r"do (one|a video) (on|about)|explain|topic|teach us|i want to (know|learn)|\bwhy\b|\bhow\b|\bwhat\b)", re.I)


def viewer_requests(yt, limit_videos=30):
    """Topic requests from recent comments on our videos (text only)."""
    if yt is None: return []
    try:
        st = json.load(open(os.path.join(ROOT, "episodes", "state.json"), encoding="utf-8")).get("episodes", {})
    except Exception:
        return []
    vids = [v["video_id"] for v in sorted(st.values(), key=lambda v: v.get("uploaded_at", ""), reverse=True) if isinstance(v, dict) and v.get("video_id")][:limit_videos]
    out = []
    for vid in vids:
        try:
            r = yt.commentThreads().list(videoId=vid, part="snippet", maxResults=50, order="time", textFormat="plainText").execute()
        except Exception as e:
            print("note: comments skipped:", str(e)[:100]); break
        for it in r.get("items", []):
            t = it["snippet"]["topLevelComment"]["snippet"].get("textDisplay", "")
            t = re.sub(r"https?://\S+|\S+@\S+|\+?\d[\d \-]{7,}\d|@\w+", "", t).strip()  # no links, emails, phones, handles
            if 10 <= len(t) <= 220 and REQ.search(t) and _ok(_clean(t)):
                out.append(t.replace("\n", " "))
    return list(dict.fromkeys(out))[:30]


# ------------------------------------------------------------------ report
# ------------------------------------------------------------------ what is trending right now (owner, 2026-11-22)
TREND_GEOS = [g.strip().upper() for g in os.environ.get("RADAR_GEOS", "IN,US,MX").split(",") if g.strip()]
# extra subject words that show up in news trends (kids: sky events, weather, seasons, festivals; Spanish for Mexico)
TREND_TOPIC = set(("""eclipse comet comets meteor asteroid aurora supermoon moon nasa isro spacex launch hurricane cyclone storm
monsoon tornado earthquake volcano heatwave fog smog snowfall flood tsunami diwali holi christmas halloween fireworks
dinosaur fossil zoo panda tiger pollution climate
eclipse cometa luna sol lluvia tormenta huracán sismo terremoto volcán animales animal planeta estrellas espacio dinosaurio
navidad nieve calor frío ciencia""").split()) if KIDS else set(
"""ai chatgpt gemini claude copilot openai llm gpt nvidia deepseek grok perplexity sora midjourney apple intelligence
robot robots deepfake chip chips iphone android google microsoft meta ia inteligencia artificial""".split())


def _words(t):
    """Words of a text plus simple singulars (volcanoes -> volcano, bees -> bee), so plurals match the topic lists."""
    w = set(re.findall(r"[a-záéíóúñü0-9]+", t.lower()))
    return w | {x[:-2] for x in w if x.endswith("es") and len(x) > 4} | {x[:-1] for x in w if x.endswith("s") and len(x) > 3}


# words too common in news/sport/celebrity names to mean a science topic on their own ("Minnesota Wild", "The Sun", "Star Wars")
EXTRA_SUBJECTS = set("""octopus jellyfish dolphin turtle crab koala kangaroo cheetah gorilla monkey parrot eagle bat bats wolf fox bear
camel zebra giraffe hippo crocodile shark coral microscope telescope chemistry physics biology planet atom atoms cell cells
bacteria virus vaccine dna""".split()) if KIDS else set()
GENERIC = set("""day night light star stars sun fire water air food spring summer winter autumn color colors colour colours energy
machine machines sound rock rocks model models data agent agents eye eyes heart brain body sea earth day sky bird birds
animal animals fish tree trees snow ice wind rain cloud clouds seasons science sleep dream dreams""".split())


def _fits(text, loose=False):
    """Only the trending search itself counts (headlines mention too many everyday words), and it needs a real subject word.
    loose=True (YouTube charts, already limited to Education / Science / Animals): everyday science words count too."""
    w = _words(text)
    return _ok(_clean(text)) and bool(w & ((TOPIC if loose else TOPIC - GENERIC) | TREND_TOPIC | EXTRA_SUBJECTS))


def google_trends(geos=None):
    """Today's trending Google searches per country (public RSS, no key). Returns [(geo, term, traffic, headline, fits)]."""
    import xml.etree.ElementTree as ET
    ns = {"ht": "https://trends.google.com/trending/rss"}
    out = []
    for g in geos or TREND_GEOS:
        try:
            req = urllib.request.Request(f"https://trends.google.com/trending/rss?geo={g}", headers=UA)
            root = ET.fromstring(urllib.request.urlopen(req, timeout=20).read())
        except Exception as e:
            print(f"note: Google Trends {g} unavailable:", str(e)[:80]); continue
        for it in root.iter("item"):
            term = (it.findtext("title") or "").strip()
            traffic = (it.findtext("ht:approx_traffic", namespaces=ns) or "").strip()
            news = [n.findtext("ht:news_item_title", namespaces=ns) or "" for n in it.findall("ht:news_item", ns)]
            head = next((h for h in news if h), "")
            out.append((g, term, traffic, head, _fits(term)))
    return out


def trend_angles(term):
    """Questions kids/viewers actually search about a trending subject (YouTube suggestions), e.g. 'why does an eclipse happen'."""
    qs = [f"why does {term}", f"how does {term}", f"what is {term}"] + ([f"{term} for kids"] if KIDS else [f"{term} explained"])
    seen = []
    for q in qs:
        for x in suggestions(q)[:4]:
            x = _clean(x)
            if x and x not in seen and _ok(x): seen.append(x)
        time.sleep(0.15)
    return seen[:4]


TREND_CATS = {"27": "Education", "28": "Science & Technology", "15": "Pets & Animals"} if KIDS else {"28": "Science & Technology", "27": "Education"}


def youtube_trending(yt, geos=None):
    """YouTube's 'most popular' videos per country in our categories (Data API, 1 quota unit per call).
    Returns [(geo, category, title, views, is_short, fits)] - for ideas only; never copy titles or content."""
    global YT_CHART_ERR
    out, errs, calls = [], [], 0
    if not yt: return out
    for g in geos or TREND_GEOS:
        for cid, cname in TREND_CATS.items():
            calls += 1
            try:
                r = yt.videos().list(part="snippet,statistics,contentDetails", chart="mostPopular", regionCode=g,
                                     videoCategoryId=cid, maxResults=25).execute()
            except Exception as e:  # some countries have no chart for some categories
                errs.append(str(e)); print(f"note: YouTube trending {g}/{cname}:", str(e)[:80]); continue
            for v in r.get("items", []):
                t = v["snippet"]["title"]; views = int(v.get("statistics", {}).get("viewCount", 0) or 0)
                d = v.get("contentDetails", {}).get("duration", "")
                m_ = re.fullmatch(r"PT(?:(\d+)M)?(?:(\d+)S)?", d)
                short = bool(m_) and int(m_.group(1) or 0) * 60 + int(m_.group(2) or 0) <= 180
                out.append((g, cname, t, views, short, _fits(t, loose=True)))
    if calls and len(errs) == calls:  # every chart failed: usually the upload-only login (no read access) or a bad key
        YT_CHART_ERR = ("the YouTube login can only upload, it can't read the charts" if any("insufficient" in e.lower() or "403" in e for e in errs)
                        else "YouTube refused every chart request: " + errs[0][:120])
    return out


YT_CHART_ERR = None


def report():
    name = "The CurioKids Club" if KIDS else "AInation Studio"
    titles = covered_titles()
    dm = demand()
    ranked = sorted(((s, v) for s, v in dm.items() if not _covered(s, titles)), key=lambda x: -x[1])
    cands, seen = [], []
    for s_, v in ranked:  # merge near-duplicates ("why doesn't the moon spin" / "why does the moon not spin")
        w = {x.replace("n't", "").replace("doesn", "does") for x in s_.split()} - STOP - {"not", "isn", "doesn", "don"}
        if any(w and len(w & o) / len(w | o) >= 0.6 for o in seen): continue
        seen.append(w); cands.append((s_, v))
        if len(cands) >= 60: break
    yt = youtube()
    import growth_signal  # what already works on OUR channel (analytics): ranks topics, never blocks one
    rows = []
    for s, v in cands[:25]:
        comp = competition(yt, s) if yt else None
        if comp:
            med, top, old = comp
            opp = v * (1 + old) * math.log10(med + 10) / math.log10(top + 100)  # demand, old results, beatable top
        else:
            med = top = old = None; opp = v
        gb = growth_signal.boost(s)
        rows.append((s, v, med, top, old, opp * (1 + gb), gb))
    rows.sort(key=lambda r: -r[5])
    wk = dt.date.today().isocalendar()
    md = [f"# Topic radar {wk[0]}-W{wk[1]:02d}: {name}", "",
          "Tick the topics to make. Demand = how strongly YouTube suggests the phrase across our seed searches. "
          "Competition (when available) = median / top views of the current top 10 videos, and the share of them older than a year "
          "(old results are easier to beat). Already-covered topics are left out.", ""]
    md += ["## Top topics", "", "| | Search phrase | Demand | Median views | Top views | Old results | Our channel |", "|---|---|---|---|---|---|---|"]
    for s, v, med, top, old, opp, gb in rows[:20]:
        f = lambda n: "–" if n is None else (f"{n/1e6:.1f}M" if n >= 1e6 else f"{n/1e3:.0f}k" if n >= 1e3 else str(n))
        md.append(f"| - [ ] | {s} | {v:.0f} | {f(med)} | {f(top)} | {'–' if old is None else f'{old:.0%}'} | {growth_signal.mark(gb)} |")
    more = [s for s, _ in cands[25:45]]
    if more: md += ["", "**Also suggested:** " + ", ".join(more)]
    terms = our_search_terms()
    if terms:
        md += ["", "## Searches that already bring viewers to us (last 90 days)", ""] + [f"- {t} ({n} views)" for t, n in terms[:15]]
        md += ["", "Make more around these: they already work for us."]
    md += growth_signal.summary_md()
    md += trends_md(yt, titles)
    reqs = viewer_requests(yt)
    if reqs:
        md += ["", "## Viewers asked (from comments)", ""] + [f"- [ ] {t}" for t in reqs]
    if not yt:
        md += ["", "_Competition and comments were skipped: no YouTube Data API access (add a free `YT_API_KEY` secret, or the upload login needs the broad 'youtube' scope)._"]
    md += ["", "_Made by `pipeline/radar.py` (roadmap R2/R3). Read-only towards YouTube; no titles or content are copied from other channels._"]
    return "\n".join(md)


def trends_md(yt, titles):
    """Report sections: Google Trends + YouTube trending, only what fits the channel (kids: science/nature, never BLOCK words)."""
    f = lambda n: f"{n/1e6:.1f}M" if n >= 1e6 else f"{n/1e3:.0f}k" if n >= 1e3 else str(n)
    md = []
    gt = google_trends()
    fit = [x for x in gt if x[4]]
    md += ["", "## Trending on Google right now (" + ", ".join(TREND_GEOS) + ")", "",
           "Today's fastest-rising Google searches that fit this channel, with the questions people search about them on YouTube. "
           "Trends move fast: a Short made within 1-3 days rides the wave.", ""]
    if fit:
        md += ["| | Country | Trending search | Searches | Headline | Questions people ask |", "|---|---|---|---|---|---|"]
        seen = set()
        for g, term, traffic, head, _ in fit[:12]:
            if term.lower() in seen: continue
            seen.add(term.lower())
            ang = "; ".join(trend_angles(term)) or "–"
            md.append(f"| - [ ] | {g} | **{term}** | {traffic or '–'} | {head[:90].replace('|', '/')} | {ang} |")
    else:
        md.append(f"_No trending search fits the channel today ({len(gt)} checked). Normal: most trends are news, sport and celebrities._")
    md += ["", "## Trending on YouTube (most popular in " + ", ".join(TREND_CATS.values()) + ")", ""]
    if not yt:
        md.append("_Skipped: add the free `YT_API_KEY` secret to see YouTube's trending charts._")
        return md
    yv = youtube_trending(yt)
    keep = [x for x in yv if x[5]]  # both channels: only strict channel-fit subjects
    keep.sort(key=lambda x: (not x[4], -x[3]))  # Shorts first, then by views
    if keep:
        md += ["Ideas only: look at the subject, never copy titles or content.", "",
               "| Country | Category | Video title | Views | Short? | Already covered? |", "|---|---|---|---|---|---|"]
        seen = set()
        for g, cat, t, views, short, _ in keep[:20]:
            if t in seen: continue
            seen.add(t)
            md.append(f"| {g} | {cat} | {t[:80].replace('|', '/')} | {f(views)} | {'yes' if short else ''} | {'yes' if _covered(_clean(t), titles) else ''} |")
    elif YT_CHART_ERR:
        md.append(f"_Skipped: {YT_CHART_ERR}. Add the free `YT_API_KEY` secret (Google Cloud → Credentials → API key, YouTube Data API v3)._")
    else:
        md.append(f"_Nothing in today's charts fits the channel ({len(yv)} videos checked)._")
    return md


def recent_alerts(days=7):
    """Text of trend-alert issues from the last `days` days (so the daily check never alerts the same trend twice)."""
    repo, tok = os.environ.get("GITHUB_REPOSITORY"), os.environ.get("GITHUB_TOKEN")
    if not (repo and tok): return ""
    since = (dt.datetime.utcnow() - dt.timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/issues?labels=trend-alert&state=all&since={since}&per_page=50",
                                 headers={"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json", **UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return "\n".join((i.get("title") or "") + "\n" + (i.get("body") or "") for i in json.loads(r.read())).lower()
    except Exception as e:
        print("note: could not read earlier trend alerts:", str(e)[:80]); return ""


def trend_alert():
    """Daily quick check (RADAR_TRENDS): a GitHub issue only when a NEW trend fits the channel. Returns the body or None."""
    name = "The CurioKids Club" if KIDS else "AInation Studio"
    old = recent_alerts()
    gt = [x for x in google_trends() if x[4] and x[1].lower() not in old]
    yt = youtube(); titles = covered_titles(); yv, seen_t = [], set()
    for x in (youtube_trending(yt) if yt else []):  # each video once, only fitting, not already covered by us, not alerted before
        if x[5] and x[2] not in seen_t and x[2].lower() not in old and not _covered(_clean(x[2]), titles):
            seen_t.add(x[2]); yv.append(x)
    yv.sort(key=lambda x: (not x[4], -x[3]))
    if YT_CHART_ERR: print("note: YouTube trending skipped -", YT_CHART_ERR, "- add the YT_API_KEY secret")
    if not gt and not yv:
        print("no new trend fits the channel today"); return None
    terms = []
    for x in gt:
        if x[1] not in terms: terms.append(x[1])
    md = [f"# Trend alert {dt.date.today().isoformat()}: {', '.join(terms[:3]) or 'YouTube trending'} ({name})", "",
          "A trending subject fits the channel. A Short made in the next 1-3 days can ride the wave: "
          "write the script (or paste it in Run workflow → script) and publish with `Next video, publish now`.", ""]
    if gt:
        md += ["| | Country | Trending search | Searches | Headline | Questions people ask |", "|---|---|---|---|---|---|"]
        for g, term, traffic, head, _ in gt[:8]:
            md.append(f"| - [ ] | {g} | **{term}** | {traffic or '–'} | {head[:90].replace('|', '/')} | {'; '.join(trend_angles(term)) or '–'} |")
    if yv:
        f = lambda n: f"{n/1e6:.1f}M" if n >= 1e6 else f"{n/1e3:.0f}k" if n >= 1e3 else str(n)
        md += ["", "**On YouTube's trending charts (ideas only, never copy):**", ""]
        md += [f"- {g} · {cat}: {t[:90]} ({f(v)} views{', Short' if sh else ''})" for g, cat, t, v, sh, _ in yv[:8]]
    md += ["", "_Daily check by `pipeline/radar.py --trends-only` (Google Trends RSS + YouTube most-popular). Repo variable `RADAR_TRENDS=off` stops it._"]
    return "\n".join(md)


def open_issue(body, label="topic-radar"):
    repo, tok = os.environ.get("GITHUB_REPOSITORY"), os.environ.get("GITHUB_TOKEN")
    if not (repo and tok): print("note: no GITHUB_TOKEN/GITHUB_REPOSITORY: issue not opened"); return None
    title = body.split("\n", 1)[0].lstrip("# ").strip()
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/issues", method="POST",
                                 data=json.dumps({"title": title, "body": body[:60000], "labels": [label]}).encode(),
                                 headers={"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json", **UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            url = json.loads(r.read())["html_url"]; print("issue:", url); return url
    except Exception as e:
        print("note: issue not opened:", str(e)[:120]); return None


def main(argv=None):
    argv = argv or sys.argv[1:]
    if os.environ.get("RADAR", "on").strip().lower() in ("off", "0", "no", "false"):
        print("radar off (RADAR=off)"); return 0
    if "--trends-only" in argv:  # the daily quick check
        if os.environ.get("RADAR_TRENDS", "on").strip().lower() in ("off", "0", "no", "false"):
            print("daily trend check off (RADAR_TRENDS=off)"); return 0
        body = trend_alert()
        if body:
            if os.environ.get("GITHUB_STEP_SUMMARY"):
                open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8").write(body + "\n")
            print(body)
            if "--no-issue" not in argv: open_issue(body, "trend-alert")
        return 0
    body = report()
    os.makedirs(os.path.join(ROOT, "radar"), exist_ok=True)
    open(os.path.join(ROOT, "radar", "latest.md"), "w", encoding="utf-8").write(body)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8").write(body + "\n")
    print(body)
    if "--no-issue" not in argv: open_issue(body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
