import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import visual_layers


class VisualLayerTests(unittest.TestCase):
    def test_legacy_episode_has_no_visual_style(self):
        self.assertEqual("none", visual_layers.resolve_style())

    def test_episode_style_is_read(self):
        self.assertEqual("garden", visual_layers.resolve_style({"style": "garden"}))

    def test_environment_overrides_episode(self):
        self.assertEqual("space", visual_layers.resolve_style({"style": "garden"}, "space"))

    def test_unknown_style_falls_back_to_legacy(self):
        self.assertEqual("none", visual_layers.resolve_style({"style": "not-a-style"}))

    def test_known_styles_are_available(self):
        for style in ("ocean", "sunrise", "garden", "space", "candy", "paper"):
            self.assertIn(style, visual_layers.STYLES)


if __name__ == "__main__":
    unittest.main()
