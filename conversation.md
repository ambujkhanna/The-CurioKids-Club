# CurioKids Club — Visual Engine Conversation Log

## 2026-11-18 — Visual upgrade review

### User direction
The garden, tree and soil were an improvement, but the result still did not look like realistic or professional 3D graphics. The requested direction is to continue improving the visuals. The user also asked to be informed if an AI model or pipeline upgrade is needed.

### Implementation and validation
- Work is isolated on `feature/modern-visual-engine`; `main` has not been changed.
- The renderer uses Python + Skia for the existing 2D pipeline. A topic-aware garden backdrop was added, then polished with shaded foliage, trunk highlights, soil grain and higher-contrast roots.
- Dry-run #6 failed because the runner's installed `skia-python` did not expose `skia.BlurStyle.kNormal`. The blur dependency was removed and replaced with layered translucent ellipses; no AI model or package upgrade was needed.
- Dry-run #7 passed: https://github.com/ambujkhanna/The-CurioKids-Club/actions/runs/44341007085
- Review artifact: https://github.com/ambujkhanna/The-CurioKids-Club/actions/runs/44341007085/artifacts/14443488874
- Artifact contains `CurioKids_ep070.mp4` (1080×1920, 74.176 seconds), thumbnail and shot metadata.
- Sample frames around 8s, 25s and 45s were inspected. The garden is now clearly visible; existing 2D Leo/Mia characters are preserved. However, the result is still stylised 2D vector artwork, not professional 3D. The underground root illustration is not yet a strong central teaching visual, and the lower classroom has not been redesigned.

### Current decision
Technical validation is green, visual acceptance is not. Do not merge yet.

### Next implementation phase
1. Add reusable Blender-created 3D assets with controlled lighting/materials and transparent renders.
2. Keep Blender rendering offline/pre-rendered; composite assets in the existing Skia/FFmpeg pipeline so GitHub Actions does not perform expensive 3D rendering on every frame.
3. Build topic-specific seed germination assets: seed, root growth, sprout, mature tree and a clear soil cross-section with visible central roots.
4. Improve scene composition and classroom integration while preserving Leo/Mia character identity.
5. Keep a legacy fallback and a per-scene visual feature flag.
6. Run another dry-run, inspect the actual video/artifact, and only then consider merge.

### Model / pipeline decision
No AI model upgrade is currently justified. The main limitation is asset quality and scene composition, not script intelligence. Revisit model selection only if later testing identifies a measurable scene-planning limitation. Prefer free/open-source tooling and avoid new paid services without explicit discussion.

## 2026-11-19 — 3D direction and handoff

The user reviewed the latest artifact and confirmed it still does not look like professional 3D. The agreed diagnosis is primarily a pipeline/asset-production limitation: the current garden is procedural 2D/2.5D Skia artwork, not actual 3D geometry. No AI model upgrade is justified yet.

### Target visual standard
- Polished stylised 3D (not photorealistic), child-friendly, with dimensional geometry, believable materials, coherent lighting, shadows, perspective and deliberate camera composition.
- Preserve existing 2D Leo/Mia/Buzz character identity; build richer 3D scenes and props around them.
- For the seed-growth pilot, clearly show seed, underground branching roots, shoot and mature tree in a legible soil cutaway. Avoid duplicate focal suns, label collisions and decorative-only scenery.

### User authorisation
The user asked that this discussion be recorded for use in a fresh conversation and authorised proceeding with the remaining tasks. Continue on feature/modern-visual-engine; keep main untouched until visual and technical acceptance gates pass.

### Current verified baseline
- Dry-run #7 passed: https://github.com/ambujkhanna/The-CurioKids-Club/actions/runs/44341007085
- Artifact: https://github.com/ambujkhanna/The-CurioKids-Club/actions/runs/44341007085/artifacts/14443488874
- The artifact is technically valid but visually not accepted as professional 3D.
- Blender scene authoring, 3D asset library and 3D compositing integration remain unimplemented.

### Next task selected
Create an isolated Blender proof-of-capability for ep070: generate a real 3D seed-germination soil cutaway with a tree, seed, branching roots and sprout; render a transparent/high-resolution output and retain the .blend source. Validate it in a dedicated branch-only workflow before integrating it into the existing Skia/FFmpeg pipeline. Keep old renderer fallback and avoid full Blender rendering in every routine run.

### Remaining validation gates
1. Inspect the actual Blender render at 1080x1920; refine geometry, materials, lighting, shadows and framing.
2. Validate alpha/compositing and typography/label safe areas.
3. Integrate as optional scene assets with deterministic IDs, manifest/licence metadata and safe fallback.
4. Render ep070 and compare actual video/contact sheet against target references.
5. Run legacy episode regression, tests, QC, and GitHub Actions performance checks.
6. Only merge after visual acceptance and explicit review; green CI alone is insufficient.

### Tool/model decision
Blender is the next tool upgrade, not a paid AI model. Keep model choice unchanged unless scene-planning evaluation later demonstrates a specific model limitation.