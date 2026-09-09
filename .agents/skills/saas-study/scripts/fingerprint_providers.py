#!/usr/bin/env python3
"""Match unique network hosts against references/providers.json.

Reads:
  <study>/derived/network-summary.json

Writes:
  <study>/derived/providers.json

Usage:
  fingerprint_providers.py <study-folder>
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import known_providers  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("study")
    args = p.parse_args()

    study = Path(args.study)
    summary_path = study / "derived" / "network-summary.json"
    if not summary_path.exists():
        print(f"error: {summary_path} not found. Run scrub_network.py first.", file=sys.stderr)
        return 1

    summary = json.loads(summary_path.read_text())
    entries = summary.get("entries", [])
    unique_hosts = summary.get("unique_hosts", [])

    table = known_providers.load()
    categories = table["categories"]

    detail = []
    detected_hosts: set[str] = set()

    for category, providers in categories.items():
        for prov in providers:
            evidence = []
            hosts_pat = prov.get("match_hosts", [])
            path_hint = prov.get("path_hint")
            for e in entries:
                host = e["host"]
                if not host:
                    continue
                if hosts_pat and known_providers.host_matches(host, hosts_pat):
                    if path_hint and path_hint not in e["path"]:
                        continue
                    evidence.append({
                        "host": host,
                        "path": e["path"][:80],
                        "method": e["method"],
                        "status": e.get("status"),
                    })
                    detected_hosts.add(host)
            if evidence:
                detail.append({
                    "provider": prov["name"],
                    "category": category,
                    "confidence": "high" if len(evidence) >= 2 else "moderate",
                    "evidence": evidence[:5],
                })

    # Summary view: category -> [provider names]
    summary_view: dict[str, list[str]] = {}
    for d in detail:
        summary_view.setdefault(d["category"], []).append(d["provider"])
    for k in summary_view:
        summary_view[k] = sorted(set(summary_view[k]))

    # Unmatched hosts (likely the SaaS's own first-party hosts + uncategorized)
    unmatched = sorted(set(unique_hosts) - detected_hosts)

    out = {
        "summary": summary_view,
        "detail": detail,
        "unmatched_hosts": unmatched,
        "total_providers_detected": len(detail),
    }
    (study / "derived" / "providers.json").write_text(json.dumps(out, indent=2))
    print(f"✓ providers.json: {len(detail)} providers detected across "
          f"{len(summary_view)} categories ({len(unmatched)} unmatched hosts)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
