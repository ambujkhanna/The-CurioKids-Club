import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asset_manager


class AssetManagerTests(unittest.TestCase):
    def test_empty_manifest_is_valid(self):
        self.assertEqual([], asset_manager.validate_manifest({"assets": []}))

    def test_commercial_asset_requires_evidence(self):
        asset = {
            "id": "sample", "file": "assets/sample.png", "source": "Example",
            "source_url": "https://example.com/asset", "downloaded_on": "2026-11-18",
            "license": "CC0", "commercial_use": "allowed"
        }
        errors = asset_manager.validate_asset(asset)
        self.assertTrue(any("license_evidence" in error for error in errors))

    def test_attribution_is_required_when_flagged(self):
        asset = {
            "id": "sample", "file": "assets/sample.png", "source": "Example",
            "source_url": "https://example.com/asset", "downloaded_on": "2026-11-18",
            "license": "CC BY 4.0", "commercial_use": "allowed",
            "license_evidence": "https://example.com/license",
            "attribution_required": True
        }
        self.assertTrue(any("attribution is required" in e for e in asset_manager.validate_asset(asset)))

    def test_duplicate_ids_are_rejected(self):
        item = {
            "id": "same", "file": "assets/a.png", "source": "Example",
            "source_url": "https://example.com/a", "downloaded_on": "2026-11-18",
            "license": "CC0", "commercial_use": "allowed",
            "license_evidence": "https://example.com/license"
        }
        self.assertTrue(any("duplicate asset id" in e for e in asset_manager.validate_manifest({"assets": [item, item]})))


if __name__ == "__main__":
    unittest.main()
