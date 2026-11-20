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

## 2026-11-19 — Blender proof run #1 failure and fix
- User reported [Blender proof run #1](https://github.com/ambujkhanna/The-CurioKids-Club/actions/runs/44546473537/job/135638262911) failed. Inspected job steps/log excerpt: Blender install succeeded; render process aborted with `Couldn't open libEGL.so.1` and exit code 134.
- Diagnosis: missing EGL/Mesa runtime libraries in Ubuntu headless runner. Auto Smooth / Weighted Corner Normals messages were warnings, not the crash cause.
- Workflow now installs EGL/Mesa/OpenGL and X11 runtime libraries, sets `LIBGL_ALWAYS_SOFTWARE=1` and `EGL_PLATFORM=surfaceless`, and runs Blender with two threads. Removed unnecessary Weighted Normal modifier to suppress compatibility warnings.
- Fix commits: `91423760c0cf6a9ced2422de37cd56de778ab2ec` (workflow), `50e806f9438458e79a54cd0138c9587c04608b62` (scene script).
- Await a new branch workflow run and inspect the rendered PNG/BLEND; no claim of success until artifact verification.

## 2026-11-19 — User feedback: story graphics over background

The user asked to focus on other elements and story graphics rather than concentrating on a green-field background. We inspected the actual PNG from Blender proof artifact `14547556076` (run `44559566901`), not merely its CI metadata.

### Review findings
- The first Blender output is real 3D but uses one wide diorama in a portrait canvas.
- The tree canopy is clipped at the right and the seed is partly clipped at the left; the sapling/tree are undersized; the root network reads as disconnected; empty background occupies too much of the composition.
- It does not tell the seed → root → shoot → mature tree story clearly enough. It is not accepted for episode integration.

### Updated direction
Prioritise separate close-up 3D teaching visuals and meaningful story graphics: (1) seed coat splitting/first root, (2) branching underground roots, (3) shoot emerging with leaves and sunlight, (4) seed-to-tree growth comparison. Use restrained or transparent backgrounds. Preserve the established 2D Leo/Mia/Buzz characters.

### Implementation started
- Added `pipeline/blender/create_story_assets.py` for four separate transparent portrait PNGs.
- Updated `.github/workflows/blender-3d-proof.yml` to render and upload these assets and to avoid running on documentation-only changes.
- Commits: `be6d8503cf30292d55bb0c18c1a82b35f40cadeb`, `aaf1aafff18b5c9ef63b46f98c46e00a5f751065`.
- Awaiting workflow execution and visual review. No merge or production workflow change.


## 2026-11-20 — Story asset run and visual inspection

Blender run `44561243631` succeeded and uploaded artifact `14551633108`. All four PNGs were downloaded and visually inspected. Despite successful rendering, the first story asset versions are not accepted: the oblique camera makes title text diagonal and clipped, the mature-tree stage is clipped, and composition leaves too much negative space. The existing visual-engine dry run `44561215383` also passed, but predates integration of these new assets and therefore does not validate the new story visuals in the episode.

Committed a camera/framing correction in `5bae616dee24154a1adca80c8d6ce96ad02cf53c`: front-on camera, wider framing, adjusted titles and growth-stage spacing. Next action is to validate and inspect this rerender, then integrate approved story graphics into ep070 and render a fresh full-video dry-run. Keep `main` untouched.



## 2026-11-20 — User delegated validation and completion
The user confirmed they do not want to manually inspect routine technical outputs; I should independently validate CI, actual images/video, story clarity, regression and documentation, and ask for creative approval only when needed.

### Latest visual review and integration work
- Both workflows for commit `5bae616` passed, but the downloaded PNGs were visually inspected and still rejected: portrait cards had excessive unused vertical space, the shoot title collided with the sun, and the four-stage comparison clipped at the sides. The 74-second MP4 from run `44724430136` was also inspected via a contact sheet and still showed the legacy 2D board graphics; this confirmed the new 3D images were not integrated yet.
- Changed the Blender story outputs to the theatre-board aspect ratio (870:640) and added an optional `blender` board type to the episode renderer. It composites transparent PNGs within the board and can switch visuals at narration cue words.
- ep070 now maps seed waking to the first 3D asset, root then shoot to cue-timed assets, and the year-after-year explanation to the growth-stage comparison.
- The branch-only dry-run workflow now installs Blender and generates the story assets before rendering ep070. It remains render-only, with no upload/publishing.
- Commits: `322d297d38a595c174df7524495ef3402836ee2d`, `7fd4e3129aaed2e3a7940e1b85577a769b62f664`, `58d37e1a3e42898e5ac30ea2076915c460d17aa4`, `5628e42837086cb1b050265e8030fa92dc7b41dc`.
- Final integration run [44731557242](https://github.com/ambujkhanna/The-CurioKids-Club/actions/runs/44731557242) was pending when this entry was written. Its output must be inspected before claiming completion. Keep main and production publishing untouched.

- Follow-up camera-routing fix: Blender board scenes are now explicitly included in the renderer's board-shot routing, preventing narration lines from cutting to a character close-up while the 3D story card is meant to be read. Commit `d249f9454d01069faf5575941193cf1d50370c35`. The next integrated dry run must validate this alongside asset loading/compositing.


## 2026-11-20 — Integration validation finding and fix
- The Blender asset workflow passed on `16b1858`, producing all four story PNGs. The integrated dry-run reached the episode validation stage but failed before rendering because `pipeline/validate_episode.py` did not yet whitelist the new `blender` board type. The error was explicit: lines 3, 5 and 9 had unknown board type `blender`.
- Fixed the episode validator to recognize `blender` and include per-asset cue words in its cue validation. Commit `9a244aae0a7305f2543dd2ff3ebdde12037245b1`.
- The renderer and Blender generator are technically passing their separate checks; integrated MP4 rendering and visual inspection are still pending. A new branch dry run should run automatically from the validator change. No publish or merge has occurred.


## 2026-11-20 — CurioKids Visual Engine Skia loader failure
- User shared the integrated CurioKids render traceback. Run [44739867903](https://github.com/ambujkhanna/The-CurioKids-Club/actions/runs/44739867903) passed Blender story asset generation, manifest validation and 9 unit tests, then failed in `build_blender` because `skia.Data.MakeFromFile` is absent in the runner's skia-python API. The supported method is `MakeFromFileName`; Fontconfig output was warning-only.
- Fixed `pipeline/episode_engine.py` on `feature/modern-visual-engine` in commit `2a970167d4169d29cc3e0bf9228376373935247b`. Awaiting push-triggered end-to-end dry-run and visual review of the resulting ep070 video. No production publish or merge.


## 2026-11-20 — Review of run #20 and 3D artwork refinement
- Reviewed the user-provided final recap screenshot and the actual run #20 MP4. The screenshot is the existing 2D recap board; the new Blender story visuals appear earlier in the episode. The integrated render succeeded after the Skia API fix.
- Found that the first Blender pass was too sparse/plain for mobile viewing. Refined `pipeline/blender/create_story_assets.py` on the feature branch with larger, more legible plant forms, visible branching roots, leaf veins, water drops, richer soil layers and clearer growth-stage silhouettes. Removed 3D text labels to avoid competing with episode board typography.
- Commits: `83f4ed885a99aa7273de5cfd0b154da64c4ad047`, `7974daabab02391a9c20b18d173e5562333b68b4`. Awaiting the new automated Blender + MP4 dry-run and visual QA. No production merge/publish.


## 2026-11-20 — CurioKids CI caching improvement
- User asked why the branch dry-run repeatedly downloads dependencies. Confirmed the workflow already uses `setup-python` pip caching; the larger repeat downloads were the Kokoro ONNX/voice model files and apt-installed Blender/rendering packages on fresh GitHub-hosted runners.
- Added cache for the three Kokoro model files, keyed by `pipeline/setup_models.py` hash, and apt archive cache for Ubuntu 24.04 with apt configured to keep downloaded `.deb` files after install. Existing pip cache retained.
- Workflow change: commit `166ed77a3489bfac5539ddb111148bc74957fc3d` on `feature/modern-visual-engine`. Validate cache hit/miss in next run before claiming savings. No publish/production changes.


## 2026-11-20 — Cache safety guardrails
- Confirmed GitHub's documented default cache allowance is 10 GB per repository, with entries unused for more than 7 days eligible for eviction. Cache quota is not runner-minutes quota. Cache misses/eviction must fall back to normal downloads and must not stop rendering.
- Updated Kokoro setup to validate cached model checksum, load the voices archive and load the duration ONNX before reuse; invalid cached files are deleted and rebuilt. Model cache key hashes the setup script, invalidating old model cache after validation logic changes.
- Pip cache remains enabled; apt .deb cache is one fixed-key entry while apt update/install remains active. Video outputs remain in separate 14-day artifacts. Exact cache usage was not accessible via connector; inspect repository Settings → Actions → Caches for actual bytes.


## 2026-11-20 — User feedback changes visual direction
- User is not satisfied with the completed ep070 pipeline's graphics: they feel poor and do not read as 3D. The current implementation uses static rendered PNG story cards; this is not the quality target.
- New direction: make the germination process itself the hero, animated continuously in 3D — seed splits, root emerges and grows down/branches, shoot pushes up through the soil, leaves unfold. Keep the established 2D Leo/Mia characters, but move away from static picture swaps and decorative green-field backgrounds.
- Next work is a short bounded Blender animation proof plus Skia/episode timeline integration and actual mobile-size MP4 review. Technical pipeline success is not visual approval. Keep main and publishing unchanged.
