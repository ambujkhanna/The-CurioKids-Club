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

## Owner-supplied country and language opportunity shortlist

The following 2026 audience estimates and language options were supplied by the owner as a **market-size reference**. They have not been independently validated in this audit and must not be treated as YouTube audience counts.

| Rank | Country | Estimated audience | Primary language focus |
|---:|---|---:|---|
| 1 | India | ~573M | Hindi only |
| 2 | United States | ~268M | English |
| 3 | Indonesia | ~155M | Indonesian |
| 4 | Brazil | ~154M | Portuguese |
| 5 | Mexico | ~89.4M | Spanish |
| 6 | Japan | ~83.3M | Japanese |
| 7 | Germany | ~68.8M | German |
| 8 | Vietnam | ~62.1M | Vietnamese |
| 9 | Philippines | ~59.6M | Filipino/Tagalog |
| 10 | Turkey | ~57.9M | Turkish |

**Decision rule:** use one primary language per target country as the default. The country list is a market-size reference only; rank opportunities using each channel's actual country-level views, watch time, average viewed percentage, engaged views, subscribers gained where supported, returning viewers, sample size, content fit, localization quality and production cost. Population rank alone never justifies a new language. Do not create regional/secondary-language variants just because they are spoken in a market.

- India: Hindi is the sole planned language focus. Do not create Tamil, Telugu or Bengali videos.
- United States: English. Indonesia: Indonesian. Brazil: Portuguese. Mexico: Spanish. Japan: Japanese. Germany: German. Vietnam: Vietnamese. Philippines: Filipino/Tagalog. Turkey: Turkish.
- CurioKids: preserve its existing English, Hindi and Spanish library; use the country mapping above to guide any future market-specific production. No new language is added without explicit owner approval and audience evidence.
- AInation: English-only production remains the current approved scope; no multilingual expansion is authorised. If that policy is revisited, start with the single primary language for a target market, not secondary/regional variants.
- Do not interpret the presence of multiple languages in a country as a production requirement.

## Published-video playlist inventory preview

The current published state was read from episode/long/custom state files and CurioKids' configured library category state files. Counts below are a preview from applying the current planner keyword rules; the Python workflow has not yet produced a fresh downloadable artifact.

| Channel | Video IDs in state | Suggested assignment rows | Topic rows | Language rows | Manual topic review |
|---|---:|---:|---:|---:|---:|
| The CurioKids Club | 33 | 66 | 33 | 33 | 2 videos |
| AInation Studio | 33 | 77 | 44 | 33 | 5 videos |

CurioKids topic rows: Everyday Science & Discoveries 11; Human Body 8; Animals 5; Space & Universe 6; Nature & Plants 1. Language rows: English 21; Hindi 9; Spanish 3.

AInation topic rows: AI Explained 22; AI Tools & Workflows 6; AI Safety, Privacy & Verification 4; AI in Everyday Life 4; AI Coding & Building 2; AI Creativity 1. All 33 entries are assigned to English.

**Planner taxonomy refinement:** added regression-covered terms for octopus/zebra, blinking, planets and sky-colour topics. The preview now leaves only two CurioKids videos for manual review: the Children's Day Short and “Evolution vs Revolution”, whose fit needs human judgement. No live playlists were changed.

## YouTube API metric-gap audit

The existing read-only collector already retrieves per-video views, engaged views, estimated watch time, average view duration, average viewed percentage, likes, comments, shares and subscribers gained/lost. Country-report code exists in `pipeline/analytics.py`, but the retrieved artifacts predate that addition and contain no country/language report. A fresh analytics collection is required.

| Requirement | Finding | Recommended next step |
|---|---|---|
| Audience by country/language | Targeted Analytics API supports country reports. Current code requests views, watch time and average viewed percentage by all videos and selected language groups. | Run fresh collection; add supported engagedViews/subscriber metrics; include the missing `script` language group for custom English videos. |
| Country share | Current calculation uses up to 200 returned country rows and labels the value as share of reported views; API anonymization or unavailable rows can still mean it is not a mathematically complete global denominator. | Keep the label explicit and verify coverage from fresh report output. |
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
2. Improve planner vocabulary and add regression tests for the on-pillar examples above. (Done; 2 CurioKids and 1 AInation item remain for manual review.)
3. Extend country reporting with supported engaged/subscriber metrics, the English custom-script cohort and a clear returned-country share denominator. (Implemented; fresh API artifact verification pending.)
4. Prototype Reporting API Reach Basic and bounded retention collection.
5. Preserve publication timestamps and add age-matched cohorts.
6. Run PR CI and explicitly selected render-only Daily Short dry-runs in both repos. For AInation use EP020. Do not select a scheduled/publishing action.

