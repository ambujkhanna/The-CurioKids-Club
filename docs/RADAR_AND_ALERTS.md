# Topic radar, viewers' requests, self-check and alerts

**Added:** 2026-11-22 (roadmap R2, R3, R6). Same file in both repos. Everything here is read-only towards YouTube, never blocks a video, and has an off switch.

## 1. Weekly topic radar + viewers' requests (R2 + R3)

- **Workflow:** *Weekly topic radar* (`.github/workflows/topic-radar.yml`), Mondays 03:17 UTC (08:47 IST), or by hand from Actions → *Run workflow*.
- **Result:** a GitHub issue **"Topic radar YYYY-WNN: <channel>"** (label `topic-radar`) with tick boxes. The same report is in the run summary and as the artifact `topic-radar`. Tick what you want made and give the issue to the assistant.
- **What it uses** (each part skips quietly if not available):
  1. **YouTube search suggestions** (no key): our seed phrases plus "seed a…z". Phrases that appear for many seeds and high in the lists = demand.
     - Kids phrases must name a real subject (animals, body, space, plants, weather…, plus our own title words). Scary, adult and brand words are blocked, and pop culture is filtered out.
     - AInation phrases must name AI, a tool or a related term.
     - Already-covered topics and near-duplicates are left out.
  2. **Competition:** views and age of the current top 10 videos per phrase (YouTube Data API). Needs the upload login with the broad `youtube` scope (kids has it) or a free **`YT_API_KEY`** secret (optional; Google Cloud console → APIs & Services → Credentials → API key, restricted to YouTube Data API v3). AInation's upload login is upload-only, so it needs `YT_API_KEY` for this part.
  3. **Our own search terms:** the searches that already bring viewers to us (YouTube Analytics, the existing `YT_ANALYTICS_REFRESH_TOKEN`).
  4. **Viewers asked:** topic requests from recent comments on our last 30 videos. Only the request text is shown (no names, links, emails or phone numbers). It never replies.
- **Switch:** repo variable `RADAR=off`. Test locally with `python pipeline/radar.py --no-issue`.
- **Honest limits:** suggestions show what people type, not exact search volumes. Treat the list as a shortlist and choose with your judgement (and the YouTube Studio → Research tab).

## 1b. Trending now: Google Trends + YouTube trending (added 2026-11-22, owner)

- **Google Trends:** today's fastest-rising Google searches for India, USA and Mexico (`RADAR_GEOS`, default `IN,US,MX`), from Google's public RSS feed (free, no key).
- **YouTube trending:** YouTube's "most popular" charts per country in Education, Science & Technology (+ Pets & Animals for kids). Needs the free `YT_API_KEY` secret; 1 quota unit per chart.
- **Only what fits the channel:** a trend is kept only if the search itself names a real subject (kids: space, weather, animals, body, festivals…, never the block list; AInation: AI, chips, phones, apps). Sport, celebrities and news are left out. For each kept trend the radar adds the questions people actually search on YouTube ("why does solar eclipse happen").
- **Weekly report (Mondays):** two new sections, "Trending on Google right now" and "Trending on YouTube".
- **Daily check (07:17 IST):** opens a **"Trend alert"** issue (label `trend-alert`) only when something NEW fits, so GitHub emails you; the same trend is never alerted twice in 7 days. Make the Short within 1-3 days: Run workflow → script (paste) → `Next video, publish now`. `RADAR_TRENDS=off` stops the daily check.
- Ideas only: never copy other channels' titles or content.

## 2. Self-check (R6)

- After the normal quality check, English Shorts are "listened to" with **faster-whisper** (MIT, CPU, ~10–60 s) and compared with the script.
- The run summary shows "Self-check: heard 98 % of the script's 202 words", plus the first places where words went missing.
- Below **85 %** it warns (and sends an alert) but still uploads. Listen to that video in Studio before it goes public.
- Hindi and long videos are skipped for now. The install step is optional and non-blocking; `SELFCHECK=off` turns it off.
- Tested on ep081: 100 % with its own script; 19 % with a different episode's script (clear warning).

## 3. Phone alerts (R6)

- Sends: ✅ uploaded (title, link, publish time) · ❌ QC failed · ⚠️ self-check warning · ❌ workflow failed (with the run link).
- **Off until you add secrets** (both repos):
  - **WhatsApp (owner's choice, 2026-11-22):** free CallMeBot service (callmebot.com → "Free API WhatsApp").
    1. Save CallMeBot's number shown on their page in your phone contacts.
    2. From your WhatsApp, send it the activation message shown on that page (e.g. "I allow callmebot to send me messages").
    3. You get an API key back on WhatsApp.
    4. GitHub → each repo → Settings → Secrets → Actions: `WHATSAPP_PHONE` = your number with country code (`+91…`), `WHATSAPP_APIKEY` = the key.
    Personal use only (messages go to your own number); a slow or busy CallMeBot never breaks a run.
    5. Test: Actions → the daily Short workflow → Run workflow → action **Send a test alert (WhatsApp)**. You get a WhatsApp text in a minute; the run summary says `alert sent via: ['whatsapp']`.
  - **Telegram:** create a bot with **@BotFather** → `TELEGRAM_BOT_TOKEN`. Send your bot a message, then open `https://api.telegram.org/bot<token>/getUpdates` and copy `chat.id` → `TELEGRAM_CHAT_ID`.
  - **or Discord:** a channel → Edit → Integrations → Webhooks → copy URL → `DISCORD_WEBHOOK_URL`.
- Never paste these into chat; GitHub Secrets only. Test: Actions → any daily workflow, or locally `python pipeline/notify.py "test"`.
