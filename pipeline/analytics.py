#!/usr/bin/env python3
"""Read-only per-video YouTube Analytics collector. Requires a separate youtube.readonly refresh token."""
from __future__ import annotations
import argparse, csv, datetime as dt, json, os, sqlite3, sys
from pathlib import Path
from typing import Any

SCOPE = "https://www.googleapis.com/auth/yt-analytics.readonly"
METRICS = "views,engagedViews,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,likes,comments,shares,subscribersGained,subscribersLost"
PAGE_SIZE = 200
ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = ROOT / "out" / "analytics"

def default_period(today: dt.date | None = None) -> tuple[dt.date, dt.date]:
    end = (today or dt.date.today()) - dt.timedelta(days=3)
    return end - dt.timedelta(days=27), end

def validate_period(start: str, end: str) -> tuple[dt.date, dt.date]:
    a, b = dt.date.fromisoformat(start), dt.date.fromisoformat(end)
    if a > b: raise ValueError("start date must be on or before end date")
    if b > dt.date.today(): raise ValueError("end date cannot be in the future")
    return a, b

def number(value: Any) -> float:
    try: return float(value or 0)
    except (TypeError, ValueError): return 0.0

def parse_report_rows(response: dict[str, Any]) -> list[dict[str, Any]]:
    headers = [item["name"] for item in response.get("columnHeaders", [])]
    parsed = []
    for values in response.get("rows", []) or []:
        row = dict(zip(headers, values))
        if not row.get("video"): continue
        parsed.append({
            "video_id": str(row["video"]), "views": int(number(row.get("views"))),
            "engaged_views": int(number(row.get("engagedViews"))),
            "estimated_minutes_watched": number(row.get("estimatedMinutesWatched")),
            "average_view_duration": number(row.get("averageViewDuration")),
            "average_view_percentage": number(row.get("averageViewPercentage")),
            "likes": int(number(row.get("likes"))), "comments": int(number(row.get("comments"))),
            "shares": int(number(row.get("shares"))), "subscribers_gained": int(number(row.get("subscribersGained"))),
            "subscribers_lost": int(number(row.get("subscribersLost"))),
        })
    return parsed

def safe_rate(numerator: float, denominator: float) -> float:
    return round(numerator / denominator * 100, 2) if denominator else 0.0

def metadata_from_state(root: Path = ROOT) -> dict[str, dict[str, str]]:
    paths = [root / "episodes" / "state.json", root / "long" / "state.json", root / "custom" / "state.json"]
    paths.extend(sorted((root / "library").glob("*/state.json")))
    metadata: dict[str, dict[str, str]] = {}
    for path in paths:
        if not path.exists(): continue
        try: state = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError): continue
        kind = "long" if path.parent.name == "long" else "short"
        for eid, record in state.get("episodes", {}).items():
            if not isinstance(record, dict): continue
            # 2026-11-23: Spanish versions ("es") and script/trend Shorts (custom/) were missing -> showed as "unknown"
            for language, item in (("default", record), ("hi", record.get("hi", {})), ("es", record.get("es", {}))):
                if not isinstance(item, dict) or not item.get("video_id"): continue
                if path.parent.name == "custom" and language == "default":
                    language = "trend" if record.get("trend_topic") else "script"
                metadata[str(item["video_id"])] = {
                    "episode_id": str(eid), "title": str(item.get("title") or record.get("title") or eid),
                    "content_type": kind, "language": language, "video_url": str(item.get("url") or ""),
                    "published_at": str(item.get("publish_at_ist") or item.get("published_at") or item.get("uploaded_at") or ""),
                    "published_at_source": "publish_at_ist" if item.get("publish_at_ist") else ("published_at" if item.get("published_at") else ("uploaded_at_fallback" if item.get("uploaded_at") else "")),
                }
    return metadata

