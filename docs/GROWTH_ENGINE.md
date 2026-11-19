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
