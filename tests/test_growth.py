import sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))
import growth

class GrowthBriefTests(unittest.TestCase):
    def test_curio_profile_and_metadata_quality_are_reported(self):
        rows = [
            {"video_id":"a","title":"Why Is the Sky Blue?","content_type":"short","views":"1309","engaged_views":"964","average_view_percentage":"56.49","average_view_duration":"35","subscribers_gained":"8"},
            {"video_id":"b","title":"unknown","content_type":"unknown","views":"480","engaged_views":"57","average_view_percentage":"15.87","subscribers_gained":"1"},
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

    def test_empty_rows_are_safe(self):
        data, md = growth.build_brief([], "aination-studio")
        self.assertEqual(data["video_rows"], 0)
        self.assertIn("No identified Shorts", md)

if __name__ == "__main__": unittest.main()
