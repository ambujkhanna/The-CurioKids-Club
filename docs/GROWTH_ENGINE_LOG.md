# Growth engine: validation log

Moved verbatim from `docs/GROWTH_ENGINE.md` on 2026-11-21 13:04 IST (07:34 UTC) so the design doc stays short. Newest last.

## Live validation snapshot — 2026-11-18 22:04 IST

- Latest analytics collection on this feature branch completed successfully and uploaded its report artifact.
- Latest observed episode/video metadata coverage: **43.8%**. The growth brief flags unknown mappings; resolve these before relying on topic-level rankings.
- The PR to `main` remains open and currently has merge conflicts (`mergeable_state=dirty`). Synchronize with current `main`, resolve conflicts and revalidate before merging. No force merge.
- Daily-workflow integration has been committed, but it is advisory: it surfaces the brief in the Actions summary and does not alter scripts or publishing.


## Post-merge audit — 2026-11-19 19:18 IST

PR #1 is merged to `main`. A post-merge daily workflow run #70 completed successfully, but its log shows the growth brief loader did not find the report because artifact download contents are nested beneath an artifact directory while the script checks only the output root. Correct the loader to locate `growth_brief.md` recursively and copy the matching JSON/MD pair into the expected path.

The latest observed analytics run #24 failed with Google OAuth `invalid_grant`; refresh the analytics-only token. After that, manually validate fresh analytics collection and run a daily dry-run to verify the brief is present in the summary. Previous valid report metadata coverage: 43.8%. Recommendations remain advisory; no automated script rewriting or publishing changes.


## Retry fixes — 2026-11-19 19:35 IST

The analytics token worked in earlier successful runs, but later retries including main run #26 fail with OAuth `invalid_grant`. Root cause is not conclusively identifiable from logs. A new analytics-only refresh token is required to restore collection; upload token is separate and must remain untouched.

Daily workflow artifact loader now recursively locates the growth brief in the downloaded artifact directory tree and copies the MD/JSON pair into `out/analytics`. Analytics workflow push trigger includes main. Daily system package installation timeout increased to 30 minutes. End-to-end loader validation remains pending until a fresh successful analytics artifact is produced.


## 2026-11-19 Analytics token recovery

- The user replaced the `YT_ANALYTICS_REFRESH_TOKEN` GitHub Actions secret in this repository. The upload secret `YT_REFRESH_TOKEN` was not changed.
- Retried the failed YouTube Analytics workflow (run attempt 2). Google OAuth refresh succeeded; analytics collection, channel-specific growth brief generation, and artifact upload all succeeded.
- Verified 7 analytics/growth unit tests passed in the workflow.
- Successful run: https://github.com/ambujkhanna/The-CurioKids-Club/actions/runs/44546121847 (artifact youtube-analytics-29).
- Remaining validation: confirm the next scheduled daily video workflow downloads the analytics artifact and displays the growth brief in its Actions summary. No daily video workflow was manually dispatched and no video was published as part of this recovery.


## Current-main audit — 2026-11-19 21:30 IST

- Rechecked the current `main` workflow and collector files. The Daily Short workflow includes recursive discovery of `growth_brief.md` inside downloaded artifact subfolders and places it in the Actions summary.
- The manual `Dry run (render only, nothing uploaded)` action is available for safe end-to-end validation; that post-fix run has not yet been executed.
- The Weekly Long Video workflow is separate and does not currently load the growth brief. Its package-install timeout was increased from 15 to 30 minutes (commit `cc245c9307c7d2719103c8e67420c353ae6786ca`).
- Latest known metadata coverage remains 43.8%. The current Short state file contains 17 distinct video IDs; do not infer mappings for analytics rows absent from the state.
- No production workflow was dispatched and no upload/publishing behavior changed.

## 2026-11-19 — Unmapped-video audit

The latest inspected analytics artifact contains 18 rows, 16 mapped (88.9%). Unknown IDs: `r_GUBf5Flho` (68 views) and `5iwnr-Y9hqc` (32 views). These are surfaced in the growth brief for manual review; the system deliberately does not guess episode IDs. PR #2 adds this output and regression coverage: https://github.com/ambujkhanna/The-CurioKids-Club/pull/2.


