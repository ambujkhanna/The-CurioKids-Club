# Visual asset library

This folder stores reusable visual assets for the CurioKids renderer.

## Sources to evaluate

| Source | Intended use | Handling |
|---|---|---|
| [Kenney](https://kenney.nl/) | Low-poly props, vehicles and environments | Record the exact pack page and licence |
| [3dicons](https://3dicons.co/) | Educational 3D icons | Record the exact asset/version and licence |
| [Lummi](https://www.lummi.ai/) | Stylised illustrations and backgrounds | Check the current plan and asset terms |
| [Pixabay](https://pixabay.com/) | Motion clips and overlays | Check the individual content and third-party rights |
| [IconScout](https://iconscout.com/) | Specialised education packs | Optional; confirm free-tier, attribution and commercial terms |

These are candidate sources, not blanket approvals. Licensing can vary by asset, contributor, plan, download date and intended use. Never mark an asset as approved for monetized publishing based only on a general website summary.

## Required manifest fields

Add one entry to `manifest.json` per imported asset:

- `id`: stable unique identifier.
- `file`: repository-relative path.
- `source` and `source_url`: provider and exact asset/pack page.
- `downloaded_on`: ISO date.
- `license`: exact licence name/version or provider terms.
- `commercial_use`: `allowed`, `not_allowed` or `unverified`.
- `license_evidence`: URL or local note/snapshot reference supporting the decision.
- `attribution_required` and `attribution`: exact credit if required.
- Optional `format`, `resolution`, `notes`.

Example (do not copy without checking the actual asset):

```json
{
  "id": "kenney-example-prop",
  "file": "assets/3d/kenney/example.png",
  "source": "Kenney",
  "source_url": "https://kenney.nl/assets/",
  "downloaded_on": "2026-11-18",
  "license": "CC0",
  "commercial_use": "allowed",
  "license_evidence": "https://kenney.nl/support",
  "attribution_required": false,
  "attribution": "",
  "format": "PNG",
  "resolution": "1024x1024"
}
```

Validate before committing:

```bash
python pipeline/asset_manager.py
```

Do not add assets with `commercial_use: unverified` to monetized/published scenes. Keep original licence files or screenshots where practical. Avoid redistributing source packs as standalone collections.

## Rendering guidance

- Prefer transparent PNG/WebP for direct compositing in the existing Skia pipeline.
- Keep source 3D files (e.g. Blender or glTF/GLB) only when they provide useful future editing value.
- Use 1000px+ source images where practical for gentle zooms/crops; don't upscale tiny assets.
- Keep character art separate from environment/prop art to preserve Leo/Mia consistency.
- Prefer pre-rendered reusable 3D stills/sequences over full 3D rendering on every GitHub Actions run.
