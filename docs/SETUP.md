# The CurioKids Club: one-time setup (about 30 minutes, no cost)

This is the same process as AInation Studio, so you can reuse most of what you already have.

## 1. Create the YouTube channel

1. Go to YouTube, then your profile picture → **Settings** → **Add or manage your channel(s)** → **Create a channel**.
   Name it **The CurioKids Club**. This creates a Brand Account under the same Google login.
2. Set the handle to **@CurioKidsClub**.
   - **If that handle is taken:** pick another one. Then in Git Bash, inside this repo, run this (replace `NEWHANDLE`):
     ```bash
     sed -i 's/@CurioKidsClub/@NEWHANDLE/g' episodes/*/episode.json episodes/README.md
     ```
3. In YouTube Studio for the new channel, go to **Settings → Channel → Advanced settings → Audience** and choose the audience.
   The uploader follows the repo variable `MADE_FOR_KIDS` (default `false` = "No, it's not made for kids"; set it to `true` to mark videos as made for kids).
   With `false`, choose **"I want to review this setting for every video"** here. Otherwise the channel setting overrides each video.

**What "Made for Kids" means:** YouTube's law-based rules for children's content (COPPA) apply:
- comments are turned off
- no personalised ads (so earnings per view are lower)
- no notification bell and no mini-player on these videos
- the uploader also marks every video as Made for Kids

**Owner decision (2026-11-07):** videos are uploaded as **not made for kids** (`MADE_FOR_KIDS=false`).
YouTube and the FTC judge the content itself (cartoon characters, nursery-style topics) and can override this setting.
Wrongly marking child-directed videos as not made for kids can lead to penalties under COPPA.
To go back, add the repo variable `MADE_FOR_KIDS` = `true`, then run the workflow with **fix_existing**.

## 2. Put the code on GitHub

1. Create a new **private** repository, for example `curio-kids-automation`. Don't add a README.
2. Unzip this bundle into a folder.
3. In Git Bash, from inside that folder, run:
   ```bash
   git init -b main
   ```
   ```bash
   git add . && git commit -m "The CurioKids Club pipeline + 75 episodes"
   ```
   ```bash
   git remote add origin https://github.com/ambujkhanna/curio-kids-automation.git
   ```
   ```bash
   git push -u origin main
   ```
4. Open the repo's **Settings → Actions → General**. Under **Workflow permissions**, choose **Read and write permissions** and save. This lets the run save `state.json`.

## 3. Give the workflow permission to upload (reuse your Google project)

You can use the **same** Google Cloud project, "AInation Automation". It's already In production, so no new app is needed.

1. Open https://developers.google.com/oauthplayground.
2. Click the gear icon, tick **Use your own OAuth credentials**, and paste the **same** Client ID and Client secret you used for AInation.
3. In Step 1, scope:
   ```text
   https://www.googleapis.com/auth/youtube.upload
   ```
   (`youtube.upload` is enough. Use `https://www.googleapis.com/auth/youtube` instead only if you want automatic playlists or fix_existing.)
   Click **Authorize APIs**. When asked which channel, **choose The CurioKids Club**.
4. In Step 2, click **Exchange authorization code for tokens** and copy the **Refresh token**.
5. In the new repo, go to **Settings → Secrets and variables → Actions → New repository secret**, three times:
   - `YT_CLIENT_ID`: same as AInation
   - `YT_CLIENT_SECRET`: same as AInation
   - `YT_REFRESH_TOKEN`: the **new** token for The CurioKids Club

Notes:
- **Quota:** both channels share the project's free 10,000 units a day. Two uploads use about 3,200.
- **Privacy page:** add one line to `privacy.html` in the `ambujkhanna.github.io` repo saying the tool is also used for The CurioKids Club channel.

## 4. First runs

1. **Test without uploading:** Actions → **Daily Curio Kids Short** → **Run workflow**, tick **dry_run**.
   After about 15 minutes, download the MP4 from the run's **Artifacts** and watch it. Listen to Leo's voice especially. If you want a different voice, see "Changing voices" in `README.md`.
2. **Real run:** run the workflow again with dry_run unticked. The video arrives in YouTube Studio for The CurioKids Club as **Private**, scheduled for 16:00–19:00 IST.

Your Google project isn't audited, so every upload is Private. As with AInation, open Studio each day and set the new video to **Public** or **Schedule** it.

## 4b. Custom thumbnails

