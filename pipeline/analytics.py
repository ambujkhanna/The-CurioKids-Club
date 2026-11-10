#!/usr/bin/env python3
"""Read-only per-video YouTube Analytics collector. Requires a separate youtube.readonly refresh token."""
from __future__ import annotations
import argparse, csv, datetime as dt, json, os, sqlite3, sys
from pathlib import Path
from typing import Any

SCOPE = "https://www.googleapis.com/auth/youtube.readonly"
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
    paths = [root / "episodes" / "state.json", root / "long" / "state.json"]
    paths.extend(sorted((root / "library").glob("*/state.json")))
    metadata: dict[str, dict[str, str]] = {}
    for path in paths:
        if not path.exists(): continue
        try: state = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError): continue
        kind = "long" if path.parent.name == "long" else "short"
        for eid, record in state.get("episodes", {}).items():
            if not isinstance(record, dict): continue
            for language, item in (("default", record), ("hi", record.get("hi", {}))):
                if not isinstance(item, dict) or not item.get("video_id"): continue
                metadata[str(item["video_id"])] = {
                    "episode_id": str(eid), "title": str(item.get("title") or record.get("title") or eid),
                    "content_type": kind, "language": language, "video_url": str(item.get("url") or ""),
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

def initialise_db(db: sqlite3.Connection) -> None:
    db.execute("""CREATE TABLE IF NOT EXISTS video_snapshots (
      channel_key TEXT NOT NULL, period_start TEXT NOT NULL, period_end TEXT NOT NULL, video_id TEXT NOT NULL,
      episode_id TEXT NOT NULL DEFAULT '', title TEXT NOT NULL DEFAULT '', content_type TEXT NOT NULL DEFAULT 'unknown',
      language TEXT NOT NULL DEFAULT '', video_url TEXT NOT NULL DEFAULT '', views INTEGER NOT NULL DEFAULT 0,
      engaged_views INTEGER NOT NULL DEFAULT 0, estimated_minutes_watched REAL NOT NULL DEFAULT 0,
      average_view_duration REAL NOT NULL DEFAULT 0, average_view_percentage REAL NOT NULL DEFAULT 0,
      likes INTEGER NOT NULL DEFAULT 0, comments INTEGER NOT NULL DEFAULT 0, shares INTEGER NOT NULL DEFAULT 0,
      subscribers_gained INTEGER NOT NULL DEFAULT 0, subscribers_lost INTEGER NOT NULL DEFAULT 0,
      collected_at_utc TEXT NOT NULL, PRIMARY KEY(channel_key, period_start, period_end, video_id))""")
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
                "video_url": meta.get("video_url", ""), "collected_at_utc": stamp}
            db.execute("""INSERT OR REPLACE INTO video_snapshots (
              channel_key,period_start,period_end,video_id,episode_id,title,content_type,language,video_url,
              views,engaged_views,estimated_minutes_watched,average_view_duration,average_view_percentage,
              likes,comments,shares,subscribers_gained,subscribers_lost,collected_at_utc)
              VALUES (:channel_key,:period_start,:period_end,:video_id,:episode_id,:title,:content_type,:language,
              :video_url,:views,:engaged_views,:estimated_minutes_watched,:average_view_duration,
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

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-date"); parser.add_argument("--end-date")
    parser.add_argument("--output-dir", default=os.environ.get("ANALYTICS_OUTPUT_DIR", str(DEFAULT_OUTPUT)))
    parser.add_argument("--channel-key", default=os.environ.get("ANALYTICS_CHANNEL_KEY") or ROOT.name)
    args = parser.parse_args(argv)
    ds, de = default_period()
    start, end = args.start_date or ds.isoformat(), args.end_date or de.isoformat()
    try:
        validate_period(start, end)
        rows = fetch_video_report(analytics_service(), start, end)
        out = Path(args.output_dir)
        db_path = Path(os.environ.get("ANALYTICS_DB_PATH") or out / "analytics.sqlite3")
        db_path.parent.mkdir(parents=True, exist_ok=True)
        db = sqlite3.connect(db_path)
        try:
            initialise_db(db); stamp = store_snapshot(db, args.channel_key, start, end, rows, metadata_from_state())
            csv_path, md_path = export_outputs(db, out, args.channel_key, start, end)
        finally: db.close()
    except Exception as exc:
        print(f"Analytics collection failed: {exc}", file=sys.stderr); return 1
    print(f"Collected {len(rows)} video rows for {args.channel_key} ({start} to {end}) at {stamp}.")
    print(f"SQLite: {db_path}\nCSV: {csv_path}\nMarkdown report: {md_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
