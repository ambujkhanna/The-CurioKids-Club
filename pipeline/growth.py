#!/usr/bin/env python3
"""Build a channel-specific, evidence-based content brief from a YouTube Analytics CSV."""
from __future__ import annotations
import argparse, csv, json
from pathlib import Path

PROFILES = {
    "curiokids-club": {
        "name": "The CurioKids Club",
        "voice": "curious, warm, simple and playful; age-appropriate explanations",
        "content": [
            "Prioritise specific child-friendly 'Why…?' and 'How…?' questions; retain a clear curiosity gap.",
            "Open with the surprising question or visual payoff in the first spoken line; avoid greetings and long setup.",
            "Use one central science/nature/body fact per Short, concrete examples and a simple visual change every few seconds.",
            "Keep dialogue short and vocabulary accessible; finish with a satisfying answer or tiny experiment/prompt.",
        ],
        "avoid": "Do not copy an adult tech explainer format, use frightening claims, or sacrifice factual accuracy for a hook.",
    },
    "aination-studio": {
        "name": "AInation Studio",
        "voice": "practical, credible, direct and globally understandable; demonstrate rather than hype",
        "content": [
            "Prioritise practical AI safety, useful workflows and clear comparisons that solve a recognisable problem.",
            "Start with a concrete risk, outcome or before/after; avoid generic 'AI is changing everything' openings.",
            "Show one usable example or workflow, then explain the limitation or verification step.",
            "Use plain-English titles framed around a specific benefit, mistake or decision; avoid unsupported superlatives.",
        ],
        "avoid": "Do not present correlation as causation, imply AI is infallible, or treat low-sample metrics as a firm trend.",
    },
}

def read_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k in ("views", "engaged_views", "average_view_percentage", "average_view_duration",
                  "likes", "comments", "shares", "subscribers_gained", "subscribers_lost"):
            try: r[k] = float(r.get(k) or 0)
            except (TypeError, ValueError): r[k] = 0.0
        r["title"] = (r.get("title") or "").strip()
        r["content_type"] = (r.get("content_type") or "unknown").strip().lower()
    return rows

