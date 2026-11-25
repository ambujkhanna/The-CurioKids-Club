#!/usr/bin/env python3
"""Build a review-only topic + language playlist assignment from published episode state.

This script never calls YouTube's write API and never creates playlists or changes video metadata.
Run: python pipeline/playlist_plan.py [--output-dir out/analytics]
"""
from __future__ import annotations
import argparse, csv, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import analytics

KIDS = (ROOT / "library").exists() or "curio" in ROOT.name.lower()

if KIDS:
    TOPICS = {
        "Space & Universe": {"space", "moon", "sun", "star", "planet", "mars", "galaxy", "astronaut", "rocket", "eclipse", "comet", "earth"},
        "Nature & Plants": {"plant", "plants", "tree", "trees", "seed", "seeds", "leaf", "leaves", "flower", "flowers", "soil", "garden", "photosynthesis"},
        "Animals": {"animal", "animals", "cat", "cats", "dog", "dogs", "bee", "bees", "bird", "birds", "fish", "whale", "shark", "dinosaur", "butterfly", "frog", "elephant", "lion"},
        "Human Body": {"body", "brain", "heart", "blood", "bone", "bones", "teeth", "tooth", "eye", "eyes", "ear", "ears", "skin", "muscle", "sleep", "stomach", "lungs"},
        "Everyday Science & Discoveries": {"science", "magnet", "magnets", "shadow", "shadows", "light", "sound", "water", "rain", "rainbow", "cloud", "clouds", "gravity", "energy", "electricity", "experiment", "experiments", "metal", "ice"},
    }
    LANGUAGE = {"default": "English", "hi": "Hindi", "es": "Spanish"}
else:
    TOPICS = {
        "AI Explained": {"ai", "artificial", "intelligence", "llm", "llms", "gpt", "model", "models", "token", "tokens", "embedding", "embeddings", "context", "prompt", "prompts"},
        "AI Tools & Workflows": {"chatgpt", "gemini", "claude", "copilot", "ollama", "tool", "tools", "workflow", "workflows", "automation", "agent", "agents", "mcp"},
        "AI Coding & Building": {"code", "coding", "developer", "development", "api", "build", "building", "app", "apps", "programming", "rag"},
        "AI Creativity": {"image", "images", "video", "videos", "creative", "creativity", "music", "design", "generation", "sora"},
        "AI in Everyday Life": {"everyday", "life", "use", "using", "work", "productivity", "personal"},
        "AI Safety, Privacy & Verification": {"safety", "safe", "privacy", "security", "verify", "verification", "hallucination", "hallucinations", "deepfake", "deepfakes", "guardrails", "risk"},
    }
    LANGUAGE = {"default": "English", "en": "English", "hi": "Hindi", "es": "Spanish", "trend": "English", "script": "English"}

def assignments(meta: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    out = []
    for video_id, item in sorted(meta.items()):
        title = item.get("title", "").strip()
        words = set(__import__("re").findall(r"[a-z0-9]+", title.lower()))
        matched = [name for name, terms in TOPICS.items() if words & terms]
        language = LANGUAGE.get(item.get("language", "default"))
        playlists = matched[:]
        if language:
            playlists.append(language)
        if not matched:
            playlists.append("Needs manual topic review")
        for playlist in playlists:
            out.append({
                "video_id": video_id, "title": title, "language": language or "Unknown",
                "episode_id": item.get("episode_id", ""), "content_type": item.get("content_type", "unknown"),
                "playlist": playlist, "review_status": "manual review" if playlist == "Needs manual topic review" else "suggested",
                "video_url": item.get("video_url", ""),
            })
    return out

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir", default=str(ROOT / "out" / "analytics"))
    args = p.parse_args(argv)
    rows = assignments(analytics.metadata_from_state(ROOT))
    out = Path(args.output_dir); out.mkdir(parents=True, exist_ok=True)
    csv_path = out / "playlist_plan.csv"
    fields = ["video_id", "title", "language", "episode_id", "content_type", "playlist", "review_status", "video_url"]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader(); writer.writerows(rows)
    md = ["# Playlist assignment plan", "", "Review-only suggestions generated from published episode state. A video may appear in multiple playlists: one topic playlist plus one language playlist. No YouTube playlist or video metadata is changed.", ""]
    if rows:
        md += ["| Video | Language | Playlist | Review |", "|---|---|---|---|"]
        for r in rows:
            label = r["title"].replace("|", "/") or r["video_id"]
            url = r["video_url"] or ("https://www.youtube.com/watch?v=" + r["video_id"])
            md.append(f"| [{label}]({url}) | {r['language']} | {r['playlist']} | {r['review_status']} |")
    else:
        md.append("No published video IDs were found in the local episode state files.")
    (out / "playlist_plan.md").write_text("\\n".join(md) + "\\n", encoding="utf-8")
    print(f"Wrote {len(rows)} playlist assignments to {csv_path} (review only).")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