def analytics_service():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    client_id = os.environ.get("YT_ANALYTICS_CLIENT_ID") or os.environ.get("YT_CLIENT_ID")
    client_secret = os.environ.get("YT_ANALYTICS_CLIENT_SECRET") or os.environ.get("YT_CLIENT_SECRET")
    token = os.environ.get("YT_ANALYTICS_REFRESH_TOKEN")
    missing = [k for k, v in (("YT_ANALYTICS_CLIENT_ID (or YT_CLIENT_ID)", client_id),
                               ("YT_ANALYTICS_CLIENT_SECRET (or YT_CLIENT_SECRET)", client_secret),
                               ("YT_ANALYTICS_REFRESH_TOKEN", token)) if not v]
    if missing: raise RuntimeError("Missing analytics credentials: " + ", ".join(missing))
    creds = Credentials(None, refresh_token=token, token_uri="https://oauth2.googleapis.com/token",
                         client_id=client_id, client_secret=client_secret, scopes=[SCOPE])
    return build("youtubeAnalytics", "v2", credentials=creds, cache_discovery=False)

def fetch_video_report(service, start_date: str, end_date: str) -> list[dict[str, Any]]:
    rows, start_index = [], 1
    while True:
        response = service.reports().query(ids="channel==MINE", startDate=start_date, endDate=end_date,
            dimensions="video", metrics=METRICS, sort="-views", maxResults=PAGE_SIZE,
            startIndex=start_index).execute()
        page = parse_report_rows(response)
        rows.extend(page)
        if len(page) < PAGE_SIZE: break
        start_index += len(page)
    return rows

COUNTRY_METRICS = "views,engagedViews,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained,subscribersLost"


def fetch_countries(service, start_date: str, end_date: str, video_ids=None, top=15) -> list[dict[str, Any]]:
    """Views by viewer country for the whole channel, or for a group of videos (chunks of 150 ids, merged)."""
    groups = [None] if not video_ids else [list(video_ids)[i:i + 150] for i in range(0, len(video_ids), 150)]
    acc: dict[str, dict[str, float]] = {}
    for ids in groups:
        kw = {"filters": "video==" + ",".join(ids)} if ids else {}
        resp = service.reports().query(ids="channel==MINE", startDate=start_date, endDate=end_date, dimensions="country",
                                       metrics=COUNTRY_METRICS, sort="-views", maxResults=200, **kw).execute()
        heads = [h["name"] for h in resp.get("columnHeaders", [])]
        for vals in resp.get("rows", []) or []:
            r = dict(zip(heads, vals)); c = str(r.get("country") or "??")
            a = acc.setdefault(c, {"views": 0.0, "engaged_views": 0.0, "minutes": 0.0, "pct_x_views": 0.0, "subs_gained": 0.0, "subs_lost": 0.0})
            v = number(r.get("views")); a["views"] += v; a["minutes"] += number(r.get("estimatedMinutesWatched"))
            a["engaged_views"] += number(r.get("engagedViews"))
            a["subs_gained"] += number(r.get("subscribersGained")); a["subs_lost"] += number(r.get("subscribersLost"))
            a["pct_x_views"] += number(r.get("averageViewPercentage")) * v
    tot = sum(a["views"] for a in acc.values()) or 1.0
    out = [{"country": c, "views": int(a["views"]), "share_pct": round(100 * a["views"] / tot, 1),
            "engaged_views": int(a["engaged_views"]),
            "engaged_view_rate_pct": round(100 * a["engaged_views"] / a["views"], 1) if a["views"] else 0.0,
            "minutes": round(a["minutes"], 1), "avg_viewed_pct": round(a["pct_x_views"] / a["views"], 1) if a["views"] else 0.0,
            "subscribers_gained": int(a["subs_gained"]), "subscribers_lost": int(a["subs_lost"]),
            "subs_per_1k_views": round(1000 * a["subs_gained"] / a["views"], 2) if a["views"] else 0.0}
           for c, a in acc.items()]
    return sorted(out, key=lambda x: -x["views"])[:top]