Each run designs a thumbnail and uploads it with the video. YouTube only accepts custom thumbnails from **verified** channels.
Verify each channel once at https://www.youtube.com/verify (a phone code). Until then the run still succeeds and the run summary says `Thumbnail: not set`.
The thumbnail JPG is also in the run's Artifacts if you want to add it by hand.

## 5. Running two channels from one GitHub account

- **AInation Studio** runs at 14:45 IST and posts at 17:00–20:00. **The CurioKids Club** runs at 14:10 IST and posts at 16:00–19:00.
- **GitHub's free minutes:** private repos get 2,000 minutes a month in total, shared by both repos. Each run takes about 15 minutes, so two channels use about 900 minutes a month, which is fine.
- **When episodes run out:** the run stays green and says "No ready episode left in the backlog". Add more episode files.

## 6. Keeping the channel healthy (kids' content rules)

- **Facts:** keep them accurate and gentle. Avoid anything scary, unsafe experiments, brands and copyrighted characters or songs.
- **Variety:** YouTube rewards it and limits mass-produced, repetitive content. Mix topics, poems and casts, as the 75 included episodes do.
- **AI disclosure:** the voices are AI-generated and the upload marks the video as altered or synthetic content.
- **Check before posting:** spot-check each video in Studio before you set it to Public. That daily click is your quality check.

## Weekly long videos (16:9, 3–8 min) — added 2026-11-06

- **Workflow:** `.github/workflows/curio-kids-long.yml` runs **once a week**. It takes the next ready script in `long/` (L01, L02, …) and renders a **1920×1080** video. The board or stage is on the left, the characters are on the right, and captions sit under the board.
- **Upload:** it uploads the video like a Short (Private until the API audit, then scheduled in the PUBLISH_WINDOW). YouTube **chapters** are added to the description automatically from the script's `"chapter"` markers, and `#Shorts` is removed. A **16:9 thumbnail** is designed and uploaded.
- **Run time:** a long render takes about 40–60 minutes. One per week per channel fits GitHub's free minutes. To test it, go to Actions → the weekly workflow → Run workflow and tick **dry_run**. The MP4 and thumbnail appear in the run's Artifacts.
- **Scripts:** 8 are ready in `long/`. The format is in `long/README.md`. Check scripts with:
  ```bash
  python pipeline/validate_episode.py long/*/episode.json
  ```
- **Tip:** in YouTube Studio, set each Short's "Related video" to its long version.

## Real illustrations, diagrams and fonts — added 2026-11-06

- **Real science drawings:** any icon can be `img:<Category>/<Author>/<name>`; the full list is in `assets/IMAGE_INDEX.txt`. They come from Bioicons (Servier Medical Art and others), using only licences that allow commercial use. The daily run downloads any missing drawing from GitHub, and the credits required by CC BY are **added to the YouTube description automatically**.
- **Animated diagrams:** `body` (blood, nerve, air and food flows), `cycle`, `journey` and `orbit`. See `episodes/README.md` and `pipeline/diagrams.py`.
- **Fonts** (SIL Open Font License, licence files in `fonts/`): The CurioKids Club uses Fredoka for boards and Lilita One for captions. AInation Studio uses Poppins.

## Facebook Page + Instagram (Reels) — added 2026-11-06

After each YouTube upload, the same video is also posted as a **Reel** to the channel's Facebook Page and Instagram (long 16:9 videos go to Facebook only, as a normal video). It does nothing until these GitHub secrets exist:

| Secret | Where it comes from |
|---|---|
| `META_PAGE_ID` | Graph API Explorer → `me/accounts?fields=id,name,access_token,instagram_business_account` → the Page's `id` |
| `META_PAGE_TOKEN` | the Page's `access_token` from that same query, run **with the extended (long) user token**. Check that it says "Expires: Never" |
| `META_IG_USER_ID` | `instagram_business_account.id` from that same query |

**One-time setup:**
1. Create a Facebook Page and an Instagram **Business** account, then link the Instagram account to the Page (Page → Settings → Linked accounts).
2. Create a Meta developer app (Business type). Add the use cases "Manage everything on your Page" and "Manage messaging & content on Instagram (API setup with Facebook login)".
3. Add a **Facebook Login for Business** configuration with these permissions: pages_show_list, pages_read_engagement, pages_manage_posts, instagram_basic, instagram_content_publish and business_management.
4. In the Graph API Explorer, generate a token with that configuration, extend it in the Access Token Debugger, then run the query above.

**How it posts:**
- **When:** right after the YouTube upload. Instagram's API can't schedule.
- **Caption:** the title, the first paragraph of the description, the brand line and the hashtags.
- **Results:** shown in the run summary (Facebook / Instagram: posted or failed). A failure never blocks the YouTube upload.

