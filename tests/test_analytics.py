import datetime as dt
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))
import analytics


class AnalyticsTests(unittest.TestCase):
    def test_default_period_is_28_days_ending_three_days_ago(self):
        start, end = analytics.default_period(dt.date(2026, 11, 10))
        self.assertEqual(end, dt.date(2026, 11, 7))
        self.assertEqual((end - start).days, 27)

    def test_reversed_period_is_rejected(self):
        with self.assertRaises(ValueError):
            analytics.validate_period("2026-11-08", "2026-11-07")

    def test_report_rows_are_normalized(self):
        response = {
            "columnHeaders": [
                {"name": "video"}, {"name": "views"}, {"name": "engagedViews"},
                {"name": "averageViewPercentage"}, {"name": "likes"},
            ],
            "rows": [["abc123", 120, 80, 67.5, 9], ["", 3, 2, 50, 1]],
        }
        rows = analytics.parse_report_rows(response)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["video_id"], "abc123")
        self.assertEqual(rows[0]["views"], 120)
        self.assertEqual(rows[0]["engaged_views"], 80)
        self.assertEqual(rows[0]["average_view_percentage"], 67.5)
        self.assertEqual(rows[0]["likes"], 9)

    def test_snapshot_is_persisted_and_exports_are_created(self):
        import sqlite3
        import tempfile
        from pathlib import Path

        row = {
            "video_id": "video123", "views": 100, "engaged_views": 70,
            "estimated_minutes_watched": 12.5, "average_view_duration": 7.5,
            "average_view_percentage": 62.0, "likes": 8, "comments": 1,
            "shares": 2, "subscribers_gained": 1, "subscribers_lost": 0,
        }
        metadata = {"video123": {
            "episode_id": "ep001", "title": "Test episode", "content_type": "short",
            "language": "default", "video_url": "https://youtu.be/video123",
        }}
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            db = sqlite3.connect(root / "analytics.sqlite3")
            try:
                analytics.initialise_db(db)
                analytics.store_snapshot(db, "test-channel", "2026-10-01", "2026-10-28", [row], metadata)
                saved = db.execute("SELECT title, views FROM video_snapshots").fetchone()
                self.assertEqual(saved, ("Test episode", 100))
                csv_path, md_path = analytics.export_outputs(
                    db, root / "reports", "test-channel", "2026-10-01", "2026-10-28"
                )
                self.assertTrue(csv_path.exists())
                self.assertTrue(md_path.exists())
                self.assertIn("Test episode", md_path.read_text(encoding="utf-8"))
            finally:
                db.close()


    def test_build_age_cohorts_only_emits_complete_windows(self):
        start = dt.date(2026, 1, 1)
        daily = []
        for i in range(28):
            day = start + dt.timedelta(days=i)
            daily.append({"day": day.isoformat(), "views": 10, "engaged_views": 6,
                          "minutes": 2.5, "avg_duration": 15, "avg_viewed_pct": 50,
                          "subs_gained": 1})
        cohorts = analytics.build_age_cohorts(daily, "2026-01-01T10:00:00+05:30", "2026-01-20")
        self.assertEqual([x["age_days"] for x in cohorts], [7, 14])
        self.assertEqual(cohorts[0]["views"], 70)
        self.assertEqual(cohorts[0]["engaged_view_rate_pct"], 60.0)
        full = analytics.build_age_cohorts(daily, "2026-01-01", "2026-01-28")
        self.assertEqual([x["age_days"] for x in full], [7, 14, 28])
        self.assertEqual(full[-1]["views"], 280)

    def test_parse_daily_rows_uses_header_names(self):
        response = {
            "columnHeaders": [{"name": "day"}, {"name": "views"}, {"name": "engagedViews"},
                              {"name": "averageViewPercentage"}],
            "rows": [["2026-01-01", 20, 12, 60]],
        }
        rows = analytics.parse_daily_rows(response)
        self.assertEqual(rows[0]["views"], 20)
        self.assertEqual(rows[0]["engaged_views"], 12)
        self.assertEqual(rows[0]["avg_viewed_pct"], 60)

    def test_snapshot_schema_migrates_published_at_columns(self):
        import sqlite3
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            db = sqlite3.connect(Path(folder) / "old.sqlite3")
            try:
                db.execute("""CREATE TABLE video_snapshots (
                    channel_key TEXT, period_start TEXT, period_end TEXT, video_id TEXT,
                    episode_id TEXT, title TEXT, content_type TEXT, language TEXT, video_url TEXT,
                    views INTEGER, engaged_views INTEGER, estimated_minutes_watched REAL,
                    average_view_duration REAL, average_view_percentage REAL, likes INTEGER,
                    comments INTEGER, shares INTEGER, subscribers_gained INTEGER, subscribers_lost INTEGER,
                    collected_at_utc TEXT)""")
                analytics.initialise_db(db)
                cols = {x[1] for x in db.execute("PRAGMA table_info(video_snapshots)")}
                self.assertIn("published_at", cols)
                self.assertIn("published_at_source", cols)
            finally:
                db.close()

    def test_country_report_includes_engaged_and_subscriber_metrics(self):
        class Query:
            def query(self, **kwargs):
                self.kwargs = kwargs
                return self
            def execute(self):
                return {
                    "columnHeaders": [
                        {"name": "country"}, {"name": "views"}, {"name": "engagedViews"},
                        {"name": "estimatedMinutesWatched"}, {"name": "averageViewDuration"},
                        {"name": "averageViewPercentage"}, {"name": "subscribersGained"},
                        {"name": "subscribersLost"},
                    ],
                    "rows": [["IN", 100, 70, 50, 5, 60, 4, 1]],
                }
        query = Query()
        class Service:
            def reports(self):
                return query

        rows = analytics.fetch_countries(Service(), "2026-10-01", "2026-10-28")
        self.assertEqual(query.kwargs["maxResults"], 200)
        self.assertEqual(rows[0]["engaged_views"], 70)
        self.assertEqual(rows[0]["engaged_view_rate_pct"], 70.0)
        self.assertEqual(rows[0]["subscribers_gained"], 4)
        self.assertEqual(rows[0]["subs_per_1k_views"], 40.0)

    def test_audience_report_includes_custom_script_english_group(self):
        from unittest.mock import patch
        import tempfile
        from pathlib import Path

        calls = []
        def fake_fetch(service, start, end, ids=None, top=15):
            calls.append(ids)
            return []
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(analytics, "fetch_countries", side_effect=fake_fetch):
                analytics.audience_report(None, "2026-10-01", "2026-10-28",
                    {"script-video": {"language": "script"}}, Path(folder))
            report = (Path(folder) / "audience_countries.md").read_text(encoding="utf-8")
        self.assertIn(["script-video"], calls)
        self.assertIn("English custom/script videos", report)


if __name__ == "__main__":
    unittest.main()
