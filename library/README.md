# Category library (published on demand from the "category" dropdown)

Folders:
- `library/comedy`, `library/quiz`, `library/knowledge`, `library/science`, `library/abc`, `library/counting`, `library/rhymes`
- Each episode lives in `library/<category>/<ID>-<slug>/episode.json`, with its own `state.json` per category.
- **IDs:**

| Category | IDs |
|---|---|
| comedy | COM01… |
| quiz | QUZ01… |
| knowledge | KNW01… |
| science | SCI01… |
| abc | ABC01… |
| counting | CNT01… |
| rhymes | RHY01… |

**Format:** the same as `episodes/README.md` (Shorts, 11–15 lines, 45–75 s). Extra boards:
- **guess** (quiz): `{"type": "guess", "title", "clues": [{icon, label, cue}] (up to 3), "answer": {icon, label, cue}}`. The answer cue may be spoken in a later line before the next board.
- **letter** (abc): `{"type": "letter", "letter": "B", "cue": "word", "items": [{"icon": "🐻", "label": "Bear", "cue": "bear"}] (up to 4)}`
- **count** (counting): `{"type": "count", "icon": "🍎", "count": 5, "start": 1, "step": 1}`. The objects appear when the number words ("one", "two", …) are spoken in that line. Write the numbers as words in the spoken text.

Check episodes with:
```bash
python pipeline/validate_episode.py library/*/*/episode.json
```