**Test, or post an older episode:** Actions → daily workflow → Run workflow → tick **social_only** and enter the **episode** id (e.g. `ep002`). It renders that episode and posts it to Facebook and Instagram only.

## Category videos on demand (comedy, quiz, knowledge, science, ABC, counting, rhymes): added 2026-11-06

To post a video from a particular category, go to Actions → **Daily Curio Kids Short** → Run workflow → pick a **category** from the dropdown, then **Run**.

- **What gets published:** the next unpublished episode from `library/<category>/` is rendered and uploaded to YouTube, Facebook and Instagram, like a normal Short.
- **What it doesn't affect:** the regular daily Short, which runs when category is "none" or on schedule. Each category keeps its own `state.json`, so nothing repeats.
- **The categories:**

| Category | What's in it |
|---|---|
| comedy | kind jokes, silly stories, would-you-rather, tongue twisters, silly-but-true facts |
| quiz | guess the animal / sound / job, riddles, odd one out, true or false (the **guess** board flips a ? card to the answer) |
| knowledge | general knowledge: transport, jobs, the world, habits and safety |
| science | extra science explainers with diagrams and real drawings |
| abc | letters A–Z with the giant **letter** board (A a + picture words), plus phonics and review |
| counting | numbers with the **count** board (objects appear as numbers are spoken), counting by 2s, simple sums |
| rhymes | original rhymes and poems (karaoke-style lines) |

- **Adding more:** see `library/README.md`.

## Playlist, audience and Instagram test: added 2026-11-07

- **Playlist:** **off by default.** The owner adds videos to the **curiokids** playlist by hand in YouTube Studio.
  - To automate it later: make a refresh token with the `https://www.googleapis.com/auth/youtube` scope (section 3) and update `YT_REFRESH_TOKEN`.
  - Then add the repo variable `YT_PLAYLIST` = `curiokids` (Settings → Secrets and variables → Actions → Variables). Every upload is then added automatically.
- **Audience:** repo variable `MADE_FOR_KIDS` (default `false`). See section 1.
- **fix_existing:** Run workflow → tick **fix_existing**. It adds every already-uploaded video to the playlist (no duplicates) and applies the `MADE_FOR_KIDS` setting, keeping each video's privacy and schedule. No new video is made.
- **ig_test with an episode:** tick **ig_test** and also type an episode id (e.g. `ep004`). The run renders that episode and checks 6 versions with Instagram **without posting anything**: full length, first 30 s, first 60 s, first 89 s, no audio, and 720×1280. Instagram accepts or rejects each one, which shows what to change.
- **ig_test:** Run workflow → tick **ig_test**. It posts an 8-second test clip (a colour test pattern) to Instagram only and shows the account details and the 24-hour publishing limit.
  - **If it posts:** the account works and the problem is in our episode videos. Delete the test Reel.
  - **If it fails:** the problem is the Instagram account, app or token.

## Voices: Chatterbox (added 2026-11-07)

- **The voices:** the kids channel now speaks with **Chatterbox** (MIT licence, by Resemble AI), an expressive open-source voice model. It runs on GitHub's computer like everything else.
  - Mia, Leo and Dad keep their voices: Chatterbox copies the voice in `assets/voices/mia.wav`, `leo.wav` and `dad.wav`.
  - To change a character's voice, replace their file with a clean 5–10 second recording.
- **Style per category** (`EXAGGERATION` in `pipeline/daily.py`):
  - comedy and quiz are **animated** (0.8)
  - everything else (daily Shorts, science, knowledge, ABC, counting, rhymes, long videos) is **natural** (0.5)
  - one episode can override this with `"exaggeration": 0.6` in its episode.json
- **Lip-sync and cues:** each line is also read silently by Kokoro, and the two readings are matched. Mouths, captions and board pop-ins still land on the right words (median error under 0.02 s).
- **Speed:** the first run installs Chatterbox and downloads its model (about 5–10 extra minutes); later runs reuse the cache. A Short takes roughly 20–40 minutes in total, a long video longer.
- **Safety net:** if Chatterbox fails for any reason, or a Short comes out longer than 3 minutes, the run uses the Kokoro voices instead and still posts. The run summary shows `Voices: chatterbox` or `Voices: kokoro`.
- **Switching back:** add the repo variable `TTS_ENGINE` = `kokoro` (Settings → Secrets and variables → Actions → Variables).
- **Voice Lab:** Actions → Voice Lab still makes Chatterbox samples (Bark was removed: it failed on GitHub's computer).
