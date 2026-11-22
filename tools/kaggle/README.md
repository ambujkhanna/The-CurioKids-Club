# Kaggle notebooks for HD pictures (free GPU)

- `art_v2.ipynb`: the notebook that made the pictures in `assets/art/` (kids only). It has 12 kept picks from v1, 7 backgrounds and 7 picture-board close-ups. Model: FLUX.1-schnell (Apache 2.0).
- `art_pilot_v1.ipynb`: the first pilot (both channels; its AInation pictures were not used).
- `icons_v1.ipynb`: 165 realistic 3D house icons for both channels (276 pictures, about 2 h; background removed with rembg). It keeps Kaggle's numpy version (a newer numpy broke the model loader: if you see a numpy `_slice` error, stop the session with the power button and start a fresh one). Run it with **Save Version → Save & Run All** so the output is kept.
- The plan to run these automatically every week from GitHub: `docs/AUTOMATION_KAGGLE.md`.

## How to run (owner, about 1 hour, free)

1. Kaggle account, phone-verified (needed for internet and the GPU).
2. **One time:** a free Hugging Face account. Accept the licence on the FLUX.1-schnell model page, then create a **Read** token and add it in the notebook under Add-ons → Secrets as `HF_TOKEN`. Keep the token only there.
3. Kaggle → Create → Notebook → File → Import Notebook → pick the `.ipynb`.
4. Session options: **GPU T4 x2**, Internet **On** (not P100).
5. Start session → **Run All**, and keep the tab open.
6. When the contact sheet shows, **download the zip from Output first**. Stopping the session deletes the files.
7. Give the zip to the assistant: it checks every picture, including the corners at full size, picks the best and adds them to `assets/art/` + `manifest.json`.

## To make new pictures

- Edit the `PICTURES` list in cell 3. Use the `CLAY` style for new ones, keep "no people, no text", and use 2 seeds each.
- The same prompt and seed always give the same picture.
- The pink "CLIP … truncated" notes in the log are harmless.
- `art_kids_v3.ipynb` / `art_v3_both.ipynb`: kids 3D picture boards (+ AInation key visuals in the merged one). The merged notebook runs both channels at once (model loads once, about 50 min).
