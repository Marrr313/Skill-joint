#!/usr/bin/env python3
"""Group network entries into the SaaS's own-host API endpoint inventory.

Reads:
  <study>/derived/network-summary.json
  <study>/derived/providers.json   (to identify which hosts are third-party)
  <study>/study.json               (to know the SaaS's domain)

Writes:
  <study>/derived/api-endpoints.json

Usage:
  extract_endpoints.py <study-folder>
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("study")
    args = p.parse_args()

    study = Path(args.study)
    summary = json.loads((study / "derived" / "network-summary.json").read_text())
    manifest = json.loads((study / "study.json").read_text())
    domain = manifest["domain"]

    # Identify third-party hosts (matched providers)
    third_party_hosts: set[str] = set()
    providers_path = study / "derived" / "providers.json"
    if providers_path.exists():
        providers = json.loads(providers_path.read_text())
        for d in providers.get("detail", []):
            for ev in d.get("evidence", []):
                if ev.get("host"):
                    third_party_hosts.add(ev["host"])

    own_hosts: dict[str, list[dict]] = {}
    third_party_unmatched: dict[str, int] = {}

    for e in summary.get("entries", []):
        host = e["host"]
        if not host:
            continue
        # Own host: matches domain (apex or any subdomain)
        is_own = host == domain or host.endswith("." + domain)
        if is_own:
            own_hosts.setdefault(host, []).append(e)
        elif host in third_party_hosts:
            continue  # already accounted for in providers.json
        else:
            third_party_unmatched[host] = third_party_unmatched.get(host, 0) + e.get("seen_count", 1)

    # Group endpoints per own-host by (method, path)
    endpoints_by_host: dict[str, dict] = {}
    for host, entries in own_hosts.items():
        groups: dict[tuple, dict] = {}
        for e in entries:
            key = (e["method"], e["path"])
            if key in groups:
                groups[key]["seen_count"] += e.get("seen_count", 1)
            else:
                groups[key] = {
                    "method": e["method"],
                    "path": e["path"],
                    "seen_count": e.get("seen_count", 1),
                    "content_type": e.get("content_type", ""),
                    "last_status": e.get("status"),
                }
        endpoints_by_host[host] = {
            "endpoints": sorted(
                groups.values(),
                key=lambda x: (-x["seen_count"], x["method"], x["path"]),
            ),
            "endpoint_count": len(groups),
        }

    out = {
        "own_domain": domain,
        "own_hosts": sorted(own_hosts.keys()),
        "endpoints_by_host": endpoints_by_host,
        "total_own_endpoints": sum(h["endpoint_count"] for h in endpoints_by_host.values()),
        "third_party_unmatched": sorted(
            ({"host": h, "request_count": c} for h, c in third_party_unmatched.items()),
            key=lambda x: -x["request_count"],
        )[:30],
    }
    (study / "derived" / "api-endpoints.json").write_text(json.dumps(out, indent=2))
    print(f"✓ api-endpoints.json: {out['total_own_endpoints']} own endpoints across "
          f"{len(out['own_hosts'])} hosts; {len(out['third_party_unmatched'])} unmatched 3p hosts", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
