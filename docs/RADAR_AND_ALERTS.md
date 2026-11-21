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

## 2. Self-check (R6)

- After the normal quality check, English Shorts are "listened to" with **faster-whisper** (MIT, CPU, ~10–60 s) and compared with the script.
- The run summary shows "Self-check: heard 98 % of the script's 202 words", plus the first places where words went missing.
- Below **85 %** it warns (and sends an alert) but still uploads. Listen to that video in Studio before it goes public.
- Hindi and long videos are skipped for now. The install step is optional and non-blocking; `SELFCHECK=off` turns it off.
- Tested on ep081: 100 % with its own script; 19 % with a different episode's script (clear warning).

## 3. Phone alerts (R6)

- Sends: ✅ uploaded (title, link, publish time) · ❌ QC failed · ⚠️ self-check warning · ❌ workflow failed (with the run link).
- **Off until you add secrets** (both repos):
  - **Telegram:** create a bot with **@BotFather** → `TELEGRAM_BOT_TOKEN`. Send your bot a message, then open `https://api.telegram.org/bot<token>/getUpdates` and copy `chat.id` → `TELEGRAM_CHAT_ID`.
  - **or Discord:** a channel → Edit → Integrations → Webhooks → copy URL → `DISCORD_WEBHOOK_URL`.
- Never paste these into chat; GitHub Secrets only. Test: Actions → any daily workflow, or locally `python pipeline/notify.py "test"`.
