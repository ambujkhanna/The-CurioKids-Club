# Make a video from your own script (The CurioKids Club)

Write a script as a plain text file in this `scripts/` folder. Then run **Actions → Daily Curio Kids Short → Run workflow** and type its path in **script** (for example `scripts/how-bees-make-honey.txt`). The pipeline checks the script, turns it into an episode, and renders, uploads and posts it like any other video.

**Safe by design:** if anything in the script is wrong, the run **stops before making a video** and the run summary lists every problem with its line number. A broken or half-made video can't be uploaded.

## 1. Create the file (on GitHub, no software needed)
1. Open the repo on github.com and go into the **scripts** folder.
2. Click **Add file → Create new file**.
3. **File name:** lowercase words joined by `-`, ending in `.txt`, with **no spaces**, e.g. `how-bees-make-honey.txt`. Each file becomes **one** video. To post another video, use a **new** file name (a file that was already uploaded won't be uploaded twice).
4. Paste your script (start from `TEMPLATE.txt`), then click **Commit changes**.

## 2. The format

```text
TITLE: How Do Bees Make Honey? 🐝 Fun Facts for Kids
COVER: BEE MAGIC
HASHTAGS: #Bees #Honey #ScienceForKids
TITLE_BOARD: 🌸 Flowers -> 🍯 Honey
---
LEO: Mia, how do bees make honey?
MIA: It starts with flowers! Bees sip a sweet juice called nectar.   | 🌸 Sweet nectar
LEO: Like drinking juice with a straw?
...
```

**Header (above the `---` line)**

| Line | Required? | What it is | Rules |
|---|---|---|---|
| `TITLE:` | **yes** | YouTube title | max **70** characters; one emoji at the end is nice |
| `COVER:` | no | 1–3 BIG words on the thumbnail | default: from the title |
| `HASHTAGS:` | no | your topic hashtags, space-separated (most important first) | the channel tag **#TheCurioKidsClub** is always added (2nd place). Instagram gets **5** in total, Facebook 10, YouTube 15 (+ `#Shorts`) |
| `DESCRIPTION:` | no | 1–2 sentences for YouTube/Facebook/Instagram | default: the first answer line |
| `TAGS:` | no | YouTube search tags, comma-separated | |
| `TITLE_BOARD:` | no | the opening board: `emoji Word -> emoji Word` | default: a big board with the title question |
| `TITLE_HI:` | only for Hindi | the Hindi title (the video title becomes `Hindi \| English`) | |
| `DESCRIPTION_HI:` | no | Hindi description | |

**Dialogue (below `---`):** one line per spoken line: `NAME: what they say`

| Rule | Value |
|---|---|
| Characters | `MIA` (big sister, explains), `LEO` (little brother, asks), `DAD`; use **1 or 2** per video |
| Number of lines | **9–16** (best **11–14**), including the Subscribe line |
| Length of a line | max **230** characters (about 2 sentences); split longer ones |
| Total length | about **110–180 words** ≈ **45–90 seconds** (hard limits: 50–180 words, 20–180 s) |
| First line | a question (it becomes the opening board) |
| Last line | the Subscribe line. If you leave it out, it's added automatically: *"Ask a grown-up to subscribe to The Curio Kids Club for more fun!"* |

## 3. Pictures on the board (strongly recommended)
Add `|` after a line, then **one emoji** and **up to 5 words** (max 32 characters):
```text
MIA: Their tongue works like a tiny straw.   | 👅 A tongue straw!
```
- **When it appears:** the board changes on that line, and the picture pops in when the matching word is spoken.
- **Second line of text:** add `;` then up to 32 characters: `| 🐝 Fan, fan, fan! ; until it's thick`.
- **How often:** add a picture every **2–3 lines** (about 4–6 per video). If you skip some, the pipeline adds a picture by itself when it recognises a word (cat, heart, robot, chat…).
- **What works:** use **one simple emoji**. Combined emoji like 👨‍👩‍👧 don't work.

## 4. Sounds and expressions
| Write | Result |
|---|---|
| `Ha!` / `Ha ha!` / `Hee hee!` | a real laugh or chuckle, with a short pause before and after it |
| `[laugh]` `[chuckle]` `[gasp]` `[sigh]` `[cough]` | the sound, e.g. `[gasp] Whoa! That's huge!` (never shown in subtitles) |
| `Zzz!` | a cartoon snore sound |
| `...` | a small dramatic pause |
Other tags like `[giggle]` are **not** supported, and the check will tell you.

## 4b. Hindi version (optional)
After **each** dialogue line, add a `HI:` line with the Hindi translation, and add `TITLE_HI:` to the header:
```text
LEO: Mia, how do bees make honey?
HI: मिया दीदी, मधुमक्खियाँ शहद कैसे बनाती हैं?
```
- **All lines or none:** every line needs its `HI:`, or none of them.
- **Script:** write English words in Hindi letters (साइंस, ब्रेन). The Subscribe line's Hindi is added automatically.
- **Result:** run with **language: hi** to get Hindi voices with English subtitles. Run with **language: en** to get the English video from the same file.

## 5. Run it
**Actions → Daily Curio Kids Short → Run workflow**:
| Field | Value |
|---|---|
| script | `scripts/your-file.txt` |
| dry_run | ✅ **for the first try**: you get the MP4 in the run's **Artifacts** to watch |
| publish_now | optional: publish right away instead of the next 17:00–20:00 IST (English) or 09:00–11:00 IST (Hindi) slot |
| language | `en`, or `hi` for the Hindi version (needs `HI:` lines) |
Then run again **without** dry_run to upload it to YouTube and post it to Facebook and Instagram. The summary shows the links.

## 6. Checklist before you run
- [ ] `TITLE:` present, ≤ 70 characters
- [ ] a `---` line between the header and the dialogue
- [ ] every dialogue line starts with `MIA:`, `LEO:` or `DAD:` and a colon
- [ ] only 1–2 characters, 9–16 lines, about 110–180 words
- [ ] a picture hint (`| emoji words`) every 2–3 lines
- [ ] facts double-checked (it's for kids: keep it accurate, gentle and safe)
- [ ] new file name for a new video, no spaces
