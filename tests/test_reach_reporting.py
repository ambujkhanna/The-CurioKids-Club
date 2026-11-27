import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))
import reach_reporting


class ReachReportingTests(unittest.TestCase):
    def test_parse_reach_csv_uses_column_names(self):
        text = "date,channel_id,video_id,video_thumbnail_impressions,video_thumbnail_impressions_ctr\n2026-11-01,UC123,vid1,1200,0.045\n"
        rows = reach_reporting.parse_reach_csv(text)
        self.assertEqual(rows[0]["video_id"], "vid1")
        self.assertEqual(rows[0]["impressions"], 1200)
        self.assertEqual(rows[0]["impressions_ctr"], 0.045)

    def test_ctr_is_weighted_by_impressions(self):
        rows = [
            {"video_id": "vid1", "impressions": 100, "impressions_ctr": 0.10},
            {"video_id": "vid1", "impressions": 300, "impressions_ctr": 0.02},
        ]
        result = reach_reporting.summarise_reach(rows)
        self.assertEqual(result[0]["impressions"], 400)
        self.assertAlmostEqual(result[0]["impressions_ctr"], 0.04)


if __name__ == "__main__":
    unittest.main()
