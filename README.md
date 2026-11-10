# The CurioKids Club: automated YouTube Shorts for kids

**Created:** 2026-11-04 (Claude Code session), built from the AInation Studio pipeline.

The CurioKids Club makes short, curious answers to kids' big questions (animals, the human body, space, nature, everyday science) plus original rhymes and poems. Each Short is about 55 seconds.

- **Cast** (chosen per episode): **Leo**, the curious little brother who asks "why?"; **Mia**, the big sister who explains; and sometimes **Dad**. Poems are often Mia on her own.
- **Look:** a colourful **playroom** with a **puppet theatre** (wooden frame, velvet curtains that open at the start, spotlight, footlights). Big pictures and phone-readable words slide in from the wings like puppets; poems show one big verse line at a time. Doodle line-art characters stand in front, with Buzz the helper bee.
- **Cost:** no paid services and no AI API. Everything runs free on GitHub Actions.

## Follow The CurioKids Club

| Platform | Link |
|---|---|
| ▶️ YouTube | https://www.youtube.com/@CurioKidsClub |
| 📘 Facebook | https://www.facebook.com/profile.php?id=61596461063065 |
| 📸 Instagram | https://www.instagram.com/thecuriokidsclub/ |

Hashtag: **#TheCurioKidsClub**

## How it works (every day, automatically)

```text
GitHub Actions, 08:40 UTC (14:10 IST), or Actions → "Daily Curio Kids Short" → Run workflow
  → pick the next ready episode in episodes/   (skips ones already uploaded)
  → voices (Kokoro, free; Leo's voice is pitch-shifted to sound younger)
  → frames (skia) → MP4 with captions + a different original music track per episode (FFmpeg)
  → designed thumbnail (headline + question + pictures + characters)
  → QC (1080×1920, 45–180 s, audio level, captions, title/description)
  → upload to YouTube as "Made for Kids", category Education, AI-content flag on, then set the thumbnail
  → scheduled in a random slot 16:00–19:00 IST (change with repo variable PUBLISH_WINDOW)
  → write episodes/state.json, keep the MP4 as a run artifact for 14 days
```

If any step fails, nothing is uploaded. Setup instructions are in **`docs/SETUP.md`**.

## Contents

| Path | What it is |
|---|---|
| `episodes/` | 74 ready episodes (ep002–ep075, about 2.5 months; ep001 was removed), `TOPICS.md` and the format guide `README.md` |
| `pipeline/daily.py` | daily run: pick, render, QC, upload |
| `pipeline/tts.py` | voices and lip-sync timing |
| `pipeline/episode_engine.py` | whiteboard scenes, acting, camera |
| `pipeline/char_line.py` | the characters |
| `pipeline/bg_line.py`, `pipeline/kit2d.py` | playroom, logo and helper bee |
| `pipeline/theatre.py` | the puppet theatre (back layer + curtains in front of the content) |
| `pipeline/finish.py` | captions, sound mix, MP4 |
| `pipeline/music.py` | a different original music track per episode (or your own tracks in `music/`) |
| `pipeline/thumbnail.py` | designed thumbnail for each video |
| `pipeline/upload_youtube.py` | YouTube upload (Made for Kids) |
| `pipeline/validate_episode.py` | checks episode files before you push |
| `.github/workflows/curio-kids-short.yml` | the daily schedule |
| `fonts/` | caption fonts (OFL) |

## Adding episodes later

1. Copy any episode folder, rename it to the next id, and edit the text. `episodes/README.md` explains every field.
2. Check your files:
   ```bash
   python pipeline/validate_episode.py episodes/*/episode.json
   ```
   This is optional. The daily run also refuses broken files.
3. Push.

Any AI chat can draft new episodes if you give it `episodes/README.md` and one example `episode.json`. Keep at least a week of `"status": "ready"` episodes in the queue.

## Changing voices

The defaults are in `pipeline/tts.py`:

| Speaker | Voice | Speed | Pitch |
|---|---|---|---|
| MIA | `af_heart` | 1.05 | normal |
| LEO | `af_sky` | 1.08 | +2.5 semitones |
| DAD | `am_michael` | 0.95 | normal |

To change a voice for one episode, add for example `"voices": {"LEO": ["af_bella", 1.1, 3]}` to its `episode.json`. Other Kokoro voices: af_bella, af_nicole, af_sarah, af_nova, am_puck, am_liam, bf_emma, bm_george and more.
