# Plan: automatic weekly picture run (GitHub → Kaggle GPU → GitHub)

**Status:** PLANNED (owner approved planning on 2026-11-21). Nothing in this file is built yet. Same file in both repos.
**Why:** HD pictures (backgrounds, picture boards, house icons, later short video clips) need a GPU. GitHub's free runners have none. Kaggle gives the owner 30 free GPU hours a week and has an official API, so GitHub can drive it with no clicking.

## 1. What is decided, and why

| Question | Decision | Reason |
|---|---|---|
| Generate inside GitHub Actions? | **No** | CPU only. FLUX takes many minutes, even hours, per picture. Smaller "turbo" models are worse and some limit commercial use. |
| Hugging Face API? | **No** | Only a tiny free allowance, then paid (against the free-only rule). |
| Public Hugging Face Spaces? | **No** | Small daily quotas, and they change or vanish: not reliable enough for a pipeline. |
| GitHub Actions → **Kaggle API** | **Yes** | Free GPU (T4), official API, runs while nobody is watching, and the output is kept. |
| Ollama | **Yes, for text only** | Runs free open models on the GitHub CPU to write picture prompts and choose boards/backgrounds. It **cannot** make images or video. |
| Video clips | **Later, as a pilot** | Wan 2.1 T2V 1.3B (Apache 2.0) on the Kaggle T4: 3–5 s at 480p, about 10–20 min per clip. Only where real motion helps. |

## 2. How it will run (one weekly cycle)

```
GitHub Actions (weekly-art.yml, e.g. Friday 22:00 UTC, + manual "Run workflow")
 1. art_queue.py      look at the next ~7 days of episodes (same order as daily.pick: "order" first, then folders)
                      -> list what is missing: background, picture-board pictures, house icons (emoji keys without a file)
 2. (optional) Ollama write a picture prompt for each missing item from the episode's lines (house style is added after)
 3. kaggle datasets version   upload the request list (art_requests.json) to a private Kaggle dataset
 4. kaggle kernels push       start the private Kaggle notebook (GPU + internet on) that reads the requests
 5. wait                      poll `kaggle kernels status` every 2 min (stop waiting after 5 h; the job limit is 6 h)
 6. kaggle kernels output     download the pictures + manifest
 7. auto-check                size, not black/blank, cut-out coverage, no text (tesseract OCR flags letters), corners clean
 8. install                   good ones -> assets/art/ or assets/icons_house/ + manifest.json; rejected -> run summary
 9. commit + push             same way as "Daily run: update episode state" (or open for review, see ART_AUTO_COMMIT)
```

If anything fails (Kaggle queue, quota, model download, check), the videos still render with the safe fallbacks: the drawn playroom, Fluent 3D icons, icon boards. The run summary says what was missing.

## 3. Pieces to build

| File | Job |
|---|---|
| `pipeline/art_queue.py` | Finds missing assets for the next N episodes; writes `art_requests.json` (name, kind, prompt, orientation, seeds) |
| `pipeline/art_prompts.py` | Optional Ollama step (`ollama run <model>` with a fixed instruction) → one-line object/scene descriptions; house style appended by code |
| `tools/kaggle/auto/kernel-metadata.json` | Kaggle notebook settings: `id` (owner/curio-art-auto), `enable_gpu: true`, `enable_internet: true`, `is_private: true`, `dataset_sources: [owner/curio-art-requests]`, `kernel_type: script` |
| `tools/kaggle/auto/art_auto.py` | The Kaggle script: reads the requests, loads FLUX.1-schnell 4-bit (same code as `art_v2.ipynb` / `icons_v1.ipynb`), makes the pictures, cuts icons out with rembg, writes a manifest |
| `pipeline/art_install.py` | Checks the downloaded pictures and installs the good ones (JPEG q90 for pictures, 512 px PNG for icons) |
| `.github/workflows/weekly-art.yml` | Runs the steps above |
| `pipeline/icons3d.py` (change) | Looks for icons in this order: `assets/icons_house/<key>.png` → Fluent 3D → flat (`ICON_STYLE=house\|3d\|flat`) |

## 4. One-time setup by the owner

1. **Kaggle API token:** kaggle.com → Settings → API → **Create New Token** (downloads `kaggle.json`). Put its two values in **GitHub → repo → Settings → Secrets and variables → Actions** as `KAGGLE_USERNAME` and `KAGGLE_KEY`. Never paste them in chat.
2. **Hugging Face token on Kaggle:** already stored as the Kaggle secret `HF_TOKEN`. After the first API push of the notebook, open it once in Kaggle → Add-ons → Secrets → tick `HF_TOKEN` for it. Kaggle keeps that attachment for later versions; this is the first thing the pilot must confirm.
3. Phone-verified Kaggle account (already done).

## 5. Repo variables (planned)

| Variable | Default | Meaning |
|---|---|---|
| `ART_WEEKLY` | `off` until the pilot passes | Turns the weekly run on |
| `ART_AUTO_COMMIT` | `off` (review first) | `on` = good pictures are committed automatically; `off` = they are uploaded as a run artifact + summary for the owner to approve |
| `ART_DAYS` | `7` | How many upcoming days of episodes to prepare |
| `ART_OLLAMA` | `off` | `on` = Ollama writes the prompts; `off` = prompt templates by kind/topic |
| `OLLAMA_MODEL` | `qwen2.5:7b` | Any Apache-2.0 model (e.g. `qwen2.5:7b`, `mistral:7b`) |

## 6. Limits and risks (honest)

- **Kaggle queue:** a run can wait from minutes to hours for a GPU. That's fine for a weekly job that prepares a week ahead.
- **Quota:** 30 GPU h/week per account. A typical week (≈7 backgrounds/close-ups + ≈20 icons) ≈ 30–60 min.
- **Model access:** FLUX.1-schnell needs the HF token (step 4.2). If Kaggle ever drops secret attachments for API pushes, the fallback is to run that week by hand with the notebooks in `tools/kaggle/`.
- **Quality:** AI pictures can contain odd details or made-up letters. The OCR and the size/blank checks catch most problems; `ART_AUTO_COMMIT=off` keeps a human look before anything goes live.
- **API changes:** the Kaggle CLI (`kaggle` pip package) is official but can change. Pin its version in the workflow.
- **Licences:** FLUX.1-schnell Apache 2.0, rembg MIT, Wan 2.1 Apache 2.0, Ollama MIT, plus the chosen model's own licence (pick Apache 2.0). Every asset records model, seed, prompt and date in its manifest.

## 7. Phases

1. **Now:** icons_v1 by hand (running) → `icons3d` lookup order house → Fluent → flat → owner approves side-by-side boards.
2. **Pilot of the weekly run:** build the pieces above; run it by hand (`Run workflow`) with `ART_AUTO_COMMIT=off`; confirm the HF secret works on API pushes; check queue time and output.
3. **Switch on:** `ART_WEEKLY=on`. After a few good weeks, optionally `ART_AUTO_COMMIT=on`.
4. **Ollama prompts:** `ART_OLLAMA=on` after comparing its prompts with the templates on 10 episodes.
5. **Video pilot:** 5 clips with Wan 2.1 1.3B (water drop falling, seed sprouting, planet turning, waves, a robot arm for AInation). If they look good: a `clip` board type that plays a short clip inside the card.
