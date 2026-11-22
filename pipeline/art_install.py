"""Weekly art run, step 3 (roadmap R7, built 2026-11-23): check the pictures Kaggle made and install the good ones.
Same file in both repos.

    python pipeline/art_install.py out/kaggle_out        # folder with manifest.json (+ icons/, art/), or art_auto.zip in it

Checks per file: opens, right size, not blank/black, icons: the cut-out covers 8-90 % of the square (not empty, not a box).
Of the two versions (seeds) the one with the best score is kept:
  icons    -> assets/icons_house/<key>.webp (512 px) + an entry in assets/icons_house/manifest.json
  pictures -> assets/art/<key>_landscape.jpg (1920x1080, JPEG q90) + an entry in assets/art/manifest.json
Writes a Markdown summary (GITHUB_STEP_SUMMARY) and out/art_install.json. Never deletes or overwrites an existing asset.
"""
import glob, json, os, sys, zipfile
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)


def score(path, kind):
    """(ok, score, reason)"""
    try:
        im = Image.open(path)
    except Exception as e:
        return False, 0, f"can't open ({e})"
    if kind == "icon":
        if im.size != (512, 512) or im.mode != "RGBA": return False, 0, f"unexpected {im.size} {im.mode}"
        a = np.asarray(im)[:, :, 3] > 20; cov = a.mean()
        if not 0.08 <= cov <= 0.9: return False, 0, f"cut-out covers {cov:.0%} (empty or a box)"
        rgb = np.asarray(im.convert("RGB"))[a]
        if rgb.size == 0 or rgb.std() < 8: return False, 0, "flat colour"
        return True, float(rgb.std()) * (1 - abs(cov - 0.45)), f"coverage {cov:.0%}"
    rgb = np.asarray(im.convert("RGB")).astype(float)
    if im.size[0] < 1280: return False, 0, f"too small {im.size}"
    if rgb.mean() < 12 or rgb.mean() > 245: return False, 0, "blank (too dark or too bright)"
    if rgb.std() < 18: return False, 0, "almost one colour"
    return True, float(rgb.std()), "ok"


def install(src):
    zips = glob.glob(os.path.join(src, "**", "*.zip"), recursive=True)
    for z in zips:
        zipfile.ZipFile(z).extractall(os.path.join(src, "unzipped"))
    mans = glob.glob(os.path.join(src, "**", "manifest.json"), recursive=True)
    st = glob.glob(os.path.join(src, "**", "status.json"), recursive=True)
    status = json.load(open(st[0])) if st else {}
    if not mans:
        return {"status": status, "installed": [], "rejected": [], "note": "no manifest (nothing made)"}
    man = json.load(open(mans[0])); base = os.path.dirname(mans[0])
    best = {}
    rejected = []
    for m in man:
        p = os.path.join(base, m["file"])
        ok, sc, why = score(p, m["kind"])
        if not ok: rejected.append({"file": m["file"], "why": why}); continue
        if m["key"] not in best or sc > best[m["key"]][0]: best[m["key"]] = (sc, p, m)
    installed = []
    for key, (sc, p, m) in best.items():
        if m["kind"] == "icon":
            dst = os.path.join(ROOT, "assets", "icons_house", key + ".webp"); manp = os.path.join(ROOT, "assets", "icons_house", "manifest.json")
            if os.path.exists(dst): rejected.append({"file": m["file"], "why": "already have this icon"}); continue
            Image.open(p).save(dst, "WEBP", quality=90, method=6)
            try:
                mj = json.load(open(manp, encoding="utf-8"))
            except Exception:
                mj = {"icons": []}
            entry = {"key": key, "file": os.path.basename(dst), "prompt": m["prompt"], "seed": m["seed"], "model": m["model"],
                     "licence": m["licence"], "date": m["date"], "source": "weekly art run"}
            if isinstance(mj.get("icons"), list): mj["icons"].append(entry)
            elif isinstance(mj.get("icons"), dict): mj["icons"][key] = entry
            json.dump(mj, open(manp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        else:
            dst = os.path.join(ROOT, "assets", "art", f"{key}_landscape.jpg"); manp = os.path.join(ROOT, "assets", "art", "manifest.json")
            if os.path.exists(dst): rejected.append({"file": m["file"], "why": "already have this picture"}); continue
            Image.open(p).convert("RGB").resize((1920, 1080), Image.LANCZOS).save(dst, quality=90, optimize=True)
            try:
                mj = json.load(open(manp, encoding="utf-8"))
            except Exception:
                mj = []
            entry = {"file": os.path.basename(dst), "name": key, "prompt": m["prompt"], "seed": m["seed"], "model": m["model"],
                     "licence": m["licence"], "date": m["date"], "source": "weekly art run"}
            if isinstance(mj, list): mj.append(entry)
            elif isinstance(mj, dict): mj.setdefault("pictures", []).append(entry)
            json.dump(mj, open(manp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        installed.append({"key": key, "kind": m["kind"], "file": os.path.relpath(dst, ROOT), "why": m.get("why", "")})
    return {"status": status, "installed": installed, "rejected": rejected}


def markdown(res):
    md = ["### 🎨 Weekly art run", ""]
    if res.get("status"): md.append(f"- Kaggle: {res['status'].get('message', '')}")
    md.append(f"- Installed: **{len(res['installed'])}**, rejected: {len(res['rejected'])}")
    md += [f"  - ✅ `{i['file']}` ({i['why']})" for i in res["installed"]]
    md += [f"  - ❌ `{r['file']}`: {r['why']}" for r in res["rejected"]]
    if res.get("note"): md.append(f"- {res['note']}")
    return "\n".join(md) + "\n"


if __name__ == "__main__":
    res = install(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "out", "kaggle_out"))
    os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
    json.dump(res, open(os.path.join(ROOT, "out", "art_install.json"), "w"), indent=1)
    md = markdown(res); print(md)
    if os.environ.get("GITHUB_STEP_SUMMARY"): open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8").write(md)
    if os.environ.get("GITHUB_OUTPUT"): open(os.environ["GITHUB_OUTPUT"], "a").write(f"installed={len(res['installed'])}\n")
