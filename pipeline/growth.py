#!/usr/bin/env python3
"""Build a channel-specific, evidence-based content brief from a YouTube Analytics CSV."""
from __future__ import annotations
import argparse, csv, json
from pathlib import Path
import playlist_plan
import re
from difflib import SequenceMatcher

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



TITLE_STOPWORDS = {"why", "what", "how", "does", "do", "is", "are", "the", "a", "an", "your", "our",
                   "my", "for", "kids", "fun", "facts", "full", "video", "short", "explained", "guide",
                   "and", "with", "to", "of", "in", "on", "can", "you", "it", "from", "this", "that", "ai"}


def build_related_video_candidates(rows: list[dict], per_short: int = 2) -> list[dict]:
    """Suggest only reviewable Short-to-long matches; never edits YouTube Related Video settings."""
    shorts = [r for r in rows if str(r.get("content_type") or "").lower() == "short"]
    longs = [r for r in rows if str(r.get("content_type") or "").lower() == "long"]
    candidates = []
    for short in shorts:
        short_title = str(short.get("title") or "")
        short_words = set(re.findall(r"[a-z0-9]+", short_title.lower())) - TITLE_STOPWORDS
        short_topics = set(playlist_plan.classify_topics(short_title))
        matches = []
        for long in longs:
            long_title = str(long.get("title") or "")
            long_words = set(re.findall(r"[a-z0-9]+", long_title.lower())) - TITLE_STOPWORDS
            shared = sorted(short_words & long_words)
            long_topics = set(playlist_plan.classify_topics(long_title))
            shared_topics = sorted(short_topics & long_topics)
            similarity = SequenceMatcher(None, " ".join(sorted(short_words)), " ".join(sorted(long_words))).ratio()
            if not shared or not shared_topics or (len(shared) < 2 and similarity < 0.5):
                continue
            union = short_words | long_words
            jaccard = len(shared) / len(union) if union else 0.0
            score = 0.6 * jaccard + 0.4 * similarity + 0.1
            if score < 0.25:
                continue
            matches.append({
                "short_video_id": str(short.get("video_id") or ""),
                "short_title": short_title,
                "long_video_id": str(long.get("video_id") or ""),
                "long_title": long_title,
                "shared_terms": shared, "shared_topics": shared_topics, "title_similarity": round(similarity, 3),
                "match_score": round(score, 3), "review_status": "manual review",
            })
        matches.sort(key=lambda x: (-x["match_score"], x["long_video_id"]))
        candidates.extend(matches[:per_short])
    return candidates


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
    related_video_candidates = build_related_video_candidates(rows)
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
        "long_form_packaging": long_form_packaging, "related_video_candidates": related_video_candidates,
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
    lines += ["", "## Short-to-long Related Video candidates", "",
              "Review-only suggestions based on shared title terms and topic tags. Confirm the long-form video is genuinely the same lesson before adding a Related Video in YouTube Studio; nothing is changed automatically.", ""]
    if related_video_candidates:
        lines += ["| Short | Suggested long-form video | Shared terms | Shared topic | Match score | Review |",
                  "|---|---|---|---|---:|---|"]
        for item in related_video_candidates:
            lines.append(f"| {item['short_title'].replace('|','/')} ({item['short_video_id']}) | {item['long_title'].replace('|','/')} ({item['long_video_id']}) | {', '.join(item['shared_terms'])} | {', '.join(item['shared_topics'])} | {item['match_score']:.3f} | manual review |")
    else:
        lines.append("No sufficiently similar Short-to-long title pairs were found in the current report window.")
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
