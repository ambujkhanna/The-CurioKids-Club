# YouTube Analytics collection

This repository includes a read-only collector at `pipeline/analytics.py`.

## Collected metrics

Per-video views, engaged views, estimated minutes watched, average view duration, average view percentage, likes, comments, shares, and subscribers gained/lost from the video's watch page. Video IDs are joined to local episode state for title, episode ID, language and format.

## One-time authorization

Add a new GitHub Actions secret named `YT_ANALYTICS_REFRESH_TOKEN`. It must be a refresh token authorized for the correct channel/Brand Account with scope:

```
https://www.googleapis.com/auth/yt-analytics.readonly
```

The collector requests the least-privilege YouTube Analytics read-only scope (`yt-analytics.readonly`). Enable **YouTube Analytics API** in the Google Cloud project. The workflow uses existing `YT_CLIENT_ID` and `YT_CLIENT_SECRET`; alternatively configure `YT_ANALYTICS_CLIENT_ID` and `YT_ANALYTICS_CLIENT_SECRET`. Do not replace or reuse the upload refresh token. Never put credentials in source files or artifacts.

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
- The targeted Analytics API report itself does not include thumbnail impressions or CTR; the separate Reach Basic Reporting API collector provides those metrics when that API is enabled.
- Analytics reporting has a processing delay; recent dates can be incomplete.
- Correlation is not proof of causation. Treat topic, hook, format and thumbnail changes as experiments.

## References

- [YouTube Analytics API — reports.query](https://developers.google.com/youtube/analytics/reference/reports/query)
- [YouTube Analytics API — metrics](https://developers.google.com/youtube/analytics/metrics)
- [YouTube Analytics API — sample requests](https://developers.google.com/youtube/analytics/sample-requests)


## Audience by country (added 2026-11-23 06:30 IST (01:00 UTC))

Every analytics run also asks YouTube where the views come from (`dimensions=country`), for the whole channel and for each language version (English/main, Hindi, Spanish, trend Shorts). The result (`audience_countries.md/.json`) is added to the growth brief, so it shows in every daily run's summary. Use it to decide whether a language version is worth keeping or adding (owner, 2026-11-23: "is the audience really coming from these locations?").
Also fixed the same day: Spanish versions (`es`) and script/trend Shorts (`custom/`) are now matched to their episodes (they were "unknown" before).


## Extended reports (2026-11-25)

The analytics collector now additionally produces:

- `audience_countries.md/.json`: country distribution for all videos and each published language group.
- `market_opportunities.md/.json`: target-country view ranking using the owner's primary-language policy. It separates localized-language evidence from all-language country totals. India is Hindi only; Tamil, Telugu and Bengali are excluded. CurioKids retains its existing English/Hindi/Spanish versions; AInation remains English-only.
- `age_matched_cohorts.md/.json`: cumulative 7/14/28-day performance windows from state-file publish dates (upload timestamp fallback), for the top 20 videos with complete windows. State timestamps should be checked against actual YouTube publish dates before drawing conclusions.
- `retention_curves.md/.json`: bounded audience retention curves for the top 10 videos, one Analytics API query per video.
- `reach_basic_daily.csv` and `reach_basic.md`: thumbnail impressions and CTR from YouTube Reporting API Reach Basic.

The workflow creates the Reach Basic reporting job if it does not exist. YouTube may take up to 24 hours to generate the first report. Reach CTR applies to eligible thumbnail surfaces and is not a Shorts-feed swipe metric. The analytics workflow uses the read-only Analytics OAuth token only; it does not touch upload credentials.

To run the Reach collector manually after authorisation: `python pipeline/reach_reporting.py --ensure-job --output-dir out/analytics`. Normal workflow runs also ensure the job exists and collect reports when available.


## Reporting API enablement blocker

The Reach Basic collector is implemented and tested, but the first workflow run returned HTTP 403 SERVICE_DISABLED for Google Cloud project 702229494667. Enable **YouTube Reporting API** in the same Google Cloud project used by the analytics OAuth client: https://console.developers.google.com/apis/api/youtubereporting.googleapis.com/overview?project=702229494667. No new OAuth scope is needed; the existing read-only scope is supported. After enabling, allow propagation and rerun the analytics workflow. The workflow creates the Reach Basic daily job if absent; the first report may take up to 24 hours.


## Topic and packaging insights

The growth brief groups video performance by channel-specific topic taxonomy and format (Shorts/long-form). Metrics include video count, views, engaged views, engaged-view rate, weighted average viewed percentage and subscribers per 1,000 views. Topic matches are non-exclusive; unmatched titles remain manual review. When Reach Basic data is available, the brief also shows long-form thumbnail impressions and CTR by video. Do not use thumbnail CTR as a Shorts-feed swipe metric.
