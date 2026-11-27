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

## Current status (2026-11-21 13:04 IST)

- Analytics collection works in both repos with the analytics-only refresh token (`YT_ANALYTICS_REFRESH_TOKEN`); the upload token is separate and untouched.
- The daily workflow loads the latest brief into its run summary. The step is optional (`continue-on-error`, 5-minute limit): a GitHub API problem there never stops a video.
- Open check: one daily **Dry run** that shows the brief in its summary.
- Dated validation notes are kept in `docs/GROWTH_ENGINE_LOG.md`; status changes go to the channel handoff's change log.


## Shared channel growth roadmap and audit (2026-11-25)

See [`docs/GROWTH_ROADMAP.md`](GROWTH_ROADMAP.md) for channel-specific priorities and [`docs/GROWTH_AUDIT_2026-11-25.md`](GROWTH_AUDIT_2026-11-25.md) for the latest shared analytics baseline, playlist inventory preview and API metric-gap audit.

The growth brief remains advisory. Topic-fit filtering and review-only playlist planning do not modify episode queues, live playlists, metadata or publishing. Fresh analytics collection, planner taxonomy refinement, CI and render-only workflow validation remain pending.
