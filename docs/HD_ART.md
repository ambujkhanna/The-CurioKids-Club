# HD backgrounds, picture boards, glass card and polished characters (The CurioKids Club)

**Added:** 2026-11-21. Code: `pipeline/art.py`, `pipeline/bg_line.py` (glass card), `pipeline/thumbnail.py`. Pictures: `assets/art/`.
AInation does **not** use backgrounds (owner, 2026-11-21: its plain Studio Open look stays).

The characters stay 2D. Backgrounds and some boards are HD pictures in a soft 3D clay / animated-film style.

## The pictures (`assets/art/`, 31 files, 5.9 MB)

- **Backgrounds (portrait 1080×1920 + landscape 1920×1080):** garden, playroom, space, night_sky, earth, bathroom, kitchen, ocean, river_valley, reading_nook, windy_hills.
- **Picture boards (landscape):** sprout, waterdrop, earth, soil_layers, desert, teeth, moon_day, waves.
- Made once, on a free Kaggle GPU, with **FLUX.1-schnell** (Black Forest Labs, **Apache 2.0**: free for commercial use and monetised videos).
- Nothing is generated during the daily run, and no paid API is used.
- `assets/art/manifest.json` records the prompt, seed, model, licence and date for every file.
- The tooth picture's right edge was cropped to remove made-up letters on the toothpaste tube.
- Left out: the straw-in-a-glass picture (the straw wasn't bent) and the cut apple (it didn't show browning, and one version had a signature).
- The notebook that made them, with run steps, is `tools/kaggle/art_v2.ipynb` (see `tools/kaggle/README.md`).

## How a video gets its background

1. Repo variable **`BACKDROP`**: forces one picture for every video (tests only).
2. The episode's **`"backdrop"`** field: every episode in `episodes/` and `long/` now has one, reviewed by hand. `"none"` means the old drawn playroom.
3. **Automatic**, for scripts and episodes without the field: the picture whose topic words appear most in the title (counted 5×) and the dialogue (counted 1×), else the playroom. `ART_AUTO=off` turns this off.

Repo variable **`ART=off`** turns every picture off and brings back the drawn room and the puppet stage.

## What changes on screen when a picture is on

- **Background:** a very slow zoom over the whole video, a little depth when the camera moves, and drifting sparkles. Soft shadows under the characters' feet, and a soft white pill behind the logo so it reads on any picture.
- **Board:** a floating white **glass card** with a thin rainbow edge replaces the puppet stage, which is too heavy over a picture. Board items **rise and fade in** instead of sliding in from the theatre wings.
- **Camera:** speaker shots are a **gentle push-in** (up to about 8%) toward whoever is speaking, so the card is never cut. Shots **glide** into each other instead of cutting. The key-word punch zooms stay.
- **Thumbnails** (Shorts and 16:9) use the same picture.
- **Long videos (16:9)** show the picture full-frame behind the room and the board; there are no string lights over a picture.
- Repo variable **`PANEL`** forces a board look: `stage`, `card`, `cloud` or `book`. Empty means automatic: card with a picture, stage without.

## Picture board

```json
"board": {"type": "picture", "art": "teeth", "caption": "About 2 minutes", "cue": "two", "icon": "⏱️"}
```
The picture fills the card with a slow push-in, and `caption` is a pill at the bottom. If the picture is missing, it becomes a big board with `icon` and `caption`. Used in ep079 (teeth), ep096 (moon_day), ep097 (earth), ep104 (soil_layers) and ep107 (waves).

## In scripts (`scripts/*.txt`)

Add an optional header line, `BACKDROP: night sky` (any name above, or `none`). Without it, the background is picked automatically from the title. A wrong name is reported, with the list of valid names.

## Polished characters (`CHAR_STYLE`)

`CHAR_STYLE=polished` gives the same shapes and rig with one clean outline, a soft light edge, a soft shadow and a second eye sparkle. The default is `doodle` until the owner switches it with the repo variable. It works in both repos.

## Adding pictures later

1. Run the Kaggle notebook with new prompts. Keep "no people, no text" in every prompt.
2. Check the corners at full size for signatures or made-up letters.
3. Save the picture as `assets/art/<name>_portrait.jpg` / `<name>_landscape.jpg` (JPEG quality 90).
4. Add its entry to `manifest.json`.
5. Add its topic words to `TOPICS` in `pipeline/art.py`.
