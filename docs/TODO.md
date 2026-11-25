# To-do list (owner + Claude)

**Same file in both repos.** Newest tasks first. Tick a box when done and add the date. Detailed steps are in the linked plans.

## A. Keep the code private, runs stay free (owner chose option 2, 2026-11-23)
Plan: [`docs/PRIVATE_CODE_PLAN.md`](PRIVATE_CODE_PLAN.md)
- [x] `LICENSE` "All rights reserved" notice added (2026-11-23)
- [ ] **Owner:** create private repos `curiokids-core` + `aination-core` (§3.1)
- [ ] **Owner:** copy the history into them, clone them locally (§3.2)
- [ ] **Owner:** fine-grained token (1 year) → secret `CORE_TOKEN`; variable `CORE_REPO`; secret `ARTIFACT_PASSWORD` in both public repos (§3.3–3.4)
- [ ] **Claude:** bundle A for the core repos (private logs, analytics into `data/`, issues to the core repo)
- [ ] **Claude:** bundle B for the public runner repos (workflows check out the core repo)
- [ ] **Owner:** manual test runs pass (dry run, trend dry run, radar, analytics) in both runner repos
- [ ] **Claude + owner:** empty the public repos (keep workflows, README, LICENSE), delete old run logs
- [ ] **Owner:** one full day of scheduled runs OK

## B. Pinterest for The CurioKids Club (owner, 2026-11-23)
Plan: [`docs/PINTEREST_PLAN.md`](PINTEREST_PLAN.md)
- [ ] **Owner:** Pinterest Business account, claim the YouTube channel, 3–5 boards (§1.1–1.3)
- [ ] **Owner:** developer app (App ID + secret), request Standard access (§1.4–1.5)
- [ ] **Claude:** one-time login helper → **owner** saves `PINTEREST_REFRESH_TOKEN` + app secrets (§3)
- [ ] **Claude:** `pinterest_post.py`, wiring in `daily.py` + workflows, tests, docs (§4)
- [ ] **Owner:** backfill test "Post 3 old videos to Pinterest"; then `PINTEREST=on` after Standard access (§5)

## C. Open from earlier
- [ ] **Owner:** first weekly art run by hand (kids repo), tick `HF_TOKEN` on the Kaggle kernel after the first try (`docs/AUTOMATION_KAGGLE.md` §0); then `ART_WEEKLY=on`
- [ ] **Owner:** look at "Audience by country" in the next analytics brief, then decide on Spanish (`ES_SHORTS`) and any other language
- [ ] **Owner:** daily: make API uploads public in YouTube Studio until Google approves the API audit
- [ ] Old branch `feature/modern-visual-engine` (kids): archive tag + delete, or keep
- [ ] Old branches still on GitHub (both repos): `feat/growth-unmapped-review`, `feat/youtube-growth-engine`, `fix/analytics-push-paths` (+ AInation `fix/episode-id-case-insensitive`): delete (all merged)


## D. Channel growth roadmap (approved 2026-11-25)
Plan: [`docs/GROWTH_ROADMAP.md`](GROWTH_ROADMAP.md)

### Shared foundation — both channels
- [ ] **Claude:** baseline latest successful analytics; report metric availability and video/episode metadata coverage.
- [ ] **Claude:** investigate/add eligible impressions and impressions CTR metrics; document API/report limitations.
- [ ] **Claude:** investigate/add Shorts Stayed to watch / Viewed vs. swiped away where available; do not fabricate if API access is unavailable.
- [ ] **Claude:** investigate audience-retention curve availability; document gaps if unavailable.
- [ ] **Claude:** separate Shorts and long-form comparisons and account for publication age.
- [ ] **Claude:** enrich growth brief with topic-pillar, search, retention and subscriber-conversion insights only where supported by data.
- [x] **Claude:** enforce strict channel-fit filtering across search suggestions, Google/YouTube trends, trend angles and viewer requests; reject unrelated finance/market/news/gossip and off-pillar trends. Added regression tests; CI validation pending.
- [ ] **Claude:** add advisory script/content quality checks for opening hook, first frame, purposeful visual progression, payoff and factual/editorial quality.
- [ ] **Claude:** create historical-video opportunity report; suggestions only, no automatic metadata edits.
- [ ] **Claude + owner:** validate sample reports, tests and explicit render-only dry-runs; owner reviews before any production behaviour changes.

### The CurioKids Club-specific tasks
- [ ] **Claude:** evaluate English/Hindi/Spanish performance using language/country data; flag sample-size limitations.
- [ ] **Claude + owner:** compare current separate-language workflow with a small YouTube multi-language-audio feasibility pilot; no migration or language expansion without approval.
- [ ] **Owner:** review Instagram bio/channel link and update it to reflect Leo & Mia's family-learning show.
- [x] **Claude:** add `pipeline/playlist_plan.py` to generate a review-only topic + language playlist assignment from published episode state; unmatched topics go to manual review and videos can appear in multiple playlists. Inventory generation and CI validation pending.
- [ ] **Owner:** review and create/approve the playlist set in YouTube Studio; no live playlist changes until owner review.
- [ ] **Claude:** identify eligible Shorts ↔ long-video matches for Related Video recommendations; owner applies links in Studio.
- [ ] **Claude + owner:** continue 3D storytelling work separately; require mobile-size MP4 visual approval.

**Guardrails:** no publishing/visibility/schedule changes, no upload-token changes, no paid SEO dependency, no automatic script/title/thumbnail edits. Respect Made for Kids feature restrictions on CurioKids.