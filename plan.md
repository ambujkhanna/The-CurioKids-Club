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
