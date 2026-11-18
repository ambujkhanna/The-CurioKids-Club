"""Validate provenance and publication rights for reusable visual assets.

The manifest is intentionally local and dependency-free. It does not download assets
or infer rights from a provider name: each asset must record its own licence evidence.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_MANIFEST = os.path.join(ROOT, "assets", "manifest.json")
REQUIRED = ("id", "file", "source", "source_url", "downloaded_on", "license", "commercial_use")
VALID_COMMERCIAL = {"allowed", "not_allowed", "unverified"}


def load_manifest(path=DEFAULT_MANIFEST):
    with open(path, encoding="utf-8") as stream:
        data = json.load(stream)
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("manifest must be an object with schema_version=1")
    if not isinstance(data.get("assets"), list):
        raise ValueError("manifest.assets must be a list")
    return data


def validate_asset(asset, index=0):
    errors = []
    if not isinstance(asset, dict):
        return [f"assets[{index}] must be an object"]
    for field in REQUIRED:
        if not asset.get(field):
            errors.append(f"assets[{index}].{field} is required")
    if asset.get("commercial_use") not in VALID_COMMERCIAL:
        errors.append(f"assets[{index}].commercial_use must be one of {sorted(VALID_COMMERCIAL)}")
    if asset.get("commercial_use") == "allowed" and not asset.get("license_evidence"):
        errors.append(f"assets[{index}].license_evidence is required when commercial_use=allowed")
    if asset.get("attribution_required") is True and not asset.get("attribution"):
        errors.append(f"assets[{index}].attribution is required when attribution_required=true")
    if asset.get("file") and not os.path.isabs(asset["file"]):
        full = os.path.abspath(os.path.join(ROOT, asset["file"]))
        if not full.startswith(ROOT + os.sep) and full != ROOT:
            errors.append(f"assets[{index}].file must stay inside the repository")
    return errors


def validate_manifest(data):
    errors = []
    seen = set()
    for index, asset in enumerate(data["assets"]):
        errors.extend(validate_asset(asset, index))
        if isinstance(asset, dict) and asset.get("id"):
            if asset["id"] in seen:
                errors.append(f"duplicate asset id: {asset['id']}")
            seen.add(asset["id"])
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", nargs="?", default=DEFAULT_MANIFEST)
    args = parser.parse_args(argv)
    try:
        data = load_manifest(args.manifest)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Invalid asset manifest: {exc}", file=sys.stderr)
        return 1
    errors = validate_manifest(data)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Asset manifest OK: {len(data['assets'])} asset(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
