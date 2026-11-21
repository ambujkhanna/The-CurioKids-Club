# Roadmap: free tools to add to the GitHub automation (pick-and-build plans)

**Status:** PLANNED, 2026-11-21 (owner: "looks nice"). Same file in both repos. Each item below is written so it can be picked up and built directly.
Rules: free first; no paid AI APIs inside the pipeline; secrets only in GitHub Secrets; a human approves anything that changes facts or what goes public; every feature has an off switch and falls back to today's behaviour.

**Recommended order:** R1 real stock clips → R2 topic radar → R3 comments → topics → R4 subtitles → R5 dubbed versions → R6 self-check + alerts → R7 weekly Kaggle run (`docs/AUTOMATION_KAGGLE.md`) → R8 more platforms → R9 extra Kaggle tools.

---

## R1. Real stock clips and photos (Pixabay, NASA, Openverse, Wikimedia; Pexels optional): realism without a GPU

> **2026-11-21:** Pexels has paused issuing new API keys (the owner tried). Build with **Pixabay** (photos + videos, free key) as the main source, **NASA** for space (no key), **Openverse** (`api.openverse.org`, no key needed; filter `license_type=commercial`) and **Wikimedia Commons** (no key; only CC0 / public domain / CC-BY with the credit in the description) as photo backups. Pexels is optional, used only if `PEXELS_API_KEY` exists.

- **Goal:** realistic footage (a falling water drop, planets, animals, a sprouting seed, a laptop at work…) inside boards or as a background. The quickest big jump towards "realistic videos".
- **How:**
  1. `pipeline/stock.py` searches Pexels (`api.pexels.com/videos/search`, `/v1/search`) and Pixabay (`pixabay.com/api/videos/`, `/api/`) for a board's `"stock": "falling water drop"` (or automatically from the board text).
  2. It keeps portrait/landscape-fitting results ≤ 15 s, ≥ 720p, and no people for kids unless asked.
  3. Downloads go to a cache (`assets/stock/`, not committed; the Actions cache keeps them between runs), and the source URL, author and licence go in `assets/stock/manifest.json`.
  4. New board type `"clip"`: plays the clip muted inside the card (or the picture board for photos), with a slow push-in.
  5. NASA Image Library (`images-api.nasa.gov`, public domain) for space topics.
- **Engine:** read video frames with ffmpeg (already installed) at the 24 fps timeline; fall back to the picture board / icon board when nothing is found.
- **Secrets:** `PIXABAY_API_KEY` (free account; required). `PEXELS_API_KEY` optional, if Pexels reopens keys. **Variables:** `STOCK=on|off`, `STOCK_PEOPLE=off` (kids).
- **Licences:** the Pixabay (and Pexels) licences allow free commercial use in videos without attribution (credit added in the description anyway). Don't sell or redistribute the clips as they are. NASA: public domain (no NASA logo or endorsement).
- **Effort:** about 1 day. **Risks:** search results can be off-topic → a fixed query per board plus an owner preview of the first week.
- **Done when:** 5 episodes render with real clips, the owner approves, and the fallbacks work offline.

## R2. Topic and keyword radar: what people actually search for

- **Goal:** each week, a ranked list of topics and title words with real demand and beatable competition, for both channels.
- **Free signals, combined:**
  1. **YouTube search suggestions** (the autocomplete YouTube shows while typing; endpoint `suggestqueries.google.com/complete/search?client=youtube&ds=yt&q=...`, no key). Seeds per channel, expanded with "seed + a…z":
     - Kids: "why do", "why is the", "how do", "what is", "how does", "facts for kids", "for kids science", plus the topic areas.
     - AInation: "how to use chatgpt", "ai for", "is ai", "ai tools for", "chatgpt vs", "how ai".
     - A suggestion that appears for many seeds and high in the list = strong demand.
  2. **Competition** (YouTube Data API `search.list` + `videos.list`, the existing key): for the top suggestions, look at views, age and channel size of the top 10 results. Lots of views on old or small-channel videos = an opportunity. API quota: search costs 100 units of 10,000 a day, so about 40–60 checks a day is fine.
  3. **Our own search terms** (YouTube Analytics API, the existing `YT_ANALYTICS_REFRESH_TOKEN`): `insightTrafficSourceDetail` with `insightTrafficSourceType==YT_SEARCH` shows the exact searches that already bring viewers to our videos. Make more around those.
  4. **Google Trends** (seasonality, e.g. "solar eclipse", "Diwali", "exam tips"): read by hand at trends.google.com, or a weekly try of the unofficial `pytrends`. It often gets blocked, so it's an optional signal.
  5. **YouTube Studio → Research tab** (manual, official): shows what your viewers search for and the "content gaps". The owner checks it monthly; the best single signal.
- **Output:**
  - `docs/TOPIC_RADAR.md` (newest week on top): the top 20 per channel with demand, competition, a suggested title and cover words, and "already covered?" (matched against our episode titles).
  - Plus a GitHub issue "Topic radar YYYY-WW" with tick boxes; the owner ticks topics to make.
  - Optional Ollama step (`ART_OLLAMA`-style switch `RADAR_OLLAMA`) to group similar searches and write kid-friendly titles.
