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
