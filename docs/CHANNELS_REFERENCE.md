# Channels reference: The CurioKids Club & AInation Studio

**Last updated:** 2026-11-10 09:57 IST (04:27 UTC)

This is the quick reference for both channels: links, schedules, workflow options, secrets and variables. It's updated whenever any of these change; see the change log at the bottom. The full history is in `TheCurioKidsClub_handoff.md` and `AInation_Studio_handoff.md`.

## Channels and links

| Item | The CurioKids Club | AInation Studio |
|---|---|---|
| **GitHub repo** | https://github.com/ambujkhanna/The-CurioKids-Club | https://github.com/ambujkhanna/youtube-studio-automation |
| **YouTube** | @CurioKidsClub (Made for Kids: off, "not made for kids") | @AI.nationstudio (channel ID UCexKyxd_qyUUmFQHKs983nw) |
| **Facebook Page** | https://www.facebook.com/profile.php?id=61596461063065 | https://www.facebook.com/profile.php?id=61596527993377 (Graph Page id 1419246047936930) |
| **Instagram** | https://www.instagram.com/thecuriokidsclub/ | https://www.instagram.com/ai.nationstudio/ |
| **Characters** | Mia (big sister), Leo (little brother), Dad | Dad, Teen |
| **Voices** | Chatterbox (cloned Mia/Leo/Dad) + Turbo for laughs/[tags]; Hindi via multilingual Chatterbox; Kokoro as backup | Chatterbox (cloned Dad/Teen) + Turbo for laughs/[tags]; Kokoro as backup |
| **Meta app** | "Studio Publisher" (shared by both channels) | "Studio Publisher" (shared) |

## Workflows and automatic schedule (IST)

