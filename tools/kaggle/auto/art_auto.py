# Weekly art run, step 2 (roadmap R7, built 2026-11-23): runs ON KAGGLE as a script kernel, pushed by .github/workflows/weekly-art.yml.
# Same model and settings as the hand-run notebooks in tools/kaggle/ (FLUX.1-schnell 4-bit, Apache 2.0; rembg cut-outs, MIT).
# Input : /kaggle/input/<dataset>/art_requests.json  (written by pipeline/art_queue.py)
# Output: /kaggle/working/art_auto/{icons,art}/... + manifest.json (+ art_auto.zip); the workflow downloads it.
# One-time owner step: open this kernel on Kaggle once -> Add-ons -> Secrets -> tick HF_TOKEN (Kaggle keeps it for later versions).
import glob, json, os, subprocess, sys, time, datetime

OUT = "/kaggle/working/art_auto"
os.makedirs(OUT, exist_ok=True)


def status(msg, ok=True):
    print(msg, flush=True)
    json.dump({"ok": ok, "message": msg, "time": datetime.datetime.utcnow().isoformat()}, open(os.path.join(OUT, "status.json"), "w"))


req_files = glob.glob("/kaggle/input/**/art_requests.json", recursive=True)
if not req_files:
    status("no art_requests.json in the input dataset", False); sys.exit(0)
REQ = json.load(open(req_files[0], encoding="utf-8"))
reqs = REQ.get("requests", [])
print(len(reqs), "request(s) for", REQ.get("channel"))
if not reqs:
    status("nothing to make"); sys.exit(0)

# 1) libraries (Kaggle's own numpy is kept: a newer numpy breaks the model loader)
import numpy
NP = numpy.__version__
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "diffusers>=0.32", "transformers>=4.46", "accelerate",
                "bitsandbytes", "sentencepiece", f"numpy=={NP}"], check=True)
if any(r["kind"] == "icon" for r in reqs):
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "rembg>=2.0.50", "pymatting", "onnxruntime", f"numpy=={NP}"], check=True)

import torch
if not torch.cuda.is_available():
    status("no GPU: the kernel must run with a GPU (enable_gpu in kernel-metadata.json)", False); sys.exit(0)
DTYPE = torch.bfloat16 if torch.cuda.get_device_capability(0)[0] >= 8 else torch.float16

# 2) model (needs the HF_TOKEN Kaggle secret attached to this kernel)
try:
    from kaggle_secrets import UserSecretsClient
    os.environ["HF_TOKEN"] = UserSecretsClient().get_secret("HF_TOKEN")
except Exception:
    status("HF_TOKEN secret not attached: open this kernel on kaggle.com -> Add-ons -> Secrets -> tick HF_TOKEN, then run the workflow again", False)
    sys.exit(0)
import gc
from diffusers import FluxPipeline, FluxTransformer2DModel, BitsAndBytesConfig as DiffBnb
from transformers import T5EncoderModel, BitsAndBytesConfig as TfBnb
MODEL = "black-forest-labs/FLUX.1-schnell"
q = dict(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=DTYPE)
transformer = FluxTransformer2DModel.from_pretrained(MODEL, subfolder="transformer", quantization_config=DiffBnb(**q), torch_dtype=DTYPE)
text_encoder_2 = T5EncoderModel.from_pretrained(MODEL, subfolder="text_encoder_2", quantization_config=TfBnb(**q), torch_dtype=DTYPE)
pipe = FluxPipeline.from_pretrained(MODEL, transformer=transformer, text_encoder_2=text_encoder_2, torch_dtype=DTYPE)
pipe.enable_model_cpu_offload(); pipe.vae.enable_tiling()
gc.collect(); torch.cuda.empty_cache()
print("model ready", flush=True)

import numpy as np
from PIL import Image
RB = None
if any(r["kind"] == "icon" for r in reqs):
    from rembg import new_session, remove
    try: RB = new_session("isnet-general-use")
    except Exception: RB = new_session("u2net")


def cutout(img):
    rgba = remove(img, session=RB, post_process_mask=True)
    a = np.asarray(rgba)[:, :, 3]; ys, xs = np.where(a > 10)
    if len(xs) == 0: return None
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    side = int(max(x1 - x0, y1 - y0) * 1.08) + 2
    sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    sq.paste(rgba.crop((x0, y0, x1 + 1, y1 + 1)), ((side - (x1 - x0)) // 2, (side - (y1 - y0)) // 2))
    return sq.resize((512, 512), Image.LANCZOS)


manifest, t0 = [], time.time()
for i, r in enumerate(reqs, 1):
    for seed in (7, 21):  # two versions; the installer keeps the best one
        g = torch.Generator("cpu").manual_seed(seed)
        try:
            if r["kind"] == "icon":
                img = pipe(r["prompt"], width=768, height=768, num_inference_steps=4, guidance_scale=0.0, max_sequence_length=256, generator=g).images[0]
                cut = cutout(img)
                if cut is None: continue
                fn = f"icons/{r['key']}_s{seed}.png"; os.makedirs(os.path.join(OUT, "icons"), exist_ok=True)
                cut.save(os.path.join(OUT, fn))
            else:
                img = pipe(r["prompt"], width=1536, height=864, num_inference_steps=4, guidance_scale=0.0, max_sequence_length=256, generator=g).images[0]
                fn = f"art/{r['key']}_s{seed}.jpg"; os.makedirs(os.path.join(OUT, "art"), exist_ok=True)
                img.resize((1920, 1080), Image.LANCZOS).save(os.path.join(OUT, fn), quality=92)
            manifest.append({"file": fn, "kind": r["kind"], "key": r["key"], "seed": seed, "prompt": r["prompt"], "why": r.get("why", ""),
                             "model": MODEL, "steps": 4, "licence": "Apache-2.0 (FLUX.1-schnell)" + ("; cut-out rembg (MIT)" if r["kind"] == "icon" else ""),
                             "date": datetime.date.today().isoformat()})
            print(f"[{i}/{len(reqs)}] {fn}", flush=True)
        except Exception as e:
            print("failed:", r["key"], seed, str(e)[:120], flush=True)
json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"), indent=1)
import shutil
shutil.make_archive("/kaggle/working/art_auto", "zip", OUT)
status(f"made {len(manifest)} file(s) for {len(reqs)} request(s) in {(time.time() - t0) / 60:.0f} min")