def build_brief(rows: list[dict], channel_key: str, period: str = "latest available report") -> tuple[dict, str]:
    # Accept raw CSV strings as well as already-normalised numeric rows (useful for tests and reuse).
    rows = [dict(r) for r in rows]
    for r in rows:
        for key in ("views", "engaged_views", "average_view_percentage", "average_view_duration", "likes", "comments", "shares", "subscribers_gained", "subscribers_lost"):
            try: r[key] = float(r.get(key) or 0)
            except (TypeError, ValueError): r[key] = 0.0
        r["content_type"] = str(r.get("content_type") or "unknown").lower()
        r["title"] = str(r.get("title") or "").strip()
    profile = PROFILES.get(channel_key, PROFILES["aination-studio"])
    shorts = [r for r in rows if r["content_type"] == "short" and r["views"] > 0]
    identified = [r for r in rows if r["content_type"] != "unknown"]
    total_views = sum(r["views"] for r in rows)
    total_engaged = sum(r["engaged_views"] for r in rows)
    top = sorted(shorts, key=lambda r: (r["engaged_views"], r["average_view_percentage"], r["views"]), reverse=True)
    high_retention = sorted([r for r in shorts if r["average_view_percentage"] > 0],
                            key=lambda r: r["average_view_percentage"], reverse=True)
    mapping_pct = round(100 * len(identified) / len(rows), 1) if rows else 0.0
    unmapped = sorted((r for r in rows if r["content_type"] == "unknown"),
                      key=lambda r: (r["views"], r.get("video_id", "")), reverse=True)
    unmapped_videos = [{
        "video_id": str(r.get("video_id") or ""), "views": int(r["views"]),
        "observed_title": str(r.get("title") or ""),
        "video_url": str(r.get("video_url") or ("https://www.youtube.com/watch?v=" + str(r.get("video_id") or ""))),
    } for r in unmapped]
    brief = {
        "channel_key": channel_key, "channel_name": profile["name"], "period": period,
        "video_rows": len(rows), "short_rows": len(shorts), "identified_rows": len(identified),
        "metadata_coverage_pct": mapping_pct, "unmapped_videos": unmapped_videos,
        "views": int(total_views), "engaged_views": int(total_engaged),
        "top_shorts": [{"title": r["title"] or r.get("video_id", "unknown video"),
                        "video_id": r.get("video_id", ""), "views": int(r["views"]),
                        "engaged_views": int(r["engaged_views"]),
                        "average_view_percentage": round(r["average_view_percentage"], 1),
                        "subscribers_gained": int(r["subscribers_gained"])} for r in top[:5]],
        "highest_average_viewed": [{"title": r["title"] or r.get("video_id", "unknown video"),
                                    "average_view_percentage": round(r["average_view_percentage"], 1),
                                    "views": int(r["views"])} for r in high_retention[:3]],
        "content_guidance": profile["content"], "voice": profile["voice"], "avoid": profile["avoid"],
    }
    lines = [f"# Growth brief — {profile['name']}", "", f"**Reporting period:** {period}", "",
             f"- Video rows: **{len(rows)}**; identified metadata: **{len(identified)} ({mapping_pct:.1f}%)**",
             f"- Views: **{int(total_views):,}**; engaged views: **{int(total_engaged):,}**",
             f"- Shorts with data: **{len(shorts)}**", "",
             "## Best Shorts by engaged views", ""]
    if top:
        lines += ["| Video | Views | Engaged views | Avg viewed | Subs gained |", "|---|---:|---:|---:|---:|"]
        for r in top[:5]:
            lines.append(f"| {(r['title'] or r.get('video_id','unknown')).replace('|','/')} | {int(r['views']):,} | {int(r['engaged_views']):,} | {r['average_view_percentage']:.1f}% | {int(r['subscribers_gained'])} |")
    else: lines.append("No identified Shorts are available; collect more data before ranking content.")
    lines += ["", "## Unmapped videos — review before topic analysis", ""]
    if unmapped_videos:
        lines += ["| Video ID | Views |", "|---|---:|"]
        for item in unmapped_videos:
            video_id = item["video_id"]
            url = item["video_url"]
            label = "[" + video_id + "](" + url + ")" if url else (video_id or "unknown ID")
            lines.append("| " + label + " | " + format(item["views"], ",") + " |")
        lines.append("")
        lines.append("These rows are deliberately not assigned to episodes automatically. Add a verified video ID to the relevant episode state only after checking the video.")
    else:
        lines.append("All report rows are mapped to known episode metadata.")
    lines += ["", "## Content guidance for the next scripts", ""] + [f"- {x}" for x in profile["content"]]
    lines += ["", "## Data-quality and interpretation checks", "",
              f"- Metadata coverage is **{mapping_pct:.1f}%**. Repair missing episode/video mappings before drawing topic-level conclusions." if rows and mapping_pct < 90 else "- Metadata mapping coverage is adequate for this report; continue checking unknown rows.",
              "- Rank Shorts using engaged views and average viewed together; do not rank solely by public views.",
              "- Compare videos with similar publication ages and formats. A 28-day aggregate is not a controlled experiment.",
              "- This report does not include impressions, click-through rate or audience-retention curves.",
              "- These are directional heuristics, not causal findings. Keep human editorial review and factual checks.",
              f"- Avoid: {profile['avoid']}", ""]
    return brief, "\n".join(lines)

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--csv", required=True); p.add_argument("--channel-key", required=True)
    p.add_argument("--period", default="latest available report"); p.add_argument("--output-dir", default="out/analytics")
    a = p.parse_args(argv)
    rows = read_rows(Path(a.csv)); data, md = build_brief(rows, a.channel_key, a.period)
    out = Path(a.output_dir); out.mkdir(parents=True, exist_ok=True)
    (out / "growth_brief.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "growth_brief.md").write_text(md, encoding="utf-8")
    print(f"Built growth brief from {len(rows)} video rows ({data['metadata_coverage_pct']}% metadata coverage).")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
