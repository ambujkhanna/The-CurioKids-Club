# Modern Visual Engine — Progress

**Branch:** `feature/modern-visual-engine`  
**Base branch:** `main`  
**Status:** In progress; technical dry-run passed, visual upgrade still requires further work and owner review before merge.

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
- Dry-run #7 [completed successfully](https://github.com/ambujkhanna/The-CurioKids-Club/actions/runs/44341007085) at commit `9104c4b51261f7aef74a21d38fcc109f0883e63a`.
- All workflow stages passed: dependency installation, voice-model preparation, asset-manifest validation, unit tests, pilot rendering/QC and review-artifact upload.
- The run produced `CurioKids_ep070.mp4` (1080×1920, 74.176 seconds) and a thumbnail. Artifact: [curiokids-modern-visual-engine-review](https://github.com/ambujkhanna/The-CurioKids-Club/actions/runs/44341007085/artifacts/14443488874).
- I downloaded and inspected sample frames at approximately 8s, 25s and 45s. The garden backdrop is clearly visible and consistent; the characters remain intact. However, the environment still reads as stylised 2D vector art rather than professional 3D. The seed/root teaching scene also lacks a convincing central underground root cross-section; the current thin decorative roots are mostly near the sides. The classroom below remains the old design.
- Dry-run #6 [failed](https://github.com/ambujkhanna/The-CurioKids-Club/actions/runs/44339743954) because the installed `skia-python` did not expose `skia.BlurStyle.kNormal`. The renderer was corrected by replacing that version-specific blur call with layered translucent shadow ellipses. No new dependency was added.
- Dry-run #5 passed; #4 was cancelled as a duplicate. Earlier failed runs were setup/integration issues and are not evidence of a production upload failure.
- No production workflow or publishing configuration has been changed. No third-party assets have been downloaded; `assets/manifest.json` remains an intentionally empty registry.
- This branch is not ready to merge: the technical pipeline passes, but the requested professional 3D visual quality has not yet been achieved and the Blender/pre-rendered asset stage is not implemented.

- Next: implement a real reusable 3D asset workflow (Blender offline render to transparent PNG/sequence, material/lighting presets, reusable GLB/Blend source assets), integrate it behind a per-scene feature flag, and build a proper soil cross-section with centrally visible seed/root/sprout stages. Keep the current Skia path as fallback. Then render and inspect a new pilot before considering merge.

- Follow-up visual polish: introduced radial material shading for tree foliage, multi-lobe leaf clusters, shaded trunk highlights, subtle deterministic soil grain and higher-contrast root edges. Lowered the soil horizon to reduce collisions with the cycle labels. These are still procedural 2D/2.5D materials; a true 3D asset pass using Blender-rendered transparent objects remains planned rather than being misrepresented as complete.

- Dry-run #6 failed in frame rendering: installed skia-python does not expose `skia.BlurStyle.kNormal`. Dependency setup, asset validation and all 9 unit tests passed. Replaced the version-specific blur call with layered translucent shadow ellipses (no new dependency); next push triggers a fresh dry-run.


## Current review snapshot (2026-11-18 22:03 IST)
- Latest branch head at this snapshot: `9104c4b51261f7aef74a21d38fcc109f0883e63a`.
- Latest dry-run #7 passed end-to-end and produced a review MP4; see artifact link above.
- Visual acceptance remains open. Do not merge based on workflow success alone.
