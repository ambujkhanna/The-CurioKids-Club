#!/usr/bin/env python3
"""Fetch read-only YouTube Reporting API Reach Basic reports (thumbnail impressions and CTR)."""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import gzip
import io
import os
from pathlib import Path
from typing import Any


REPORT_TYPE = "channel_reach_basic_a1"
SCOPE = "https://www.googleapis.com/auth/yt-analytics.readonly"


def parse_reach_csv(text: str) -> list[dict[str, Any]]:
    rows = []
    for row in csv.DictReader(io.StringIO(text)):
        try:
            impressions = int(float(row.get("video_thumbnail_impressions") or 0))
            ctr = float(row.get("video_thumbnail_impressions_ctr") or 0)
        except (TypeError, ValueError):
            continue
        rows.append({
            "date": str(row.get("date") or ""),
            "channel_id": str(row.get("channel_id") or ""),
            "video_id": str(row.get("video_id") or ""),
            "impressions": impressions,
            "impressions_ctr": ctr,
        })
    return rows


def reporting_clients():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from google.auth.transport.requests import AuthorizedSession

    client_id = os.environ.get("YT_ANALYTICS_CLIENT_ID") or os.environ.get("YT_CLIENT_ID")
    client_secret = os.environ.get("YT_ANALYTICS_CLIENT_SECRET") or os.environ.get("YT_CLIENT_SECRET")
    token = os.environ.get("YT_ANALYTICS_REFRESH_TOKEN")
    missing = [name for name, value in (
        ("YT_ANALYTICS_CLIENT_ID (or YT_CLIENT_ID)", client_id),
        ("YT_ANALYTICS_CLIENT_SECRET (or YT_CLIENT_SECRET)", client_secret),
        ("YT_ANALYTICS_REFRESH_TOKEN", token),
    ) if not value]
    if missing:
        raise RuntimeError("Missing analytics credentials: " + ", ".join(missing))
    credentials = Credentials(None, refresh_token=token, token_uri="https://oauth2.googleapis.com/token",
                              client_id=client_id, client_secret=client_secret, scopes=[SCOPE])
    return build("youtubereporting", "v1", credentials=credentials, cache_discovery=False), AuthorizedSession(credentials)


def find_or_create_job(service, ensure_job: bool = False) -> dict[str, Any] | None:
    response = service.jobs().list(pageSize=50).execute()
    jobs = response.get("jobs", []) or []
    for job in jobs:
        if job.get("reportTypeId") == REPORT_TYPE:
            return job
    if not ensure_job:
        return None
    return service.jobs().create(body={"reportTypeId": REPORT_TYPE}).execute()


def list_reports(service, job_id: str, start_time: str, end_time: str) -> list[dict[str, Any]]:
    response = service.jobs().reports().list(
        jobId=job_id, startTimeAtOrAfter=start_time, endTimeBefore=end_time, pageSize=50
    ).execute()
    return response.get("reports", []) or []


def download_report(session, url: str) -> str:
    response = session.get(url, timeout=90)
    response.raise_for_status()
    body = response.content
    if body[:2] == b"\x1f\x8b":
        body = gzip.decompress(body)
    return body.decode("utf-8-sig")


def summarise_reach(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, float]] = {}
    for row in rows:
        video = row["video_id"] or "(channel-level)"
        item = grouped.setdefault(video, {"impressions": 0.0, "weighted_ctr": 0.0, "days": 0.0})
        impressions = float(row["impressions"])
        item["impressions"] += impressions
        item["weighted_ctr"] += impressions * float(row["impressions_ctr"])
        item["days"] += 1
    result = []
    for video, item in grouped.items():
        impressions = item["impressions"]
        result.append({
            "video_id": video,
            "impressions": int(impressions),
            "impressions_ctr": round(item["weighted_ctr"] / impressions, 6) if impressions else 0.0,
            "report_days": int(item["days"]),
        })
    return sorted(result, key=lambda x: x["impressions"], reverse=True)


def collect(output_dir: Path, start_time: str, end_time: str, ensure_job: bool = False) -> tuple[int, str]:
    service, session = reporting_clients()
    job = find_or_create_job(service, ensure_job=ensure_job)
    if not job:
        return 0, f"No {REPORT_TYPE} reporting job exists. Run once with --ensure-job; YouTube may take up to 24 hours to produce the first report."
    reports = list_reports(service, job["id"], start_time, end_time)
    all_rows = []
    for report in reports:
        url = report.get("downloadUrl")
        if not url:
            continue
        all_rows.extend(parse_reach_csv(download_report(session, url)))
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "reach_basic_daily.csv"
    fields = ["date", "channel_id", "video_id", "impressions", "impressions_ctr"]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(all_rows)
    summary = summarise_reach(all_rows)
    summary_path = output_dir / "reach_by_video.csv"
    with summary_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["video_id", "impressions", "impressions_ctr", "report_days"])
        writer.writeheader()
        writer.writerows(summary)
    md = ["# Thumbnail reach report", "", f"**Report window:** {start_time} to {end_time}", "",
          "Reach metrics are reported for eligible thumbnail surfaces; they are not a Shorts-feed hook metric. CTR is stored as returned by the Reporting API (fractional ratio).", "",
          "| Video ID | Thumbnail impressions | Weighted CTR | Report days |", "|---|---:|---:|---:|"]
    for row in summary:
        md.append(f"| {row['video_id']} | {row['impressions']:,} | {row['impressions_ctr']:.4%} | {row['report_days']} |")
    if not summary:
        md.append("| No report rows available yet | | | |")
    (output_dir / "reach_basic.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return len(all_rows), f"Downloaded {len(all_rows)} reach rows to {csv_path}; video summary: {summary_path}"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="out/analytics")
    parser.add_argument("--days", type=int, default=28)
    parser.add_argument("--ensure-job", action="store_true", help="Create the daily Reach Basic reporting job if absent.")
    args = parser.parse_args(argv)
    if args.days < 1 or args.days > 60:
        parser.error("--days must be between 1 and 60")
    end = dt.datetime.now(dt.timezone.utc).date() - dt.timedelta(days=3)
    start = end - dt.timedelta(days=args.days - 1)
    try:
        count, message = collect(Path(args.output_dir), start.isoformat() + "T00:00:00Z",
                                 (end + dt.timedelta(days=1)).isoformat() + "T00:00:00Z", args.ensure_job)
    except Exception as exc:
        print(f"Reach report unavailable: {exc}")
        return 0
    print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