- **Files:** `pipeline/radar.py`, `.github/workflows/topic-radar.yml` (weekly, e.g. Monday 03:00 UTC). **Variables:** `RADAR=on|off`, `RADAR_SEEDS_EXTRA`.
- **Safety:** kids filter (block-list words, no scary or adult topics); never copy other channels' titles or content.
- **Effort:** about 1 day. **Done when:** a weekly issue appears with sensible topics for both channels.

## R3. Comments → topic list (closes the loop with "drop a topic in the comments")

- **Goal:** every topic a viewer asks for lands in a list the owner can pick from.
- **How:** a weekly workflow reads new comments on our last 30 videos (`commentThreads.list`, 1 unit per call), finds topic requests ("make a video on…", "why do…", "?"), removes spam and personal data, merges duplicates, and adds them to the radar issue (R2) as "Viewers asked". It never replies automatically.
- **Kids channel:** comments are on (the channel is "not made for kids"). Show only the topic text, never names.
- **Effort:** half a day, built together with R2.

## R4. Subtitles in more languages (reach + search)

- **Goal:** Spanish, Portuguese, Indonesian, Arabic, French and German subtitle tracks on every video, for both channels.
- **How:**
  1. The script plus word timing already exist (`timing.json`), so English captions are exact. **faster-whisper** (MIT) is only needed for R6.
  2. Translate each line with **Argos Translate** (MIT, offline, CPU). It's the default: good enough for short lines. Or Ollama (7B, better, slower) when `SUBS_OLLAMA=on`.
  3. Upload with `captions.insert` (400 quota units per track, so about 6 tracks per video a day is fine). Also translate the title and description into the same languages (`localizations` in `videos.update`).
- **Variables:** `SUBS_LANGS=es,pt,id,ar,fr,de`, `SUBS=on|off`. **Effort:** about 1 day. **Risks:** machine translation quality → keep lines short (already the style); owner spot-checks one language a week.

## R5. Dubbed versions (Spanish first): the biggest reach lever

- **Goal:** a Spanish (then Portuguese) version of each kids Short, like the Hindi version today.
- **How:** the same pattern as `hi.json`:
  1. `es.json` holds the translated lines (Argos or Ollama, then the owner reviews the first few).
  2. **Kokoro** Spanish voices (Apache 2.0; already in the pipeline) give natural Spanish.
  3. The boards stay visual (icons + short words; translate the board words too).
  4. Publish on alternate days or in the morning slot; title "Spanish | English".
- **Choice to make:** the same channel (simple; YouTube shows the right language) or a second channel later.
- **Effort:** 1–2 days (the Hindi code path already exists). **Risks:** translation quality on jokes and rhymes → skip poem episodes at first.

## R6. Self-check and alerts

- **Self-check:** after rendering, **faster-whisper** (small model, CPU, about 1 minute) transcribes the video's audio and compares it with the script. Missing or garbled words (> 8% word error) → re-render that line or flag it. Also checks the video isn't silent and that the music isn't too loud (ffmpeg `ebur128`).
- **Alerts:** a Telegram bot (free; `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` secrets) or a Discord webhook sends "✅ posted: <title> <link>" or "❌ run failed: <step>" to the owner's phone.
- **Effort:** half a day each.

## R7. Weekly Kaggle GPU run

See `docs/AUTOMATION_KAGGLE.md`: backgrounds, picture boards and house icons made automatically each week; later, Wan 2.1 video clips.

## R8. Post the same videos to more places (free APIs)

| Platform | Fit | API |
|---|---|---|
| Bluesky | both | free, video posts supported |
| Telegram channel | both | free bot API |
| Pinterest | kids (parents and teachers) | free; app approval needed |
| LinkedIn | AInation | app approval needed |
| TikTok | both | Content Posting API needs an app audit |
| X | – | posting API is paid |

Same video, captions from `hashtags.py`. One module per platform in `meta_post.py` style, each with its own on/off variable.

## R9. More free tools for the Kaggle run (later)

- **Real-ESRGAN** (BSD-3): sharper and bigger pictures and icons.
- **RIFE** (MIT): smooth slow motion for clips.
- **ACE-Step** (Apache 2.0): AI background music with more variety (check the outputs for copyright look-alikes; keep the procedural music as the fallback).
- **Wan 2.1 T2V 1.3B** (Apache 2.0): 3–5 s AI clips where no stock footage exists.

## Paid, only if ever wanted (for reference)

| Service | Use | Price (check current terms) |
|---|---|---|
| Modal | GPU from GitHub with no queue (FLUX/Wan per episode) | monthly free credits (about $30), then per second |
| Replicate / fal.ai | one API call per image or clip | FLUX-schnell ~ $0.003/image; video ~ $0.1–1/clip |
| Hugging Face PRO | more Spaces GPU quota + inference credits | ~ $9/month |
| vidIQ / TubeBuddy | keyword research | free tier; paid ~ $5–8/month |
| Kling / Runway / Veo | the most realistic AI video | expensive; only for special videos |
