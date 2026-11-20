# Modern Visual Engine — Implementation Plan

**Branch:** `feature/modern-visual-engine`  
**Base:** `main`  
**Goal:** Improve visual variety and production quality while preserving the existing CurioKids renderer, characters, episode format, and publishing workflow.

## Design constraints

- Leo, Mia, Dad and Buzz remain the established 2D characters.
- Use richer 2D, layered 2.5D and pre-rendered 3D environments/objects around them.
- Keep the current Skia/FFmpeg pipeline as the reliable baseline.
- No paid services, mandatory subscriptions, or external AI API dependencies.
- Do not run full Blender rendering in every GitHub Actions job; prefer reusable pre-rendered transparent assets.
- Preserve compatibility with existing episode JSON. New visual settings must be optional.
- Track asset provenance and the exact licence for each downloaded asset. A source website's general licence summary is not a substitute for the individual asset's terms.

## Asset sources to evaluate

- 3dicons — https://3dicons.co/
- Lummi — https://www.lummi.ai/
- Kenney — https://kenney.nl/
- Pixabay — https://pixabay.com/
- IconScout — https://iconscout.com/ (optional; attribution/plan restrictions need per-asset review)

Use Kenney and 3dicons as initial candidates. Add assets only after recording the exact asset page, download date, licence/version, commercial-use status and attribution requirement. Do not assume every item on a platform has identical rights.

## Architecture and rollout

### Phase 1 — Foundation (this branch, first increment)
- Add an asset manifest format and a small standard-library-only manager/validator.
- Document asset acquisition, licence checks, naming, resolution and attribution.
- Add a modern visual design specification and implementation progress log.
- Keep the new module isolated; do not change the live renderer or upload workflow yet.

### Phase 2 — Modern 2D and 2.5D rendering
- Add topic-specific environments with foreground/midground/background layers, depth/parallax and camera motion.
- Add custom vector scene props (soil cross-sections, roots, leaves and sunlit atmosphere), not just emoji as the primary illustration.
- Improve scene composition, colour themes, typography and transitions.
- Preserve current 2D character drawing and lip-sync.
- Add deterministic, optional visual configuration with legacy defaults.

### Phase 3 — Reusable 3D assets (next priority)
- First build an isolated Blender proof-of-capability for the ep070 seed-growth cutaway: actual 3D soil slab, seed, branching roots, sprout, mature tree, camera, materials and lighting.
- Save the Blender .blend source and render high-resolution transparent PNG stills/layers; validate alpha and vertical-video framing.
- Review and refine the render before adding any assets to the episode pipeline.
- Create/select reusable Blender assets and export transparent PNG sequences/stills.
- Support glTF/GLB as source interchange where useful.
- Composite pre-rendered assets through the existing Skia/FFmpeg flow.
- Record source/licence/attribution metadata for every imported asset.

### Phase 4 — Compositing integration
- Add optional scene asset references and deterministic asset IDs to episode configuration.
- Composite pre-rendered transparent assets through Skia/FFmpeg; retain legacy renderer fallback and emit clear warnings when assets are missing.
- Keep Blender rendering out of routine frame rendering until measured performance justifies a different design.

### Phase 5 — Scene planning and quality gates
- Add optional per-scene visual hints (style, background, objects, layout, motion).
- Keep existing board types valid; missing optional assets should warn and fall back safely.
- Produce contact sheets and visual QC artifacts for review.
- Test representative episodes before changing any default.

## Proposed visual styles

`modern_2d`, `layered_2d`, `isometric`, `3d_objects`, `hybrid_space`, `motion_infographic`, `character_story`.

## Acceptance criteria

- Existing episode JSON continues to render unchanged.
- Existing scheduled publishing workflow is not altered during the pilot.
- 2D character appearance remains consistent.
- New assets are traceable to source and licence evidence.
- Missing assets never silently break a render.
- Render time and memory remain suitable for GitHub Actions.
- A human can inspect a dry-run MP4/contact sheet before any merge to `main`.
- The 3D pilot uses actual 3D geometry/materials/lighting/shadows and is visibly distinct from the current procedural 2D/2.5D artwork.
- Alpha compositing, vertical framing, label-safe areas, deterministic rendering and legacy episode fallback are validated.

## Review / merge policy

All work stays on `feature/modern-visual-engine`. Do not merge to `main` or change the production default until the owner reviews the generated output and explicitly approves merging.

### Phase 3A — Story-first 3D assets (active)
- Do not use a single wide landscape as the primary teaching visual. Create separate close-up story compositions for each learning beat: seed waking, underground roots, shoot emerging, and growth-stage comparison.
- Keep the background restrained/transparent; allocate most of the portrait frame to the educational object and its action.
- Generate reusable transparent 1080×1920 PNG assets from Blender, with editable `.blend` sources and deterministic filenames.
- Add readable stage labels only where they support the narration; reserve safe areas for captions and 2D characters.
- Review all four assets as a contact sheet and then composite them into the ep070 dry-run before deciding on integration.

### Phase 3B — Existing proof review outcome
- The first Blender proof is genuine 3D geometry, but its single portrait diorama is compositionally weak: the tree canopy and seed are clipped, the key objects are too small, roots are visually disconnected, and the empty backdrop dominates. It is not accepted as the episode visual.
- The next proof is story-led, not background-led. The original wide diorama remains a technical reference only; do not promote it into the episode by default.


### Review gate — story assets (2026-11-20)
- CI generation passed on run `44561243631`, but visual review rejected the first four outputs due to diagonal/cropped typography and clipped growth-stage composition.
- A front-on camera and wider portrait safe framing were committed in `5bae616`. Re-run and inspect before wiring assets into episode scenes.
- Do not treat a successful asset-generation job or the earlier Visual Engine Dry Run as proof that ep070 uses these graphics. Integration and a fresh full-video visual review are still required.



## 2026-11-20 — Integrating Blender story cards into the episode renderer
- The latest front-on portrait renders were inspected. They are still not acceptable as portrait cards: the growth-stage row clips at both sides, while the other assets waste too much vertical space. Reframed the assets for the actual 870×640 theatre board instead of a full 1080×1920 canvas.
- Added an optional `blender` board type to `pipeline/episode_engine.py`. It loads transparent PNGs from `out/blender/story/`, places them inside the existing board frame, and supports narration cue changes between multiple assets. Existing board types remain unchanged.
- Updated ep070 to use the seed visual for the seed-waking explanation, switch from root to shoot visuals on their spoken cues, and use the growth-stage comparison for the years-of-growth explanation.
- Updated the branch-only dry-run workflow to install Blender and render the required assets before the normal episode render. Nothing is published; main and production workflows remain untouched.
- Integration commits: story framing `322d297d38a595c174df7524495ef3402836ee2d`; episode engine `7fd4e3129aaed2e3a7940e1b85577a769b62f664`; episode mapping `58d37e1a3e42898e5ac30ea2076915c460d17aa4`; dry-run workflow `5628e42837086cb1b050265e8030fa92dc7b41dc`.
- Validation is pending on the final workflow run. Do not mark visually accepted until the actual rerendered PNGs and ep070 MP4 are inspected. If the scene-card composition or alpha blending is poor, refine it before merge.

- Follow-up camera-routing fix: Blender board scenes are now explicitly included in the renderer's board-shot routing, preventing narration lines from cutting to a character close-up while the 3D story card is meant to be read. Commit `d249f9454d01069faf5575941193cf1d50370c35`. The next integrated dry run must validate this alongside asset loading/compositing.
