# CurioKids Club — conversation log

## 2026-11-18T22:04:00+05:30 — Current analytics-led growth implementation status

User asked for implementation, validation and merge after satisfaction. The feature branch now contains the read-only analytics collector, channel-specific growth brief generator, tests, workflow integration and documentation. Latest analytics workflow run #18 succeeded and generated artifact 14444286367. The artifact includes CSV, Markdown, SQLite and growth brief outputs.

The daily Short workflow retrieves the latest successful analytics artifact and adds the advisory growth brief to the GitHub Actions run summary. It does not modify queued episode JSON, render/upload behavior, publishing schedule, or compliance settings.

PR #1: https://github.com/ambujkhanna/The-CurioKids-Club/pull/1. As of 2026-11-18T22:04:00+05:30, GitHub reports the PR as non-mergeable (`dirty`); feature branch is 10 commits ahead and 32 behind main. Merge intentionally deferred to avoid overwriting production changes. Next: synchronize with main, resolve conflicts, run unit tests and daily workflow dry run, inspect results, then merge.

Latest report metadata coverage: 43.8%. Unknown video/episode mappings need repair before drawing strong topic-level conclusions.


## 2026-11-18T22:12:00+05:30 — PR merge-readiness and documentation policy

User confirmed the Markdown progress/conversation files are to be maintained by the assistant throughout this project; do not ask the user to create or update them. Verified that `PROGRESS.md`, `CONVERSATION.md`, and `docs/GROWTH_ENGINE.md` are pushed on `feat/youtube-growth-engine`.

Current PR #1 remains open and is not merge-ready: GitHub reports `mergeable=false` / `dirty`; branch is 13 commits ahead and 32 behind main. Latest analytics run #21 failed during Google OAuth refresh with `invalid_grant: Token has been expired or revoked`. The workflow's artifact upload step still ran, but it must not be treated as a fresh valid metrics report. Required: rotate only the CurioKids `YT_ANALYTICS_REFRESH_TOKEN` secret, then sync/rebase with main, resolve conflicts and rerun tests plus daily-workflow validation before merge. Upload token and publishing behavior must remain untouched.


## 2026-11-19 19:18 IST — User confirmed both PRs merged; post-merge audit

Verified PR #1 is merged on main. Merge commit: `0c733be795993528955c8b5f51f4cee5d9f5af3d` (2026-11-18 16:49:36Z). Latest inspected daily workflow run #70 succeeded, including analytics loader, render/QC/upload, artifact upload and state commit. However, loader log states: `No growth brief artifact available yet`. Root cause: downloaded artifact files are nested under an artifact-named subdirectory, while workflow checks only `out/analytics/growth_brief.md` at root. Fix loader to find file recursively/copy into expected location.

Latest observed analytics run #24 failed at OAuth refresh with `invalid_grant: Token has been expired or revoked`; rotate only CurioKids `YT_ANALYTICS_REFRESH_TOKEN` secret, leaving upload credentials untouched. Previous valid report metadata coverage 43.8%. Daily run #69 timed out on apt package installation; later #70 succeeded, so likely transient. Next: fix nested artifact path, reauthorize analytics token, manually run analytics, verify fresh artifact, then dry-run daily workflow and confirm brief appears in Actions summary. Do not auto-edit scripts or publishing settings.


## 2026-11-19 19:35 IST — User asked to explain token status and retry pending work

