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

## 2026-11-19 — Handoff and remaining work

### User confirmation and target
- User confirmed the current graphics still do not meet the requested professional 3D quality and asked whether the limitation is the AI model or the pipeline. Decision: the primary gap is the content-production/rendering pipeline and its lack of actual 3D assets; no AI model upgrade is justified yet.
- Target direction: professional stylised 3D environments and educational objects, with established 2D Leo/Mia/Buzz characters preserved unless a later explicit design decision changes them. The target is not photorealism; it is polished, dimensional, child-friendly 3D with coherent lighting, materials, shadows, camera composition and animation.
- User asked that this conversation be recorded for continuity and authorised proceeding with remaining tasks.

### Confirmed repository state
- Branch: feature/modern-visual-engine; base: main. Main remains untouched; no PR/merge.
- Latest validated renderer run: [Dry Run #7](https://github.com/ambujkhanna/The-CurioKids-Club/actions/runs/44341007085), success at 9104c4b51261f7aef74a21d38fcc109f0883e63a.
- Review artifact: [CurioKids review artifact](https://github.com/ambujkhanna/The-CurioKids-Club/actions/runs/44341007085/artifacts/14443488874); MP4 is 1080x1920, 74.176 seconds.
- #6 failed due to unsupported skia.BlurStyle.kNormal in runner's skia-python; fixed with layered shadow ellipses. #7 passed.
- Current visual_layers.py garden output is still procedural 2D/2.5D. It is not a real 3D scene. assets/manifest.json is empty. Blender production/integration is not implemented.
- Current dry-run workflow is branch-only, renders ep070 with --dry-run, uploads review artifacts, and does not publish.

### Remaining work — ordered backlog
1. 3D proof of capability (next task): add an isolated Blender scene-generation script that creates a polished stylised 3D seed-germination cutaway (terrain/soil slab, seed, branching roots, sprout, tree, lighting, camera, shadows). Render transparent PNG layers/stills and save the .blend source. Run it in a dedicated branch-only GitHub Actions workflow; do not yet wire it into every video render.
2. Review and iterate the 3D prototype: inspect actual rendered output at 1080x1920 composition; tune materials, geometry, lighting, shadows, camera and typography safe areas until it is visibly better than current 2D scene.
3. Reusable asset pipeline: define deterministic asset IDs, output paths, resolution/scale conventions, alpha handling, metadata and licence/source records. Keep original .blend source and transparent render outputs where useful.
4. Compositing integration: add optional per-scene 3D asset references to episode configuration and composite the pre-rendered PNGs in Skia/FFmpeg. Preserve existing renderer as fallback; missing assets must warn and fall back, never silently break.
5. Pilot episode redesign: build seed → roots → shoot → mature tree scenes with meaningful visual progression; fix overlapping labels and duplicate suns; preserve character identity. Redesign classroom only after the central 3D teaching scene is proven.
6. Motion and performance: add gentle camera moves/parallax or rendered animation sequences; measure artifact size, render time and memory on GitHub Actions.
7. Regression and acceptance: test old episodes with no visual config, test new ep070 path, generate contact sheet and review MP4. Validate output on mobile-size frames and ensure captions/labels remain legible.
8. Merge gate: no merge until all technical checks pass, the actual MP4 meets visual acceptance, asset licences are recorded, legacy compatibility is proven, and user has a clear review opportunity/approval. Do not merge merely because CI is green.

### AI/model and tooling decision
- Do not upgrade the AI model yet. Model may assist with scene descriptions or Blender Python generation, but geometry/material quality is a production asset and pipeline responsibility.
- Use Blender as the free/open-source 3D authoring/rendering tool; render reusable assets offline/on-demand and composite them in the existing Python/Skia/FFmpeg workflow. Avoid full Blender rendering on every frame or every scheduled episode initially.
- No paid model, subscription, API or infrastructure change without explicit discussion.

### Continuity note
- conversation.md is the concise project decision/history log; plan.md is the architecture/acceptance plan; this file is the implementation and validation log. Update all three as material decisions, commits, runs and reviews occur.

## 2026-11-19 — Blender 3D proof implementation started
- Added `pipeline/blender/create_seed_scene.py`: a procedural Blender scene builder with a rounded soil cutaway, soil strata and pebbles, sculpted foliage clusters, shaded trunk/branches, a visible germinating seed, branching root network, young shoot, studio backdrop, orthographic camera and three-point area lighting. It saves an editable `.blend` file and a transparent 1080×1920 RGBA PNG.
- Added `.github/workflows/blender-3d-proof.yml`: branch-only Ubuntu workflow installs Blender, generates the scene, verifies PNG dimensions/alpha and uploads both source and render. It does not publish or change production workflows.
- These are generated 3D meshes and curves, not imported/licensed third-party assets. The scene is an initial proof, not yet visually accepted; inspect and refine the actual render before integration.
- Made Eevee sample configuration version-safe after initial code review.
- Next: inspect the Blender workflow result and actual PNG; refine framing/materials/geometry; then build the reusable asset manifest/export and integrate the 3D render as an optional scene layer with legacy fallback.


## 2026-11-19 — Blender CI headless graphics failure fix
- Investigated failed Blender proof run [#1](https://github.com/ambujkhanna/The-CurioKids-Club/actions/runs/44546473537), job `135638262911`. Blender installed successfully; the scene-generation process aborted before render because the runner could not load `libEGL.so.1` (exit 134). This is a Linux headless graphics runtime dependency, not an AI-model issue or a scene-script logic failure.
- Updated `.github/workflows/blender-3d-proof.yml` to install `libegl1`, `libegl-mesa0`, `libgl1`, `libgl1-mesa-dri`, `libgbm1` and X11 support libraries; set `LIBGL_ALWAYS_SOFTWARE=1` and `EGL_PLATFORM=surfaceless`; limit Blender to two threads.
- Removed the unnecessary Weighted Normal modifier from beveled box objects to avoid Blender's Auto Smooth warnings. These warnings were not the fatal cause.
- Fix commits: workflow `91423760c0cf6a9ced2422de37cd56de778ab2ec`; scene script `50e806f9438458e79a54cd0138c9587c04608b62`.
- The push-triggered Blender workflow must now validate the fix. Do not assume it works until the job completes and the actual PNG/BLEND artifacts are checked.


## 2026-11-19 — Blender proof PNG validation dependency fix
- Blender proof run [#6](https://github.com/ambujkhanna/The-CurioKids-Club/actions/runs/44548393593) successfully installed Blender and generated both the PNG and editable .blend scene. The render completed in 29.46 seconds and produced a 1080×1920 8-bit RGBA PNG.
- The workflow then failed only in its verification step because it imported Pillow (PIL), which is not installed in the runner's system Python. This was a validation-script dependency mistake; Blender rendering itself succeeded.
- Updated .github/workflows/blender-3d-proof.yml at commit b668fa393f6e282ff9e7de3c33189074333ed7b6 to validate the PNG signature, IHDR dimensions, bit depth, RGBA color type and nontrivial file size using Python's standard library. No Pillow dependency or additional install step is required.
- A fresh push-triggered run is required to confirm the workflow passes and uploads the PNG/.blend artifacts. Visual review is still pending; technical PNG metadata checks do not establish that the composition meets the requested quality.


- Follow-up correction: the first Pillow-free verifier commit contained a stray character before its pathlib import, so GitHub could not load the workflow. Corrected in commit 4319bb326937a2d16ccf6134133ec958def290ad. The next push-triggered run is the authoritative validation; prior failures were workflow syntax/verification issues after the successful Blender render.

## 2026-11-19 — First Blender render reviewed; story-first redesign
- Downloaded and inspected the actual `curiokids-blender-3d-proof` artifact from successful run [44559566901](https://github.com/ambujkhanna/The-CurioKids-Club/actions/runs/44559566901), artifact ID `14547556076` (PNG + editable `.blend`). The PNG is 1080×1920 RGBA and the Blender render itself is technically valid.
- Visual review: the render is a single wide diorama squeezed into portrait framing. The mature tree canopy is clipped at the right edge and the seed is partly clipped at the left; the sapling/tree are small; root branches appear disconnected; large unused backdrop space dominates. It does not communicate the seed → roots → shoot → mature plant progression clearly. **Not visually accepted; do not integrate this render into ep070.**
- User direction: focus on educational story objects/graphics and story beats, not a green-field background. Keep the established 2D characters and use close-up 3D story assets around them.
- Added `pipeline/blender/create_story_assets.py` to render four separate transparent portrait assets: `01_seed_wakes.png`, `02_roots_grow.png`, `03_shoot_reaches.png`, and `04_growth_stages.png`. These are procedural Blender geometry/materials authored in-repo; no third-party assets or external services are used.
- Updated `.github/workflows/blender-3d-proof.yml` to generate and upload the four story assets alongside the original proof. Narrowed path filters to Blender source and the workflow itself; edits to `progress.md`/`plan.md` no longer trigger expensive Blender setup/rendering.
- Commit `be6d8503cf30292d55bb0c18c1a82b35f40cadeb`: add story asset generator. Commit `aaf1aafff18b5c9ef63b46f98c46e00a5f751065`: workflow update.
- Validation status: generator and workflow have been committed, but the new workflow run and actual four PNGs have **not yet been validated or visually reviewed**. Do not claim success until Actions completes and the artifact is inspected.
- Next: check the push-triggered workflow, fix any Blender/runtime issues, inspect all four renders at mobile scale, refine composition/labels/geometry, then composite the approved assets into an ep070 dry-run. Keep `main` untouched and update this log after each result.

