# YouTube Analytics collection

This repository includes a read-only collector at `pipeline/analytics.py`.

## Collected metrics

Per-video views, engaged views, estimated minutes watched, average view duration, average view percentage, likes, comments, shares, and subscribers gained/lost from the video's watch page. Video IDs are joined to local episode state for title, episode ID, language and format.

## One-time authorization

Add a new GitHub Actions secret named `YT_ANALYTICS_REFRESH_TOKEN`. It must be a refresh token authorized for the correct channel/Brand Account with scope:

```
https://www.googleapis.com/auth/youtube.readonly
```

The current `reports.query` method requires this read-only scope. Enable **YouTube Analytics API** in the Google Cloud project. The workflow uses existing `YT_CLIENT_ID` and `YT_CLIENT_SECRET`; alternatively configure `YT_ANALYTICS_CLIENT_ID` and `YT_ANALYTICS_CLIENT_SECRET`. Do not replace or reuse the upload refresh token. Never put credentials in source files or artifacts.

## Run locally

```bash
export YT_ANALYTICS_CLIENT_ID="..."
export YT_ANALYTICS_CLIENT_SECRET="..."
export YT_ANALYTICS_REFRESH_TOKEN="..."
python pipeline/analytics.py
python pipeline/analytics.py --start-date 2026-10-01 --end-date 2026-10-28
```

The default period is 28 days ending three days ago to allow for YouTube reporting latency. The workflow installs only the lightweight dependencies in `pipeline/analytics-requirements.txt`, not the full video-rendering stack. Outputs are written to `out/analytics/`:

- `analytics.sqlite3`: local SQLite store, upserted by channel/date range/video.
- CSV export for analysis.
- Markdown top-video report.

Repeated local runs using the same database preserve prior reporting windows. GitHub Actions uses the Actions cache as best-effort continuity and uploads each run's SQLite/CSV/Markdown outputs as a 90-day artifact. The cache is not a permanent database; download and retain the SQLite artifact for long-term history.

## GitHub Actions

Run **YouTube Analytics — collect report** from Actions. It also runs daily. Optional manual inputs override the date range. If `YT_ANALYTICS_REFRESH_TOKEN` is absent, the workflow exits cleanly without calling Google.

This workflow is read-only: it does not upload, edit, schedule or publish videos and does not modify episode state.

## Interpretation

- Review **engaged views** and average view percentage alongside public views for Shorts.
- Compare videos at similar ages and formats; don't compare a new upload with a 28-day-old upload.
- This targeted report does not include thumbnail impressions or CTR.
- Analytics reporting has a processing delay; recent dates can be incomplete.
- Correlation is not proof of causation. Treat topic, hook, format and thumbnail changes as experiments.

## References

- [YouTube Analytics API — reports.query](https://developers.google.com/youtube/analytics/reference/reports/query)
- [YouTube Analytics API — metrics](https://developers.google.com/youtube/analytics/metrics)
- [YouTube Analytics API — sample requests](https://developers.google.com/youtube/analytics/sample-requests)
