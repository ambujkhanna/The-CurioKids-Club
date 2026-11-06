# Long videos (weekly, 16:9, 3–8 minutes)

The weekly workflow publishes the next folder in `long/` (in id order) that has `"status": "ready"` and isn't yet listed in `long/state.json`.
Each long video goes deeper on the topic of one of the Shorts.

## Format

It uses the **same JSON format as the Shorts** (`episodes/README.md`: cast, scenes, cues, icons, diagrams, `img:` illustrations), with these differences:
- **40–80 lines** (about 3–8 minutes). The checker allows 25–120.
- Some lines carry `"chapter": "Short title"`, which marks the start of a chapter. Use 4–6 chapters, at least 3. YouTube chapters (`0:00 Intro`, …) are added to the description automatically.
- `id` looks like `"L01"`, and the folder is `long/L01-<slug>/episode.json`.
- `"short_id"`: the id of the matching Short (e.g. `"ep003"`), for your reference.
- The description has no `#Shorts`. The first line is what the viewer will learn. Mention that the 60-second version is on the channel's Shorts tab.

## Structure that works

1. **Intro** (3–5 lines): a hook question, then what we'll find out.
2. **Chapters** (3–5): one idea each, explained with examples. Use a board change every 1–3 lines and at least 2 animated diagrams (`body`, `cycle`, `journey`, `orbit`) where the topic has a process.
3. **Quiz** (4–6 lines): 2–3 quick questions. Ask, pause with "Think…", then answer.
4. **Recap** (2–3 lines): a `summary` board.
5. **Ending**: the same Subscribe / Like / Share line style as the Shorts, ending with the loop-back question.

## Rules

- **Facts:** keep them correct and kind. Say "scientists think" where the science isn't settled, and don't invent numbers.
- **Text on screen:** keep it short so it stays big. Spoken lines are 230 characters at most.
- **Check your files:**
  ```bash
  python pipeline/validate_episode.py long/*/episode.json
  ```
