# Channels reference: The CurioKids Club & AInation Studio

**Last updated:** 2026-11-10 16:24 IST (10:54 UTC)

This is the quick reference for both channels: links, schedules, workflow options, secrets and variables. It's updated whenever any of these change; see the change log at the bottom. The full history is in `TheCurioKidsClub_handoff.md` and `AInation_Studio_handoff.md`.

## Channels and links

| Item | The CurioKids Club | AInation Studio |
|---|---|---|
| **GitHub repo** | https://github.com/ambujkhanna/The-CurioKids-Club | https://github.com/ambujkhanna/youtube-studio-automation |
| **YouTube** | @CurioKidsClub. Audience: **"not made for kids"**, a deliberate owner decision for wider audience and reach (repo variable `MADE_FOR_KIDS`) | @AI.nationstudio (channel ID UCexKyxd_qyUUmFQHKs983nw) |
| **Facebook Page** | https://www.facebook.com/profile.php?id=61596461063065 | https://www.facebook.com/profile.php?id=61596527993377 (Graph Page id 1419246047936930) |
| **Instagram** | https://www.instagram.com/thecuriokidsclub/ | https://www.instagram.com/ai.nationstudio/ |
| **Characters** | Mia (big sister), Leo (little brother), Dad | Dad, Teen |
| **Voices** | Chatterbox (cloned Mia/Leo/Dad) + Turbo for laughs/[tags]; **Hindi: Kokoro native Hindi voices** (Leo slowed); Kokoro as backup | Chatterbox (cloned Dad/Teen) + Turbo for laughs/[tags]; Kokoro as backup |
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
| **Channel hashtag** | **#TheCurioKidsClub**: right after the YouTube title and the first line of FB/IG captions (visible without 'more'), counted once | **#AInationstudio**: same |
| **Hashtag limits** | YouTube max 15 (channel tag in the first 3, + #Shorts) · Instagram max **5** · Facebook max 10 | same |
| **Facebook / Instagram** | Posted automatically right after each YouTube upload (Reel, designed cover; Facebook cover set once processing is done, result in the run summary) | Same |
| **Uploads on YouTube** | Private until the API audit; publish or schedule in Studio | Same |

## Run workflow options: Daily Shorts

| Option | What it does | Kids | AInation |
|---|---|---|---|
| **dry_run** ☐ | Render and check only; the MP4 and thumbnail go to Artifacts, nothing is uploaded | ✅ | ✅ |
| **episode** (text) | Force a specific episode, e.g. `ep007`; empty = next in line | ✅ | ✅ |
| **publish_now** ☐ | Publish immediately instead of scheduling | ✅ | ✅ |
| **language** (en / hi) | Hindi voices + English subtitles for a manual run; works with daily episodes **and** categories comedy / quiz | ✅ | – |
| **category** (none / comedy / quiz / knowledge / science / abc / counting / rhymes / varnamala) | Post the next episode from that category instead of the daily Short | ✅ | – |
| **social_only** ☐ | Post the chosen `episode` to Facebook + Instagram only, no YouTube | ✅ | ✅ |
| **social_backfill** (0–4) | Post that many already-uploaded videos to Facebook/Instagram, oldest first (skips what's already posted) | ✅ | ✅ |
| **refresh_thumbnails** ☐ | Redesign and re-upload thumbnails for all uploaded videos, and update Facebook Reel covers | ✅ | ✅ |
| **script** (text) | **Make a video from your own script**: path like `scripts/bees.txt` (format: `scripts/README.md`); problems stop the run before rendering | ✅ | ✅ |
| **board_style** (default / hanging / display / whiteboard) | Board look for this run only; `default` = repo variable `BOARD_STYLE`, else hanging | – | ✅ |
| **ig_test** ☐ | Instagram check: an 8 s test post; with `episode` filled in, tests 4 versions of it without posting | ✅ | – |
| ~~fix_existing~~ | Removed from the form (GitHub allows 10 options; it needs the full `youtube`-scope token anyway). Still available in code: `daily.py --fix-existing` | – | – |

**Weekly long workflows (both channels):** dry_run, episode, publish_now, social_only, refresh_thumbnails (+ **board_style** on AInation).
**Board look for one AInation video:** Run-workflow `board_style` > episode `"board_style"` / script `BOARD:` line > repo variable `BOARD_STYLE` > `hanging`.
**Voice Lab (kids):** `which` = hindi / turbo / chatterbox. `hindi` = Hindi accent test: every line in versions A (today) / B (cfg 0) / C (Hindi clip) / D (Hindi clip, cfg 0.2).

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
| `BOARD_STYLE` | `hanging` (dark border, ceiling rods) · `display` (3D screen, black bezel) · `whiteboard` (aluminium frame, magnets, marker tray) | – | ✅ |
| `HI_TTS_ENGINE` | `kokoro` (native Hindi voices; `chatterbox` = cloned voices) | ✅ | – |
| `HI_VOICE_CLIP` | `english` (`hindi` = clone Hindi lines from the native Hindi clips in `assets/voices/hi/`) | ✅ | – |
| `CB_CFG_HI` | empty = 0.35 (lower, e.g. `0` or `0.2` = less English accent in Hindi) | ✅ | – |
| `MADE_FOR_KIDS` | `false` | ✅ | – |
| `YT_PLAYLIST` | empty (off; videos are added to playlists by hand) | ✅ | – |

## Content in each repo

| Item | The CurioKids Club | AInation Studio |
|---|---|---|
| **Daily Shorts** | `episodes/`: ep002–ep075 (74), each with a Hindi version `hi.json` | `episodes/` (backlog up to EP038) |
| **Weekly long videos** | `long/`: L01–L08 | `long/`: L01–L08 |
| **Your scripts** | `scripts/` (guide `README.md`, `TEMPLATE.txt`, example `how-bees-make-honey.txt`) → made into `custom/<id>/` at run time | `scripts/` (guide, template, example `what-is-a-prompt.txt`) |
| **Category library** | `library/`: comedy COM01–10, quiz QUZ01–10, all with Hindi versions; **varnamala** VAR01–VAR11 (Hindi alphabet) (knowledge, science, abc, counting, rhymes: empty) | – |

## Change log (IST, UTC in brackets; newest last)

| When | Change |
|---|---|
| 2026-11-08 12:32 IST (07:02 UTC) | File created. Kids weekly long workflow: default `PUBLISH_WINDOW` corrected from 16:00-19:00 to 17:00-20:00 (also copied to the repos as `docs/CHANNELS_REFERENCE.md`). |
| 2026-11-08 12:46 IST (07:16 UTC) | **Script → video** for both channels: workflow option `script` (kids: replaces `fix_existing` in the form to stay within 10 options). New `pipeline/script2episode.py`, guide `scripts/README.md`, `scripts/TEMPLATE.txt`, example scripts; progress kept in `custom/state.json`. |
| 2026-11-08 13:09 IST (07:39 UTC) | **Channel hashtags**: #TheCurioKidsClub / #AInationstudio always included, in 2nd place; per-platform limits YouTube 15, Instagram 5, Facebook 10 (`pipeline/hashtags.py`). Hindi videos keep #Hindi in the first three. |
| 2026-11-08 13:38 IST (08:08 UTC) | Kids: **Hindi for categories**: comedy and quiz translated (20 `hi.json`, jokes and riddles rewritten where English puns don't work in Hindi, with replacement boards via `hi.json` `boards`); `category` + `language: hi` now works. Both: clearer messages when a video was deleted ("video not found … (deleted?)"). |
| 2026-11-10 09:57 IST (04:27 UTC) | **Reach**: opening hook (question in the first 2.3 s, 2 lines if long; kids curtains start half open), spoken share line in all endings (kids EN 102, HI 94; AInation 3 that had 'Follow…'), save/share line in IG/FB captions and YouTube descriptions (`hashtags.ENGAGE`), end card 'Search "<channel>" on YouTube, Instagram, Facebook'. No other platforms' logos (Instagram limits reach for them). |
| 2026-11-10 13:11 IST (07:41 UTC) | Outdated docs fixed after the external audit (ChatGPT plan, points 2–6): kids README (voices, schedule, 45–90 s, audience), kids episodes guide (length), kids SETUP (window, Made for Kids wording); AInation README status, channel README/config (live, 45–90 s, 17–20 IST; config marked as reference only), AUTOMATION_SETUP, DAILY_AUTOMATION marked historical. Owner reconfirmed "not made for kids" as a deliberate choice for reach. |
| 2026-11-10 13:38 IST (08:08 UTC) | **Captions** lighter with clear word gaps (both; AInation SemiBold, thinner outlines, hard space between words). **Fonts:** AInation → M PLUS U (static Latin-only Bold/SemiBold/ExtraBold made from Google Fonts' variable font, OFL); kids Hindi text → Poppins Bold with HarfBuzz shaping. **AInation board** → 3D smart display (thick black bezel with depth, deep shadow, shaded header, recessed screen, glass reflection) with a 0.45 s hinge swing-in. **Kids: varnamala category** (11 Hindi alphabet episodes, letter boards in Hindi, Hindi-aware thumbnails). New `docs/PROJECT_ROADMAP_FOR_AI_AGENTS.md` (brief + capability test for ChatGPT/other agents). |
| 2026-11-10 13:51 IST (08:21 UTC) | **Characters**: arms and legs drawn as thick coloured tubes with a bold outline (trousers on legs, skin forearms, Leo in shorts) instead of thin stick lines, in both channels. Env `LIMBS=stick` restores the old look. |
| 2026-11-10 13:56 IST (08:26 UTC) | AInation: **3 board looks** selectable with the repo variable `BOARD_STYLE` (display / whiteboard / hanging; original drawings inspired by the owner's reference images). Default stays `display`. |
| 2026-11-10 14:08 IST (08:38 UTC) | AInation: **modern UI** inside the board: content stays inside the screen (no avatar cut off by the bezel), messenger-style chat (blue bubble for you on the right, white bubble with avatar for the AI on the left, typing dots), soft-shadow cards, pills that shrink to fit. Kids: owner approved the thick 'tube' limbs (default). |
| 2026-11-10 14:20 IST (08:50 UTC) | AInation: owner chose the **hanging board** as the default look (`BOARD_STYLE` default `hanging` in `bg_line.py` and both workflows). `display` and `whiteboard` still selectable with the repo variable. |
| 2026-11-10 14:35 IST (09:05 UTC) | AInation: board look can be chosen **per video**: new Run workflow option `board_style` (daily and weekly), episode field `"board_style"`, script line `BOARD:`. Order: run option > episode > repo variable `BOARD_STYLE` > hanging. Validator and script check reject unknown looks. |
| 2026-11-10 15:47 IST (10:17 UTC) | Kids: **Hindi accent fix, choose by ear**: native Hindi voice clips `assets/voices/hi/` (Kokoro Hindi voices); repo variables `HI_VOICE_CLIP` (english/hindi) and `CB_CFG_HI`; Voice Lab `hindi` now makes an A/B/C/D comparison on varnamala lines. Default sound unchanged until the owner picks. |
| 2026-11-10 15:53 IST (10:23 UTC) | Kids: owner approved the Kokoro native Hindi sample → **Hindi videos now use Kokoro's Hindi voices** (repo variable `HI_TTS_ENGINE`, default `kokoro`); English stays on Chatterbox. Leo's Hindi voice slowed (speed 1.05 → 0.92). |
| 2026-11-10 16:24 IST (10:54 UTC) | Both: owner saw no channel hashtag and no designed cover on a new AInation video (ep011). **Channel tag now right after the title** on YouTube and in the first line of Facebook/Instagram captions (Shorts/Reels hide the description); tag counted once so Instagram stays at 5. **Facebook cover** is set after Facebook finishes processing (it silently failed when set straight after upload); the run summary shows `cover set` / `designed cover`. Old Facebook covers: run `refresh_thumbnails`. Old YouTube titles stay as they are (changing them needs a wider token). |