**Guardrails:** analytics-only OAuth remains read-only; do not touch upload credentials. No publishing, live playlist, video metadata, queue, schedule or channel-setting changes. Recommendations remain advisory and require owner review.


## Post-sync validation update — 2026-11-25

- CurioKids feature branch was synced with the latest `main`, including the merged thumbnail language-badge work (sync PR #16; merge commit `49ddf4d3862fe9fbcab24647b859d9913ed78e46`). It is now 0 commits behind `main`.
- Post-sync growth-engine CI passed in run 45655541204. The `unit-tests` job and analytics/growth unit-test step completed successfully.
- The explicit render-only Daily Curio Kids Short workflow option was inspected. It is available as `Dry run (render only, nothing uploaded)`, but could not be dispatched through the connected GitHub actions interface. It remains pending; no scheduled or publishing action was selected.
- Fresh analytics artifacts and the AInation EP020 render-only dry-run also remain pending.


## Owner language direction — 2026-11-25

- Use one primary language per target country; do not expand into secondary or regional languages by default.
- India: Hindi only. Explicitly exclude Tamil, Telugu and Bengali video production.
- United States: English; Indonesia: Indonesian; Brazil: Portuguese; Mexico: Spanish; Japan: Japanese; Germany: German; Vietnam: Vietnamese; Philippines: Filipino/Tagalog; Turkey: Turkish.
- CurioKids may continue its existing English/Hindi/Spanish library. New language production still requires owner approval and audience evidence.
- AInation remains English-only; multilingual production is not in scope unless separately approved.
- Analytics may still report other languages or audience locations. Reporting them does not authorise creating videos in those languages.


## Implementation update — 2026-11-25

Implemented on `feat/shared-growth-audit-2026-11` in both repositories:

- Read-only YouTube Analytics country reports with engaged views, subscribers gained/lost and clearly labelled returned-country share.
- Primary-language market opportunity report ranked by actual channel country views. Localized-language metrics are only shown when matching published language-version data exists; country totals are not treated as proof of local-language demand.
- Publish timestamp persistence from episode state, with upload timestamp fallback, and complete 7/14/28-day cumulative age cohorts for the top 20 videos.
- Bounded audience-retention curves for the top 10 videos using one targeted query per video.
- YouTube Reporting API Reach Basic collector for thumbnail impressions and CTR; workflow creates the daily reporting job if absent and downloads available reports.
- Unit tests for cohort windows, publish-date migration/fallback, primary-language market policy, Reach CSV parsing and weighted CTR.

CI results: CurioKids latest analytics/growth suite run 45656948802 passed; AInation latest suite run 45656964107 passed. Fresh collection workflows were triggered on the feature branch; report artifacts and Reach API job/report availability still require run completion and inspection. No publishing credentials or upload workflows were used.


## Fresh analytics verification — 2026-11-25

Both read-only analytics workflows completed successfully on the feature branch and uploaded artifacts:

- CurioKids: run [45657091511](https://github.com/ambujkhanna/The-CurioKids-Club/actions/runs/45657091511), report window 2026-10-26 to 2026-11-22, 25 per-video rows, 3,247 views and 1,559 engaged views.
- AInation: run [45657143932](https://github.com/ambujkhanna/youtube-studio-automation/actions/runs/45657143932), same report window, 28 per-video rows, 1,100 views and 443 engaged views.

Country data is partial/anonymized and shares are explicitly shares of returned rows, not all channel views. CurioKids returned-country leaders: USA 1,322 views (English-main group 1,233); India 642 (Hindi group 344); Philippines 108; Indonesia 30. The Hindi group had 344 views and 13.3% average viewed in this period; this is a signal for editorial review, not a causal conclusion or reason to discontinue Hindi. AInation returned-country leaders: India 90, USA 66, Philippines 51, Indonesia 35; AInation remains English-only.

Retention collection returned 10 curves per channel with 961 CurioKids points and 900 AInation points, no per-video query errors. Age-cohort output contains 16 CurioKids rows across 12 videos and 21 AInation rows across 15 videos, with no query errors; only complete 7/14/28-day windows are included. Playlist plan artifacts were generated and uploaded; assignments remain review-only and no live playlists were changed.

Reach Basic code and workflow integration are implemented, but the run log reports HTTP 403 SERVICE_DISABLED: YouTube Reporting API is not enabled in Google Cloud project 702229494667. No Reach report job or Reach artifact was created. Enable the API in that project, then the next scheduled/triggered workflow will create the daily report job; YouTube may take up to 24 hours to produce the first report.

The first market report exposed a calculation issue in the localized average-viewed field; the code and regression test have been corrected and a fresh run is in progress. Do not use the old 0.0% localized values.
