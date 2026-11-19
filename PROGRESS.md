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
