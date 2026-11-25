# The CurioKids Club — Progress


## 2026-11-18T22:04:00+05:30 — Analytics-led growth loop status

- [x] Read-only YouTube Analytics collection verified on feature branch; latest run #18 completed successfully (GitHub Actions run 44341675445).
- [x] Latest artifact generated (artifact 14444286367); includes CSV, Markdown, SQLite and generated growth brief files.
- [x] Channel-specific growth brief generator and unit tests are committed on `feat/youtube-growth-engine`.
- [x] Daily Short workflow updated to retrieve the latest successful analytics artifact and surface its brief in the run summary; this is advisory only.
- [x] Pull request opened: https://github.com/ambujkhanna/The-CurioKids-Club/pull/1
- [ ] Merge blocked: GitHub currently reports PR mergeability as `dirty`; branch is 10 commits ahead and 32 behind `main`. Do not force-merge or overwrite newer main changes.
- [ ] Rebase/sync feature work with current main, resolve conflicts, rerun tests and daily-workflow dry run, then merge only after clean validation.
- Data-quality issue: latest report metadata coverage was 43.8%; repair unknown video/episode mappings before topic-level conclusions.
- Guardrails: no upload credentials, episode queue, publishing settings, schedule, or upload behavior changed. Growth brief does not auto-edit scripts or publish.


## 2026-11-18T22:12:00+05:30 — Latest PR readiness check

- [x] Confirmed `PROGRESS.md`, `CONVERSATION.md`, and `docs/GROWTH_ENGINE.md` are pushed to `feat/youtube-growth-engine`.
- [x] Rechecked PR #1 and branch comparison against `main`.
- [ ] Not ready to merge: PR is open but GitHub reports `mergeable=false`, `mergeable_state=dirty`; branch diverged (13 commits ahead, 32 behind main).
- [ ] Latest analytics workflow run #21 failed at token exchange with Google OAuth `invalid_grant: Token has been expired or revoked`. Artifact upload still ran, but it is not a fresh successful analytics collection.
- Next: user must rotate/reauthorize the CurioKids analytics refresh token and update only `YT_ANALYTICS_REFRESH_TOKEN` in this repo; do not change upload token. Then sync branch with main, resolve conflicts, run tests and daily-workflow validation, and merge only when clean.


## 2026-11-19 19:18 IST — Post-merge verification

- [x] PR #1 merged into `main` on 2026-11-18; merge commit `0c733be795993528955c8b5f51f4cee5d9f5af3d`.
- [x] Confirmed the daily Short workflow on main run #70 succeeded, including the render/QC/upload step.
- [ ] Growth brief was **not loaded** in run #70: the loader looked for `out/analytics/growth_brief.md` at the root, but `gh run download` places artifact contents in a nested directory. Run log explicitly said no brief was available. Fix loader to locate/copy the file recursively and test it.
- [ ] Analytics workflow latest observed run #24 failed with Google OAuth `invalid_grant: Token has been expired or revoked`. Rotate only this repo's `YT_ANALYTICS_REFRESH_TOKEN`; never change upload token.
- [ ] CurioKids daily run #69 also timed out during apt system-package installation; run #70 subsequently succeeded, so treat #69 as transient runner/package-install failure unless repeated.
- [ ] Metadata coverage in last valid analytics report was 43.8%; unknown video/episode mappings need repair.
- [ ] After token rotation and loader fix, run analytics workflow manually, confirm fresh CSV/MD/SQLite/growth brief artifact, then run a daily dry-run and verify the summary includes the brief.
- [ ] No automatic script rewrite/publishing based on analytics: recommendations remain advisory. Upload and scheduling logic unchanged.


## 2026-11-19 19:35 IST — Retry and integration fixes

