"""Real science illustrations from Bioicons (https://bioicons.com, GitHub duerrsimon/bioicons).

In an episode, any "icon" can be  "img:<Category>/<Author>/<name>"  e.g.  "img:Human_physiology/Servier/heart-valves".
The full list of usable pictures is in assets/IMAGE_INDEX.txt (only free-for-commercial-use licences:
CC0, CC BY 3.0, CC BY 4.0, MIT, BSD; share-alike ones are excluded).

- resolve(name)        -> local SVG path in assets/img/ (or None)
- fetch(names)         -> downloads missing ones from GitHub (git sparse checkout), used by the daily run
- credits(episode)     -> the attribution lines that CC BY requires, added to the YouTube description
    python pipeline/images.py episodes/*/episode.json      # fetch every picture the episodes use
"""
import glob, json, os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "assets", "img")
LICENSES = ("cc-0", "cc-by-3.0", "cc-by-4.0", "mit", "bsd")
LIC_TEXT = {"cc-0": "CC0", "cc-by-3.0": "CC BY 3.0", "cc-by-4.0": "CC BY 4.0", "mit": "MIT", "bsd": "BSD"}
AUTHOR_URL = {"Servier": "https://smart.servier.com/"}
REPO = "https://github.com/duerrsimon/bioicons.git"


# real organ drawings used inside the animated "body" diagram (emoji are only a fallback)
BODY_IMG = {"heart": "img:Human_physiology/Servier/heart-front", "lungs": "img:Human_physiology/Servier/healthy-lung",
            "brain": "img:Human_physiology/Servier/brain-1", "stomach": "img:Human_physiology/Servier/stomach",
            "eyes": "img:Human_physiology/Servier/eye", "ears": "img:Human_physiology/Servier/ear",
            "muscles": "img:Human_physiology/Servier/muscle-1"}


def _rel(name):
    return name[4:] if name.startswith("img:") else name


def resolve(name):
    rel = _rel(name)
    for lic in LICENSES:
        p = os.path.join(IMG, lic, rel + ".svg")
        if os.path.exists(p):
            return p
    return None


def used(ep):
    out = []
    def walk(o):
        if isinstance(o, dict):
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
        elif isinstance(o, str) and o.startswith("img:"):
            out.append(o)
    walk(ep.get("lines", [])); walk(ep.get("loop_card", {}))
    for l in ep.get("lines", []):
        bd = l.get("board") or {}
        if bd.get("type") == "body":
            out += [BODY_IMG[n] for n in bd.get("show", []) if n in BODY_IMG]
    return sorted(set(out))


def fetch(names):
    missing = [n for n in names if not resolve(n)]
    if not missing:
        return []
    tmp = tempfile.mkdtemp()
    try:
        subprocess.run(["git", "clone", "-q", "--depth", "1", "--filter=blob:none", "--sparse", REPO, tmp], check=True)
        pats = [f"/static/icons/{lic}/{_rel(n)}.svg" for n in missing for lic in LICENSES]
        subprocess.run(["git", "-C", tmp, "sparse-checkout", "set", "--no-cone", *pats], check=True)
        got = []
        for n in missing:
            for lic in LICENSES:
                src = os.path.join(tmp, "static", "icons", lic, _rel(n) + ".svg")
                if os.path.exists(src):
                    dst = os.path.join(IMG, lic, _rel(n) + ".svg"); os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy(src, dst); got.append(n); break
        return got
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def credits(ep):
    lines = []
    for n in used(ep):
        p = resolve(n)
        if not p: continue
        lic = os.path.relpath(p, IMG).split(os.sep)[0]
        parts = _rel(n).split("/"); author = parts[-2] if len(parts) >= 2 else "unknown"; icon = parts[-1]
        url = AUTHOR_URL.get(author, "")
        lines.append(f"{icon} icon by {author.replace('_', ' ')}{' ' + url if url else ''} ({LIC_TEXT[lic]}) via bioicons.com")
    return ("Illustrations: " + "; ".join(lines)) if lines else ""


if __name__ == "__main__":
    names = set()
    for f in sys.argv[1:]:
        names |= set(used(json.load(open(f, encoding="utf-8"))))
    got = fetch(sorted(names))
    print(f"{len(names)} pictures used, {len(got)} downloaded, missing: {[n for n in sorted(names) if not resolve(n)]}")
