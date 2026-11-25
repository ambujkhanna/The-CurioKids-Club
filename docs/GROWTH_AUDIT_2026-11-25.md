# Shared channel growth audit — 2026-11-25

**Scope:** Shared analytics/growth-engine work for The CurioKids Club and AInation Studio. Channel-specific creative decisions remain separate.  
**Status:** Historical baseline and API gap audit completed; fresh analytics, planner taxonomy refinement, CI and render-only workflow validation remain pending.

## Analytics baseline and freshness

Latest retrievable successful artifacts: CurioKids run 44739181837 and AInation run 44724594920, collected 2026-11-20, covering 2026-10-21 through 2026-11-17. These are historical, not a current audience baseline.

| Channel | Video rows | Shorts rows | Identified rows | Metadata coverage | Views (all rows) | Engaged views (all rows) |
|---|---:|---:|---:|---:|---:|---:|
| The CurioKids Club | 18 | 13 | 16 | 88.9% | 3,004 | 1,465 |
| AInation Studio | 21 | 17 | 19 | 90.5% | 919 | 376 |

Shorts-only context:
- CurioKids: 13 Shorts, 2,894 views, 1,425 engaged views (49.2% engaged views/views). Top Short: “Why Is the Sky Blue?” — 1,293 views, 955 engaged views, 56.5% average viewed, 8 subscribers gained.
- AInation: 17 Shorts, 726 views, 314 engaged views (43.3% engaged views/views). Top Short: “What Not to Tell AI” — 198 views, 111 engaged views, 47.0% average viewed, 1 subscriber gained.

These are descriptive observations, not targets or causal findings. Engaged views/views must not be presented as Shorts “Stayed to watch”.

Historical unknown IDs:
- CurioKids: `r_GUBf5Flho` (68 views), `5iwnr-Y9hqc` (32 views).
- AInation: `uhSn_4CVPHQ` (139 views), `ToSaTHNDoEg` (46 views).

Current custom/script state now contains `r_GUBf5Flho` (CurioKids) and `ToSaTHNDoEg` (AInation), so the old artifact predates those mappings. `5iwnr-Y9hqc` and `uhSn_4CVPHQ` were not found in the current state files scanned and need manual verification. Do not guess episode IDs.

## Published-video playlist inventory preview

The current published state was read from episode/long/custom state files and CurioKids' configured library category state files. Counts below are a preview from applying the current planner keyword rules; the Python workflow has not yet produced a fresh downloadable artifact.

| Channel | Video IDs in state | Suggested assignment rows | Topic rows | Language rows | Manual topic review |
|---|---:|---:|---:|---:|---:|
| The CurioKids Club | 33 | 66 | 33 | 33 | 11 videos |
| AInation Studio | 33 | 77 | 44 | 33 | 5 videos |

CurioKids topic rows: Everyday Science & Discoveries 9; Space & Universe 5; Human Body 5; Animals 2; Nature & Plants 1. Language rows: English 21; Hindi 9; Spanish 3.

AInation topic rows: AI Explained 22; AI Tools & Workflows 6; AI Safety, Privacy & Verification 4; AI in Everyday Life 4; AI Coding & Building 2; AI Creativity 1. All 33 entries are assigned to English.

**Planner taxonomy issue:** obvious on-pillar titles are falling into manual review because the keyword vocabulary is narrow. Examples: CurioKids octopus, zebra, eye-blinking, planets-rhyme and sky-colour videos; AInation neural networks, voice assistants, YouTube recommendations and machine learning. Add deliberate vocabulary/phrase coverage and regression tests before using this as the final playlist plan. Children's Day and genuinely off-pillar items should remain manual review. No live playlists were changed.

## YouTube API metric-gap audit

The existing read-only collector already retrieves per-video views, engaged views, estimated watch time, average view duration, average viewed percentage, likes, comments, shares and subscribers gained/lost. Country-report code exists in `pipeline/analytics.py`, but the retrieved artifacts predate that addition and contain no country/language report. A fresh analytics collection is required.

| Requirement | Finding | Recommended next step |
|---|---|---|
| Audience by country/language | Targeted Analytics API supports country reports. Current code requests views, watch time and average viewed percentage by all videos and selected language groups. | Run fresh collection; add supported engagedViews/subscriber metrics; include the missing `script` language group for custom English videos. |
| Country share | Current calculation is based on returned country rows (currently capped at 50), so it may not represent the full channel total. | Retrieve all supported countries for the denominator or label share as share of returned countries. |
| Thumbnail impressions/CTR | Not part of the current targeted per-video query. Reporting API provides `channel_reach_basic_a1` and `channel_reach_combined_a1`, with `video_thumbnail_impressions` and `video_thumbnail_impressions_ctr`. | Check/enable YouTube Reporting API in each Cloud project; create Reach report jobs and ingest daily CSVs. |
| Shorts Stayed to watch | Not exposed as a standalone metric in the targeted API list. `engagedViews` is not the ratio and does not expose the swiped-away denominator. | Do not derive it from engaged views. Use Studio/exported data if available; otherwise mark unavailable via API. |
| Audience-retention curve | Supported with `elapsedVideoTimeRatio` and `audienceWatchRatio` / `relativeRetentionPerformance`; one video ID per request. | Add bounded optional queries for selected/top videos, not every video on every daily run. |
| Publication-age cohorts | Existing report uses a common window; metadata extraction does not preserve a normalized publication timestamp. | Preserve verified `uploaded_at` / publish timestamp and compare first 7/14/28 days using daily video reports. |
| Subscriber conversion | Per-video `subscribersGained` is supported, but in video-dimension reports it counts subscriptions from that video's watch page, not all channel-level sources. | Show subscribers gained per 1,000 views as a video-attributed indicator, not total channel conversion. |

## Official API references

- https://developers.google.com/youtube/analytics/metrics
- https://developers.google.com/youtube/analytics/channel_reports
- https://developers.google.com/youtube/reporting/v1/reports/channel_reports
- https://developers.google.com/youtube/reporting/v1/reports

## Safe next steps

1. Run analytics manually in each repo and verify a fresh artifact includes `audience_countries.md/.json` and `playlist_plan.csv/.md`. This GitHub integration does not expose workflow dispatch.
2. Improve planner vocabulary and add regression tests for the on-pillar examples above.
3. Extend country reporting with supported engaged/subscriber metrics, the English custom-script cohort and a correct share denominator.
4. Prototype Reporting API Reach Basic and bounded retention collection.
5. Preserve publication timestamps and add age-matched cohorts.
6. Run PR CI and explicitly selected render-only Daily Short dry-runs in both repos. For AInation use EP020. Do not select a scheduled/publishing action.

**Guardrails:** analytics-only OAuth remains read-only; do not touch upload credentials. No publishing, live playlist, video metadata, queue, schedule or channel-setting changes. Recommendations remain advisory and require owner review.
