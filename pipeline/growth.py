#!/usr/bin/env python3
"""Build a channel-specific, evidence-based content brief from a YouTube Analytics CSV."""
from __future__ import annotations
import argparse, csv, json
from pathlib import Path
import playlist_plan

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


def aggregate_topic_performance(rows: list[dict]) -> tuple[list[dict], list[str]]:
    """Aggregate non-exclusive topic matches; unmatched titles stay in a manual-review list."""
    buckets = {}
    unmatched = []
    for row in rows:
        topics = playlist_plan.classify_topics(str(row.get("title") or ""))
        if not topics:
            if row.get("video_id"):
                unmatched.append(str(row["video_id"]))
            continue
        for topic in topics:
            key = (topic, str(row.get("content_type") or "unknown").lower())
            item = buckets.setdefault(key, {
                "topic": topic, "content_type": key[1], "video_ids": set(),
                "views": 0.0, "engaged_views": 0.0, "viewed_x_views": 0.0,
                "subscribers_gained": 0.0,
            })
            item["video_ids"].add(str(row.get("video_id") or row.get("title") or ""))
            views = float(row.get("views") or 0)
            item["views"] += views
            item["engaged_views"] += float(row.get("engaged_views") or 0)
            item["viewed_x_views"] += float(row.get("average_view_percentage") or 0) * views
            item["subscribers_gained"] += float(row.get("subscribers_gained") or 0)
    result = []
    for item in buckets.values():
        views = item["views"]
        result.append({
            "topic": item["topic"], "content_type": item["content_type"],
            "video_count": len(item["video_ids"]), "views": int(views),
            "engaged_views": int(item["engaged_views"]),
            "engaged_view_rate_pct": round(100 * item["engaged_views"] / views, 1) if views else 0.0,
            "average_view_percentage": round(item["viewed_x_views"] / views, 1) if views else 0.0,
            "subscribers_gained": int(item["subscribers_gained"]),
            "subscribers_per_1k_views": round(1000 * item["subscribers_gained"] / views, 2) if views else 0.0,
        })
    result.sort(key=lambda x: (x["content_type"], -x["engaged_views"], -x["views"]))
    return result, sorted(set(unmatched))


def number_or_zero(value) -> float:
    try: return float(value or 0)
    except (TypeError, ValueError): return 0.0


def read_reach_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    out = []
    for row in rows:
        try:
            out.append({"video_id": str(row.get("video_id") or ""),
                        "impressions": int(float(row.get("impressions") or 0)),
                        "impressions_ctr": float(row.get("impressions_ctr") or 0)})
        except (TypeError, ValueError):
            continue
    return out


