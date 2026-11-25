import sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))
import growth

class GrowthBriefTests(unittest.TestCase):
    def test_curio_profile_and_metadata_quality_are_reported(self):
        rows = [
            {"video_id":"a","title":"Why Is the Sky Blue?","content_type":"short","views":1309,"engaged_views":964,"average_view_percentage":56.49,"average_view_duration":35,"subscribers_gained":8},
            {"video_id":"b","title":"unknown","content_type":"unknown","views":480,"engaged_views":57,"average_view_percentage":15.87,"subscribers_gained":1},
        ]
        data, md = growth.build_brief(rows, "curiokids-club", "2026-10-19 to 2026-11-15")
        self.assertEqual(data["metadata_coverage_pct"], 50.0)
        self.assertEqual(data["top_shorts"][0]["title"], "Why Is the Sky Blue?")
        self.assertIn("curious", data["voice"])
        self.assertIn("Repair missing episode/video mappings", md)

    def test_aination_uses_distinct_guidance(self):
        data, md = growth.build_brief([{"video_id":"x","title":"What Not to Tell AI","content_type":"short","views":203,"engaged_views":112,"average_view_percentage":47,"subscribers_gained":1}], "aination-studio")
        self.assertIn("practical", data["voice"])
        self.assertIn("AI safety", md)
        self.assertNotIn("kids", data["voice"].lower())

    def test_unmapped_videos_are_listed_for_manual_review(self):
        rows = [
            {"video_id": "known", "title": "Known episode", "content_type": "short", "views": 20},
            {"video_id": "unmapped123", "title": "unmapped123", "content_type": "unknown", "views": 55},
        ]
        data, md = growth.build_brief(rows, "aination-studio")
        self.assertEqual(data["unmapped_videos"][0]["video_id"], "unmapped123")
        self.assertEqual(data["unmapped_videos"][0]["views"], 55)
        self.assertIn("unmapped123", md)
        self.assertIn("not assigned to episodes automatically", md)


    def test_topic_performance_uses_channel_taxonomy(self):
        if growth.playlist_plan.KIDS:
            title = "Why Is the Sky Blue?"
            expected = "Everyday Science & Discoveries"
        else:
            title = "What Is AI? ChatGPT prompts"
            expected = "AI Explained"
        rows = [
            {"video_id": "one", "title": title, "content_type": "short", "views": 100,
             "engaged_views": 60, "average_view_percentage": 50, "subscribers_gained": 2},
            {"video_id": "two", "title": title, "content_type": "short", "views": 50,
             "engaged_views": 30, "average_view_percentage": 70, "subscribers_gained": 1},
        ]
        topics, unmatched = growth.aggregate_topic_performance(rows)
        match = next(x for x in topics if x["topic"] == expected)
        self.assertEqual(match["video_count"], 2)
        self.assertEqual(match["views"], 150)
        self.assertEqual(match["engaged_views"], 90)
        self.assertEqual(match["engaged_view_rate_pct"], 60.0)
        self.assertEqual(unmatched, [])

    def test_reach_metrics_are_added_to_long_form_packaging_only(self):
        rows = [
            {"video_id": "short1", "title": "What Is AI? ChatGPT prompts", "content_type": "short",
             "views": 100, "engaged_views": 60, "average_view_percentage": 50},
            {"video_id": "long1", "title": "Full AI Tutorial", "content_type": "long",
             "views": 200, "engaged_views": 100, "average_view_percentage": 45},
        ]
        reach = [
            {"video_id": "short1", "impressions": 1000, "impressions_ctr": 0.05},
            {"video_id": "long1", "impressions": 5000, "impressions_ctr": 0.04},
        ]
        data, md = growth.build_brief(rows, "aination-studio", reach_rows=reach)
        self.assertEqual(len(data["long_form_packaging"]), 1)
        self.assertEqual(data["long_form_packaging"][0]["video_id"], "long1")
        self.assertEqual(data["long_form_packaging"][0]["impressions_ctr_pct"], 4.0)
        self.assertIn("Long-form thumbnail reach", md)


    def test_related_video_candidates_are_review_only_and_topic_aware(self):
        if growth.playlist_plan.KIDS:
            short_title = "How Does Your Heart Pump Blood?"
            long_title = "How Your Heart Works | Full Video for Kids"
        else:
            short_title = "What Not to Tell AI"
            long_title = "What Not to Tell AI: Privacy Rules for Chatbots"
        rows = [
            {"video_id": "short1", "title": short_title, "content_type": "short"},
            {"video_id": "long1", "title": long_title, "content_type": "long"},
        ]
        candidates = growth.build_related_video_candidates(rows)
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["short_video_id"], "short1")
        self.assertEqual(candidates[0]["long_video_id"], "long1")
        self.assertEqual(candidates[0]["review_status"], "manual review")
        self.assertTrue(candidates[0]["shared_topics"])

    def test_empty_rows_are_safe(self):
        data, md = growth.build_brief([], "aination-studio")
        self.assertEqual(data["video_rows"], 0)
        self.assertIn("No identified Shorts", md)

if __name__ == "__main__": unittest.main()
