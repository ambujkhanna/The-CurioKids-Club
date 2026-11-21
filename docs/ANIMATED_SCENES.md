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

- Any emoji (`"🦋"`) or board icon name (`"robot"`, `"lock"`, …) is drawn as its 3D Fluent icon. There are 1,594 of them, listed in `pipeline/fluent3d_index.json`.
- Icons are downloaded once per run from GitHub into `assets/icons3d/` (not committed). If one can't be fetched, the old flat icon is used, so nothing breaks.
- Repo variable `ICON_STYLE=flat` switches every board back to the old flat icons.
- `img:` pictures keep working as before.

## Safety

- The validator knows the new types and checks every cue, including `from` and `to`.
- If a scene fails to draw a frame, that frame skips the scene and the video still renders; the log says `note: scene frame skipped`.
- The camera stays on the board during scenes, as it does for diagrams.

## Ideas for the next scenes

`zoom_in` (look inside: a heart, a cell, a computer chip) · `build_up` (parts assemble: a sandwich, a robot) · `day_night` (Earth turns, Sun and Moon) · `food_chain` · `tokens` (a sentence splits into coloured chunks for AInation). Add them to `pipeline/scenes.py`, `BUILDERS` and the validator's `TYPES`.
