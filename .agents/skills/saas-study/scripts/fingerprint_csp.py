#!/usr/bin/env python3
"""Fingerprint third-party providers from Content-Security-Policy header allowlists.

Why this exists: many SaaS providers (Stripe, Supabase, PostHog, GTM, Pixel, Rewardful,
Chatway, etc.) get allowlisted in the response CSP header even when the browser never
actually fetches from them, or fetches lazily after user interaction. The CSP allowlist
is the *intended* provider list, which is usually broader and more reliable than what
network logs alone capture.

This script does best-effort CSP extraction from two places:
  1. raw/network/sample_*.network-response files where the agent saved response bodies
     that happen to contain a CSP error/echo (sometimes the body of /api/error pages
     includes the CSP).
  2. raw/html/*.html files: looks for inline `<meta http-equiv="Content-Security-Policy">`
     tags (some SaaS use meta CSP instead of/in addition to header CSP).
  3. raw/network/csp-header.txt: a file the agent can manually populate from any
     get_network_request output that included a content-security-policy: header.
     (Recommended workflow: after Phase 3, grep your transcript for "content-security-policy:"
     and paste one full CSP value into raw/network/csp-header.txt.)

Reads:
  <study>/raw/network/csp-header.txt (optional, recommended)
  <study>/raw/html/*.html
  <study>/raw/network/sample_*.network-response

Writes:
  <study>/derived/csp-providers.json

Usage:
  fingerprint_csp.py <study-folder>
"""
from __future__ import annotations
import argparse
import fnmatch
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import known_providers  # noqa: E402


CSP_DIRECTIVES = (
    "script-src",
    "connect-src",
    "frame-src",
    "img-src",
    "style-src",
    "font-src",
    "media-src",
    "worker-src",
    "child-src",
    "object-src",
    "manifest-src",
    "default-src",
)


def extract_csp_from_text(text: str) -> list[str]:
    """Return a list of CSP header-value strings found in `text`."""
    hits: list[str] = []
    # 1. Header-style: 'content-security-policy: <value>' (case-insensitive)
    for m in re.finditer(r"content-security-policy\s*:\s*(.+?)(?=\n[a-z-]+:\s|\n\n|\Z)",
                         text, re.IGNORECASE | re.DOTALL):
        hits.append(m.group(1).strip())
    # 2. Meta-tag style: <meta http-equiv="Content-Security-Policy" content="...">
    for m in re.finditer(r'<meta[^>]+content-security-policy[^>]+content=["\']([^"\']+)["\']',
                         text, re.IGNORECASE):
        hits.append(m.group(1).strip())
    return hits


def parse_csp(csp_value: str) -> dict[str, list[str]]:
    """Parse a CSP header value into {directive: [allowed-hosts]}."""
    out: dict[str, list[str]] = {}
    for chunk in csp_value.split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        parts = chunk.split()
        if not parts:
            continue
        directive = parts[0].lower()
        if directive not in CSP_DIRECTIVES:
            continue
        # Filter out keyword-tokens like 'self', 'unsafe-inline', 'data:', 'blob:', wss/etc.
        sources = []
        for src in parts[1:]:
            s = src.strip("'\"")
            if s in ("self", "unsafe-inline", "unsafe-eval", "none", "strict-dynamic",
                    "data:", "blob:", "https:", "http:", "wss:", "ws:", "filesystem:"):
                continue
            # Strip scheme prefix (NOT lstrip, that strips characters, not prefix)
            for prefix in ("https://", "http://"):
                if s.startswith(prefix):
                    s = s[len(prefix):]
                    break
            # Strip trailing path if any (CSP sources can include paths)
            if "/" in s:
                s = s.split("/", 1)[0]
            sources.append(s)
        out[directive] = sources
    return out


