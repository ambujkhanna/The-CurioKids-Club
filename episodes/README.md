# The CurioKids Club: episodes

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
  "description": "First line = the hook ...\n\nThe CurioKids Club: short, curious answers to kids' big questions. Subscribe: https://www.youtube.com/@CurioKidsClub",
  "hashtags": ["#KidsLearning", "#FunFacts", "#Shorts"],
  "tags": ["cat facts for kids", "..."],
  "cast": ["LEO", "MIA"],
  "loop_card": {"text": "Why do cats purr?", "cue": "next", "left": "🐱", "right": "❓"},
  "lines": [
    {"who": "LEO", "text": "Hook question?", "board": {"type": "title", "left": {"icon": "🐱", "label": "Cat"}, "right": {"icon": "🔊", "label": "Purr?"}, "mid": "?"}},
    {"who": "MIA", "text": "Answer with a keyword.", "punch": "keyword", "board": {"type": "big", "icon": "💡", "text": "Key idea", "cue": "keyword"}},
    {"who": "MIA", "text": "... Ask a grown-up to subscribe to The Curio Kids Club for more wonders! And next time someone asks... hook question?"}
  ]
}
```

- `board` starts a new whiteboard scene. It stays until the next line that has one. Line 0 must have one.
- `cue` is a word **from that same line**. The item pops in when that word is spoken. Matching is by word start, so the cue `hear` matches "hearts".
- `punch` is a word from the line that gets a quick camera zoom. Use about 1–3 per episode.
- `icon` is **one emoji** (🐙 ❤️ 🌧️ 🦷 🪐 …). The old named icons (bulb, check, x, sun, eye, brain, globe, book …) still work.
- `loop_card` is shown at the end, when its `cue` word ("next") is spoken in the last line.

### Scene types (keep text SHORT: it is shown big so it's readable on a phone)

Board text is drawn very large (50–90 px) and shrinks or wraps automatically if it's too long. **Fewer words = bigger and easier to read.**
Aim for 1–4 words per label and up to about 5 words for `big` text. Poems show **one verse line at a time** (karaoke style).

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

### Animated diagrams (use them whenever the topic shows a process; they make the video much clearer)

| type | what it shows | fields |
|---|---|---|
| `body` | friendly kid-body outline; organs; **animated flow** | `title`, `show`: list from heart, lungs, brain, stomach, bones, eyes, ears, muscles; `flow`: `blood` (red out from the heart / blue back), `nerves` (sparks from the brain to hands and feet), `air` (in and out of the lungs), `food` (mouth → stomach); `cue`: the word when the flow starts; `labels`: up to 4 × `{text ≤ 12, at: body part, cue}` (parts: brain, head, eyes, ears, nose, mouth, lungs, heart, stomach, arm, hand, leg, foot, muscles, skin, bones) |
| `cycle` | 3–6 steps in an oval with arrows; a glowing dot keeps going round | `title`, `center` (emoji, optional), `items`: `{icon, label ≤ 14, cue}`. Water cycle, life cycles, seasons, plant growth |
| `journey` | 2–5 stops on a dotted road; a traveller emoji moves to each stop as it is spoken | `title`, `traveler` (emoji), `items`: `{icon, label ≤ 14, cue}`. Sound to the ear, light to the eye, nectar → honey, food → energy |
| `orbit` | the Sun (or any `center`) with 1–4 things circling it | `title`, `center`, `items`: `{icon, label ≤ 10, cue}`. Planets, Moon around Earth, seasons (Earth around the Sun). Not for day and night: that comes from Earth spinning |

The camera automatically stays on the stage while a diagram is showing. Use at most 2 diagrams per episode, and keep the other scenes as they are.

## Writing rules

- **Audience:** ages 4–9 (parents watch too). Use short sentences and everyday words, one idea per line.
- **Length:** 11–14 lines, about 45–90 seconds with the expressive voices (Hindi versions run longer). QC accepts 20–180 s. Each spoken line is 230 characters at most.
- **Hook:** line 0 is the question, said by the asker in under 3 seconds.
- **Ending:** the last line is always "… Ask a grown-up to subscribe to The Curio Kids Club for more wonders! And next time someone asks… \<the hook again\>?" (the Subscribe / Like / Share end card pops up on "subscribe")
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
  - more than one Subscribe ask
- **Pronunciation:** in spoken `text`, write the channel name as "The Curio Kids Club" (two words, so it is said clearly). Captions show it as "CurioKids".
- **Poems:** must be **original**, with simple rhyming couplets and a steady beat. Don't use well-known nursery rhymes.