COUNTRY_NAMES = {"IN": "India", "US": "USA", "MX": "Mexico", "GB": "UK", "CA": "Canada", "AU": "Australia", "PK": "Pakistan",
                 "BD": "Bangladesh", "PH": "Philippines", "ID": "Indonesia", "NG": "Nigeria", "BR": "Brazil", "ES": "Spain",
                 "AR": "Argentina", "CO": "Colombia", "PE": "Peru", "CL": "Chile", "DE": "Germany", "FR": "France", "AE": "UAE",
                 "SA": "Saudi Arabia", "NP": "Nepal", "LK": "Sri Lanka", "KE": "Kenya", "ZA": "South Africa", "MY": "Malaysia",
                 "SG": "Singapore", "EG": "Egypt", "VN": "Vietnam", "TR": "Turkey", "IT": "Italy", "NL": "Netherlands"}


def audience_report(service, start: str, end: str, metadata: dict, out: Path) -> Path:
    """audience_countries.md/.json: where viewers are, for the channel and per language version (owner, 2026-11-23:
    'is the audience really coming from these locations?' -> decide extra languages on data, not guesses)."""
    groups = {"All videos": None}
    labels = {"default": "English (main) videos", "script": "English custom/script videos", "en": "English (explicit) versions", "hi": "Hindi versions", "es": "Spanish versions", "trend": "Trend Shorts"}
    for lang, label in labels.items():
        ids = [vid for vid, m in metadata.items() if m.get("language") == lang]
        if ids: groups[label] = ids
    data, lines = {}, [f"## Audience by country ({start} to {end})", "",
                       "Where the views come from, by language version. Engaged views/views is not Shorts Stayed to watch. Country shares are based on returned country rows.", ""]
    for label, ids in groups.items():
        try:
            rows = fetch_countries(service, start, end, ids)
        except Exception as exc:
            lines += [f"**{label}:** not available ({str(exc)[:80]})", ""]; continue
        data[label] = rows
        n = len(ids) if ids else len(metadata) or "all"
        lines += [f"**{label}** ({n} videos)", "", "| Country | Views | Share of reported views | Engaged views | Engaged/views | Subs gained | Subs/1k views | Avg % viewed |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
        lines += [f"| {COUNTRY_NAMES.get(r['country'], r['country'])} | {r['views']:,} | {r['share_pct']}% | {r['engaged_views']:,} | {r['engaged_view_rate_pct']}% | {r['subscribers_gained']} | {r['subs_per_1k_views']} | {r['avg_viewed_pct']}% |" for r in rows[:8]]
        lines += [""] if rows else ["| (no views yet) | | | |", ""]
    out.mkdir(parents=True, exist_ok=True)
    (out / "audience_countries.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    p = out / "audience_countries.md"; p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


def initialise_db(db: sqlite3.Connection) -> None:
    db.execute("""CREATE TABLE IF NOT EXISTS video_snapshots (
      channel_key TEXT NOT NULL, period_start TEXT NOT NULL, period_end TEXT NOT NULL, video_id TEXT NOT NULL,
      episode_id TEXT NOT NULL DEFAULT '', title TEXT NOT NULL DEFAULT '', content_type TEXT NOT NULL DEFAULT 'unknown',
      language TEXT NOT NULL DEFAULT '', video_url TEXT NOT NULL DEFAULT '', published_at TEXT NOT NULL DEFAULT '',
      published_at_source TEXT NOT NULL DEFAULT '', views INTEGER NOT NULL DEFAULT 0,
      engaged_views INTEGER NOT NULL DEFAULT 0, estimated_minutes_watched REAL NOT NULL DEFAULT 0,
      average_view_duration REAL NOT NULL DEFAULT 0, average_view_percentage REAL NOT NULL DEFAULT 0,
      likes INTEGER NOT NULL DEFAULT 0, comments INTEGER NOT NULL DEFAULT 0, shares INTEGER NOT NULL DEFAULT 0,
      subscribers_gained INTEGER NOT NULL DEFAULT 0, subscribers_lost INTEGER NOT NULL DEFAULT 0,
      collected_at_utc TEXT NOT NULL, PRIMARY KEY(channel_key, period_start, period_end, video_id))""")
    columns = {row[1] for row in db.execute("PRAGMA table_info(video_snapshots)")}
    for name in ("published_at", "published_at_source"):
        if name not in columns:
            db.execute(f"ALTER TABLE video_snapshots ADD COLUMN {name} TEXT NOT NULL DEFAULT ''")
    db.execute("""CREATE TABLE IF NOT EXISTS collection_runs (
      id INTEGER PRIMARY KEY AUTOINCREMENT, channel_key TEXT NOT NULL, period_start TEXT NOT NULL,
      period_end TEXT NOT NULL, collected_at_utc TEXT NOT NULL, video_count INTEGER NOT NULL, status TEXT NOT NULL)""")
    db.commit()

def store_snapshot(db, channel_key, start, end, rows, metadata) -> str:
    stamp = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    with db:
        for row in rows:
            meta = metadata.get(row["video_id"], {})
            values = {**row, **meta, "channel_key": channel_key, "period_start": start, "period_end": end,
                "episode_id": meta.get("episode_id", ""), "title": meta.get("title", row["video_id"]),
                "content_type": meta.get("content_type", "unknown"), "language": meta.get("language", ""),
                "video_url": meta.get("video_url", ""), "published_at": meta.get("published_at", ""),
                "published_at_source": meta.get("published_at_source", ""), "collected_at_utc": stamp}
            db.execute("""INSERT OR REPLACE INTO video_snapshots (
              channel_key,period_start,period_end,video_id,episode_id,title,content_type,language,video_url,published_at,published_at_source,
              views,engaged_views,estimated_minutes_watched,average_view_duration,average_view_percentage,
              likes,comments,shares,subscribers_gained,subscribers_lost,collected_at_utc)
              VALUES (:channel_key,:period_start,:period_end,:video_id,:episode_id,:title,:content_type,:language,:video_url,:published_at,:published_at_source,
              :views,:engaged_views,:estimated_minutes_watched,:average_view_duration,
              :average_view_percentage,:likes,:comments,:shares,:subscribers_gained,:subscribers_lost,:collected_at_utc)""", values)
        db.execute("""INSERT INTO collection_runs(channel_key,period_start,period_end,collected_at_utc,video_count,status)
          VALUES(?,?,?,?,?,'success')""", (channel_key, start, end, stamp, len(rows)))
    return stamp

def export_outputs(db, output_dir: Path, channel_key: str, start: str, end: str):
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{channel_key}_{start}_{end}"
    csv_path, md_path = output_dir / f"{stem}.csv", output_dir / f"{stem}.md"
    records = db.execute("""SELECT * FROM video_snapshots WHERE channel_key=? AND period_start=? AND period_end=?
      ORDER BY views DESC, estimated_minutes_watched DESC""", (channel_key, start, end)).fetchall()
    headers = [col[1] for col in db.execute("PRAGMA table_info(video_snapshots)")]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle); writer.writerow(headers); writer.writerows(records)
    ix = {name: headers.index(name) for name in headers}
    lines = [f"# YouTube performance — {channel_key}", "", f"**Reporting period:** {start} to {end}", "",
      "> YouTube Analytics data is delayed; the default end date is three days ago.", "",
      "## Channel video totals", "", f"- Videos with report data: **{len(records)}**",
      f"- Views: **{sum(int(r[ix['views']]) for r in records):,}**",
      f"- Engaged views: **{sum(int(r[ix['engaged_views']]) for r in records):,}**",
      f"- Estimated watch time: **{sum(float(r[ix['estimated_minutes_watched']]) for r in records):,.1f} minutes**",
      "", "## Top videos by views", "",
      "| Video | Format | Views | Engaged views | Avg viewed | Avg duration | Likes | Shares | Subs gained |",
      "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in records[:20]:
        title = str(r[ix["title"]] or r[ix["video_id"]]).replace("|", "\\|").replace("\n", " ")
        url = r[ix["video_url"]] or f"https://www.youtube.com/watch?v={r[ix['video_id']]}"
        lines.append(f"| [{title}]({url}) | {r[ix['content_type']]} | {r[ix['views']]:,} | {r[ix['engaged_views']]:,} | "
          f"{r[ix['average_view_percentage']]:.1f}% | {r[ix['average_view_duration']]:.1f}s | {r[ix['likes']]:,} | "
          f"{r[ix['shares']]:,} | {r[ix['subscribers_gained']]:,} |")
    if not records: lines.extend(["", "No per-video rows were returned for this date range."])
    lines.extend(["", "## Interpretation notes", "",
      "- Compare Shorts using **engaged views** and average view percentage alongside public views.",
      "- Compare videos at similar ages and formats; a new upload is not comparable to a 28-day-old upload.",
      "- This targeted per-video report does not include thumbnail impressions or CTR.",
      "- Correlation is not proof that a hook, topic, voice, or thumbnail caused performance.", ""])
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return csv_path, md_path



PRIMARY_MARKETS = {
    "IN": ("India", "Hindi"), "US": ("United States", "English"),
    "ID": ("Indonesia", "Indonesian"), "BR": ("Brazil", "Portuguese"),
    "MX": ("Mexico", "Spanish"), "JP": ("Japan", "Japanese"),
    "DE": ("Germany", "German"), "VN": ("Vietnam", "Vietnamese"),
    "PH": ("Philippines", "Filipino/Tagalog"), "TR": ("Turkey", "Turkish"),
}


def _merge_country_groups(data: dict, labels: list[str]) -> dict[str, dict[str, float]]:
    merged: dict[str, dict[str, float]] = {}
    for label in labels:
        for row in data.get(label, []):
            code = str(row.get("country") or "")
            item = merged.setdefault(code, {"views": 0.0, "engaged_views": 0.0, "minutes": 0.0,
                                             "viewed_x_views": 0.0, "subs": 0.0})
            views = number(row.get("views"))
            item["views"] += views
            item["engaged_views"] += number(row.get("engaged_views"))
            item["minutes"] += number(row.get("minutes"))
            item["viewed_x_views"] += number(row.get("avg_viewed_pct")) * views
            item["subs"] += number(row.get("subscribers_gained"))
    return merged


def market_opportunity_report(output_dir: Path, channel_key: str) -> Path | None:
    """Rank target markets from actual country views; distinguish localized evidence from mixed-language totals."""
    source = output_dir / "audience_countries.json"
    if not source.exists():
        return None
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    all_country = {str(r.get("country")): r for r in data.get("All videos", [])}
    english_labels = ["English (main) videos", "English custom/script videos", "English (explicit) versions"]
    english = _merge_country_groups(data, english_labels)
    hindi = _merge_country_groups(data, ["Hindi versions"])
    spanish = _merge_country_groups(data, ["Spanish versions"])
    kids = "curio" in channel_key.lower()
    output = []
    for code, (country, primary_language) in PRIMARY_MARKETS.items():
        total = all_country.get(code)
        if not total:
            continue
        localized = None
        if kids:
            if primary_language == "Hindi":
                localized = hindi.get(code)
            elif primary_language == "English":
                localized = english.get(code)
            elif primary_language == "Spanish":
                localized = spanish.get(code)
            production_language = primary_language
            available = primary_language if localized else "No matching language version in current library"
        else:
            localized = english.get(code)
            production_language = "English (current AInation policy)"
            available = "English only"
        output.append({
            "country_code": code, "country": country, "primary_market_language": primary_language,
            "planned_production_language": production_language, "current_library_language_evidence": available,
            "country_views_all_videos": int(number(total.get("views"))),
            "localized_views": int(number(localized.get("views"))) if localized else None,
            "localized_engaged_views": int(number(localized.get("engaged_views"))) if localized else None,
            "localized_avg_viewed_pct": round(number(localized.get("avg_viewed_pct")), 1) if localized else None,
            "localized_subscribers_gained": int(number(localized.get("subscribers_gained"))) if localized else None,
            "evidence_note": ("localized-language evidence" if localized else
                              "country-level channel baseline only; no localized-language evidence"),
        })
    output.sort(key=lambda x: x["country_views_all_videos"], reverse=True)
    (output_dir / "market_opportunities.json").write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = ["# Primary-language market opportunities", "", f"**Channel:** {channel_key}", "",
             "Ranked by actual country views in the collected report, not population estimates. Localized metrics are shown only when the channel has a matching language-version group. Country totals alone do not prove demand for a new language.", "",
             "| Rank | Country | Primary language focus | Production policy | Country views | Localized views | Localized avg viewed | Evidence |",
             "|---:|---|---|---|---:|---:|---:|---|"]
    for rank, item in enumerate(output, 1):
        localized_views = f"{item['localized_views']:,}" if item["localized_views"] is not None else "—"
        viewed = f"{item['localized_avg_viewed_pct']}%" if item["localized_avg_viewed_pct"] is not None else "—"
        lines.append(f"| {rank} | {item['country']} | {item['primary_market_language']} | {item['planned_production_language']} | {item['country_views_all_videos']:,} | {localized_views} | {viewed} | {item['evidence_note']} |")
    if not output:
        lines.append("| — | No target-country rows returned | | | | | | |")
    lines += ["", "India production focus is Hindi only; Tamil, Telugu and Bengali are excluded. AInation remains English-only. Analytics may report other audience languages without authorising production in them.", ""]
    path = output_dir / "market_opportunities.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def parse_daily_rows(response: dict[str, Any]) -> list[dict[str, Any]]:
    headers = [item["name"] for item in response.get("columnHeaders", [])]
    out = []
    for values in response.get("rows", []) or []:
        row = dict(zip(headers, values))
        if not row.get("day"):
            continue
        out.append({
            "day": str(row["day"]), "views": number(row.get("views")),
            "engaged_views": number(row.get("engagedViews")),
            "minutes": number(row.get("estimatedMinutesWatched")),
            "avg_duration": number(row.get("averageViewDuration")),
            "avg_viewed_pct": number(row.get("averageViewPercentage")),
            "subs_gained": number(row.get("subscribersGained")),
        })
    return out


def build_age_cohorts(daily_rows: list[dict[str, Any]], published_at: str, as_of: str) -> list[dict[str, Any]]:
    """Return cumulative 7/14/28-day metrics only when the full age window has elapsed."""
    try:
        published = dt.date.fromisoformat(str(published_at)[:10])
        cutoff = dt.date.fromisoformat(str(as_of)[:10])
    except (TypeError, ValueError):
        return []
    by_day = {str(row["day"]): row for row in daily_rows}
    results = []
    for days in (7, 14, 28):
        window_end = published + dt.timedelta(days=days - 1)
        if window_end > cutoff:
            continue
        selected = [by_day.get((published + dt.timedelta(days=i)).isoformat(), {}) for i in range(days)]
        views = sum(number(x.get("views")) for x in selected)
        engaged = sum(number(x.get("engaged_views")) for x in selected)
        minutes = sum(number(x.get("minutes")) for x in selected)
        viewed_weight = sum(number(x.get("avg_viewed_pct")) * number(x.get("views")) for x in selected)
        duration_weight = sum(number(x.get("avg_duration")) * number(x.get("views")) for x in selected)
        subs = sum(number(x.get("subs_gained")) for x in selected)
        results.append({
            "age_days": days, "window_start": published.isoformat(), "window_end": window_end.isoformat(),
            "views": int(views), "engaged_views": int(engaged), "engaged_view_rate_pct": safe_rate(engaged, views),
            "watch_minutes": round(minutes, 1),
            "average_view_percentage": round(viewed_weight / views, 2) if views else 0.0,
            "average_view_duration": round(duration_weight / views, 2) if views else 0.0,
            "subscribers_gained": int(subs),
        })
    return results


def fetch_daily_video_rows(service, video_id: str, start_date: str, end_date: str) -> list[dict[str, Any]]:
    response = service.reports().query(
        ids="channel==MINE", startDate=start_date, endDate=end_date, dimensions="day",
        metrics="views,engagedViews,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained",
        filters="video==" + video_id, sort="day", maxResults=200,
    ).execute()
    return parse_daily_rows(response)


def age_cohort_report(service, rows: list[dict[str, Any]], metadata: dict[str, dict[str, str]],
                      start: str, end: str, out: Path, top_n: int = 20) -> Path | None:
    """Build age-matched cohorts for the top N videos; one daily query per video."""
    if top_n <= 0:
        return None
    report_end = dt.date.fromisoformat(end)
    selected = sorted(rows, key=lambda x: number(x.get("views")), reverse=True)[:top_n]
    output = []
    for item in selected:
        video_id = str(item.get("video_id") or "")
        meta = metadata.get(video_id, {})
        published = meta.get("published_at", "")
        if not video_id or not published:
            continue
        try:
            published_date = dt.date.fromisoformat(str(published)[:10])
        except ValueError:
            continue
        if published_date > report_end:
            continue
        query_end = min(published_date + dt.timedelta(days=27), report_end)
        try:
            daily = fetch_daily_video_rows(service, video_id, published_date.isoformat(), query_end.isoformat())
        except Exception as exc:
            output.append({"video_id": video_id, "title": meta.get("title", video_id), "error": str(exc)[:180]})
            continue
        cohorts = build_age_cohorts(daily, published, end)
        for cohort in cohorts:
            output.append({"video_id": video_id, "title": meta.get("title", video_id),
                           "language": meta.get("language", ""), "content_type": meta.get("content_type", ""),
                           **cohort})
    out.mkdir(parents=True, exist_ok=True)
    (out / "age_matched_cohorts.json").write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md = ["# Age-matched video cohorts", "", f"**As of:** {end}", "",
          "Metrics are cumulative from each video's recorded publish date. Only complete 7/14/28-day windows are shown; compare the same format and age. Publish dates come from episode state (publish_at_ist preferred), not independently verified YouTube metadata.", "",
          "| Video | Language | Format | Age | Views | Engaged views | Engaged rate | Avg viewed | Subs gained |",
          "|---|---|---|---:|---:|---:|---:|---:|---:|"]
    for item in output:
        if "error" in item:
            md.append(f"| {item['title']} ({item['video_id']}) | | | | | | | | |")
        else:
            md.append(f"| {item['title'].replace('|', '/')} | {item.get('language','')} | {item.get('content_type','')} | {item['age_days']}d | {item['views']:,} | {item['engaged_views']:,} | {item['engaged_view_rate_pct']}% | {item['average_view_percentage']}% | {item['subscribers_gained']} |")
    if not output:
        md.append("No eligible videos had a recorded publish date and a complete cohort window.")
    path = out / "age_matched_cohorts.md"
    path.write_text("\n".join(md) + "\n", encoding="utf-8")
    return path


def fetch_retention_curve(service, video_id: str, start_date: str, end_date: str) -> list[dict[str, Any]]:
    """Targeted retention query; YouTube requires one video ID per request."""
    response = service.reports().query(
        ids="channel==MINE", startDate=start_date, endDate=end_date,
        dimensions="elapsedVideoTimeRatio", metrics="audienceWatchRatio,relativeRetentionPerformance",
        filters="video==" + video_id, sort="elapsedVideoTimeRatio", maxResults=200,
    ).execute()
    headers = [item["name"] for item in response.get("columnHeaders", [])]
    points = []
    for values in response.get("rows", []) or []:
        row = dict(zip(headers, values))
        points.append({
            "elapsed_video_time_ratio": number(row.get("elapsedVideoTimeRatio")),
            "audience_watch_ratio": number(row.get("audienceWatchRatio")),
            "relative_retention_performance": number(row.get("relativeRetentionPerformance")),
        })
    return points


def retention_report(service, rows: list[dict[str, Any]], metadata: dict[str, dict[str, str]],
                     start: str, end: str, out: Path, top_n: int = 10) -> Path | None:
    """Collect retention curves for the top N videos, bounded to avoid one request per library item."""
    if top_n <= 0:
        return None
    selected = sorted(rows, key=lambda x: number(x.get("views")), reverse=True)[:top_n]
    data = []
    for item in selected:
        video_id = str(item.get("video_id") or "")
        if not video_id:
            continue
        try:
            points = fetch_retention_curve(service, video_id, start, end)
            data.append({"video_id": video_id, "title": metadata.get(video_id, {}).get("title", video_id),
                         "language": metadata.get(video_id, {}).get("language", ""),
                         "content_type": metadata.get(video_id, {}).get("content_type", "unknown"),
                         "points": points})
        except Exception as exc:
            data.append({"video_id": video_id, "title": metadata.get(video_id, {}).get("title", video_id),
                         "error": str(exc)[:180], "points": []})
    out.mkdir(parents=True, exist_ok=True)
    path = out / "retention_curves.json"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md = ["# Audience retention curves", "", f"**Reporting period:** {start} to {end}", "",
          "Each curve is a separate video-level request. audienceWatchRatio is the share of the video's audience still watching at each elapsed-video-time ratio; relativeRetentionPerformance compares retention with similar-length videos.", ""]
    for video in data:
        md.append(f"## {video['title']} ({video['video_id']})")
        if "error" in video:
            md.append(f"- Not available: {video['error']}")
        elif not video["points"]:
            md.append("- No retention points returned.")
        else:
            md += ["| Video elapsed | Audience watch ratio | Relative retention |", "|---:|---:|---:|"]
            md += [f"| {p['elapsed_video_time_ratio']:.3f} | {p['audience_watch_ratio']:.3f} | {p['relative_retention_performance']:.3f} |" for p in video["points"]]
        md.append("")
    md_path = out / "retention_curves.md"
    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")
    return md_path


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-date"); parser.add_argument("--end-date")
    parser.add_argument("--output-dir", default=os.environ.get("ANALYTICS_OUTPUT_DIR", str(DEFAULT_OUTPUT)))
    parser.add_argument("--channel-key", default=os.environ.get("ANALYTICS_CHANNEL_KEY") or ROOT.name)
    parser.add_argument("--retention-top-n", type=int, default=int(os.environ.get("RETENTION_TOP_N", "10")))
    parser.add_argument("--cohort-top-n", type=int, default=int(os.environ.get("COHORT_TOP_N", "20")))
    args = parser.parse_args(argv)
    ds, de = default_period()
    start, end = args.start_date or ds.isoformat(), args.end_date or de.isoformat()
    try:
        validate_period(start, end)
        service = analytics_service()
        rows = fetch_video_report(service, start, end)
        out = Path(args.output_dir)
        db_path = Path(os.environ.get("ANALYTICS_DB_PATH") or out / "analytics.sqlite3")
        db_path.parent.mkdir(parents=True, exist_ok=True)
        db = sqlite3.connect(db_path)
        try:
            meta = metadata_from_state()
            initialise_db(db); stamp = store_snapshot(db, args.channel_key, start, end, rows, meta)
            csv_path, md_path = export_outputs(db, out, args.channel_key, start, end)
        finally: db.close()
        try:  # optional extra: views by country (never fails the collection)
            print("Audience by country:", audience_report(service, start, end, meta, out))
            market_path = market_opportunity_report(out, args.channel_key)
            if market_path: print("Primary-language market report:", market_path)
        except Exception as exc:
            print(f"note: audience by country skipped: {exc}", file=sys.stderr)
        for label, fn, count in (("age-matched cohorts", age_cohort_report, args.cohort_top_n),
                                 ("retention curves", retention_report, args.retention_top_n)):
            try:
                result = fn(service, rows, meta, start, end, out, count)
                if result: print(f"{label.title()}: {result}")
            except Exception as exc:
                print(f"note: {label} skipped: {exc}", file=sys.stderr)
    except Exception as exc:
        print(f"Analytics collection failed: {exc}", file=sys.stderr); return 1
    print(f"Collected {len(rows)} video rows for {args.channel_key} ({start} to {end}) at {stamp}.")
    print(f"SQLite: {db_path}\nCSV: {csv_path}\nMarkdown report: {md_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