## 2026-11-19 — Unmapped review and validation status

PR #2 is merged to main (`ce8ec46dfe2b56328aa9ce0a72b4b3808b2f274a`). Growth briefs now list unknown video IDs and views in JSON and Markdown, linking to the video for manual verification. Latest artifact: 18 rows, 16 mapped (88.9%); unresolved: `r_GUBf5Flho` (68 views), `5iwnr-Y9hqc` (32 views).

PR unit tests passed. A subsequent main analytics collection failed with `invalid_grant` (run `44561529784`), so no fresh growth brief was generated. The latest observed daily run's loader had no brief available; end-to-end summary validation is still pending. Do not infer mappings or modify upload credentials.


## 2026-11-19 — Trigger scope

PR #3 merged (`b067f31668b2217f01a304900a8b4122e0bc42fa`). Push-triggered analytics collection is limited to analytics source/dependencies/tests, episode metadata state and the analytics workflow. Documentation-only commits no longer consume refresh-token attempts. Scheduled and manual analytics runs remain enabled.


## Follow-up operational validation — 2026-11-19

- PR #3's analytics push path filter is merged in both repositories, preventing documentation-only edits from triggering token refreshes.
- Fresh analytics collection is still blocked: the latest post-merge push runs failed in CurioKids (44562221268) and AInation (44562248765). The known OAuth invalid_grant issue remains unresolved. Restore the analytics-only refresh token before treating any report as current; do not modify upload token YT_REFRESH_TOKEN.
- AInation daily run 44562499073 is in progress, but its selected workflow-dispatch inputs are not exposed in the run summary. At the latest check, the run had not reached the read-only growth-brief loader or render/upload step. Because the workflow's default action is Next video (scheduled), do not count this as a safe dry-run without confirming the selected action in GitHub Actions.
- CurioKids post-fix daily dry-run and both channels' post-fix growth-brief summary checks remain outstanding.
- No automatic script rewriting or publishing was introduced. No assistant-initiated video upload or publishing occurred during this audit.


## 2026-11-20 — Current operational status

- [x] Rechecked current workflow runs and logs. Daily scheduled run 44578898591 completed successfully and uploaded Short https://www.youtube.com/shorts/dcNLkD2l3p8 for scheduled publication on 20 Nov 2026 at 17:55 IST. The next scheduled run 44631536769 also completed successfully; its log correctly reported “Nothing due right now” because the alternate-day/time-window logic did not select a video. No duplicate upload occurred in that run.
- [x] The daily workflow's read-only growth-brief loader step completed successfully in run 44631536769. The brief is from the last successful analytics artifact, however, and is stale until fresh collection succeeds.
- [ ] Latest scheduled analytics run 44606697918 failed with Google OAuth `invalid_grant` (“Token has been expired or revoked”). Reauthorize and replace only `YT_ANALYTICS_REFRESH_TOKEN`; leave `YT_REFRESH_TOKEN` unchanged.
- [ ] A manual dry-run validation is still pending. The available GitHub integration does not expose workflow dispatch; use Actions → Daily Curio Kids Short → Run workflow → action `Dry run (render only, nothing uploaded)` to validate without publishing.
- Guardrails unchanged: no automatic script rewriting; no upload token, publishing logic, schedule or episode state changed by this audit.


## Analytics token recovery — 2026-11-20

- User clarified that the prior day's update may have replaced the short-lived access token rather than the refresh token. The user then updated `YT_ANALYTICS_REFRESH_TOKEN` in both repositories.
- Re-ran the failed analytics jobs using the current repository secrets. CurioKids run 44606697918 and AInation run 44603311245 both completed successfully.
- Both runs passed analytics unit tests, Google OAuth refresh, read-only collection, channel-specific growth brief generation, and report/database artifact upload. This validates the current analytics refresh-token configuration in both repositories.
- The upload secret `YT_REFRESH_TOKEN` was not changed. Analytics collection is read-only with respect to YouTube publishing; no video was uploaded or published by these retries.
- Remaining separate validation: run each Daily Short workflow with the explicit `Dry run (render only, nothing uploaded)` action and confirm the latest growth brief appears in the Actions summary. Do not select the scheduled/publish default for this check.


