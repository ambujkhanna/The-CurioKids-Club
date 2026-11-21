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
    return len(s) >= 8 and len(w) >= 3 and not (w & BLOCK) and not (w & NOISE) and bool(w & (TOPIC | _TITLE_WORDS))


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
            if 10 <= len(t) <= 220 and REQ.search(t) and not (set(_clean(t).split()) & BLOCK):
                out.append(t.replace("\n", " "))
    return list(dict.fromkeys(out))[:30]


# ------------------------------------------------------------------ report
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
    rows = []
    for s, v in cands[:25]:
        comp = competition(yt, s) if yt else None
        if comp:
            med, top, old = comp
            opp = v * (1 + old) * math.log10(med + 10) / math.log10(top + 100)  # demand, old results, beatable top
        else:
            med = top = old = None; opp = v
        rows.append((s, v, med, top, old, opp))
    rows.sort(key=lambda r: -r[5])
    wk = dt.date.today().isocalendar()
    md = [f"# Topic radar {wk[0]}-W{wk[1]:02d}: {name}", "",
          "Tick the topics to make. Demand = how strongly YouTube suggests the phrase across our seed searches. "
          "Competition (when available) = median / top views of the current top 10 videos, and the share of them older than a year "
          "(old results are easier to beat). Already-covered topics are left out.", ""]
    md += ["## Top topics", "", "| | Search phrase | Demand | Median views | Top views | Old results |", "|---|---|---|---|---|---|"]
    for s, v, med, top, old, opp in rows[:20]:
        f = lambda n: "–" if n is None else (f"{n/1e6:.1f}M" if n >= 1e6 else f"{n/1e3:.0f}k" if n >= 1e3 else str(n))
        md.append(f"| - [ ] | {s} | {v:.0f} | {f(med)} | {f(top)} | {'–' if old is None else f'{old:.0%}'} |")
    more = [s for s, _ in cands[25:45]]
    if more: md += ["", "**Also suggested:** " + ", ".join(more)]
    terms = our_search_terms()
    if terms:
        md += ["", "## Searches that already bring viewers to us (last 90 days)", ""] + [f"- {t} ({n} views)" for t, n in terms[:15]]
        md += ["", "Make more around these: they already work for us."]
    reqs = viewer_requests(yt)
    if reqs:
        md += ["", "## Viewers asked (from comments)", ""] + [f"- [ ] {t}" for t in reqs]
    if not yt:
        md += ["", "_Competition and comments were skipped: no YouTube Data API access (add a free `YT_API_KEY` secret, or the upload login needs the broad 'youtube' scope)._"]
    md += ["", "_Made by `pipeline/radar.py` (roadmap R2/R3). Read-only towards YouTube; no titles or content are copied from other channels._"]
    return "\n".join(md)


def open_issue(body):
    repo, tok = os.environ.get("GITHUB_REPOSITORY"), os.environ.get("GITHUB_TOKEN")
    if not (repo and tok): print("note: no GITHUB_TOKEN/GITHUB_REPOSITORY: issue not opened"); return None
    title = body.split("\n", 1)[0].lstrip("# ").strip()
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/issues", method="POST",
                                 data=json.dumps({"title": title, "body": body[:60000], "labels": ["topic-radar"]}).encode(),
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
