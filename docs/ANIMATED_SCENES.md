# Animated scenes and 3D icons (both channels)

**Added:** 2026-11-21. Code: `pipeline/scenes.py` (scenes), `pipeline/icons3d.py` (icons). Same files in both repos.

The characters stay 2D. The board now animates: a board can be an animated scene, and every icon is a glossy 3D icon (Microsoft Fluent Emoji 3D, MIT licence).

## Rule for writers

**Whenever a line explains change, a process, a journey or a cycle, use an animated scene instead of a static list.** Use static boards (`big`, `steps`, `checklist`, `compare`) for facts, tips and rules. Aim for 1–3 scenes per Short. Give the eye room: short labels (1–3 words), at most 4–5 stages.

| Use when the line says… | Scene | Example topics |
|---|---|---|
| "first…, then…, finally…" (stages of one thing) | `lifecycle` | egg → caterpillar → butterfly, seed → tree, baby → adult, raw → cooked |
| "A turns into B" | `transform` | stem → trunk, chrysalis → butterfly, ice → water, text → tokens |
| "goes from … to … to …" (something travels) | `flow` | message → AI → answer, food → stomach → body, power station → wires → home |
| the water cycle | `water_cycle` | rain, clouds, evaporation |
| how plants grow from seeds | `plant_growth` | seeds, roots, sprouts |

The existing `cycle`, `journey`, `orbit` and `body` diagrams still work.

## Copy-paste examples (`board` of the line that explains it)

Every `cue` must be the start of a word that is spoken in that line, and that's when the item appears.

```json
{"type": "lifecycle", "title": "Butterfly cycle", "items": [
  {"icon": "🥚", "label": "Egg", "cue": "egg"},
  {"icon": "🐛", "label": "Caterpillar", "cue": "caterpillar"},
  {"icon": "🫛", "label": "Chrysalis", "cue": "chrysalis"},
  {"icon": "🦋", "label": "Butterfly", "cue": "butterfly"}]}
```

```json
{"type": "transform", "title": "Hello, butterfly!",
 "from": {"icon": "🫛", "label": "Chrysalis", "cue": "chrysalis"},
 "to":   {"icon": "🦋", "label": "Butterfly!", "cue": "butterfly"}}
```

```json
{"type": "flow", "title": "BOOK A TRAIN", "packet": "🎫", "items": [
  {"icon": "🔍", "label": "Find trains", "cue": "find"},
  {"icon": "🚆", "label": "Compare times", "cue": "compare"},
  {"icon": "📝", "label": "Fill in the booking", "cue": "booking"}]}
```

```json
{"type": "water_cycle", "title": "The water cycle", "items": [
  {"label": "Water rises", "cue": "floats"}, {"label": "Clouds form", "cue": "clouds"},
  {"label": "Rain falls", "cue": "falls"}, {"label": "Round again", "cue": "round"}]}
```

```json
{"type": "plant_growth", "title": "Sprouting", "items": [
  {"label": "Seed", "cue": "first"}, {"label": "Root grows down", "cue": "root"},
  {"label": "Shoot pushes up", "cue": "shoot"}, {"label": "Toward the light", "cue": "light"}]}
```
(`plant_growth` stages are drawn in this order: seed, roots, shoot, leaves, tree. Use 3–5 items.)

## Lighter list boards (tiles)

`steps`, `checklist` and `summary` boards are now drawn as **airy tiles**: a row of 1–4 soft cards, each with a big 3D icon and a short label, popping in as it is spoken. Checklist items without an icon show a 3D ✅ or ❌; items with an icon get a small tick/cross badge. A 5-item step list becomes a slim **timeline** that highlights the item being spoken. Lists longer than that keep the old rows. Repo variable `LIST_STYLE=classic` brings back the old full-width rows everywhere. Keep labels to 1–3 words.

## Icons

