# Configuration: every variable, secret and run option

**Same file in both repos** (`ambujkhanna/The-CurioKids-Club` and `ambujkhanna/youtube-studio-automation`). Last updated 2026-11-22 (IST).
When you add or change a variable, update this file in both repos and add a line to the change log at the bottom.

## Where to set things

| What | Where in GitHub | Who can see the value |
|---|---|---|
| **Variables** (switches, styles, times) | repo → Settings → Secrets and variables → Actions → **Variables** tab → New repository variable | anyone with repo access |
| **Secrets** (keys, tokens) | same page → **Secrets** tab → New repository secret | nobody (GitHub hides them) |
| **Run options** (one run only) | repo → Actions → pick the workflow → **Run workflow** | shown in the run log |

- A variable you never create uses the **default** shown below. Delete a variable to go back to the default.
- Values are not case-sensitive (`on`, `On`, `ON` all work). For on/off switches, `off`, `0`, `no`, `false` all mean off.
- **Never paste a secret into chat, a file or a commit.** Secrets go only in GitHub Secrets (or Kaggle Secrets for `HF_TOKEN`).

---

## 1. Repo variables: look and style

| Variable | Kids default | AInation default | Values and what they do |
|---|---|---|---|
| `THEME` | (not used: kids look) | `studio_open` | AInation room look: `classic` (old living room) · `studio_light` · `studio_dark` · `studio_open` (light studio, no board frame; **chosen**) |
| `BOARD_STYLE` | – | `hanging` | AInation board look: `hanging` · `display` · `whiteboard`. The long-video **Run workflow** box can override it for one run |
| `PANEL` | empty = automatic | – | Kids board look: empty = glass `card` when a HD background is on, else `stage` · force `stage` · `card` · `cloud` · `book` |
| `ART` | `on` | – | Kids HD clay backgrounds and picture boards (`assets/art/`). `off` = old drawn playroom, picture boards fall back to icon boards |
| `ART_AUTO` | `on` | – | Kids: pick a background by topic automatically. `off` = only episodes that name a `"backdrop"` get one |
| `BACKDROP` | empty | – | Tests only: force one background by file name for every video (`none` = drawn room) |
| `ICON_STYLE` | `house` | `house` | `house` = curated mix (our 151 house icons where they look best, Fluent 3D for the rest) · `house_all` = house icon whenever one exists · `3d` = Fluent 3D only · `flat` = old flat icons |
| `CHAR_STYLE` | `doodle` | `doodle` | Presenter drawing: `doodle` (hand-drawn) · `polished` (cleaner lines) |
| `STOCK` | `off` | `on` | Real photos/clips (NASA + Openverse, free licences, credited in the description). Kids `off` because photos looked "pasted"; 3D art is always tried first |
| `STOCK_STYLE` | – | `plain` | How a real photo is shown: `plain` (fills the card) · `polaroid` (tilted snapshot + "REAL!" sticker) |
| `LIST_STYLE` | `tiles` | `tiles` | List boards: `tiles` (cards with icons) · `classic` (old plain list) |
| `CTA_STYLE` | `bar` | `pop` | End "subscribe" moment: `bar` (action bar) · `pop` (big pop) · `card` (old end card) |
| `THUMB_STYLE` | `punch` | `punch` | Thumbnails: `punch` (big words, presenter, picture) · `classic` (old style) |
| `THUMB_MARK` | `sticker` | `sticker` | How the picture is highlighted on a punch thumbnail: `sticker` (speech-bubble sticker under the picture; **chosen**) · `circle` · `glow` |
| `KEEP_THUMBS` | `2` | `2` | How many old thumbnail files to keep per video (0 = keep none) |

## 2. Repo variables: intro, outro, publishing

