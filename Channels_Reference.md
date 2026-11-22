# Channels reference: The CurioKids Club & AInation Studio

**Last updated:** 2026-11-22 11:30 IST (06:00 UTC)

This is the quick reference for both channels: links, schedules, workflow options, secrets and variables. It's updated whenever any of these change; see the change log at the bottom. The full history is in `TheCurioKidsClub_handoff.md` and `AInation_Studio_handoff.md`.

## Channels and links

| Item | The CurioKids Club | AInation Studio |
|---|---|---|
| **GitHub repo** | https://github.com/ambujkhanna/The-CurioKids-Club | https://github.com/ambujkhanna/youtube-studio-automation |
| **YouTube** | @CurioKidsClub. Audience: **"not made for kids"**, a deliberate owner decision for wider audience and reach (repo variable `MADE_FOR_KIDS`) | @AI.nationstudio (channel ID UCexKyxd_qyUUmFQHKs983nw) |
| **Facebook Page** | https://www.facebook.com/TheCurioKidsClub | https://www.facebook.com/AI.nationStudio (Graph Page id 1419246047936930) |
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
| **Topic radar** | *Weekly topic radar*: Mondays 08:47 → GitHub issue with topics + viewers' requests | same |
| **Opening hook** | The episode's question in big yellow letters for the first 2.3 s; curtains start half open (optional `"hook"` field in episode.json overrides the text) | Same (no curtains) |
| **Intro** | **Shorts: none** (since 2026-11-22: they open straight on the question hook; `SHORT_INTRO=on` brings it back). Long videos: 2 s logo intro + music sting. **Rule:** whenever an intro is used, it shows the video's topic big at the top (instead of "Welcome to"), because the Shorts feed shows no thumbnail | same |
| **Ending** | Spoken: "…subscribe… and share this with a friend!"; end card Subscribe / Like / Share; then 3.5 s **"Find us online"** card with the YouTube, Facebook, Instagram links (`OUTRO`) | Spoken: "Subscribe to AI Nation Studio, and share this with a friend!"; same end card + links card |
| **Caption / description** | Save & share line (IG: "📌 Save this… share it with a curious kid", FB/YouTube share lines) + **'🔗 Find us online' block with the YouTube, Facebook, Instagram links** (YouTube description + Facebook caption; Instagram captions can't have clickable links) | Same, AI wording |
| **Channel hashtag** | **#TheCurioKidsClub**: right after the YouTube title and the first line of FB/IG captions (visible without 'more'), counted once | **#AInationstudio**: same |
| **Hashtag limits** | YouTube max 15 (channel tag in the first 3, + #Shorts) · Instagram max **5** · Facebook max 10 | same |
| **Facebook / Instagram** | Posted automatically right after each YouTube upload (Reel, designed cover; Facebook cover set once processing is done, result in the run summary) | Same |
| **Uploads on YouTube** | Private until the API audit; publish or schedule in Studio | Same |

## Run workflow options (same form in both channels, since 2026-11-14)

| # | Option | Choices | Kids | AInation |
|---|---|---|---|---|
| 1 | **action** | **Next video (scheduled)** (default) · Next video, publish now · Dry run (render only, nothing uploaded) · Refresh thumbnails · Post 1 / 3 old videos to Facebook + Instagram | ✅ | ✅ |
| 2 | **post_to** | **YouTube + Facebook + Instagram** (default) · YouTube only · Facebook + Instagram only · YouTube + Facebook · YouTube + Instagram · Facebook only · Instagram only. Without YouTube = posts the chosen episode to the social platforms only | ✅ | ✅ |
| 3 | **episode** | Episode id, e.g. `ep014`, `s-ollama`; empty = next in line. With *Refresh thumbnails*: only that video | ✅ | ✅ |
| 4 | **script** | A file path (`scripts/bees.txt`) **or the whole script pasted in** (format: `scripts/README.md`); problems stop the run before rendering | ✅ | ✅ |
| 5 | **language** | en / hi (Hindi voices + English subtitles; daily episodes and comedy / quiz / varnamala) | ✅ | – |
| 6 | **category** | none / comedy / quiz / knowledge / science / abc / counting / rhymes / varnamala | ✅ | – |
| 5 | **board_style** | default / hanging / display / whiteboard (this run only) | – | ✅ |

**Weekly long workflows (both):** action (scheduled / publish now / dry run / refresh thumbnails), post_to (YouTube + Facebook · YouTube only · Facebook only), episode (+ board_style on AInation).
**Scheduled runs** ignore the form: daily next video, every platform. **Removed:** `ig_test` (Instagram works; `daily.py --ig-test` still exists in code), `fix_existing`.
**Other workflows (both):** *YouTube Analytics — collect report* (daily 17:30 IST, manual with optional dates; read-only; 90-day report artifact + growth brief) · *Growth tests* (unit tests for analytics/growth). The daily Short run shows the latest growth brief in its summary (advisory, never blocks the run).
**Voice Lab (kids):** `which` = hindi / turbo / chatterbox.

## GitHub Secrets (required, same names in both repos, different values)

| Secret | Purpose |
|---|---|
| `YT_CLIENT_ID`, `YT_CLIENT_SECRET` | Google OAuth app (same values in both repos) |
| `YT_REFRESH_TOKEN` | Per channel: the token for that YouTube channel (scope `youtube.force-ssl` since 2026-11-22: uploads, playlists, subtitles, charts) |
| `META_PAGE_ID` | Facebook Page id |
| `META_PAGE_TOKEN` | Never-expiring Page token (from `me/accounts` with an extended user token) |
| `META_IG_USER_ID` | Instagram Business account id (`instagram_business_account.id`) |
| `YT_ANALYTICS_REFRESH_TOKEN` | Per channel, **read-only** analytics token (scope `yt-analytics.readonly`), separate from the upload token; if missing, the analytics job skips quietly |

| `YT_API_KEY` | Optional: free Data API key for the topic radar's competition check and comments (needed on AInation, whose upload token is upload-only) |
| `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | Optional: phone alerts via a Telegram bot (uploaded / QC failed / self-check warning / run failed) |
| `DISCORD_WEBHOOK_URL` | Optional: the same alerts to a Discord channel |

Never paste tokens into chat, files or commits; they go only into GitHub Secrets.

## Repo Variables (optional; defaults apply if not set)

> Full list with every value, secret and run option: **`CONFIGURATION.md`** (repo root).

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
| `CTA_STYLE` | kids `bar` · AInation `pop` (`card` = the old card with small buttons) | ✅ | ✅ |
| `THEME` | `studio_open` (clean light studio, no board frame, one blue accent, calmer outfits) · `studio_light` (same with a white board card) · `studio_dark` (deep navy + white card) · `classic` (the old living room) | – | ✅ |
| `LIST_STYLE` | `tiles` (steps/checklist/summary as airy tiles; 5 steps = timeline; `classic` = old full-width rows) | ✅ | ✅ |
| `ICON_STYLE` | `house` (our realistic icons, curated mix: weather/symbols/white things stay emoji) · `house_all` (every house icon) · `3d` (Fluent only) · `flat` (old flat icons) | ✅ | ✅ |
| `THUMB_STYLE` | `punch` (big wow faces, 1–3 huge words, "A → B" pictures with a red arrow; `classic` = the old design) | ✅ | ✅ |
| `THUMB_MARK` | `sticker` ("WHY?/HOW?/WHAT?" speech bubble on the answer picture) · `glow` · `mystery` (dark outline + ?) · `circle` (red circle) | ✅ | ✅ |
| `STOCK` | AInation `on`, kids `off` (owner: real photos look pasted-in on the kids channel). On = real photos (Openverse/NASA) and NASA clips for `photo` / `clip` boards; off = those boards become icon boards | ✅ | ✅ |
| `STOCK_STYLE` | `plain` (photo fills the card) · `polaroid` (tilted snapshot, tape, REAL! sticker) | – | ✅ |
| `RADAR` | `on` (weekly topic radar issue; `off` = no radar) | ✅ | ✅ |
| `SELFCHECK` | `on` (faster-whisper listens to English Shorts and compares with the script; warns below 85 %, never blocks) | ✅ | ✅ |
| `CHAR_STYLE` | `doodle` (`polished` = clean single outline, soft light edge and shadow, second eye sparkle; same shapes and rig) | ✅ | ✅ |
| `ART` | `on` (HD background pictures from `assets/art/`; `off` = the drawn playroom and stage everywhere) | ✅ | – |
| `ART_AUTO` | `on` (episodes/scripts without a `backdrop` get one picked from the title; `off` = drawn playroom for those) | ✅ | – |
| `PANEL` | empty = automatic (glass card on a picture, puppet stage without); `stage` / `card` / `cloud` / `book` force one look | ✅ | – |
| `BACKDROP` | empty (tests only: forces one background picture for every video) | ✅ | – |
| `SHORT_INTRO` | `off` (Shorts start straight with the content; `on` = 2 s intro **with the topic** at the top) | ✅ | ✅ |
| `SHORT_OUTRO` | empty = follow `OUTRO` (`off` = no 'Find us online' links card on Shorts) | ✅ | ✅ |
| `KEEP_THUMBS` | `2` (each upload run re-applies the designed thumbnail of this many recent videos from the last 3 days; `0` = off) | ✅ | ✅ |
| `YT_TIMEOUT` | `300` seconds per YouTube call | ✅ | ✅ |
| `INTRO` / `OUTRO` | `on` (`off` = no logo intro / no links card) | ✅ | ✅ |
| `MADE_FOR_KIDS` | `false` | ✅ | – |
| `YT_PLAYLIST` | empty (off; videos are added to playlists by hand) | ✅ | – |

## Content in each repo

| Item | The CurioKids Club | AInation Studio |
|---|---|---|
| **Daily Shorts** | `episodes/`: ep002–ep075 (74), each with a Hindi version `hi.json` | `episodes/` (backlog up to EP038) |
| **Weekly long videos** | `long/`: L01–L08 | `long/`: L01–L08 |
| **Your scripts** | `scripts/` (guide `README.md`, `TEMPLATE.txt`, example `how-bees-make-honey.txt`) → made into `custom/<id>/` at run time | `scripts/` (guide, template, example `what-is-a-prompt.txt`) |
| **HD pictures** | `assets/art/`: 11 backgrounds + 8 picture-board close-ups (FLUX.1-schnell, Apache 2.0; `manifest.json`); guide `docs/HD_ART.md` | – (plain Studio Open look) |
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
| 2026-11-11 12:26 IST (06:56 UTC) | Both: **paste a whole script** into the Run-workflow `script` box (split back into lines; saved to Artifacts as `pasted-<title>.txt`; the input now reaches the pipeline via the `SCRIPT_IN` env, safe for quotes). **End card buttons** sized to their text with padding; 'Search …' strip removed. **Intro** (2 s, logo + music sting) and **'Find us online' links card** (3.5 s) around every video (`pipeline/bumpers.py`, repo variables `INTRO` / `OUTRO`); kids logo `assets/brand/logo.png`. |
| 2026-11-11 12:31 IST (07:01 UTC) | Both: **Facebook links** are now the Pages' own names everywhere (videos' 'Find us online' card, READMEs, reference, handoffs): https://www.facebook.com/TheCurioKidsClub and https://www.facebook.com/AI.nationStudio (owner: always use these). |
| 2026-11-11 12:33 IST (07:03 UTC) | AInation: Facebook link corrected to **https://www.facebook.com/AI.nationStudio** (owner) everywhere. |
| 2026-11-11 12:34 IST (07:04 UTC) | Both: the 3 channel links (YouTube, Facebook, Instagram) are added to every new **YouTube description** and **Facebook caption** ('🔗 Find us online' block, `hashtags.links_block()`); Instagram captions stay without links (not clickable there). Already-posted videos keep their old text. |
| 2026-11-11 13:27 IST (07:57 UTC) | Both: **text can no longer run past the board** (every board text shrinks to the board's width; one-line titles keep shrinking instead of overflowing; script title boards keep the full title, cut only between words with '…'). **Speech:** version numbers and web addresses are said naturally: 'llama3.2' → 'llama 3 point 2', 'ollama.com' → 'ollama dot com' (Hindi: दशमलव / डॉट); boards and files keep the original text. |
| 2026-11-11 22:24 IST (16:54 UTC) | Both: **no more endless runs**: every YouTube call has a 5-minute limit (repo variable `YT_TIMEOUT`, seconds), Facebook cover updates 2 minutes; `refresh_thumbnails` runs skip the Chatterbox install; Ubuntu package step retries and stops after 15 min; logs print live. (After two thumbnail-refresh runs hung for 30+ min.) |
| 2026-11-12 13:16 IST (07:46 UTC) | Both: **thumbnails stick**: a fresh thumbnail file per video (an older video's thumbnail can never be uploaded by mistake), the new video's thumbnail is set again after the Facebook/Instagram posting, each upload run re-applies the thumbnails of the last 2 videos (3 days, Hindi included; `KEEP_THUMBS`), `refresh_thumbnails` also covers Hindi videos. Note: the 14 h runs had finished in 43 min (the page shows the finish time); jobs are capped at 2 h (long videos 4 h). |
| 2026-11-12 13:18 IST (07:48 UTC) | Both: script videos (`custom/`) and kids category videos are now included in `refresh_thumbnails` and in the automatic re-apply of recent thumbnails; `refresh_thumbnails` + `episode` refreshes one video only (e.g. `s-ollama`, whose YouTube thumbnail had been replaced by a video frame). |
| 2026-11-14 09:27 IST (03:57 UTC) | Both: **YouTube uploads fixed**. The 12 Nov time-limit change (custom connection) treated YouTube's '308 Resume Incomplete' as a redirect, so every video upload failed after the first 8 MB chunk ('Redirected but the response is missing a Location header'). Fix (owner's commit 6b67c7d on kids, same change now for AInation): 308 removed from redirect handling, as the YouTube library does by default; 5 retries per chunk. Verified with a 20 MB 3-chunk upload against a fake YouTube server. |
| 2026-11-14 09:44 IST (04:14 UTC) | Both: **simpler, identical Run-workflow forms**: `action` dropdown replaces dry_run / publish_now / refresh_thumbnails / social_backfill; `post_to` dropdown replaces social_only (choose any combination of YouTube, Facebook, Instagram; default all); `ig_test` removed. Daily forms now 5 (AInation) / 6 (kids) options, weekly 4 / 3. Form values reach the pipeline as environment variables; the episode id is checked. |
| 2026-11-21 13:04 IST (07:34 UTC) | AInation: **ep022–ep029 rewritten** (they came from a generic template: board text cut mid-word, the same ending in every video, Dad doing the explaining); ep026 has a new angle (*How to Keep AI on Track in a Long Project*, not a repeat of ep019), ep022 is now *Can AI Work Without Internet?* (not a repeat of the Ollama video). 20 `ai-concepts` scripts now pass the script check (9 lines), six carry an overlap note. Both: growth-brief step can't block a run; analytics secret + workflows added here; roadmap decision 5 notes the analytics SQLite exception; growth-engine logs moved to `docs/GROWTH_ENGINE_LOG.md`. |
| 2026-11-21 13:17 IST (07:47 UTC) | Both: **animated scenes + 3D icons** (first version). Every board icon is now a glossy 3D icon (Microsoft Fluent Emoji 3D, MIT; downloaded once per run, old flat icon if unavailable; `ICON_STYLE=flat` to switch back). New animated board types `lifecycle`, `transform`, `flow`, `water_cycle`, `plant_growth` (`pipeline/scenes.py`, guide `docs/ANIMATED_SCENES.md`); writing rule: use a scene whenever a line explains change, a process or a cycle. First uses: kids ep070 (seed → tree: 3 scenes), ep066 (butterfly: 2), ep012 (water cycle, for its Hindi version); AInation ep029 (flow), ep027 (transform). Scenes have more breathing room (smaller, lighter labels). |
| 2026-11-21 13:38 IST (08:08 UTC) | Both: **lighter list boards**: steps / checklists / recaps are airy tiles (big 3D icon + short label, pop in on cue; checklists with 3D ✅/❌), 5-step lists a slim highlighted timeline; `LIST_STYLE=classic` for the old rows. Chosen from 3 rendered designs (tiles, hub, timeline); hub dropped (too cramped on a phone board). |
| 2026-11-21 13:55 IST (08:25 UTC) | AInation: **new look, Studio Open** (owner's choice from 4 rendered looks): no living room, props, rug, floating robot or string lights; soft grey-white wall with two quiet blurred accent shapes and dot grids; no board frame (content sits on the wall like an infographic); one blue accent (#2F6BFF) for pills, title card and flow rings; white tiles with hairline borders; captions highlight in blue (hook white with a blue outline); calmer outfits (Dad slate-blue shirt, Teen teal hoodie). Thumbnails keep their bold design on purpose (click-through). Repo variable `THEME` switches looks (`classic` = old). Kids unchanged. |
| 2026-11-21 15:16 IST (09:46 UTC) | AInation (Studio Open): speaker close-ups are off, because without a board frame they pushed the content half out of the picture (cut text at the top). Both: script title-card labels keep whole words (up to 28 characters, wrapping to 2 lines) instead of being cut at 12 letters ("SMALL LANGUA"). |
| 2026-11-21 15:50 IST (10:20 UTC) | Kids: **fun-facts series** ep076–ep083, ep090–ep097, ep104–ep112 (25 episodes incl. soil Part 1/2, English + Hindi) posted **first** from the next day (episode field `order` 1–25; the old queue resumes after it: English ep013, Hindi ep009). Every new episode ends with a spoken 'drop a topic in the comment section' line; the end card shows a 'Drop a topic in the comments!' bubble (both channels). **End cards:** kids = action bar (3 round 3D buttons, finger taps), AInation = big pop (one big button at a time + confetti); repo variable `CTA_STYLE` (`card` = old). |
| 2026-11-21 18:50 IST (13:20 UTC) | Kids: **HD backgrounds** (11 clay-style pictures made on a free Kaggle GPU with FLUX.1-schnell, Apache 2.0) on every video: each episode has a reviewed `backdrop`, scripts pick one from the title or set `BACKDROP:`; **glass card** instead of the puppet stage on pictures; gentle camera push-ins and glides (no half-cut board); items rise and fade in; logo pill; **picture boards** (ep079, ep096, ep097, ep104, ep107); thumbnails and 16:9 long videos use the picture. New variables `ART`, `ART_AUTO`, `PANEL`, `BACKDROP`, `SHORT_INTRO`/`SHORT_OUTRO`. Both: `CHAR_STYLE` (`doodle` default, `polished` option). AInation keeps its plain Studio Open look. |
| 2026-11-21 20:05 IST (14:35 UTC) | Both: **punchy thumbnails** (owner's pick of 4 highlight styles: the speech-bubble sticker): characters big with a wow face, the explainer pointing at the answer, 1–3 huge words, "A → B" pictures with a red arrow and a WHY?/HOW?/WHAT? sticker, PART N ribbon for series; Shorts and 16:9. Variables `THUMB_STYLE` (punch/classic), `THUMB_MARK` (sticker/glow/mystery/circle). Kids: the HINDI tag moved to a corner. AInation: the "AI EXPLAINED" tag is removed from every board look (owner). |
| 2026-11-21 23:20 IST (17:50 UTC) | Both: **realistic house icons** (151, `assets/icons_house/*.webp`, FLUX.1-schnell + rembg, `tools/kaggle/icons_v1.ipynb`): curated mix by owner's choice (weather, symbols, mostly-white objects and the robot stay emoji: `PREFER_EMOJI`); nothing deleted: `"house:<emoji>"` forces ours, `ICON_STYLE=house_all` uses all; house-only science pictures by name (`w_heart_model`, `w_soil_block`, `w_ai_chip`…). `ICON_STYLE` default now `house`. |
| 2026-11-22 00:15 IST (18:45 UTC) | Both: **real photos and NASA clips** (roadmap R1): new board types `photo` and `clip` (`pipeline/stock.py`), sources NASA (space) + Openverse (CC0/PDM/CC BY only), no keys; credits added to the YouTube description; cache `assets/stock/` (gitignored); fallback to an icon board; variable `STOCK`. Not used in any episode yet (owner to choose where). |
| 2026-11-22 00:50 IST (19:20 UTC) | Owner reviewed real photos: fine for AInation, not for kids (pasted-in look, also as polaroids; a paint filter looked muddy). Kids workflows default `STOCK=off`; AInation `STOCK=on`, `STOCK_STYLE=plain` (polaroid style available). |
| 2026-11-22 02:10 IST (20:40 UTC) | Both: **topic radar** (R2+R3: weekly issue with search-suggestion topics, competition, our own search terms, viewers' comment requests; `pipeline/radar.py`, workflow *Weekly topic radar*, variable `RADAR`, optional secret `YT_API_KEY`), **self-check** (R6: faster-whisper vs script, warns below 85 %; `SELFCHECK`), **phone alerts** (Telegram/Discord secrets; uploaded / QC failed / self-check warning / run failed). AInation: real photos pinned in ep031 and ep036 (ep033 back to an icon board: its photo was unclear) (`pin` = reviewed photo, no new search). R4 subtitles wait for a login with the caption scope. |
| 2026-11-22 03:10 IST (21:40 UTC) | Kids: the opening hook no longer overlaps the glass card (it sits in the middle of the still-empty card for 0–2.3 s and the first board pops in after it; engine writes `hook_in_card` to build/shots.json, finish.py reads it). Both: photo boards use our realistic 3D art first (`"art"` → assets/art), raw photos only as the fallback (owner's preference); AInation Kaggle notebook `tools/kaggle/art_ain_v1.ipynb` (21 key visuals for ep023–ep043); ep031/ep036 linked to `ain_jobs_ai` / `ain_health_scan`. |
| 2026-11-22 10:20 IST (04:50 UTC) | Art v3 (one merged Kaggle run, `tools/kaggle/art_v3_both.ipynb`): kids 13 realistic 3D picture-board images (incl. a 3D child blinking, shivering, spinning) used in 10 fun-facts episodes; AInation 20 realistic 3D key visuals used as `photo` boards with `"art"` in 18 upcoming episodes (3D art first, raw photo fallback). Rejected: apple/straw/eyebrows (wrong or missing effect), bath-time child images, AInation family rules (logo, made-up text). |
| 2026-11-22 10:45 IST (05:15 UTC) | Owner wants to test starting Shorts straight with the content (views). AInation's Shorts workflow now also reads `SHORT_INTRO` / `SHORT_OUTRO` (kids already did). Test: set `SHORT_INTRO=off` in both repos, compare 'Viewed vs swiped away' in YouTube Studio after 1–2 weeks; delete the variable to bring the intro back. |
| 2026-11-22 11:30 IST (06:00 UTC) | Both: **no intro on Shorts** by default (owner). If an intro is used (long videos, or `SHORT_INTRO=on`), it shows the topic big at the top instead of "Welcome to" (`bumpers.topic_from`, Hindi title for Hindi versions). |
| 2026-11-22 12:40 IST (07:10 UTC) | Kids intro: animated **blasting sparklers** (firework bursts behind the title/logo; no poppers). Both: new **`CONFIGURATION.md`** with every variable, secret and run option. |
| 2026-11-22 13:10 IST (07:40 UTC) | Both: phone alerts can go to **WhatsApp** (free CallMeBot; secrets `WHATSAPP_PHONE`, `WHATSAPP_APIKEY`). |
| 2026-11-22 15:30 IST (10:00 UTC) | Kids: **Spanish Shorts**, one a day (05:30-07:30 IST, own queue, `ES_SHORTS`), Spanish voices/captions/boards/thumbnails, 81 episodes with es.json, playlist `CurioKids_Spanish`; English + Hindi → `curiokids`. Guide: `docs/SPANISH.md`. |
| 2026-11-22 17:00 IST (11:30 UTC) | Both: **fixed blinking icons** (3D icons prefetched once before the parallel render, incl. end-card SUBSCRIBE/LIKE/SHARE icons). Run option 'Send a test alert (WhatsApp)'. |
| 2026-11-22 18:30 IST (13:00 UTC) | Both: radar adds **Google Trends + YouTube trending** (weekly) and a **daily Trend alert** issue (07:17 IST) when a new trend fits; `RADAR_TRENDS`, `RADAR_GEOS`. |
| 2026-11-22 20:30 IST (15:00 UTC) | Both: owner renewed `YT_REFRESH_TOKEN` with `youtube.force-ssl`. **Subtitles (R4)**: exact caption tracks from our script + timing after each upload (English; Spanish video es+en; Hindi video hi+en) + translated titles/descriptions (kids: from es.json/hi.json). `SUBS`, `SUBS_TRACKS` (quota: 400 units per track). |
