# CurioKids Channel Improvements — Progress

**Active branch:** `feature/language-title-badges`  
**Base:** `main`  
**Status:** Implementation committed on the feature branch; automated validation and visual inspection pending.

## 2026-11-25 — Task A: language badges

### Repository and branch
- Confirmed repository: `ambujkhanna/The-CurioKids-Club`; default branch: `main`.
- Compared old `feature/modern-visual-engine` with `main`: 85 commits ahead and 89 behind. Did not reuse that stale branch.
- Created `feature/language-title-badges` directly from `main`.

### Implementation
- Added `pipeline/language_badges.py` with EN/HI/ES label mapping and a reusable Skia badge renderer.
- Added `pipeline/thumbnail.py::apply_language_badge`; badge is placed in the title band, not in a corner, for portrait and landscape thumbnails.
- Integrated the badge into both punch and classic thumbnail paths.
- Updated `pipeline/daily.py` to pass `THUMB_LANG` during normal render and refresh.
- Removed the old Hindi/Spanish corner-overlay calls.
- Expanded thumbnail refresh enumeration to include English, Hindi and Spanish uploaded records.
- Added `pipeline/tests/test_language_badges.py` for supported labels, fallback behavior and environment selection.
- Added `.github/workflows/language-badge-checks.yml` to run label tests and compile the modified Python modules.

### Audience strategy
- Added the owner's supplied top-10 country ranking to `plan.md` as a later milestone.
- Decision rule: use CurioKids Studio analytics to rank the top 3–4 language opportunities; Spanish/Mexico (rank 5 in the supplied list) is not automatically retained.
- No publishing cadence or language rotation has been changed.

## Validation checklist
- [x] Fresh branch from latest main
- [x] Shared EN/HI/ES badge labels and drawing helper
- [x] Badge integrated in punch and classic thumbnail renderer paths
- [x] Language passed through normal render and thumbnail refresh
- [x] Old corner badge calls removed
- [x] Refresh includes EN/HI/ES records
- [x] Unit tests and branch-only CI workflow added
- [ ] CI run passes
- [ ] Render portrait EN/HI/ES samples and inspect at phone size
- [ ] Render landscape sample and inspect
- [ ] Confirm title/badge spacing and Hindi glyph shaping visually
- [ ] Final review, commit/push verification and PR creation

## Important repository note
A validation workflow file was briefly created on `main` by an omitted branch argument, then immediately deleted. There is no remaining file change from that operation, but the add/delete commits remain in `main` history. The actual workflow is now present on `feature/language-title-badges`.

## Next action
Run the branch CI, inspect the generated portrait/landscape thumbnails, fix any visual or test failures, then update this log before considering a PR. Do not merge to `main` without owner approval.