| Variable | Kids default | AInation default | Values and what they do |
|---|---|---|---|
| `INTRO` | `on` | `on` | Logo intro on **long videos** (2 s, shows the topic; kids version has blasting sparklers) |
| `SHORT_INTRO` | `off` | `off` | Logo intro on **Shorts**. Off since 2026-11-22: Shorts start straight with the hook (better for "viewed vs swiped away"). Rule: any intro must show the title/topic |
| `OUTRO` | `on` | `on` | "Find us online" end card on long videos (and Shorts, unless `SHORT_OUTRO` says otherwise) |
| `SHORT_OUTRO` | empty = follow `OUTRO` | empty = follow `OUTRO` | `off` = no end card on Shorts |
| `PUBLISH_WINDOW` | `17:00-20:00` | `17:00-20:00` | IST time window the upload is scheduled inside (English videos) |
| `PUBLISH_WINDOW_HI` | `09:00-11:00` | – | Kids Hindi videos' window |
| `MADE_FOR_KIDS` | `false` | – | YouTube "made for kids" flag. `false` keeps comments and the end screen on (needed for the topic radar's "viewers asked") |
| `YT_PLAYLIST` | empty | – | Playlist id to add each kids upload to (empty = none) |
| `YT_TIMEOUT` | `300` | `300` | Seconds before a YouTube upload call gives up |

## 3. Repo variables: voices

| Variable | Kids default | AInation default | Values and what they do |
|---|---|---|---|
| `TTS_ENGINE` | `chatterbox` | `chatterbox` | Voice engine: `chatterbox` (MIT, more natural) · `kokoro` (Apache 2.0, faster; automatic fallback) |
| `CB_TURBO_LAUGHS` | `1` | `1` | `1` = Chatterbox Turbo for lines with laughs/sighs · `0` = never |
| `HI_TTS_ENGINE` | `kokoro` | – | Hindi voice engine: `kokoro` · `chatterbox` |
| `HI_VOICE_CLIP` | `english` | – | Chatterbox Hindi: which reference voice clip to copy, `english` · `hindi` |
| `CB_CFG_HI` | empty (= 0.35) | – | Chatterbox Hindi "cfg" (lower = less English accent), e.g. `0.2` |

## 4. Repo variables: growth tools

| Variable | Kids default | AInation default | Values and what they do |
|---|---|---|---|
| `RADAR` | `on` | `on` | Weekly topic radar issue (Mondays 03:17 UTC): what people search for + what viewers asked. See `docs/RADAR_AND_ALERTS.md` |
| `SELFCHECK` | `on` | `on` | After rendering, faster-whisper listens to the video and compares it with the script; flags garbled or silent audio |

## 5. Secrets

| Secret | Needed? | Used by | What it is |
|---|---|---|---|
| `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN` | **required** for uploads | daily/long workflows, radar | YouTube upload login (Google OAuth app + refresh token) |
| `YT_ANALYTICS_CLIENT_ID`, `YT_ANALYTICS_CLIENT_SECRET`, `YT_ANALYTICS_REFRESH_TOKEN` | optional | analytics, radar | YouTube Analytics login (our own search terms, retention). Missing = those parts are skipped |
| `YT_API_KEY` | optional | radar | YouTube Data API key: competition check for radar topics. Missing = suggestions only |
| `META_PAGE_ID`, `META_PAGE_TOKEN`, `META_IG_USER_ID` | optional | daily/long workflows | Facebook Page + Instagram posting. Missing = YouTube only |
| `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | optional | daily/long workflows | "✅ posted / ❌ failed" alert to your phone |
| `DISCORD_WEBHOOK_URL` | optional | daily/long workflows | Same alerts to a Discord channel |
| `GITHUB_TOKEN` | automatic | radar | Given by GitHub to every run (opens the radar issue). Nothing to set |
| `HF_TOKEN` (**Kaggle Secret**, not GitHub) | for art runs | `tools/kaggle/*.ipynb` | Hugging Face read token so Kaggle can download FLUX.1-schnell |
| `KAGGLE_USERNAME`, `KAGGLE_KEY` | planned (R7) | weekly art run | Kaggle API token. Not used yet; see `docs/AUTOMATION_KAGGLE.md` |

Variables planned but **not built yet** (`docs/AUTOMATION_KAGGLE.md`, `docs/ROADMAP_FREE_TOOLS.md`): `ART_WEEKLY`, `ART_AUTO_COMMIT`, `ART_DAYS`, `ART_OLLAMA`, `OLLAMA_MODEL`, `SUBS`, `SUBS_LANGS`, `RADAR_SEEDS_EXTRA`, `STOCK_PEOPLE`, `PIXABAY_API_KEY`, `PEXELS_API_KEY`.

---

## 6. Run options (Actions → workflow → Run workflow)

| Workflow | Kids file | AInation file | Schedule (UTC → IST) |
|---|---|---|---|
| Daily Short | `curio-kids-short.yml` | `daily-short.yml` | Kids 08:40 + 15:40 (14:10 + 21:10 IST) · AInation 09:23 (14:53 IST) |
| Weekly long video | `curio-kids-long.yml` | `weekly-long.yml` | Kids Sat 04:30 (10:00 IST) · AInation Sun 04:37 (10:07 IST) |
| Topic radar | `topic-radar.yml` | `topic-radar.yml` | Mon 03:17 (08:47 IST) |
| YouTube analytics | `youtube-analytics.yml` | `youtube-analytics.yml` | daily 12:00 (17:30 IST) |
| Growth tests | `growth-tests.yml` | `growth-tests.yml` | automatic on pull requests that touch `pipeline/growth.py` or `tests/` |
| Voice lab (kids) | `voice-lab.yml` | – | manual: `which` = `hindi` · `turbo` · `chatterbox` sample voices |

Boxes in the Run workflow form (Short and long workflows):

| Box | Values |
|---|---|
| **action** | `Next video (scheduled)` · `Next video, publish now` · `Dry run (render only, nothing uploaded)` · `Refresh thumbnails` · `Post 1 old video to Facebook + Instagram` · `Post 3 old videos to Facebook + Instagram` (long workflows have fewer) |
| **post_to** | `YouTube + Facebook + Instagram` · `YouTube only` · `Facebook + Instagram only` · `YouTube + Facebook` · `YouTube + Instagram` · `Facebook only` · `Instagram only` |
| **episode** | an episode id (`ep094`, `s-ollama`); empty = next in line. With *Refresh thumbnails* = only that video |
| **script** | (Shorts) a file path like `scripts/bees.txt` or the whole script pasted (format: `scripts/README.md`) → becomes `custom/<id>/` |
| **language** | (kids Shorts) `en` · `hi` (Hindi voices + English subtitles) |
| **category** | (kids Shorts) make a category video instead of the daily Short: `none` (normal) · `comedy` · `quiz` · `knowledge` · `science` · `abc` · `counting` · `rhymes` · `varnamala` |
| **board_style** | (AInation long) `default` · `hanging` · `display` · `whiteboard`, this run only |
| **start_date / end_date** | (analytics) optional `YYYY-MM-DD` |

---

## 7. Per-episode settings (inside `episodes/<id>/episode.json`)

| Field | Meaning |
|---|---|
| `"backdrop"` | Kids: background picture name from `assets/art/` (`"none"` = drawn room). Wins over the automatic choice |
| `"board_style"` | AInation: board look for this episode only (`hanging` · `display` · `whiteboard`) |
| `"order"` | Position in the queue (lower = sooner) |
| `"gap"` | Seconds of pause between lines (default 0.45) |
| `"exaggeration"`, `"cfg"` | Chatterbox voice energy (0.5) and pacing (0.35) for this episode |
| board `"type": "picture"` + `"art"` | A full HD picture board (kids `kf_*`, AInation `ain_*` files) |
| board `"type": "photo"` / `"clip"` + `"stock"` | A real photo/clip searched with that phrase; `"art"` tried first; `"pin"` = reviewed fixed result |
| board icon `"house:<emoji>"` | Force the house icon for that emoji (`ICON_STYLE` aside) |

Full board reference: `SCRIPT_GUIDE_*.md` and `docs/ANIMATED_SCENES.md`.

---

## 8. Internal settings (set by the workflows or for local tests; normally never touch)

| Name | Meaning |
|---|---|
| `EPISODE` | Path of the episode being rendered (set by `daily.py`) |
| `FORMAT` | `long` for long videos, else Short |
| `VARIANT` | `full` · `short` (cut-down voice track) |
| `TTS_LANG` | `en` · `hi` (set from the language box / alternate-day Hindi runs) |
| `BG` | `kids` = kids look (set per repo) |
| `WORKERS` | Parallel render processes (default = CPU count) |
| `THUMB_ONLY` | Render only the thumbnail (Refresh thumbnails) |
| `SCRIPT_IN`, `LANG_IN`, `CATEGORY_IN` | Run-form values passed to `daily.py` |
| `POST_TO` | Run-form "Where to post", normalised |
| `TTS_GAP`, `CB_CFG`, `CB_EXAGGERATION`, `CB_PYTHON` | Voice tuning / the Chatterbox Python path (episode fields win) |
| `DOODLE`, `LIMBS` | Old drawing switches (`DOODLE=1` boiling lines; `LIMBS` = `tube` or `stick`) |
| `ART_DIR` | Folder for HD pictures (default `assets/art`) |
| `BOARD_STYLE_RUN` | AInation: the one-run board look from the form |
| `BRAND_HASHTAG` | Override the brand hashtag (`#TheCurioKidsClub` / `#AInationstudio`) |
| `STATE_BOT` | Git name used when the run saves `state.json` |
| `ANALYTICS_CHANNEL_KEY`, `ANALYTICS_DB_PATH`, `ANALYTICS_OUTPUT_DIR` | Analytics storage locations |

Fixed in code (not variables): Shorts render at 24 fps; intro 2.0 s, outro 3.5 s; kids hook card waits 2.35 s; gentle camera push-in (`SMOOTH_CAM`).

---

## Change log (IST, with UTC)

| When | Change |
|---|---|
| 2026-11-22 12:40 IST (07:10 UTC) | File created (owner asked for one place with all variables). Covers both channels' workflows, secrets, run options, episode fields and internal settings. |