def build_brief(rows: list[dict], channel_key: str, period: str = "latest available report", reach_rows: list[dict] | None = None) -> tuple[dict, str]:
    # Accept raw CSV strings as well as already-normalised numeric rows (useful for tests and reuse).
    rows = [dict(r) for r in rows]
    for r in rows:
        for key in ("views", "engaged_views", "average_view_percentage", "average_view_duration", "likes", "comments", "shares", "subscribers_gained", "subscribers_lost"):
            try: r[key] = float(r.get(key) or 0)
            except (TypeError, ValueError): r[key] = 0.0
        r["content_type"] = str(r.get("content_type") or "unknown").lower()
        r["title"] = str(r.get("title") or "").strip()
    profile = PROFILES.get(channel_key, PROFILES["aination-studio"])
    topic_performance, unclassified_topics = aggregate_topic_performance(rows)
    reach_map = {str(x.get("video_id") or ""): x for x in (reach_rows or []) if x.get("video_id")}
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
    long_form_packaging = []
    for row in rows:
        if row["content_type"] != "long":
            continue
        reach = reach_map.get(str(row.get("video_id") or ""), {})
        if number_or_zero(reach.get("impressions")) > 0:
            long_form_packaging.append({
                "video_id": str(row.get("video_id") or ""), "title": row["title"],
                "views": int(row["views"]), "impressions": int(number_or_zero(reach.get("impressions"))),
                "impressions_ctr_pct": round(number_or_zero(reach.get("impressions_ctr")) * 100, 2),
                "average_view_percentage": round(row["average_view_percentage"], 1),
                "subscribers_gained": int(row["subscribers_gained"]),
            })
    long_form_packaging.sort(key=lambda x: x["impressions"], reverse=True)
    brief = {
        "channel_key": channel_key, "channel_name": profile["name"], "period": period,
        "video_rows": len(rows), "short_rows": len(shorts), "identified_rows": len(identified),
        "metadata_coverage_pct": mapping_pct, "unmapped_videos": unmapped_videos,
        "topic_performance": topic_performance, "unclassified_topic_video_ids": unclassified_topics,
        "long_form_packaging": long_form_packaging,
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
    lines += ["", "## Topic performance (non-exclusive title matching)", "",
              "Videos may match more than one topic. Treat small samples as directional; unmatched titles remain manual review.", ""]
    if topic_performance:
        lines += ["| Topic | Format | Videos | Views | Engaged views | Engaged rate | Avg viewed | Subs/1k views |",
                  "|---|---|---:|---:|---:|---:|---:|---:|"]
        for item in topic_performance:
            lines.append(f"| {item['topic']} | {item['content_type']} | {item['video_count']} | {item['views']:,} | {item['engaged_views']:,} | {item['engaged_view_rate_pct']}% | {item['average_view_percentage']}% | {item['subscribers_per_1k_views']} |")
    else:
        lines.append("No titles matched the configured topic taxonomy.")
    if unclassified_topics:
        lines += ["", f"Titles needing manual topic classification: {len(unclassified_topics)}."]
    lines += ["", "## Long-form thumbnail reach", ""]
    if long_form_packaging:
        lines += ["| Video | Impressions | CTR | Views | Avg viewed |", "|---|---:|---:|---:|---:|"]
        for item in long_form_packaging:
            lines.append(f"| {item['title'].replace('|','/')} | {item['impressions']:,} | {item['impressions_ctr_pct']}% | {item['views']:,} | {item['average_view_percentage']}% |")
    else:
        lines.append("No Reach Basic thumbnail-impression rows are available yet; enable the YouTube Reporting API to populate this section.")
    lines += ["", "## Content guidance for the next scripts", ""] + [f"- {x}" for x in profile["content"]]
    lines += ["", "## Data-quality and interpretation checks", "",
              f"- Metadata coverage is **{mapping_pct:.1f}%**. Repair missing episode/video mappings before drawing topic-level conclusions." if rows and mapping_pct < 90 else "- Metadata mapping coverage is adequate for this report; continue checking unknown rows.",
              "- Rank Shorts using engaged views and average viewed together; do not rank solely by public views.",
              "- Compare videos with similar publication ages and formats. A 28-day aggregate is not a controlled experiment.",
              "- Shorts-feed swipe behaviour is not inferred from thumbnail CTR; use the dedicated Stayed-to-watch metric when available.",
              "- These are directional heuristics, not causal findings. Keep human editorial review and factual checks.",
              f"- Avoid: {profile['avoid']}", ""]
    return brief, "\n".join(lines)

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--csv", required=True); p.add_argument("--channel-key", required=True)
    p.add_argument("--period", default="latest available report"); p.add_argument("--output-dir", default="out/analytics")
    p.add_argument("--reach-csv", default="out/analytics/reach_by_video.csv")
    a = p.parse_args(argv)
    rows = read_rows(Path(a.csv)); reach_rows = read_reach_rows(Path(a.reach_csv))
    data, md = build_brief(rows, a.channel_key, a.period, reach_rows)
    out = Path(a.output_dir); out.mkdir(parents=True, exist_ok=True)
    (out / "growth_brief.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    aud = out / "audience_countries.md"  # analytics.py's country section (2026-11-23): shown with the brief in every daily run
    if aud.exists(): md = md.rstrip("\n") + "\n\n" + aud.read_text(encoding="utf-8")
    (out / "growth_brief.md").write_text(md, encoding="utf-8")
    print(f"Built growth brief from {len(rows)} video rows ({data['metadata_coverage_pct']}% metadata coverage).")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
