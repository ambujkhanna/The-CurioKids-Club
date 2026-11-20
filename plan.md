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


## 2026-11-20 — Integration validation finding and fix
- The Blender asset workflow passed on `16b1858`, producing all four story PNGs. The integrated dry-run reached the episode validation stage but failed before rendering because `pipeline/validate_episode.py` did not yet whitelist the new `blender` board type. The error was explicit: lines 3, 5 and 9 had unknown board type `blender`.
- Fixed the episode validator to recognize `blender` and include per-asset cue words in its cue validation. Commit `9a244aae0a7305f2543dd2ff3ebdde12037245b1`.
- The renderer and Blender generator are technically passing their separate checks; integrated MP4 rendering and visual inspection are still pending. A new branch dry run should run automatically from the validator change. No publish or merge has occurred.


## Visual acceptance reset — 2026-11-20

The user reviewed the completed technical pipeline and is not satisfied with the graphic quality. The current outputs do not read as convincing polished 3D; the latest successful dry-run only proves that the renderer can load and composite Blender PNGs. It does not pass visual acceptance.

### Revised creative direction
- Stop treating four static Blender PNG cards as the finished visual solution. Keep them only as a technical prototype/reference.
- Rebuild the central seed-germination teaching moment as a continuous, clearly staged 3D animation: seed rests in a visible soil cutaway; the seed coat splits; the first root emerges and grows downward with branching; the shoot curves upward and pushes through the soil; cotyledons/leaves unfold and turn toward light.
- Use real 3D geometry, smooth organic motion, convincing scale/material response, soft contact shadows, controlled studio/garden lighting, and a close camera composition. Avoid a giant flat soil block, floating disconnected parts, oversized empty space, decorative background-first layouts, and text baked into the render.
- Preserve Leo/Mia's established 2D character identities. Their dialogue can introduce/react to the 3D animation; the scientific action should carry the scene.
- Use transparent rendered animation frames or a short pre-rendered RGBA sequence and composite it into the existing episode board. Do not attempt to fake motion by swapping static stills. Keep render resolution, frame count, disk size and GitHub Actions runtime bounded; profile a short representative clip first.

### New acceptance gate
A technically successful workflow is not visual acceptance. Inspect the exact generated video at phone size and verify the seed split, root extension/branching, shoot emergence and leaf unfolding are visibly animated, coherent, readable, and continuous. No merge or publish until this gate is passed and the user accepts the visual direction.


## Handoff brief for Claude — ep070 plant-growth visual redesign (2026-11-20)

### Core problem
The current ep070 visual treatment is not an animation of plant growth. It is a slideshow: the renderer displays one static image, then replaces it with another static image to represent the stages of the seed-to-plant journey. Even though the stills were rendered with Blender, the result does not convincingly read as 3D motion. The user explicitly says this is merely changing one image to another image to explain plant generation.

### Decision
Do not continue polishing the static-card sequence as the final solution. Redesign the central educational visual as one continuous, coherent animated scene that demonstrates the biological transformation itself. The sequence must show visible movement and causality, not just stage-to-stage image replacement.

### Desired story/action
1. A seed sits in a cutaway of soil. Establish scale and show the seed in context.
2. The seed coat visibly cracks and opens; the embryo begins to emerge.
3. The primary root grows out of the seed and extends downward over time; smaller lateral roots branch from it.
4. The shoot grows upward from the seed, curves, and pushes through the soil surface.
5. The first leaves/cotyledons unfold visibly and orient toward the light.
6. Hold on the resulting young plant with the seed/root/soil relationship still understandable.

### Visual direction
- Convincing stylized 3D, not flat vector art, not pseudo-3D gradients, and not static 3D renders.
- Real geometry, volume, depth, perspective, physically coherent contact with soil, attractive materials, soft shadows, controlled lighting and smooth organic motion.
- Tight educational composition: the viewer must clearly see both underground root development and above-ground shoot/leaf development. Avoid oversized empty space, clipped objects, detached roots, a huge flat soil slab, or a decorative green-field background.
- No title or labels baked into the Blender render; overlay editable episode typography separately if needed.
- Keep the existing Leo/Mia 2D character identities and visual language. Characters may introduce/react to the 3D sequence; do not redesign them as 3D.
- Use camera framing and lighting that make the seed split, root growth, shoot emergence and leaf unfolding legible on a phone screen.

### Technical direction (proposal, not yet implemented/approved)
- Build a single Blender scene with the seed, soil cutaway, root system, shoot and leaves as separate controllable objects/curves.
- Animate geometry/material visibility or procedural growth over time: seed-coat halves separate; root curve length increases and branches appear/grow; shoot curve length increases and bends toward/through soil surface; leaf meshes unfold/rotate.
- Render a short bounded RGBA image sequence or video with transparent background, then composite it as a continuous timed shot in the existing episode engine. Do not implement this as a list of still PNGs selected by narration cues.
- Profile a short representative clip first (e.g. a few seconds) for render time, output size and compositing compatibility before generating the full sequence.
- Keep Blender generation reproducible and headless-CI compatible; no paid assets or APIs. Reuse procedural geometry/materials where practical.
- Include validation of frame dimensions, alpha channel, frame count, timing and missing-frame detection.

### Acceptance criteria
- A viewer can watch the seed coat split, root extend/branch, shoot emerge and leaves unfold as actual continuous motion.
- The transitions are not just crossfades or swaps between completed stage images.
- The same scene/camera/light/material setup persists through the action, so the growth feels like one coherent event.
- Clearly dimensional 3D appearance at phone size, with legible underground/above-ground relationship and no clipping.
- Rendered sequence composites correctly into ep070 and survives actual MP4 inspection.
- Technical CI success alone is not visual acceptance. Do not merge to main or publish until the user reviews and accepts the visual result.

### Existing implementation to replace/rework
- pipeline/blender/create_story_assets.py currently generates four static story images: 01_seed_wakes.png, 02_roots_grow.png, 03_shoot_reaches.png, 04_growth_stages.png.
- pipeline/episode_engine.py currently handles board type blender by loading those stills and switching images at cue times.
- episodes/ep070-seed-grows-into-tree/episode.json references those still images through asset/assets entries.
- .github/workflows/visual-engine-dry-run.yml renders those still assets before the episode render.
- This implementation is the slideshow behavior the user is rejecting. Do not mistake its successful workflow run for visual approval.