Explained that analytics token setup had previously succeeded (runs #18 and earlier); later runs failed repeatedly with OAuth `invalid_grant`. This is a later failure, not a contradiction. Logs alone cannot distinguish revoked refresh token, Google's refresh-token issuance limit, or client/consent mismatch. Re-ran via main-branch push: analytics run #26 still failed with `invalid_grant`.

Fixed artifact loader to recursively find `growth_brief.md` inside artifact-named subdirectories and copy MD/JSON to stable output path (main commit 739c3143...). Updated analytics workflow push filter to include main (48b83bca...) and increased daily system package timeout to 30 min (ff5230d6...). No daily video workflow was manually dispatched; no upload/publish action taken. Next: user must replace only CurioKids `YT_ANALYTICS_REFRESH_TOKEN` with a newly authorized refresh token; then verify analytics collection and loader summary. Do not alter upload token.


## 2026-11-19 Analytics token recovery

- The user replaced the `YT_ANALYTICS_REFRESH_TOKEN` GitHub Actions secret in this repository. The upload secret `YT_REFRESH_TOKEN` was not changed.
- Retried the failed YouTube Analytics workflow (run attempt 2). Google OAuth refresh succeeded; analytics collection, channel-specific growth brief generation, and artifact upload all succeeded.
- Verified 7 analytics/growth unit tests passed in the workflow.
- Successful run: https://github.com/ambujkhanna/The-CurioKids-Club/actions/runs/44546121847 (artifact youtube-analytics-29).
- Remaining validation: confirm the next scheduled daily video workflow downloads the analytics artifact and displays the growth brief in its Actions summary. No daily video workflow was manually dispatched and no video was published as part of this recovery.


## 2026-11-19 21:30 IST — Current-main audit and long-workflow timeout

The user asked to continue implementation and explicitly requested that all edits use the latest file versions to avoid conflicts. Re-fetched current `main` versions of workflows, analytics/growth code, state files and documentation before acting. Confirmed `.github/workflows/curio-kids-short.yml` contains the recursive analytics artifact loader and manual `Dry run (render only, nothing uploaded)` option. Its post-fix end-to-end result is still unverified.

Updated only `.github/workflows/curio-kids-long.yml`: increased the apt/system-package installation timeout from 15 to 30 minutes to align with the Short workflow and address the previously observed package-install timeout. Commit `cc245c9307c7d2719103c8e67420c353ae6786ca`. The long workflow does not currently load the growth brief; this was left unchanged pending an explicit scope decision.

The current Short state file contains 17 distinct video IDs. The prior analytics report's 43.8% metadata coverage is still the last known measured figure; videos absent from state were not guessed or manually mapped. No workflow was dispatched, and no video render/upload/publish was triggered. Upload tokens, episode state and publishing settings were not changed.

## 2026-11-19 — Growth report audit and unmapped review improvement

Inspected the actual analytics artifact from the successful collector run. It contains 18 video rows; 16 are mapped (88.9%). Two unknown video IDs remain: `r_GUBf5Flho` (68 views) and `5iwnr-Y9hqc` (32 views). Searches of repository code did not find these IDs, so no episode mapping was invented.

Added the unknown rows to `growth_brief.json` and a dedicated review table in `growth_brief.md`, with direct video links. The output explicitly states that unknown IDs must be verified before adding them to episode state. Added a regression test and a PR-only unittest workflow with no publishing secrets or production side effects.

PR #2: https://github.com/ambujkhanna/The-CurioKids-Club/pull/2. Merge is gated on passing PR checks. The workflow-dispatch integration is not exposed by the current GitHub connector, so no daily workflow was triggered and no upload/publish occurred.


## 2026-11-19 — Unmapped-video review shipped; analytics OAuth regressed

PR #2 was merged to main (merge commit `ce8ec46dfe2b56328aa9ce0a72b4b3808b2f274a`). It adds unknown video IDs and view counts to the growth brief JSON plus a linked Markdown review table. Unknown videos are deliberately not assigned to episodes without verification. The PR-only unit-test workflow passed in three runs.

The latest inspected analytics artifact had 18 rows, 16 mapped (88.9%); remaining IDs are `r_GUBf5Flho` (68 views) and `5iwnr-Y9hqc` (32 views). These were not found in repository code, so no guessed mappings were committed.

After merge, the main-branch analytics collection failed again in run `44561529784` with Google OAuth `invalid_grant`; unit tests passed but the collection and growth-brief generation did not run. AInation main-branch analytics run `44561570026` failed the same way. This is a renewed credential blocker; do not change upload token `YT_REFRESH_TOKEN`.

The latest CurioKids daily run `44413916460` succeeded in rendering/upload, but its growth-loader step reported that no growth brief was available at that time. The post-success analytics artifact must be followed by another daily run to verify the brief is actually included in the Actions summary. No dry-run dispatch was performed because the available GitHub connector does not expose workflow dispatch; no extra video was uploaded by this work.


## 2026-11-19 — Analytics push trigger narrowed

Merged PR #3 (`b067f31668b2217f01a304900a8b4122e0bc42fa`). The analytics workflow's push trigger now has a paths filter for collector/growth code, analytics dependencies, tests, episode state and the analytics workflow. Documentation-only changes will not trigger a collector run. Scheduled and manual analytics triggers remain enabled; daily video workflows are unchanged.


## 2026-11-19 — Follow-up status check after PR #3

Re-fetched the latest main versions of PROGRESS.md, CONVERSATION.md, docs/GROWTH_ENGINE.md, and the analytics/daily workflow definitions before updating documentation. The latest analytics push runs after PR #3 merged failed again: CurioKids 44562221268; AInation 44562248765. The previous invalid_grant credential issue therefore remains open; update only YT_ANALYTICS_REFRESH_TOKEN in each repository after reauthorizing. Never change YT_REFRESH_TOKEN.

AInation Daily Short workflow run 44562499073 appeared as a user-triggered workflow_dispatch and is still in progress. At inspection it was at the system-package installation step; the analytics brief loader and render/upload step had not yet executed. The GitHub run API does not expose the selected dispatch inputs, and the workflow default is Next video (scheduled), so this run cannot be assumed to be a dry-run. The assistant did not initiate or cancel it. Please verify in its Actions run page that the selected action is Dry run (render only, nothing uploaded) if you intended a safe validation. CurioKids has no new daily dispatch among the latest 10 runs; its post-fix dry-run remains pending.

No new upload/publishing action was initiated by the assistant. Growth recommendations remain advisory; no episode state, publishing schedule, upload token or workflow publishing logic was changed.


## 2026-11-20 — Current operational status

- [x] Rechecked current workflow runs and logs. Daily scheduled run 44578898591 completed successfully and uploaded Short https://www.youtube.com/shorts/dcNLkD2l3p8 for scheduled publication on 20 Nov 2026 at 17:55 IST. The next scheduled run 44631536769 also completed successfully; its log correctly reported “Nothing due right now” because the alternate-day/time-window logic did not select a video. No duplicate upload occurred in that run.
- [x] The daily workflow's read-only growth-brief loader step completed successfully in run 44631536769. The brief is from the last successful analytics artifact, however, and is stale until fresh collection succeeds.
- [ ] Latest scheduled analytics run 44606697918 failed with Google OAuth `invalid_grant` (“Token has been expired or revoked”). Reauthorize and replace only `YT_ANALYTICS_REFRESH_TOKEN`; leave `YT_REFRESH_TOKEN` unchanged.
- [ ] A manual dry-run validation is still pending. The available GitHub integration does not expose workflow dispatch; use Actions → Daily Curio Kids Short → Run workflow → action `Dry run (render only, nothing uploaded)` to validate without publishing.
- Guardrails unchanged: no automatic script rewriting; no upload token, publishing logic, schedule or episode state changed by this audit.


## 2026-11-20 — User updated the analytics refresh tokens; both channels validated

The user clarified that yesterday's update may have replaced the short-lived access token rather than the refresh token. They have now updated `YT_ANALYTICS_REFRESH_TOKEN` in both repositories. Retried the failed analytics jobs using the current secrets: CurioKids run 44606697918 and AInation run 44603311245. Both completed successfully, including Google OAuth refresh, read-only analytics collection, growth brief generation, unit tests, and artifact/database upload. This confirms that the currently configured analytics refresh tokens work in both repositories. The upload secret `YT_REFRESH_TOKEN` was not changed, and these analytics retries did not upload or publish videos. Safe Daily Short dry-run validation remains pending; use the explicit `Dry run (render only, nothing uploaded)` action, not the scheduled/publish default.


## 2026-11-20 — Follow-up after analytics recovery and Visual Engine rerun

A fresh audit found CurioKids analytics run 44739181837 successful. A newer AInation analytics push run 44724594920 had failed before the user's refresh-token correction; rerunning it as attempt 2 succeeded, so the current analytics token configuration is validated in both repositories. The CurioKids Visual Engine branch has separate progress: Blender proof-of-capability succeeded, but integrated dry-run 44732204753 failed at headless EGL initialization with `EGL_BAD_MATCH`. I reran it (attempt 2 is pending), and the validator fix also triggered integrated dry-run 44739867903, which was still running at the latest check. Next: inspect the completed render/video artifact and perform visual acceptance. Keep all Visual Engine changes on the feature branch until the owner approves the actual output. Both repositories' safe Daily Short dry-run checks also remain pending; no production publish workflow was triggered by this audit.


## 2026-11-21 18:50 IST (13:20 UTC) — HD graphics pilot, kids backgrounds, decisions (written for continuing in ChatGPT or any assistant)

**Read with:** `TheCurioKidsClub_handoff.md` / `AInation_Studio_handoff.md` (change log), `Channels_Reference.md` (variables), `docs/HD_ART.md`.

### What the owner asked (21 Nov 2026, in order)
1. A fun-facts kids series, as many episodes as possible, posted before the old queue; big topics split into parts; a spoken line asking viewers to drop a topic in the comments. **Done:** ep076–ep083, ep090–ep097 and ep104–ep112 (25 episodes, `order` 1–25), plus an on-screen "Drop a topic in the comments!" bubble. Descriptions and captions do **not** carry the topic ask (owner reverted that).
2. Better Subscribe/Like/Share: **AInation = big pop** (`CTA_STYLE=pop`), **kids = action bar** (`bar`).
3. "Why can't we use HD 3D graphics like my references?" The answer: our renderer is 2D code, and we have no free image model in the daily run. **Owner chose option 1:** make pictures once on a free Kaggle GPU with FLUX.1-schnell (Apache 2.0), commit them, and keep the characters **2D**. Also asked to improve the 2D characters without distortion → `CHAR_STYLE=polished`.
4. Kaggle: account created and phone-verified (needed for internet and GPU). HF token stored as the Kaggle secret `HF_TOKEN`, never in chat. Learned: stopping a Kaggle session deletes `/kaggle/working`, so download first. The CLIP 77-token warnings are harmless.
5. **AInation: no background** ("looking fine with plain", the Studio Open look stays).
6. Kids: backgrounds approved ("background looks great"). Owner questioned the puppet stage → **glass card** on pictures. Owner was unsure whether a white box is needed but is "fine not to change everything" (white card kept; frosted glass tried and dropped).
7. Speaker close-ups cut the card → owner is "fine with zooming if it makes the video better/interactive" → gentle push-ins + smooth glides.
8. "Text should not merge with backgrounds; use nice animation for cycle diagrams and transitions" → all text sits on the card, the logo has a pill, captions have an outline, items rise and fade in, and scenes animate inside the card.
9. Update existing episodes and scripts to the latest pattern → every episode has `backdrop`; scripts have an optional `BACKDROP:` line plus automatic choice.
10. Wants house-made icons later (own style first, Fluent 3D as fallback) → icon usage list made (`ICON_REFERENCE_LIST.md`, sent in chat): kids 421 icons (top 80 = 60% of uses), AInation 137 (top 80 = 95%). The owner will collect style references; the icon pilot is planned for the next Kaggle run (FLUX + rembg cut-out).
11. Big concern: **views are still low**. Answered in chat (below) and still open.

### Decisions in force
- Kids: HD backgrounds on (`ART=on`), the glass card on pictures, polished characters available but **default `doodle`** until the owner sets `CHAR_STYLE=polished`.
- AInation: Studio Open, no backgrounds, `CTA_STYLE=pop`, `THEME=studio_open`.
- Pictures are made only by the owner on Kaggle (free). No paid APIs, and no image model in the daily run.
- Bundles: one zip per repo with only changed files, a one-line push command, handoffs updated inside the repos, never `state.json`.

### Views: diagnosis given (21 Nov) and suggested next steps
- Every Short starts with a 2 s "Welcome to" logo intro and ends with a 3.5 s links card. On Shorts, the first second decides swipe-away, and the end card hurts loops. **Suggestion:** set `SHORT_INTRO=off` and `SHORT_OUTRO=off` (long videos keep them), then compare "Viewed vs swiped away" in YouTube Studio.
- Shorts run 60–80 s. 30–45 s retains better for kids topics. Hook: the question in the first second (already a big yellow hook).
- No tool can buy views. View bots and "view increase" tools break YouTube rules and get channels removed. Honest levers: hook and retention, titles people search for (YouTube search suggestions), consistent posting, playlists/series, Community posts, and cross-posting (FB/IG already automatic).


## 2026-11-21 20:05 IST (14:35 UTC) — Thumbnails and the AInation board tag

- The owner asked for punchier thumbnails that make viewers curious, on both channels. The new design: big characters with a wow face, the explainer pointing at the answer, 1–3 huge words, "A → B" pictures with a red arrow, and a highlight on the answer.
- The red circle felt like too much, so the owner compared 4 highlights (red circle, mystery silhouette, glow, sticker) and **picked the sticker**: a pink "WHY?/HOW?/WHAT?" speech bubble.
- Added: a PART N ribbon for series episodes. The HINDI tag moved to a corner.
- Switches: `THUMB_STYLE=classic` brings back the old design, and `THUMB_MARK` picks another highlight.
- Ideas for later: one headline word in a second colour; A/B test 3 versions with YouTube Studio's free "Test & compare" on long videos.
- AInation: the "AI EXPLAINED" text at the board's top right is removed (owner).

- 2026-11-21 20:25 IST (14:55 UTC): the sticker is centred under the answer picture, and its pointer always aims straight up at the picture (owner).
- 2026-11-21 20:40 IST (15:10 UTC): the sticker no longer overlaps the round picture: it sits fully below it, and only the pointer touches the ring (owner).


## 2026-11-21 20:55 IST (15:25 UTC) — Open items (start here in a new thread)

Read first: the channel handoff (`TheCurioKidsClub_handoff.md` / `AInation_Studio_handoff.md`), `Channels_Reference.md` (variables), this log. The kids repo also has `docs/HD_ART.md`, `tools/kaggle/` (the picture notebooks + how to run) and `docs/ICON_REFERENCE_LIST.md` / `docs/icons_all.csv`.

1. **Polished characters**: built, but the owner has not switched them on. Set repo variable `CHAR_STYLE=polished` per repo when wanted.
2. **Views (owner's big concern)**: suggested `SHORT_INTRO=off` and `SHORT_OUTRO=off` (kids; the 2 s logo intro and the end links card hurt Shorts retention and loops), then compare "Viewed vs swiped away" in YouTube Studio after a week. Shorter Shorts (30–45 s) are worth trying. No view-boosting tools: they break YouTube rules.
3. **Opening hook on the glass card**: the big yellow question text (first 2 s, `finish.py` Hook style) overlaps the top edge of the kids glass card. Small fix pending: move the hook text up when a picture background is on.
4. **Picture library run**: about 30–50 more kids backgrounds + topic close-ups on Kaggle (same notebook, new `PICTURES`), then add their topic words to `TOPICS` in `pipeline/art.py`.
5. **House icons pilot**: the owner is collecting style references for the icons in `docs/ICON_REFERENCE_LIST.md`. Plan: FLUX + rembg cut-out on Kaggle, the top 40 kids icons first, compared side by side with Fluent; lookup order house → Fluent 3D → flat.
6. Thumbnail ideas not done yet: one headline word in a second colour; YouTube "Test & compare" with 3 versions on long videos.
7. AInation stays on the plain Studio Open look (no backgrounds), by owner decision.

## 2026-11-21 21:30 IST (16:00 UTC) — Realistic icons running, weekly Kaggle automation planned

- The owner wants a **realistic** look (references: glossy water drops, a soft 3D weather icon, a dreamy moon scene, a realistic Earth, glossy confetti), a longer icon list including general future topics, and realistic icons for AInation too (AInation still has no backgrounds). Notebook `tools/kaggle/icons_v1.ipynb` (165 icons, 276 pictures) is **running on Kaggle**. Next: check the zip, pick, add `assets/icons_house/` with the lookup order house → Fluent → flat, then show side-by-side boards to the owner.
- Plan written: `docs/AUTOMATION_KAGGLE.md`, a weekly GitHub → Kaggle API picture run. Ollama is for text only (prompts and choices), Wan 2.1 for a later video pilot. To build after the icons are in.

## 2026-11-21 21:50 IST (16:20 UTC) — Roadmap of free tools, keyword research

- Wrote `docs/ROADMAP_FREE_TOOLS.md`: R1–R9 with goal, how, files, secrets, variables, effort, risks and "done when" for each. Suggested order: real stock clips → topic radar → comments → topics → subtitles → Spanish dub → self-check + alerts → weekly Kaggle run → more platforms.
- Keyword research answer: YouTube search suggestions (free), competition checks with the YouTube Data API, our own search terms from YouTube Analytics, Google Trends (manual), and the **YouTube Studio Research tab** (manual, best signal). Built as R2 "topic radar" + R3 "comments → topics".

## 2026-11-21 23:20 IST (17:50 UTC) — House icons are in (curated mix)

- 151 realistic icons were installed in both repos and 14 were rejected. The owner chose the **curated mix**: our icons for objects, animals, nature, science and tech; emoji for weather, symbols and white things. **Every icon is kept** for later use (`"house:<emoji>"`, `w_*` names, `ICON_STYLE=house_all`). Details: `docs/ANIMATED_SCENES.md` → Icons.
- Open item 5 (house icons pilot) is **done**. Possible later run: remake the 14 rejects (see-through objects on a darker background), more `w_*` science pictures, and AInation tech icons on a darker backdrop.

## 2026-11-22 00:15 IST (18:45 UTC) — R1 real photos and NASA clips built

- `photo` / `clip` boards work in both channels (NASA + Openverse, credited, with a safe fallback). They are **not used in any episode yet**: the next step is the owner choosing where (proposal: NASA photos and clips in the space series ep094–ep097; Openverse photos for animals, nature and machines).
- The owner will keep pushing bundles by hand. Pushing from a session needs their GitHub (ambujkhanna) connected at claude.ai/connect-github and the Claude GitHub App on both repos; never tokens in chat.

- 2026-11-22 00:50 IST (19:20 UTC): **Real photos: AInation yes (plain), kids no** (the owner felt they looked pasted-in next to the cartoon world, even as polaroids). Kids workflows have `STOCK=off`. Next for AInation: choose episodes for real photos.

## 2026-11-22 02:10 IST (20:40 UTC) — Radar, self-check, alerts (one bundle)

- Built R2 + R3 (weekly topic radar issue with viewers' requests), R6 (self-check + phone alerts). AInation: pinned real photos in ep031 and ep036 (the owner found the ep033 server close-up and the first ep036 MRI scan unclear: ep036 now shows a doctor with an X-ray, ep033 is an icon board again). Guide: `docs/RADAR_AND_ALERTS.md`.
- **Open items now:** (1) the owner may add `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` (or `DISCORD_WEBHOOK_URL`) for alerts, and `YT_API_KEY` for the AInation radar competition check and comments; (2) R4 subtitles need a new YouTube login with the caption scope (owner's decision); (3) R5 Spanish dub (same channel or new?); (4) R7 weekly Kaggle run (needs a Kaggle API key); (5) R8 more platforms (accounts/apps); (6) the polished characters and `SHORT_INTRO`/`SHORT_OUTRO` are still the owner's switches; (7) the hook text vs kids glass card fix is still pending.

- 2026-11-22 03:10 IST (21:40 UTC): kids hook overlap fixed. **Picture rule (owner): realistic 3D art first; raw photos only when no better 3D art exists.** AInation art notebook `tools/kaggle/art_ain_v1.ipynb` is waiting for the owner to run it on Kaggle; after that: check, pick, add `assets/art/` and link the boards.

## 2026-11-22 10:20 IST (04:50 UTC) — 3D picture boards in both channels

- The owner ran the merged notebook. Kids: 3D picture boards in 10 fun-facts episodes (a 3D child blinking, shivering, spinning; astronaut; star; clouds; touch; shadows; spoons; tummy). AInation: 3D key visuals in 18 upcoming episodes (3D art first, raw photos only as the fallback). Rejects and reasons are in the handoffs.

- 2026-11-22 10:45 IST (05:15 UTC): **Views test:** the owner sets `SHORT_INTRO=off` (both repos) so Shorts start with the hook. Compare YouTube Studio → Shorts → 'Viewed vs swiped away' before/after (1–2 weeks). Delete the variable to undo.

- 2026-11-22 11:30 IST (06:00 UTC): **Decision: no intro on Shorts** (they open on the question hook). **Rule for the future: any intro must show the video's title/topic** (already built: big yellow topic at the top of the intro, Hindi title for Hindi). Long videos keep the intro, with the topic. Measure 'Viewed vs swiped away' after 1–2 weeks.
- 2026-11-22 12:05 IST (06:35 UTC): intro topic restyled: punchy 3D lettering (kids yellow-orange, AInation gold), as the owner asked. Used whenever an intro is on (long videos; Shorts only if `SHORT_INTRO=on`).
- 2026-11-22 12:40 IST (07:10 UTC): kids intro: **animated blasting sparklers** only (poppers dropped by the owner); bursts sit behind the words.
- 2026-11-22 12:40 IST (07:10 UTC): **`CONFIGURATION.md`** added (both repos): the single list of every variable, secret, run option and episode field. Update it whenever a variable changes.
- 2026-11-22 13:10 IST (07:40 UTC): **Alerts on WhatsApp** (owner doesn't use Telegram): CallMeBot, secrets `WHATSAPP_PHONE` + `WHATSAPP_APIKEY`. Next: R5 Spanish versions of kids Shorts.
- 2026-11-22 15:30 IST (10:00 UTC): **Spanish kids Shorts built (R5)**: voices B (Dora/Alex), one extra Short a day at 05:30-07:30 IST, 81 episodes translated, playlists `curiokids` (en/hi) and `CurioKids_Spanish`. Open: rhymes/poems + English-lesson episodes in Spanish? (owner). Guide: kids docs/SPANISH.md.
- 2026-11-22 17:00 IST (11:30 UTC): **Blinking icons fixed** (3D icons downloaded once before the parallel render; was: some workers fell back to the flat icon). WhatsApp: step-by-step set-up + 'Send a test alert' run option. Trending topics: weekly radar = YouTube search suggestions (+ competition with YT_API_KEY); Google Trends / YouTube most-popular offered as an add-on.
- 2026-11-22 18:30 IST (13:00 UTC): CallMeBot is full → owner: no alerts for now (checks daily). **Radar + trends**: Google Trends (IN/US/MX) + YouTube trending in the Monday report, and a daily 'Trend alert' issue when a new fitting trend appears (make that Short within 1-3 days).
- 2026-11-22 20:30 IST (15:00 UTC): New login scope `youtube.force-ssl` on both channels. **Subtitles built (R4)**: exact tracks + translated titles after every upload. Next asked by owner: automatic Shorts from trending/top-searched topics (extra to the daily queue).
- 2026-11-22 22:30 IST (17:00 UTC): **Automatic trend Shorts** built (docs/TREND_SHORTS.md): one extra Short a day from the first relevant top search, free model (Ollama Qwen 2.5 7B) + Wikipedia facts + 2 fact checks, public in 12:00-14:00 IST. Kids on; AInation waits for its own Google Cloud project (API quota).
- 2026-11-23 00:30 IST (2026-11-22 19:00 UTC): Kids look fixes (owner approved stills): steady camera + golden spotlight under the speaker, boards bridge gaps (no empty card), keyword pictures (grass 🌾 etc.). Open: same camera for AInation?
- 2026-11-23 01:30 IST (2026-11-22 20:00 UTC): Trend dry run failed on a combined emoji (🦸‍♂️). Fixed (auto plain emoji + full check inside the writer); all episodes/scripts/queues re-validated OK. Branch clean-up: growth-engine branch fully merged; feature/modern-visual-engine not merged (archive tag suggested).
- 2026-11-23 02:15 IST (2026-11-22 20:45 UTC): **docs/HOW_IT_WORKS.md**: plain-language diagrams of the whole system (for non-technical readers) + a presentation page.
- 2026-11-23 03:15 IST (2026-11-22 21:45 UTC): Trend Short dry run passed on GitHub. **Topics now also ranked by what works on our channel** (analytics → ★/▼ in the weekly report, trend Short order).
- 2026-11-23 05:00 IST (2026-11-22 23:30 UTC): AInation: steady camera + golden speaker spotlight (like kids). Each channel has its own Google project → AInation trend Shorts switched on.
- 2026-11-23 07:15 IST (01:45 UTC): Owner: decide more languages on data → **audience by country** added to analytics. **Weekly Kaggle art run** built (secrets added; first manual run next). Hybrid trend model option. AInation board bridge. **docs/PLATFORMS.md** for more platforms (advice: Threads → Pinterest → LinkedIn → Bluesky).
- 2026-11-23 08:30 IST (03:00 UTC): **Plans:** make the code private but keep free runs (docs/PRIVATE_CODE_PLAN.md), Pinterest for kids (docs/PINTEREST_PLAN.md); open tasks in **docs/TODO.md**. LICENSE: All rights reserved. 14B model not better than 7B.
