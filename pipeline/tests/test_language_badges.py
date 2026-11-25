import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import language_badges


class TestLanguageBadges(unittest.TestCase):
    def test_supported_labels(self):
        self.assertEqual(language_badges.label_for("en"), "ENGLISH")
        self.assertEqual(language_badges.label_for("hi"), "\u0939\u093f\u0928\u094d\u0926\u0940")
        self.assertEqual(language_badges.label_for("es"), "ESPAÑOL")

    def test_unknown_defaults_to_english(self):
        self.assertEqual(language_badges.label_for("fr"), "ENGLISH")

    def test_environment_fallback(self):
        with patch.dict(os.environ, {"THUMB_LANG": "es"}):
            self.assertEqual(language_badges.label_for(), "ESPAÑOL")
