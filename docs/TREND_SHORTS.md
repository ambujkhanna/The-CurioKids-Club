# Automatic trend Shorts (built 2026-11-22, owner's request)

**What it does:** one EXTRA Short a day about what people search for right now. It has its own queue (`custom/`), so the normal daily episodes (English/Hindi, Spanish) are not touched. Same files in both repos.

| | Kids (The CurioKids Club) | AInation Studio |
|---|---|---|
| Schedule | 06:11 UTC (11:41 IST) | 06:23 UTC (11:53 IST) |
| Publishes | 12:00–14:00 IST (`PUBLISH_WINDOW_TREND`) | 12:00–14:00 IST |
| Switch | `TREND_SHORTS` default **on** | `TREND_SHORTS` default **off** until AInation has its own Google Cloud project (see below) |
| Facts from | Simple English Wikipedia, then English Wikipedia | English Wikipedia |
| Characters | Leo asks, Mia explains | Dad asks, Teen explains |

Owner's choices (2026-11-22): both channels; **public automatically** in the slot (no human check); 12:00–14:00 IST. Note: until Google approves the API audit, YouTube keeps every API upload Private anyway.

## How a topic becomes a video (`pipeline/trend_short.py`)

1. **Topic: the first relevant search wins** (owner's rule), in this order:
   1. today's Google Trends (India, USA, Mexico) that fit the channel, turned into the question people search ("why does solar eclipse happen");
   2. YouTube's trending charts (Education, Science & Technology, + Animals for kids), needs the `youtube.force-ssl` login or `YT_API_KEY`;
   3. the radar's most-searched YouTube questions (evergreen demand), so there is a topic every day.
   Already-covered subjects and earlier trend topics are skipped. Kid block list as everywhere.
2. **Facts:** the matching Wikipedia article (its title must name the subject; long articles: intro + the paragraphs about the topic).
3. **Script:** a free open model on the GitHub runner, **Ollama + Qwen 2.5 7B** (Apache 2.0, no paid API, ~3 min on CPU), writes it in the `scripts/README.md` format, told to use only the Wikipedia facts. The same checker as your own scripts runs; problems are fed back (3 tries). The code trims extra lines and always adds the channel's closing line.
4. **Fact check (two gates, every explaining line):**
   - in code: every number must appear in the Wikipedia text (caught "13%" when the source says 14%);
   - the model: "does the source contradict this sentence?" One rewrite is allowed; if a line still fails, the topic is **dropped** and the next topic is tried (max 4). If all fail, nothing is posted that day and the run summary says why.
5. **Video:** `daily.py --script` renders, checks, uploads, adds subtitles, posts to Facebook/Instagram like any Short. The script and its Wikipedia source are in the run summary and Artifacts; the record keeps `trend_topic`.

## Run it by hand

Actions → daily Short workflow → Run workflow → action:
- **Trend Short (auto topic)**: picks the topic and posts (in the trend window).
- **Trend Short dry run (auto topic)**: everything except the upload; download the video from Artifacts.

## Variables

| Variable | Default | Meaning |
|---|---|---|
| `TREND_SHORTS` | kids `on`, AInation `off` | the daily automatic trend Short |
| `TREND_MODEL` | `qwen2.5:7b` | any Ollama model (e.g. `qwen2.5:14b`: better writing, ~3× slower) |
| `PUBLISH_WINDOW_TREND` | `12:00-14:00` | IST window for trend Shorts |

## YouTube API allowance (important)

Both channels share ONE Google Cloud project = 10,000 units/day. Each upload ≈ 1,600, each subtitle track 400, thumbnail/playlist/titles 50 each.
Kids: English/Hindi ≈ 2,550 + Spanish ≈ 2,550 + trend ≈ 2,150. AInation: daily ≈ 2,100 (+ weekly long). Total ≈ 9,350 → **no room for an AInation trend Short** on the shared project.

**To switch on AInation trend Shorts (about 15 minutes, free):**
1. Google Cloud Console → project menu → **New project** ("AInation Studio API").
2. APIs & Services → Library → enable **YouTube Data API v3** (and YouTube Analytics API if you use analytics).
3. OAuth consent screen → External → app name, your email → add yourself as test user → **Publish app** ("In production"; otherwise tokens expire after 7 days).
4. Credentials → Create credentials → OAuth client ID → **Web application** → redirect URI `https://developers.google.com/oauthplayground`.
5. OAuth Playground (gear → own credentials, paste the NEW client ID + secret) → scope `https://www.googleapis.com/auth/youtube.force-ssl` → choose the **AInation Studio** channel → exchange → copy the refresh token.
6. AInation repo → Settings → Secrets → update `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN` with the new values.
7. AInation repo → Variables → `TREND_SHORTS` = `on`.
AInation then has its own 10,000 units and the kids channel gets more room too.

## Quality notes

- The 7B model writes simple, correct, slightly plain scripts. For livelier writing try `TREND_MODEL=qwen2.5:14b` (fits the free runner; the job takes ~10 min longer).
- If a trend Short looks wrong: delete it in YouTube Studio; to stop the feature set `TREND_SHORTS=off`.

## Troubleshooting (log)

| When | Problem | Fix |
|---|---|---|
| 2026-11-23 01:30 IST (2026-11-22 20:00 UTC) | First dry run failed: `episode check: line 11: icon '🦸\u200d♂️' is not an emoji or known icon`. The model used a **combined emoji** (🦸 + invisible joiner + ♂️), which the video engine can't draw, and the writer's retry loop only ran the format check, so it never saw the problem. | (1) `script2episode.plain_emoji()` turns combined emoji into the first plain picture (🦸‍♂️ → 🦸, 👍🏽 → 👍) for every script; (2) the writer now runs the **full** check (`script2episode.convert` + episode check) inside its retry loop, so any check failure is fed back to the model or the topic is skipped, never a failed run; (3) the prompt forbids combined emoji. All 99 + 47 queued episodes, 8 + 8 long videos, 31 category episodes and all script files re-validated: OK. |

**Rule for the future:** anything the pipeline makes by itself must pass the same full check the real run uses *before* it is handed to `daily.py`; a failed check means "try again / next topic", never a failed workflow.