- [x] Clarified prior token history: the analytics tokens did work in the successful feature-branch runs (#18). Subsequent analytics runs #21–#26 repeatedly failed at Google OAuth refresh with `invalid_grant`; this is a new observed failure, not evidence the original setup was wrong. The precise cause (revoked/invalidated token, token limit, consent/client mismatch) is not established from GitHub logs alone.
- [x] Fixed daily growth-brief loader to search recursively inside downloaded artifact subfolders, then copy Markdown/JSON to a stable path. Commit on main: `739c3143a00cea7339234d24a462895320fe280d`.
- [x] Analytics workflow now triggers on main changes as well as the legacy feature branch. Commit: `48b83bcad29f006d9305c1e9d85e89201604077c`.
- [x] Increased system package installation timeout from 15 to 30 minutes. Commit: `ff5230d601bb08c37458c97945a59fb62274f2e5`.
- [ ] Retry analytics run #26 still failed with `invalid_grant`; a fresh analytics-only refresh token is still needed. Do not change `YT_REFRESH_TOKEN`.
- [ ] Validate loader end-to-end after fresh analytics artifact exists. Daily production workflow was not manually dispatched; no video was published as part of this retry.
- Previous report metadata coverage: 43.8%; repair unmapped episode/video IDs.


## 2026-11-19 Analytics token recovery

- The user replaced the `YT_ANALYTICS_REFRESH_TOKEN` GitHub Actions secret in this repository. The upload secret `YT_REFRESH_TOKEN` was not changed.
- Retried the failed YouTube Analytics workflow (run attempt 2). Google OAuth refresh succeeded; analytics collection, channel-specific growth brief generation, and artifact upload all succeeded.
- Verified 7 analytics/growth unit tests passed in the workflow.
- Successful run: https://github.com/ambujkhanna/The-CurioKids-Club/actions/runs/44546121847 (artifact youtube-analytics-29).
- Remaining validation: confirm the next scheduled daily video workflow downloads the analytics artifact and displays the growth brief in its Actions summary. No daily video workflow was manually dispatched and no video was published as part of this recovery.


## 2026-11-19 21:30 IST — Current-main audit and CI resilience

- Re-fetched current files from `main` before changes; did not use feature-branch copies.
- Confirmed the Daily Short workflow already has the recursive analytics-artifact loader and a safe manual action, `Dry run (render only, nothing uploaded)`. It is not yet verified end-to-end in a post-fix run.
- Extended the Weekly Long Video workflow's system-package installation timeout from 15 to 30 minutes, matching the already-updated Short workflow. Commit: `cc245c9307c7d2719103c8e67420c353ae6786ca`.
- Current state file contains 17 distinct Short video IDs plus separate long-video state. Historical analytics metadata coverage remains 43.8%; do not guess mappings for videos absent from state.
- No workflow was dispatched in this change; no video was rendered, uploaded, published, or rescheduled. Upload credentials and episode state were untouched.
- Next: run the Short workflow with its explicit dry-run action and confirm the Actions summary includes the growth brief; separately decide whether the Long workflow should also surface the brief.

## 2026-11-19 — Growth report unmapped-video review

- Downloaded and inspected the latest successful analytics artifacts. CurioKids report: 18 rows, 16 mapped (88.9%); two unknown IDs remain: `r_GUBf5Flho` (68 views) and `5iwnr-Y9hqc` (32 views).
- Added an explicit unmapped-video review list to the growth brief JSON and Markdown. Unknown IDs are linked for manual inspection and are never assigned to episodes automatically.
- Added regression test coverage and a lightweight pull-request unit-test workflow.
- PR #2: https://github.com/ambujkhanna/The-CurioKids-Club/pull/2
- Validation/merge: waiting for GitHub Actions PR checks. Daily render-only dry-run remains unverified; no video was uploaded or published.


## 2026-11-19 — Growth review PR #2 merged

- [x] Inspected the latest analytics artifact: 18 rows, 16 mapped (88.9%); unknown IDs `r_GUBf5Flho` (68 views) and `5iwnr-Y9hqc` (32 views).
- [x] Growth brief now exports unmapped video IDs/views in JSON and a linked Markdown review table; no speculative episode mapping is performed.
- [x] Added regression test and PR-only unit-test workflow. PR #2 merged: https://github.com/ambujkhanna/The-CurioKids-Club/pull/2 (merge commit `ce8ec46dfe2b56328aa9ce0a72b4b3808b2f274a`); three PR test runs succeeded.
- [ ] Fresh analytics collection is blocked again: main push run `44561529784` failed with Google OAuth `invalid_grant`. Analytics tests passed; collection failed before growth brief generation. Upload token was not changed.
- [ ] Daily workflow's latest observed run `44413916460` completed, but its analytics loader reported no growth brief available at that time. A new post-analytics-success run is needed to confirm summary display.
- [ ] AInation and CurioKids daily dry-run validation remains pending; no production workflow was dispatched as part of this work.


## 2026-11-19 — Analytics trigger noise reduction

- [x] Merged PR #3: https://github.com/ambujkhanna/The-CurioKids-Club/pull/3 (merge commit `b067f31668b2217f01a304900a8b4122e0bc42fa`).
- Analytics push collection now runs only for analytics code/dependencies/tests, episode metadata state and the analytics workflow itself; documentation-only commits no longer trigger an OAuth refresh.
- Scheduled and manual analytics triggers remain enabled. Daily publishing workflows are unchanged.


## 2026-11-19 — Follow-up audit: current workflow status

- [x] Re-fetched current main versions of all three tracking documents and the Daily Short / analytics workflows before this update.
- [x] Confirmed PR #3's path filter is active; documentation-only commits will not trigger analytics collection. The latest analytics push runs after the merge still failed (CurioKids run 44562221268; AInation run 44562248765) and the earlier OAuth failure pattern remains unresolved. Do not change YT_REFRESH_TOKEN.
- [ ] AInation Daily Short workflow dispatch 44562499073 is currently in progress. GitHub's run summary does not expose the selected action input, so this audit cannot safely classify it as dry-run versus publish. Its job is still at the bounded system-package installation step; analytics brief loading and render/upload have not yet run. Do not infer that it is a safe dry-run.
- [ ] CurioKids daily post-fix dry-run remains unverified; no new CurioKids daily workflow dispatch was found in the latest 10 runs.
- [ ] Need a fresh valid YT_ANALYTICS_REFRESH_TOKEN in each repository, then a successful analytics collection followed by safe daily dry-run(s) to prove the growth brief appears in the Actions summary.
- Guardrails unchanged: no assistant-initiated video upload, publish, schedule change, episode-state edit or upload-token change.


## 2026-11-20 — Current operational status

- [x] Rechecked current workflow runs and logs. Daily scheduled run 44578898591 completed successfully and uploaded Short https://www.youtube.com/shorts/dcNLkD2l3p8 for scheduled publication on 20 Nov 2026 at 17:55 IST. The next scheduled run 44631536769 also completed successfully; its log correctly reported “Nothing due right now” because the alternate-day/time-window logic did not select a video. No duplicate upload occurred in that run.
- [x] The daily workflow's read-only growth-brief loader step completed successfully in run 44631536769. The brief is from the last successful analytics artifact, however, and is stale until fresh collection succeeds.
- [ ] Latest scheduled analytics run 44606697918 failed with Google OAuth `invalid_grant` (“Token has been expired or revoked”). Reauthorize and replace only `YT_ANALYTICS_REFRESH_TOKEN`; leave `YT_REFRESH_TOKEN` unchanged.
- [ ] A manual dry-run validation is still pending. The available GitHub integration does not expose workflow dispatch; use Actions → Daily Curio Kids Short → Run workflow → action `Dry run (render only, nothing uploaded)` to validate without publishing.
- Guardrails unchanged: no automatic script rewriting; no upload token, publishing logic, schedule or episode state changed by this audit.


## 2026-11-20 — Analytics refresh-token validation

- [x] User clarified that yesterday's update may have replaced the short-lived access token rather than the refresh token. User has now updated `YT_ANALYTICS_REFRESH_TOKEN` in both repositories.
- [x] Retried the previously failed analytics workflow jobs using the current repository secrets. CurioKids run 44606697918 completed successfully; AInation run 44603311245 completed successfully.
- [x] In both runs, OAuth collection, channel-specific growth brief generation, and report/database artifact upload succeeded. Analytics unit tests also passed. This validates the current analytics refresh tokens in both repositories.
- [ ] Safe Daily Short dry-run remains a separate pending validation; do not use the default scheduled/publish action.
- Upload credential `YT_REFRESH_TOKEN` was not changed. No video was uploaded or published by these analytics retries.


## 2026-11-20 — Follow-up audit and Visual Engine validation

- [x] Confirmed latest CurioKids analytics run 44739181837 completed successfully after the refresh-token update.
- [x] Re-ran AInation's newer push-triggered analytics failure 44724594920 (attempt 2); it completed successfully with the current `YT_ANALYTICS_REFRESH_TOKEN`. Both channels' latest analytics refresh-token configurations are therefore validated.
- [x] Investigated Visual Engine dry-run 44732204753. Blender proof-of-capability succeeded, while the integrated episode dry-run failed during headless EGL initialization (`EGL_BAD_MATCH`), not episode validation. Re-ran it; attempt 2 is queued/pending.
- [ ] New Visual Engine integrated dry-run 44739867903, triggered by the episode-validator fix on `feature/modern-visual-engine`, is still in progress. Inspect its final MP4/contact-sheet artifact and visually review before accepting.
- [ ] Safe Daily Short dry-run remains pending in both repositories; the GitHub integration used here does not expose workflow dispatch. Do not use the scheduled/publish default.
- [ ] Visual Engine remains feature-branch-only; no merge to `main` or production default change without owner visual approval.


## 2026-11-25 — Shared channel growth audit

- [x] Compared the previous roadmap branch with current `main`: it was diverged and behind (CurioKids by 5 commits; AInation by 3). Created fresh branch `feat/shared-growth-audit-2026-11` from each current `main`; did not force-update the old branch.
- [x] Retrieved the latest available successful analytics artifacts (runs 44739181837 and 44724594920; collected 2026-11-20; report window 2026-10-21 to 2026-11-17). Historical baseline: CurioKids 18 rows / 88.9% metadata coverage / 3,004 views / 1,465 engaged views; AInation 21 rows / 90.5% / 919 views / 376 engaged views.
- [x] Audited current published episode-state inventory: 33 video IDs per channel. Current playlist rules preview: CurioKids 66 assignment rows with 2 manual-topic-review videos; AInation 79 rows with 1 manual-topic-review video.
- [x] Identified and improved narrow planner vocabulary; added regression tests for common on-pillar topics. See `docs/GROWTH_AUDIT_2026-11-25.md`.
- [x] Audited API support: country reports are supported; thumbnail impressions/CTR are available through Reporting API Reach reports; retention curves are available through single-video Analytics API queries; Stayed-to-watch is not a standalone targeted API metric and must not be inferred from engaged views.
- [x] Recorded the owner-supplied top-10 country/language opportunity shortlist as a market reference; the top 3–4 opportunities must be ranked separately per channel from actual YouTube analytics. AInation multilingual production remains out of scope.
- [ ] Obtain fresh analytics artifacts including country/language report and playlist plan; manual workflow dispatch is required.
- [x] Improve planner taxonomy and add regression tests; remaining manual review is 2 CurioKids videos and 1 AInation video.
- [ ] Fix country report language grouping/share denominator and add supported country metrics.
- [ ] Prototype Reporting API Reach Basic and bounded retention collection; preserve publication timestamps for age-matched cohorts.
- [ ] Run PR CI and explicit render-only Daily Short dry-runs in both repositories (AInation EP020). No scheduled/publishing action.

**Safety:** no upload token was touched; no live playlist, video metadata, queue, schedule or publishing behaviour changed. Historical analytics are not presented as current. Work is scoped to shared analytics and recommendations.


## 2026-11-25 — Shared growth CI validation update

- [x] CurioKids growth-engine PR unit tests passed: run 45653482421.
- [x] AInation growth-engine PR unit tests passed after normalizing topic-filter input case: run 45653499001.
- [x] Expanded playlist planner vocabulary and added regression tests for on-pillar topic titles. Current preview leaves 2 CurioKids items and 1 AInation item for manual review.
- [ ] Fresh analytics collection and artifact inspection remain pending.
- [ ] Explicit render-only Daily Short dry-run remains pending in both repos; AInation regression path should use EP020.
- No PR merged. No publishing workflow dispatched. No upload credential or live channel state changed.


## 2026-11-25 — Country report enrichment implemented

- [x] Extended the read-only country report with engaged views, engaged views/views, subscribers gained/lost, subscribers gained per 1,000 views, average view duration and average viewed percentage.
- [x] Added the `script` and `en` language groups so custom English/script uploads are not omitted from the language report.
- [x] Increased country result retrieval to 200 rows and labelled the percentage as share of reported country views; anonymized/unavailable rows may still affect full-global coverage.
- [x] Added unit tests for country aggregation and the custom-script language group. CI rerun pending.
- No OAuth scope or secret changed. No YouTube write API used.


## 2026-11-25 — Country report tests passed

- [x] CurioKids country-report and growth-engine unit tests passed: run 45654199219.
- [x] AInation country-report and growth-engine unit tests passed: run 45654217704.
- [ ] Live analytics artifact verification remains pending; country reporting still requires a manual analytics workflow run on this feature branch.


## 2026-11-25 — Main sync and post-sync validation

- [x] Synced the latest CurioKids `main` history into `feat/shared-growth-audit-2026-11`, including the merged thumbnail language-badge implementation (PR #16; merge commit `49ddf4d3862fe9fbcab24647b859d9913ed78e46`). The branch is now 0 commits behind `main`.
- [x] Post-sync growth-engine CI passed: GitHub Actions run 45655541204; the `unit-tests` job and its analytics/growth unit-test step completed successfully.
- [ ] Render-only Daily Curio Kids Short validation remains pending. The workflow has an explicit `Dry run (render only, nothing uploaded)` option, but this GitHub connection has no workflow-dispatch action. Do not use the scheduled/publish default.
- [ ] Fresh analytics workflow and artifact verification remain pending for both channels.
- No video was rendered or uploaded in this validation; no publishing, playlist or metadata changes were made.


## 2026-11-25 — Primary-language market focus clarified

- Owner direction: target one primary language per country; do not produce secondary/regional-language variants by default.
- India: Hindi only. Explicitly do not create Tamil, Telugu or Bengali videos.
- United States: English; Indonesia: Indonesian; Brazil: Portuguese; Mexico: Spanish; Japan: Japanese; Germany: German; Vietnam: Vietnamese; Philippines: Filipino/Tagalog; Turkey: Turkish.
- CurioKids retains its existing English/Hindi/Spanish library; any additional language requires owner approval and channel analytics evidence.
- AInation remains English-only; multilingual production is outside current scope.
- Updated growth roadmap, country/language audit, TODO and progress tracking. Analytics can still report audiences in other languages; reporting does not imply production approval.


## 2026-11-25 — Analytics and measurement implementation

- [x] Added publish timestamp fields to analytics metadata and SQLite with backward-compatible schema migration; use episode publish time first and upload time only as fallback.
- [x] Added 7/14/28-day cumulative age-matched cohorts for top 20 videos using per-video daily Analytics API data; incomplete windows are omitted.
- [x] Added bounded retention curve collection for top 10 videos (one query per video).
- [x] Added YouTube Reporting API Reach Basic collector for thumbnail impressions and CTR; workflow ensures the daily report job exists and downloads available reports.
- [x] Added primary-language market report based on actual country views, clearly separating localized-language evidence from all-language country totals. India Hindi only; AInation English-only.
- [x] Added unit tests for new cohort, market-policy, publish-date and Reach API parsing logic. CurioKids run 45656948802 and AInation run 45656964107 passed.
- [ ] Inspect fresh analytics artifacts and verify whether the OAuth token and Reach Reporting job produce live data.
- [ ] Run CurioKids render-only Daily Short and verify language badges visually.
- [ ] Run AInation Daily Short render-only using EP020.
- No upload token, publishing state, live playlists, public metadata, queues or schedules were changed.


## 2026-11-25 — First live analytics artifact review

- [x] CurioKids read-only analytics workflow completed and artifact verified: run 45657091511; period 2026-10-26 to 2026-11-22; 25 per-video rows, 3,247 views, 1,559 engaged views.
- [x] AInation read-only analytics workflow completed and artifact verified: run 45657143932; same period; 28 per-video rows, 1,100 views, 443 engaged views.
- [x] Country reports and review-only playlist plans generated for both channels.
- [x] Retention curves collected for top 10 videos per channel (961 CurioKids points; 900 AInation points; no per-video query errors).
- [x] Age-matched cohort reports generated (16 CurioKids rows/12 videos; 21 AInation rows/15 videos; no query errors).
- [ ] Reach Basic report is blocked because YouTube Reporting API is disabled in Google Cloud project 702229494667 (HTTP 403 SERVICE_DISABLED). Owner must enable API; workflow will create the job and collect reports after propagation (first report may take up to 24 hours).
- [ ] Review corrected market report output after latest re-run; prior 0.0% localized average-viewed values are invalid and should not be used.
- [ ] Owner render-only visual checks remain pending in both production workflows.


## 2026-11-25 — Corrected market report and artifact validation

- [x] Regenerated and inspected corrected market-opportunity outputs: CurioKids run 45657535212; AInation run 45657556902.
- [x] Verified localized average-viewed values (CurioKids US English 56.3%, India Hindi 13.3%; AInation English-only US 35.2%, Philippines 41.0%, Indonesia 45.6%). Earlier 0.0% values were a calculation defect and are superseded.
- [x] Verified playlist plan counts: CurioKids 66 assignments / 2 manual reviews; AInation 79 / 1.
- [x] Verified retention and age-cohort artifacts: 10 curves per channel; 961/900 retention points; 16/21 cohort rows; no per-video errors.
- [ ] Enable YouTube Reporting API in Google Cloud project 702229494667; Reach Basic collector currently receives HTTP 403 SERVICE_DISABLED.
- [ ] Owner visual validation: CurioKids render-only run and AInation EP020 render-only run.


## 2026-11-25 — Topic-performance and reach integration

- [x] Exposed the channel-specific playlist taxonomy classifier for growth reporting.
- [x] Added non-exclusive topic-by-format performance summaries to growth briefs; unmatched titles are left for manual review.
- [x] Added Reach Basic per-video summary CSV and optional long-form thumbnail impressions/CTR enrichment in the growth brief.
- [x] Updated analytics workflows to enrich the growth brief after the Reach collector step.
- [x] Latest tests passed: CurioKids run 45658446499; AInation run 45658455277.
- [x] Latest analytics workflows completed: CurioKids run 45658430722; AInation run 45658440732. Topic reports verified; long-form CTR remains blocked by disabled YouTube Reporting API.
- [ ] Owner enable YouTube Reporting API in project 702229494667; rerun/allow the daily report to populate CTR.
