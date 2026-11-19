# Analytics-led growth loop

**Last updated:** 2026-11-18T21:50:00+05:30

## What the automation does

1. The read-only analytics workflow fetches per-video views, engaged views, watch time, average view duration, average viewed percentage, likes, comments, shares, and subscriber gains/losses.
2. It exports CSV, Markdown and SQLite, then runs `pipeline/growth.py` to create `growth_brief.md` and `growth_brief.json`.
3. The analytics artifact retains those files for 90 days.
4. The daily Short workflow downloads the latest successful analytics artifact, if one exists, and places the growth brief in that run's GitHub Actions summary for editorial use.

## Editorial use

Use the latest growth brief when selecting and drafting the next episodes. Treat its ranked videos and guidance as directional evidence, not causal proof. Compare like formats and similar publication ages. Repair unknown episode mappings before making topic-level decisions.

Channel-specific guidance is embedded in `pipeline/growth.py`:
- CurioKids: curiosity-led child-friendly questions, immediate visual/verbal hooks, one clear concept, accessible vocabulary and a satisfying answer.
- AInation: practical AI use and safety, concrete problem/outcome openings, demonstrations, and explicit limitations/verification.

## Guardrails and limitations

- Analytics uses a separate read-only refresh token; upload credentials and publishing behavior are unchanged.
- The growth brief is advisory. It does not rewrite queued episode JSON, change titles, alter schedules, upload videos, or publish automatically.
- Current reports do not include impressions, CTR or audience-retention curves.
- Unknown metadata remains visible and lowers the metadata-coverage score; no titles or episode IDs are guessed.
- Keep analytics reports in Actions artifacts; do not commit private performance snapshots to the public repository.

## Validation

Run locally:
```bash
PYTHONPATH=pipeline python -m unittest discover -s tests -v
python pipeline/growth.py --csv out/analytics/<report>.csv --channel-key CHANNEL_KEY
```


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
