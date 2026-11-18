# The CurioKids Club: automated YouTube Shorts for kids

**Created:** 2026-11-04 (Claude Code session), built from the AInation Studio pipeline.

The CurioKids Club makes short, curious answers to kids' big questions (animals, the human body, space, nature, everyday science) plus original rhymes, jokes and quizzes. Each Short is about 45–90 seconds (QC allows 20–180 s). Shorts alternate daily between **English** and **Hindi** (Hindi voices with English subtitles).

- **Cast** (chosen per episode): **Leo**, the curious little brother who asks "why?"; **Mia**, the big sister who explains; and sometimes **Dad**. Poems are often Mia on her own.
- **Look:** a colourful **playroom** with a **puppet theatre** (wooden frame, velvet curtains that start half open, spotlight, footlights). Big pictures and phone-readable words slide in from the wings like puppets; poems show one big verse line at a time. Doodle line-art characters stand in front, with Buzz the helper bee.
- **Cost:** no paid services and no AI API. Everything runs free on GitHub Actions.
- **Audience setting (owner decision, 2026-11-07):** videos are uploaded as **"not made for kids"** (repo variable `MADE_FOR_KIDS`, default `false`), chosen deliberately for wider audience and reach. See `docs/SETUP.md` for the trade-offs and how to switch back.

## Follow The CurioKids Club

| Platform | Link |
|---|---|
| ▶️ YouTube | https://www.youtube.com/@CurioKidsClub |
| 📘 Facebook | https://www.facebook.com/TheCurioKidsClub |
| 📸 Instagram | https://www.instagram.com/thecuriokidsclub/ |

Hashtag: **#TheCurioKidsClub**

## How it works (every day, automatically)

```text
GitHub Actions, twice a day (14:10 and 21:10 IST, automatic mode), or Actions → "Daily Curio Kids Short" → Run workflow
  → decide what's due: alternate days, Hindi Short (publishes 09:00–11:00 IST) / English Short (17:00–20:00 IST)
  → pick the next ready episode in episodes/   (skips ones already uploaded; Hindi and English tracked separately)
  → voices: Chatterbox (expressive, Mia/Leo/Dad cloned) + Chatterbox-Turbo for real laughs; Kokoro as automatic backup
  → frames (skia) → MP4 with captions, opening hook, end card + an original music track per episode (FFmpeg)
  → designed 3D thumbnail (HINDI tag on Hindi videos)
  → QC (1080×1920, 20–180 s, audio level, captions, title/description)
  → upload to YouTube ("not made for kids" by owner decision, category Education, AI-content flag on), set the thumbnail
  → scheduled in a random 5-minute slot inside the day's window (repo variables PUBLISH_WINDOW / PUBLISH_WINDOW_HI)
  → post to the Facebook Page + Instagram as a Reel (designed cover, channel hashtag)
  → save the results in episodes/state.json, keep the MP4 as a run artifact for 14 days
```

Also: **category videos** on demand (comedy, quiz, … in `library/`, English or Hindi), **your own scripts** (`scripts/`, see `scripts/README.md`), and a **weekly long video** (16:9, Saturday 10:00 IST, from `long/`). All options are listed in `docs/CHANNELS_REFERENCE.md`.

If any step fails, nothing is uploaded. Setup instructions are in **`docs/SETUP.md`**.

## Contents

| Path | What it is |
|---|---|
| `episodes/` | 74 ready episodes (ep002–ep075, about 2.5 months; ep001 was removed), `TOPICS.md` and the format guide `README.md` |
| `pipeline/daily.py` | daily run: pick, render, QC, upload |
| `pipeline/tts.py`, `pipeline/cb_gen.py` | voices (Chatterbox / Kokoro) and lip-sync timing |
| `pipeline/episode_engine.py` | whiteboard scenes, acting, camera |
| `pipeline/char_line.py` | the characters |
| `pipeline/bg_line.py`, `pipeline/kit2d.py` | playroom, logo and helper bee |
| `pipeline/theatre.py` | the puppet theatre (back layer + curtains in front of the content) |
| `pipeline/finish.py` | captions, sound mix, MP4 |
| `pipeline/music.py` | a different original music track per episode (or your own tracks in `music/`) |
| `pipeline/thumbnail.py` | designed thumbnail for each video |
| `pipeline/upload_youtube.py` | YouTube upload (audience setting from `MADE_FOR_KIDS`) |
| `pipeline/meta_post.py`, `pipeline/hashtags.py` | Facebook + Instagram posting, hashtags per platform |
| `pipeline/script2episode.py` | turns your own script (`scripts/*.txt`) into an episode |
| `pipeline/validate_episode.py` | checks episode files before you push |
| `.github/workflows/curio-kids-short.yml` | the daily Shorts (twice-daily automatic runs + manual options) |
| `.github/workflows/curio-kids-long.yml` | the weekly long video |
| `.github/workflows/voice-lab.yml` | voice samples (Chatterbox / Turbo / Hindi) |
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

The main voices are Chatterbox clones of `assets/voices/mia.wav`, `leo.wav` and `dad.wav` (replace a file to change a character's voice). The settings below only affect the **Kokoro backup voices**. To change a backup voice for one episode, add for example `"voices": {"LEO": ["af_bella", 1.1, 3]}` to its `episode.json`. Other Kokoro voices: af_bella, af_nicole, af_sarah, af_nova, am_puck, am_liam, bf_emma, bm_george and more.
