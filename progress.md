# CurioKids Channel Improvements — Progress

**Active branch:** `feature/language-title-badges-v2`  
**Base:** `main`  
**Draft PR:** [#12 — Add inline language badges to CurioKids thumbnails](https://github.com/ambujkhanna/The-CurioKids-Club/pull/12)  
**Status:** Implementation is on the clean feature branch; automated execution and visual review remain pending.

## 2026-11-25 — Task A: language badges

### Repository and branch
- Confirmed repository: `ambujkhanna/The-CurioKids-Club`; default branch: `main`.
- Compared old `feature/modern-visual-engine` with `main`: 85 commits ahead and 89 behind. Did not reuse that stale branch.
- Created `feature/language-title-badges-v2` directly from the latest `main`.
- Verified branch comparison: 8 commits ahead, 0 behind at initial sync; later task commits are on this branch only.
- Superseded and closed draft PR #11. No changes from PR #11 were merged.

### Implementation
- Added `pipeline/language_badges.py` with EN/HI/ES labels and a reusable Skia badge renderer. Hindi label uses Devanagari shaping when `deva` is available.
- Updated `pipeline/thumbnail.py` so punch and classic thumbnail paths receive a language badge in the title band for portrait and landscape output.
- Updated `pipeline/daily.py` to pass `THUMB_LANG` during normal render and refresh.
- Removed the old Hindi/Spanish corner-overlay calls.
- Expanded thumbnail refresh enumeration to include English, Hindi and Spanish uploaded records.
- Added `pipeline/tests/test_language_badges.py` for supported labels, unknown-language fallback and environment selection.
- Added `.github/workflows/language-badge-checks.yml` to run the unit tests and compile modified pipeline modules.

### Audience strategy
- Recorded the full supplied top-10 country ranking in `plan.md` as a later milestone.
- Decision rule: use CurioKids Studio analytics to rank the top 3–4 language opportunities. Spanish/Mexico (rank 5 in the supplied country list) is not automatically retained.
- No publishing cadence or language rotation has been changed.

## Validation checklist
- [x] Fresh feature branch created from latest main (0 commits behind)
- [x] Shared EN/HI/ES labels and reusable badge renderer
- [x] Badge integrated in punch and classic portrait/landscape paths
- [x] Language passed through normal rendering and thumbnail refresh
- [x] Old corner-badge calls removed
- [x] Refresh includes EN/HI/ES records
- [x] Unit tests and branch-only validation workflow added
- [ ] CI run passes (no run/status has appeared for the connector-created commits yet)
- [ ] Render portrait EN/HI/ES samples and inspect at phone size
- [ ] Render landscape sample and inspect
- [ ] Confirm headline/badge spacing and Hindi glyph shaping visually
- [ ] Owner review and approval; do not merge automatically

## Next actions
1. Run the branch validation workflow from GitHub Actions after a normal push/synchronize event.
2. Generate and inspect actual portrait/landscape thumbnails; adjust placement if any headline collision occurs.
3. Update this log and PR #12 with final validation evidence.
