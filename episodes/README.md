# Curio Kids Club: episodes

One folder per episode: `episodes/<id>-<slug>/episode.json`. Each day the automation publishes the next folder, in id order, that has `"status": "ready"` and isn't already listed in `state.json`. The topic plan is in `TOPICS.md`.

Before you push new episodes, check them:

```bash
python pipeline/validate_episode.py episodes/*/episode.json
```

## Cast (pick per topic)

| Code | Who | Voice | Typical role |
|---|---|---|---|
| `LEO` | little brother, about 6–7 | young, pitched-up voice | asks "why?", reacts, sums up |
| `MIA` | big sister, about 14 | friendly, clear | explains, recites poems |
| `DAD` | dad | warm | sometimes explains everyday science |

- `"cast": ["LEO", "MIA"]`: the default. The **first** name stands on the left and asks; the second stands on the right and explains.
- `"cast": ["LEO", "DAD"]`: use for about 1 in 6 explainers (kitchen and everyday science).
- `"cast": ["MIA"]`: solo. Mia talks to the viewer (good for poems). Poems can also be `["LEO", "MIA"]`, taking turns with the verses.

## Format

```json
{
  "id": "ep002", "slug": "why-cats-purr", "status": "ready",
  "title": "Why Do Cats Purr? 🐱 Fun Facts for Kids",
  "cover_text": "PURRR?",
  "description": "First line = the hook ...\n\nCurio Kids Club: short, curious answers to kids' big questions. Subscribe: https://www.youtube.com/@CurioKidsClub",
  "hashtags": ["#KidsLearning", "#FunFacts", "#Shorts"],
  "tags": ["cat facts for kids", "..."],
  "cast": ["LEO", "MIA"],
  "loop_card": {"text": "Why do cats purr?", "cue": "next", "left": "🐱", "right": "❓"},
  "lines": [
    {"who": "LEO", "text": "Hook question?", "board": {"type": "title", "left": {"icon": "🐱", "label": "Cat"}, "right": {"icon": "🔊", "label": "Purr?"}, "mid": "?"}},
    {"who": "MIA", "text": "Answer with a keyword.", "punch": "keyword", "board": {"type": "big", "icon": "💡", "text": "Key idea", "cue": "keyword"}},
    {"who": "MIA", "text": "... Follow Curio Kids Club for more wonders. And next time someone asks... hook question?"}
  ]
}
```

- `board` starts a new whiteboard scene. It stays until the next line that has one. Line 0 must have one.
- `cue` is a word **from that same line**. The item pops in when that word is spoken. Matching is by word start, so the cue `hear` matches "hearts".
- `punch` is a word from the line that gets a quick camera zoom. Use about 1–3 per episode.
- `icon` is **one emoji** (🐙 ❤️ 🌧️ 🦷 🪐 …). The old named icons (bulb, check, x, sun, eye, brain, globe, book …) still work.
- `loop_card` is shown at the end, when its `cue` word ("next") is spoken in the last line.

### Scene types (keep board text short; it must fit)

| type | fields |
|---|---|
| `title` | `left`/`right`: `{icon, label ≤ 14 chars}`, `mid` (default "?"), optional `subtitle` |
| `big` | `icon`, `text` ≤ 28 chars, `cue`, optional `sub` ≤ 30 chars + `sub_cue` |
| `gallery` | `title` ≤ 24, `items`: up to 6 × `{icon, label ≤ 16, cue}`. A picture grid, good for body parts, planets, animals |
| `poem` | `title` ≤ 24, `icon`, `lines`: up to 4 × `{text ≤ 34, icon, cue}`. Verse lines appear one by one |
| `steps` | `title`, `items`: up to 5 × `{label ≤ 30, icon, cue}` |
| `compare` | `left`/`right`: `{label ≤ 12, items: up to 4 × {text ≤ 16, icon, cue}}` |
| `checklist` | `title`, `icon`, `items`: up to 4 × `{text ≤ 26, icon, cue, ok: true/false}` |
| `summary` | `rows`: up to 4 × `{text ≤ 26, icon, cue}` |

## Writing rules

- **Audience:** ages 4–9 (parents watch too). Use short sentences and everyday words, one idea per line.
- **Length:** 11–14 lines, about 50–65 seconds. Each spoken line is 230 characters at most.
- **Hook:** line 0 is the question, said by the asker in under 3 seconds.
- **Ending:** the last line is always "… Follow Curio Kids Club for more wonders. And next time someone asks… \<the hook again\>?"
- **Facts:** only well-established facts.
  - If scientists aren't sure (yawning, zebra stripes), say "scientists think …".
  - Never invent numbers or sources. Use a round number only when it is well known, and say "about".
- **Safety:**
  - Nothing scary, gross or unsafe.
  - No experiments with fire, heat, knives or electricity. Any safe at-home idea says "ask a grown-up".
  - No medical advice beyond general healthy habits.
- **No:**
  - brands, real people, or copyrighted songs or characters
  - "comment below" (comments are off on kids' videos)
  - begging for likes
  - more than one Follow ask
- **Pronunciation:** write the channel name as "Curio Kids Club".
- **Poems:** must be **original**, with simple rhyming couplets and a steady beat. Don't use well-known nursery rhymes.
