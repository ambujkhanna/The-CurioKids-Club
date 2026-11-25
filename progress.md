# CurioKids Channel Improvements — Progress

**Active branch:** `feature/language-title-badges`
**Base:** `main`
**Status:** In progress — repository inspection and branch setup complete; implementation pending.

## 2026-11-25 — Task A: language badges
- Confirmed repository: `ambujkhanna/The-CurioKids-Club`; default branch is `main`.
- Confirmed the previous `feature/modern-visual-engine` branch is heavily diverged from current `main` (85 commits ahead and 89 behind). Per the owner's direction, did not build on or merge that branch.
- Created fresh branch `feature/language-title-badges` directly from `main`.
- Inspected current `pipeline/thumbnail.py`, `pipeline/thumb_punch.py`, `pipeline/daily.py` and the Shorts workflow.
- Findings:
  - Current Hindi and Spanish badges are applied as a separate corner overlay in `daily.py`.
  - English thumbnails have no language badge.
  - Punch-style thumbnail headlines are drawn in `thumb_punch.py`; the badge must be composed with the headline there, not pasted into a corner afterward.
  - The refresh path currently rebuilds English/Hindi records but does not fully cover Spanish records.
- Added the audience-led multilingual strategy to `plan.md` as a later milestone. No publishing schedule or language rotation changes are included in this task.

## Task A checklist
- [ ] Shared badge helper and label mapping (EN/HI/ES)
- [ ] Badge adjacent to title in punch portrait and landscape layouts
- [ ] Badge adjacent to title in classic portrait and landscape layouts
- [ ] Language passed through normal render and refresh workflows
- [ ] Remove old corner-badge overlay
- [ ] Refresh existing EN/HI/ES thumbnail records
- [ ] Automated tests
- [ ] Portrait and landscape render inspection
- [ ] Final validation, commit and push

## Validation log
- Not run yet. Record exact commands/results and links to generated artifacts here before declaring completion.
