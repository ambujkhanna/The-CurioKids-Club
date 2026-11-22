# Spanish Shorts (roadmap R5, built 2026-11-22)

**What runs:** one Spanish Short a day on The CurioKids Club, besides the English/Hindi one. Cron 21:41 UTC (03:11 IST) → publishes 05:30–07:30 IST (= 18:00–20:00 Mexico City). Own queue (`state.json` → `rec["es"]`), same order as English, only episodes that have `es.json`. Playlist `CurioKids_Spanish` (English + Hindi go to `curiokids`). Pause with repo variable `ES_SHORTS=off`. Manual run: Run workflow → language `es`.

**How it looks:** Spanish voices (Kokoro, Apache 2.0: Mia = `ef_dora`, Leo = `em_alex` pitched +5, Dad = `em_santa`; owner's pick "B"), Spanish captions with real word timing, every board translated, Spanish hook and thumbnail headline, sticker "¿POR QUÉ?/¿CÓMO?…", green **ESPAÑOL** badge, title "Spanish | English", Spanish + English description, `#EnEspañol #CienciaParaNiños`.

**Status:** 81 of 99 episodes have `es.json` (written 2026-11-22, all pass `validate_episode.py`). Not translated on purpose: English-language lessons (ep076, ep077, ep078) and rhymes/poems (ep004, ep011, ep016, ep019, ep026, ep031, ep034, ep041, ep046, ep049, ep056, ep060, ep063, ep069, ep073); the owner decides on those later. Word choice: Latin-American, Mexico-leaning ("jalar", "papalote", "lonchera"), since the slot is Mexico's evening.

**Code:** `tts.py` (`TTS_LANG=es`), `episode_engine.py` (boards/cover/loop card/punch from es.json), `finish.py` (Spanish hook), `thumb_punch.py` (Spanish sticker word), `daily.py` (`--lang es`, `plan_es`, `spanish_ep`, badge, playlist), `validate_episode.py` (`check_es`), `setup_models.py` (adds the Spanish voices), `upload_youtube.py` (playlist by name, created if missing).

---

## How to write es.json for a new episode (works with any assistant)

Repo working copy: the repo root  (channel "The CurioKids Club": 45-60 s science Shorts for kids 4-9; Leo, a curious little boy, asks; his big sister Mia explains).
For each episode folder you are given, read `episodes/<folder>/episode.json` and write `episodes/<folder>/es.json`. Touch NO other file.

**The model file (study it first):** `episodes/ep094-why-space-is-cold/es.json` next to its `episode.json`. Copy its structure exactly.

## es.json fields
- `title_es`: the question in Spanish + the same emoji as the English title (drop "Fun Facts for Kids"). len(title_es) + len(English title without "Fun Facts for Kids") must be ≤ 97.
- `description_es`: 1-3 sentences in Spanish, like the English description's first paragraph (no links).
- `cover_text_es`: 1-3 HUGE thumbnail words in CAPITALS with Spanish punctuation (e.g. "¡QUÉ FRÍO!").
- `hook`: the opening question, ≤ 50 characters, starting with "¿" (e.g. "¿Por qué hace tanto frío en el espacio?").
- `tags_es`: 3 Spanish search phrases parents would type.
- `loop_card_es`: ONLY if episode.json has `loop_card`: same `left`/`right` icons, `text` translated, and `cue` = a word that appears in the LAST Spanish line (the end card waits for that word; ep094 uses "próxima" from "Y la próxima vez que alguien pregunte...").
- `lines`: exactly the same number of lines, same order, same speaker meaning. Natural, warm, neutral Latin-American Spanish a 6-year-old understands ("tú" for the child; "Pídele a un adulto..." for the asks). Mia calls Leo "Leo"; Leo calls her "Mía". Keep any tags like [laugh] [gasp] exactly where they are. Keep lines short (≤ 260 chars, ideally similar length to English). Write numbers as words when they are said ("doscientos setenta grados bajo cero"); the voice reads digits poorly. Brand name stays "The CurioKids Club". The LAST line must contain "suscriba" or "suscríbete" (e.g. "Pídele a un adulto que se suscriba a The CurioKids Club...") and must keep the closing callback the English last line has.
- `punch`: optional object {"<line index>": "<spanish word said in that line>"} for each English line that has "punch".
- `boards`: for EVERY English line that has a "board", the same board translated, keyed by line index as a string. Keep EXACTLY the same structure: same `type`, same keys, same number of items/rows/steps, same `icon`/`art`/`stock`/`ok` values. Translate only the visible words (`text`, `label`, `caption`, `title`, `sub`, `mid` if it is a word). Board words are SHORT (1-4 words; they appear big on screen).
  - Every `cue` / `sub_cue` must be the BEGINNING of a word that is actually said in the Spanish line of that board (or one of the next two lines). Pick a distinctive word near the point where the English cue word was said. Accents count ("vacío" ≠ "vacio").

## Skip these (write nothing, just list them in your report)
- Episodes about ENGLISH spelling, grammar or pronunciation (e.g. "a apple or an apple", "silent k in knife", "why 'the' sounds different") — they make no sense in Spanish.
- Rhymes and poems (folder names with "rhyme" or "poem") — the owner will decide on them later.

## Check every file (must print OK)
python pipeline/validate_episode.py episodes/<folder>/episode.json
Fix until it prints OK. (It checks line count, board shape, that cues are spoken, the subscribe line, the title length.)

## Report back (short)
Folders written (with OK), folders skipped and why, anything you were unsure about (max 5 bullets). Don't paste file contents.