| Item | The CurioKids Club | AInation Studio |
|---|---|---|
| **Daily Shorts workflow** | *Daily Curio Kids Short*: runs 14:10 and 21:10 daily (automatic mode) | *Daily AInation Short*: runs 14:45 daily |
| **Short publish time** | Alternate days: **Hindi 09:00–11:00** (from Mon 9 Nov 2026), **English 17:00–20:00** on the days in between | 17:00–20:00 every day |
| **Weekly long video (16:9)** | *Weekly Curio Kids Long Video*: Saturday 10:00 | *Weekly AInation Long Video*: Sunday 10:00 |
| **Voice Lab** | *Voice Lab (Chatterbox / Turbo voice samples)*: manual only | – |
| **Opening hook** | The episode's question in big yellow letters for the first 2.3 s; curtains start half open (optional `"hook"` field in episode.json overrides the text) | Same (no curtains) |
| **Ending** | Spoken: "…subscribe… and share this with a friend!"; end card with Subscribe / Like / Share + "Search "The CurioKids Club" on YouTube, Instagram, Facebook" | Spoken: "Subscribe to AI Nation Studio, and share this with a friend!"; same end card with "Search "AInation Studio" …" |
| **Caption / description** | Save & share line (IG: "📌 Save this… share it with a curious kid", FB/YouTube share lines) | Same, AI wording |
| **Channel hashtag** | **#TheCurioKidsClub** (always included) | **#AInationstudio** (always included) |
| **Hashtag limits** | YouTube max 15 (channel tag in the first 3, + #Shorts) · Instagram max **5** · Facebook max 10 | same |
| **Facebook / Instagram** | Posted automatically right after each YouTube upload (Reel, designed cover) | Same |
| **Uploads on YouTube** | Private until the API audit; publish or schedule in Studio | Same |

## Run workflow options: Daily Shorts

| Option | What it does | Kids | AInation |
|---|---|---|---|
| **dry_run** ☐ | Render and check only; the MP4 and thumbnail go to Artifacts, nothing is uploaded | ✅ | ✅ |
| **episode** (text) | Force a specific episode, e.g. `ep007`; empty = next in line | ✅ | ✅ |
| **publish_now** ☐ | Publish immediately instead of scheduling | ✅ | ✅ |
| **language** (en / hi) | Hindi voices + English subtitles for a manual run; works with daily episodes **and** categories comedy / quiz | ✅ | – |
| **category** (none / comedy / quiz / knowledge / science / abc / counting / rhymes) | Post the next episode from that category instead of the daily Short | ✅ | – |
| **social_only** ☐ | Post the chosen `episode` to Facebook + Instagram only, no YouTube | ✅ | ✅ |
| **social_backfill** (0–4) | Post that many already-uploaded videos to Facebook/Instagram, oldest first (skips what's already posted) | ✅ | ✅ |
| **refresh_thumbnails** ☐ | Redesign and re-upload thumbnails for all uploaded videos, and update Facebook Reel covers | ✅ | ✅ |
| **script** (text) | **Make a video from your own script**: path like `scripts/bees.txt` (format: `scripts/README.md`); problems stop the run before rendering | ✅ | ✅ |
| **ig_test** ☐ | Instagram check: an 8 s test post; with `episode` filled in, tests 4 versions of it without posting | ✅ | – |
| ~~fix_existing~~ | Removed from the form (GitHub allows 10 options; it needs the full `youtube`-scope token anyway). Still available in code: `daily.py --fix-existing` | – | – |

**Weekly long workflows (both channels):** dry_run, episode, publish_now, social_only, refresh_thumbnails.
**Voice Lab (kids):** `which` = hindi / turbo / chatterbox.

## GitHub Secrets (required, same names in both repos, different values)

| Secret | Purpose |
|---|---|
| `YT_CLIENT_ID`, `YT_CLIENT_SECRET` | Google OAuth app (same values in both repos) |
| `YT_REFRESH_TOKEN` | Per channel: the token for that YouTube channel (scope `youtube.upload`) |
| `META_PAGE_ID` | Facebook Page id |
| `META_PAGE_TOKEN` | Never-expiring Page token (from `me/accounts` with an extended user token) |
| `META_IG_USER_ID` | Instagram Business account id (`instagram_business_account.id`) |

Never paste tokens into chat, files or commits; they go only into GitHub Secrets.

## Repo Variables (optional; defaults apply if not set)

| Variable | Default | Kids | AInation |
|---|---|---|---|
| `TTS_ENGINE` | `chatterbox` (`kokoro` = the old voices) | ✅ | ✅ |
| `CB_TURBO_LAUGHS` | `1` (`0` = no Turbo laughs) | ✅ | ✅ |
| `PUBLISH_WINDOW` | `17:00-20:00` (English Shorts and weekly long video) | ✅ | ✅ |
| `PUBLISH_WINDOW_HI` | `09:00-11:00` (Hindi Shorts) | ✅ | – |
| `MADE_FOR_KIDS` | `false` | ✅ | – |
| `YT_PLAYLIST` | empty (off; videos are added to playlists by hand) | ✅ | – |

## Content in each repo

| Item | The CurioKids Club | AInation Studio |
|---|---|---|
| **Daily Shorts** | `episodes/`: ep002–ep075 (74), each with a Hindi version `hi.json` | `episodes/` (backlog up to EP038) |
| **Weekly long videos** | `long/`: L01–L08 | `long/`: L01–L08 |
| **Your scripts** | `scripts/` (guide `README.md`, `TEMPLATE.txt`, example `how-bees-make-honey.txt`) → made into `custom/<id>/` at run time | `scripts/` (guide, template, example `what-is-a-prompt.txt`) |
| **Category library** | `library/`: comedy COM01–10, quiz QUZ01–10, all with Hindi versions (knowledge, science, abc, counting, rhymes: empty) | – |

## Change log (IST, UTC in brackets; newest last)

| When | Change |
|---|---|
| 2026-11-08 12:32 IST (07:02 UTC) | File created. Kids weekly long workflow: default `PUBLISH_WINDOW` corrected from 16:00-19:00 to 17:00-20:00 (also copied to the repos as `docs/CHANNELS_REFERENCE.md`). |
| 2026-11-08 12:46 IST (07:16 UTC) | **Script → video** for both channels: workflow option `script` (kids: replaces `fix_existing` in the form to stay within 10 options). New `pipeline/script2episode.py`, guide `scripts/README.md`, `scripts/TEMPLATE.txt`, example scripts; progress kept in `custom/state.json`. |
| 2026-11-08 13:09 IST (07:39 UTC) | **Channel hashtags**: #TheCurioKidsClub / #AInationstudio always included, in 2nd place; per-platform limits YouTube 15, Instagram 5, Facebook 10 (`pipeline/hashtags.py`). Hindi videos keep #Hindi in the first three. |
| 2026-11-08 13:38 IST (08:08 UTC) | Kids: **Hindi for categories**: comedy and quiz translated (20 `hi.json`, jokes and riddles rewritten where English puns don't work in Hindi, with replacement boards via `hi.json` `boards`); `category` + `language: hi` now works. Both: clearer messages when a video was deleted ("video not found … (deleted?)"). |
| 2026-11-10 09:57 IST (04:27 UTC) | **Reach**: opening hook (question in the first 2.3 s, 2 lines if long; kids curtains start half open), spoken share line in all endings (kids EN 102, HI 94; AInation 3 that had 'Follow…'), save/share line in IG/FB captions and YouTube descriptions (`hashtags.ENGAGE`), end card 'Search "<channel>" on YouTube, Instagram, Facebook'. No other platforms' logos (Instagram limits reach for them). |
