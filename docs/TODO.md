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