## Follow-up validation — 2026-11-20

- CurioKids analytics run 44739181837 completed successfully after the refresh-token update.
- The newer AInation push-triggered analytics run 44724594920 was initially a failure from before the token correction; retry attempt 2 completed successfully. Current analytics refresh-token configuration is validated in both channels.
- Separate end-to-end integration validation is still required: run each Daily Short workflow using its explicit `Dry run (render only, nothing uploaded)` action and verify that the current growth brief appears in the Actions summary. Do not use the scheduled/publish default.


## 2026-11-25 — Shared growth baseline and API metric-gap audit

- Latest retrievable successful artifacts: CurioKids run 44739181837 and AInation run 44724594920, collected 2026-11-20 for 2026-10-21 through 2026-11-17. These are historical, not a fresh baseline.
- CurioKids: 18 video rows, 13 Shorts, 16 mapped (88.9%), 3,004 views and 1,465 engaged views. AInation: 21 rows, 17 Shorts, 19 mapped (90.5%), 919 views and 376 engaged views.
- Current state inventory preview: 33 video IDs per channel. Planner preview: 66 CurioKids assignment rows (11 videos need manual topic review) and 77 AInation rows (5 need manual review). Improve keyword/phrase coverage before treating this as the final owner-facing playlist plan.
- Country-report code exists in the targeted Analytics collector, but retrieved artifacts predate it. Country report needs the English custom-script cohort, supported engaged/subscriber metrics and a correct denominator for country shares.
- Official API audit: thumbnail impressions/CTR are in YouTube Reporting API Reach Basic/Reach Combined; audience-retention curves are supported through single-video Analytics API queries; Shorts Stayed-to-watch is not a standalone targeted API metric and must not be derived from engagedViews.
- Publication-age cohorts require normalized publication timestamps from state plus daily video reports. Per-video subscribersGained must be labelled as watch-page-attributed, not total channel subscriber conversion.
- Fresh analytics collection, CI and render-only workflow checks remain pending. No upload token or publishing behaviour was changed.


## 2026-11-25 — CI validation

- CurioKids growth-engine tests passed in GitHub Actions run 45653482421.
- AInation growth-engine tests passed in run 45653499001 after normalizing topic-filter inputs in `_ok()`.
- Playlist planner taxonomy refinements and regression tests are included in both branches. Current state preview leaves 2 CurioKids and 1 AInation item for manual review.
- Fresh analytics artifact and explicit render-only daily workflow checks remain pending. No PR merged or publishing action dispatched.


## 2026-11-25 — Country report enrichment

The country report now includes engaged views, engaged views/views (not Shorts Stayed to watch), subscribers gained/lost, subscribers gained per 1,000 views, average duration and average viewed percentage. Added custom `script` and explicit `en` language groups. Country share is labelled as a share of returned country rows (up to 200), not asserted to be a perfect global denominator. Unit tests added; CI rerun and live artifact verification pending.


## 2026-11-25 — Country report CI result

The enriched country-report tests passed in CurioKids run 45654199219 and AInation run 45654217704. Live API output still needs verification by manually running the YouTube Analytics workflow on `feat/shared-growth-audit-2026-11`.


## 2026-11-25 — Main sync and post-sync validation

- Synced latest CurioKids `main` into the shared growth branch, including language-badge changes (PR #16; merge commit `49ddf4d3862fe9fbcab24647b859d9913ed78e46`). Branch is 0 commits behind `main`.
- Post-sync growth-engine CI passed: run 45655541204 (`unit-tests` job).
- Render-only Daily Curio Kids Short remains pending because workflow dispatch is not exposed by the connected GitHub action tools. The workflow option is confirmed as `Dry run (render only, nothing uploaded)`; do not select the scheduled/publish default.
- No video render/upload, live playlist change, metadata edit or publishing action was performed.
