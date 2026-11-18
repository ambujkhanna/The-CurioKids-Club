# Modern Visual Engine — Progress

**Branch:** `feature/modern-visual-engine`  
**Base branch:** `main`  
**Status:** In progress; owner review required before merge.

## 2026-11-18

- Created isolated branch `feature/modern-visual-engine` from `main`.
- Inspected the current renderer, episode format and image/illustration handling.
- Confirmed the current pipeline uses Skia for frame rendering, with existing board scenes, diagrams, SVG illustrations and a separate finishing stage.
- Added the implementation plan and asset-source/licensing requirements.
- Added `assets/manifest.json` as an initially empty asset registry.
- Added `assets/README.md` with candidate sources, per-asset licence checks, required metadata and rendering guidance.
- Added `pipeline/asset_manager.py`, a standard-library-only manifest validator; commercial-use approvals require licence evidence and attribution-required assets require a credit line.
- Added unit tests in `pipeline/tests/test_asset_manager.py` for empty manifests, evidence, attribution and duplicate IDs.
- Replaced the subtle garden backdrop with a topic-specific 2D/2.5D garden diorama: gradient sky, sun glow/rays, drifting clouds, layered hills, shaded edge trees, soil strata, visible roots, grass and stones. Other palettes retain a generic fallback. Existing board graphics and Leo/Mia character art remain intact.
- Integrated the visual layer behind existing board content in `pipeline/episode_engine.py`. It is opt-in via episode `visual.style` or `CURIO_VISUAL_STYLE`; absent/unknown styles preserve legacy output. Existing 2D characters are unchanged.
- Added style-resolution unit tests in `pipeline/tests/test_visual_layers.py`.
- Added `.github/workflows/visual-engine-dry-run.yml`, a branch-only push workflow that runs validation/tests and renders `ep070` with the `garden` palette using `--dry-run`; it uploads review artifacts and never publishes.
- First dry-run attempt exposed an unavailable `numpy==2.5.4` pin in the existing requirements file. Updated the feature branch pin to `numpy==2.4.6` (available on the runner index); no change to `main`.
- Dry-run [#44322612970](https://github.com/ambujkhanna/The-CurioKids-Club/actions/runs/44322612970) succeeded technically, but owner review found the initial background too subtle. This follow-up makes the garden environment materially more visible and enables it explicitly in the ep070 pilot. A fresh render is required.

## Validation

- No production workflow or publishing configuration has been changed.
- No third-party assets have been downloaded or added yet; the manifest is intentionally empty.
- The first workflow attempt stopped during dependency installation because the NumPy pin was unavailable; it produced no video. The corrected second attempt is in progress.
- This branch is not ready to merge until the renderer changes are demonstrated with a dry-run video and reviewed by the owner.

- Next: run a new branch-only dry-run, inspect the updated MP4/contact sheet, then continue refining any weak scenes before merge review.

- Follow-up visual polish: introduced radial material shading for tree foliage, multi-lobe leaf clusters, shaded trunk highlights, subtle deterministic soil grain and higher-contrast root edges. Lowered the soil horizon to reduce collisions with the cycle labels. These are still procedural 2D/2.5D materials; a true 3D asset pass using Blender-rendered transparent objects remains planned rather than being misrepresented as complete.