- **Our own realistic icons come first** (since 2026-11-21): 151 house icons in `assets/icons_house/<emoji code>.webp` (512 px, transparent), made on Kaggle with FLUX.1-schnell plus the rembg cut-out (`tools/kaggle/icons_v1.ipynb` in the kids repo, `assets/icons_house/manifest.json`). They cover objects, animals, food, nature, science kit, anatomy models and tech hardware.
- **Curated mix:** for weather and symbols, mostly-white objects and the small robot, the emoji reads better on a white card, so these stay emoji: ☀️ ☁️ ❄️ 🌀 ✅ ❌ ⚠️ 🚫 🛑 💬 📄 ✉️ 📅 📝 📖 🤖 🧼 🦴 🪶 🥛 🥚 🎲 🥤 🧴 🩹 (`PREFER_EMOJI` in `pipeline/icons3d.py`; edit the list to change it).
- **Nothing was thrown away.** Force our version on a board with `"house:<emoji>"`, e.g. `"icon": "house:☀️"`, or use every house icon with repo variable `ICON_STYLE=house_all`.
- **House-only pictures** (no emoji exists): use the name as the icon, e.g. `"icon": "w_soil_block"`. Available: `w_ai_chip`, `w_cloud_data`, `w_deepfake_mask`, `w_eye_model`, `w_heart_model`, `w_inner_ear`, `w_neural_net`, `w_plant_cell`, `w_seed_cut`, `w_server`, `w_skin_layers`, `w_soil_block`, `w_sound_wave`, `w_stomach_model`, `w_tongue_model`, `w_tooth_cavity`.
- Otherwise every emoji (`"🦋"`) or board icon name (`"robot"`, `"lock"`, …) is drawn as its 3D Fluent icon (1,594 of them, listed in `pipeline/fluent3d_index.json`; downloaded once per run into `assets/icons3d/`, not committed). If one can't be fetched, the old flat icon is used, so nothing breaks.
- Repo variable `ICON_STYLE`: `house` (default, curated mix) · `house_all` · `3d` (Fluent only) · `flat` (the old flat icons).
- 14 generated icons were rejected (made-up letters or logos, failed cut-outs of see-through things, wrong objects): 💧 💨 🌧️ 🧊 🦷 🧲 🪙 📰 📷 ⚽ 🔋 🎁, prism, password. They stay on Fluent; remake them in a later Kaggle run if wanted (put see-through objects on a darker background).
- `img:` pictures keep working as before.

## Real photos and video clips (since 2026-11-21, roadmap R1)

Two board types put **real** pictures in the card. They use no API key and are credited automatically.

```json
{"type": "photo", "query": "oak tree", "caption": "A giant oak", "cue": "oak", "icon": "🌳"}
{"type": "clip",  "query": "earth from space station", "caption": "Our planet", "cue": "planet", "icon": "🌍"}
```

- **Channels (owner, 2026-11-22):** **AInation uses real photos** (style `plain`; `STOCK_STYLE=polaroid` gives a tilted snapshot with a REAL! sticker). **The CurioKids Club does not**: next to the cartoon world they looked pasted-in, even as polaroids, and a simple paint filter looked muddy. Kids workflows default `STOCK=off`, so a photo/clip board there becomes an icon board. Kids realism comes from our clay-style pictures and the house icons; a later Kaggle option could restyle a photo into the clay style with the image model.
- **Sources:** NASA (space topics; photos and videos) and Openverse (everything else; openly licensed photos, only CC0, Public Domain Mark or CC BY: commercial use and changes allowed, no share-alike).
  - Space words in the query (planet, moon, mars, astronaut, galaxy…) → NASA first. Otherwise Openverse only.
  - `"source": "nasa"` or `"openverse"` forces one.
  - Pixabay (and Pexels, if it reopens keys) can be added later.
- **On screen:** the photo fills the card with a slow push-in. A clip plays 14 s of the NASA video, muted and looping. The caption pops on the cue word, and a small "Photo: …" / "Video: NASA" credit sits in the corner.
- **Credits** (title, creator, licence, link) go into the YouTube description automatically, together with the Bioicons credits.
- **3D art first (owner, 2026-11-22):** add `"art": "<name>"` to a photo board. When `assets/art/<name>_landscape.jpg` exists (made on Kaggle: AInation `tools/kaggle/art_ain_v1.ipynb`), our realistic 3D picture is shown and the raw photo is only the fallback. No credit is needed for our own art.
- **Pinned photos:** after a photo has been reviewed, its details are stored in the board as `"pin": {url, title, source, creator, licence, landing, credit}`. The daily run then uses exactly that photo (no new search, so it can't change or hit Openverse's rate limit). Used in AInation ep031 (office worker) and ep036 (doctor looking at an X-ray).
- **Wrong picture?** Add `"pick": 1` (2, 3…) to use the next search result, or change the `query` wording. Search results are cached per board in `assets/stock/` (not committed); a changed query or pick fetches again.
- **Safety:** if a search finds nothing, a download fails, or repo variable `STOCK=off` is set, the board becomes a big icon board with the `icon` and `caption`. Check kids photos for people or anything unsuitable before posting: Openverse photos aren't filtered for people.
- The validator requires `query` for both types. `python pipeline/stock.py episodes/epNNN-*/episode.json` fetches and prints the credits (good for a preview).

## Safety

- The validator knows the new types and checks every cue, including `from` and `to`.
- If a scene fails to draw a frame, that frame skips the scene and the video still renders; the log says `note: scene frame skipped`.
- The camera stays on the board during scenes, as it does for diagrams.

## Ideas for the next scenes

`zoom_in` (look inside: a heart, a cell, a computer chip) · `build_up` (parts assemble: a sandwich, a robot) · `day_night` (Earth turns, Sun and Moon) · `food_chain` · `tokens` (a sentence splits into coloured chunks for AInation). Add them to `pipeline/scenes.py`, `BUILDERS` and the validator's `TYPES`.
