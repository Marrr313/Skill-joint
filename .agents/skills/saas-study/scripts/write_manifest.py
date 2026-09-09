#!/usr/bin/env python3
"""Update <study>/study.json with current artifact list + counts.

Reads:
  All files in <study>/
  <study>/derived/*.json

Writes:
  <study>/study.json (preserves user-set fields like created_at, duration_seconds)

Usage:
  write_manifest.py <study-folder>
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.token_estimate import estimate  # noqa: E402

TIER_BY_FOLDER = {
    "": 1,
    "derived": 1,
    "extracted": 2,
    "screenshots": 3,
    "raw": 3,
    "notes": 1,
}

TOP_LEVEL_TIER1 = {"GAMEPLAN.md", "GAMEPLAN-EXECUTED.md", "BRIEF.md", "study.json"}


def relative(p: Path, study: Path) -> str:
    return str(p.relative_to(study))


def tier_for(rel_path: str) -> int:
    if rel_path in TOP_LEVEL_TIER1:
        return 1
    first = rel_path.split("/", 1)[0]
    return TIER_BY_FOLDER.get(first, 2)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("study")
    args = p.parse_args()

    study = Path(args.study)
    manifest_path = study / "study.json"
    if not manifest_path.exists():
        print(f"error: {manifest_path} not found. Run new_study.py first.", file=sys.stderr)
        return 1

    manifest = json.loads(manifest_path.read_text())

    artifacts: dict[str, dict] = {}
    for f in sorted(study.rglob("*")):
        if not f.is_file():
            continue
        if f.name == "study.json":
            continue
        if f.name.startswith(".") and f.parent == study:
            continue
        rel = relative(f, study)
        artifacts[rel] = {
            "tier": tier_for(rel),
            "size_bytes": f.stat().st_size,
            "tokens_est": estimate(f),
        }

    manifest["artifacts"] = artifacts

    # Counts
    counts = manifest.get("counts", {})
    counts["screenshots"] = sum(1 for k in artifacts if k.startswith("screenshots/") and k.endswith(".png"))
    counts["html_pages"] = sum(1 for k in artifacts if k.startswith("raw/html/") and k.endswith(".html"))
    counts["public_pages"] = sum(1 for k in artifacts if k.startswith("raw/html/") and not k.startswith("raw/html/step-") and not k.startswith("raw/html/post-login"))
    counts["authed_pages"] = sum(1 for k in artifacts if k.startswith("raw/html/step-") or k.startswith("raw/html/post-login"))

    # From derived files
    try:
        prov = json.loads((study / "derived" / "providers.json").read_text())
        counts["providers_detected"] = prov.get("total_providers_detected", 0)
    except FileNotFoundError:
        pass
    try:
        eps = json.loads((study / "derived" / "api-endpoints.json").read_text())
        counts["endpoints_observed"] = eps.get("total_own_endpoints", 0)
    except FileNotFoundError:
        pass
    try:
        netsum = json.loads((study / "derived" / "network-summary.json").read_text())
        counts["unique_hosts"] = len(netsum.get("unique_hosts", []))
    except FileNotFoundError:
        pass

    manifest["counts"] = counts

    # Auth used = there's an authed.json or post-login.* file
    manifest["auth_used"] = any(
        k.startswith("raw/network/authed") or k.startswith("raw/html/post-login") or k.startswith("raw/html/step-")
        for k in artifacts
    )

    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"✓ study.json: {len(artifacts)} artifacts tracked", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