def url_to_host(url_or_pattern: str) -> str:
    """Strip protocol/path. Leave wildcards in place."""
    u = url_or_pattern.strip()
    for prefix in ("https://", "http://"):
        if u.startswith(prefix):
            u = u[len(prefix):]
    # Strip path
    if "/" in u:
        u = u.split("/", 1)[0]
    return u.lower()


def host_matches_pattern(host: str, pattern: str) -> bool:
    """fnmatch with leading-wildcard support."""
    return fnmatch.fnmatch(host, pattern.lower())


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("study")
    args = p.parse_args()

    study = Path(args.study)
    out_path = study / "derived" / "csp-providers.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    sources_scanned: list[str] = []
    csp_values: list[str] = []

    # 1. Dedicated csp-header.txt (highest priority, manually curated by agent)
    csp_txt = study / "raw" / "network" / "csp-header.txt"
    if csp_txt.exists():
        sources_scanned.append(str(csp_txt.relative_to(study)))
        csp_values.extend(extract_csp_from_text(csp_txt.read_text())
                          or [csp_txt.read_text().strip()])

    # 2. raw/html/*.html (meta-csp tag)
    html_dir = study / "raw" / "html"
    if html_dir.exists():
        for h in sorted(html_dir.glob("*.html")):
            try:
                csps = extract_csp_from_text(h.read_text(errors="replace"))
            except Exception:
                continue
            if csps:
                sources_scanned.append(str(h.relative_to(study)))
                csp_values.extend(csps)

    # 3. raw/network/sample_*.network-response (sometimes CSP echoed in error bodies)
    net_dir = study / "raw" / "network"
    if net_dir.exists():
        for f in sorted(net_dir.glob("sample_*.network-response")):
            try:
                csps = extract_csp_from_text(f.read_text(errors="replace"))
            except Exception:
                continue
            if csps:
                sources_scanned.append(str(f.relative_to(study)))
                csp_values.extend(csps)

    # De-dupe CSP values
    csp_values = list({v.strip(): None for v in csp_values}.keys())

    # Aggregate all allowlisted hosts across all observed CSP headers
    allowlisted_hosts: set[str] = set()
    per_directive: dict[str, set[str]] = {}
    for v in csp_values:
        parsed = parse_csp(v)
        for directive, hosts in parsed.items():
            per_directive.setdefault(directive, set()).update(hosts)
            allowlisted_hosts.update(hosts)

    # Match against known_providers
    table = known_providers.load()
    matched: list[dict] = []
    matched_hosts: set[str] = set()

    for category, providers in table["categories"].items():
        for prov in providers:
            evidence_hosts: list[str] = []
            for pat in prov.get("match_hosts", []):
                pat_host = url_to_host(pat)
                for h in allowlisted_hosts:
                    if host_matches_pattern(h, pat_host):
                        evidence_hosts.append(h)
                        matched_hosts.add(h)
            if evidence_hosts:
                matched.append({
                    "provider": prov["name"],
                    "category": category,
                    "csp_hosts": sorted(set(evidence_hosts)),
                    "confidence": "high",
                    "source": "CSP allowlist",
                })

    unmatched = sorted(allowlisted_hosts - matched_hosts)

    out = {
        "csp_sources_scanned": sources_scanned,
        "csp_values_found": len(csp_values),
        "allowlisted_hosts_total": len(allowlisted_hosts),
        "per_directive": {k: sorted(v) for k, v in per_directive.items()},
        "matched_providers": matched,
        "unmatched_hosts": unmatched,
        "note": (
            "CSP allowlists reveal *intended* third-party providers, which is often "
            "broader than what browser network logs capture (many providers fetch lazily "
            "or only on certain user actions). Tip: drop the full content-security-policy "
            "header value into raw/network/csp-header.txt for best-effort matching."
        ),
    }
    out_path.write_text(json.dumps(out, indent=2))
    print(f"✓ csp-providers.json: {len(matched)} providers from CSP "
          f"({len(allowlisted_hosts)} hosts allowlisted across {len(csp_values)} CSP values)",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
