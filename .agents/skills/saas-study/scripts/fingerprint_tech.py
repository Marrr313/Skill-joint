#!/usr/bin/env python3
"""Framework / hosting detection from HTML + (when available) response headers.

Reads:
  <study>/raw/html/*.html
  <study>/derived/network-summary.json   (for response headers, best effort)
  <study>/raw/network/*.json|*.har        (for response headers fallback)

Writes:
  <study>/derived/tech-fingerprint.json

Usage:
  fingerprint_tech.py <study-folder>
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path


def detect_from_html(html: str) -> dict:
    out = {}
    # Next.js: handle both Pages Router (emits __NEXT_DATA__) and App Router (no __NEXT_DATA__, only RSC chunks)
    if "__NEXT_DATA__" in html:
        out["frontend_framework"] = "Next.js (Pages Router)"
        m = re.search(r'"buildId":"([^"]+)"', html)
        if m:
            out["next_build_id"] = m.group(1)
        m = re.search(r"/_next/static/", html)
        if m:
            out.setdefault("build_signals", []).append("_next/static")
    elif "/_next/static/chunks/" in html:
        # App Router signature: RSC + server actions; no __NEXT_DATA__ blob
        out["frontend_framework"] = "Next.js (App Router)"
        out.setdefault("build_signals", []).append("_next/static (App Router)")
        # Detect route groups visible in chunk paths like /_next/static/chunks/app/(logged-out)/layout-*.js
        groups = set(re.findall(r"/_next/static/chunks/app/\(([^)]+)\)/", html))
        if groups:
            out["next_route_groups"] = sorted(groups)
    # Nuxt
    if "__NUXT__" in html or "/_nuxt/" in html:
        out["frontend_framework"] = "Nuxt"
        out.setdefault("build_signals", []).append("_nuxt")
    # Astro
    if "astro-island" in html or "/_astro/" in html:
        out["frontend_framework"] = "Astro"
        out.setdefault("build_signals", []).append("astro")
    # SvelteKit
    if "data-sveltekit" in html or "/_app/immutable/" in html:
        out["frontend_framework"] = "SvelteKit"
    # Remix
    if "__remixContext" in html or "__remixManifest" in html:
        out["frontend_framework"] = "Remix"
    # Gatsby
    if "___gatsby" in html or "/page-data/" in html:
        out["frontend_framework"] = "Gatsby"
    # Vite (build only, not framework)
    if 'src="/assets/index-' in html or 'crossorigin src="/assets/' in html:
        out.setdefault("build_signals", []).append("vite_assets")
    # Webflow
    if "webflow" in html.lower() or "w-mod-js" in html or 'data-wf-page' in html:
        out["frontend_framework"] = out.get("frontend_framework") or "Webflow"
        out.setdefault("build_signals", []).append("webflow")
    # WordPress
    if "wp-content/" in html or "wp-includes/" in html or 'name="generator" content="WordPress' in html:
        out["frontend_framework"] = "WordPress"
    # Squarespace
    if "squarespace.com" in html and "Static.SQUARESPACE_CONTEXT" in html:
        out["frontend_framework"] = "Squarespace"
    # Framer
    if "framerusercontent.com" in html:
        out.setdefault("build_signals", []).append("framer_assets")

    # CSS framework
    if re.search(r'class="[^"]*\b(?:flex|grid|p-\d|m-\d|text-(?:xs|sm|base|lg|xl)|bg-(?:white|gray|black|blue|red|green)|rounded(?:-(?:sm|md|lg|xl|full))?|w-\d+|h-\d+)\b', html):
        if html.count('class="') > 30:
            out["css_framework"] = "Tailwind (heuristic)"
    if "bootstrap" in html.lower() and "container-fluid" in html.lower():
        out["css_framework"] = out.get("css_framework") or "Bootstrap"
    if "chakra-ui" in html or "css-chakra" in html:
        out["css_framework"] = "Chakra UI"
    if "MuiButton" in html or "css-mui" in html:
        out["css_framework"] = "Material UI"
    # Mantine: emits data-mantine-color-scheme on <html> and m_<hash> class prefixes on every component
    if "data-mantine-color-scheme" in html or "mantine-Input-input" in html or "mantine-Button-root" in html:
        out["ui_library"] = "Mantine"
    # shadcn/ui leaves no fingerprint by design (it's copy-paste Tailwind), but Radix primitives do
    if "data-radix-collection-item" in html or "data-state=\"open\"" in html or "@radix-ui" in html:
        out.setdefault("ui_library", "Radix UI (likely shadcn/ui)")

    # Generator meta
    gen = re.search(r'<meta\s+name="generator"\s+content="([^"]+)"', html, re.I)
    if gen:
        out["generator_meta"] = gen.group(1)

    return out


def detect_from_headers(all_headers: list[dict]) -> dict:
    """all_headers = list of header dicts (one per response).
    Returns hosting/CDN/server signals."""
    out = {}
    seen = {k.lower(): v for h in all_headers for k, v in (h or {}).items()}
    server = (seen.get("server") or "").lower()
    via = (seen.get("via") or "").lower()
    report_to = (seen.get("report-to") or "").lower()

    if "x-vercel-id" in seen or "x-vercel-cache" in seen or server == "vercel":
        out["hosting"] = "Vercel"
        # Extract region from x-vercel-id, format: region::region::worker-id (e.g. "sfo1::sfo1::stdrs-...")
        vid = seen.get("x-vercel-id", "")
        if vid and "::" in vid:
            out["vercel_region"] = vid.split("::")[0]
    elif "x-nf-request-id" in seen or server == "netlify":
        out["hosting"] = "Netlify"
    elif "x-render-origin-server" in seen:
        out["hosting"] = "Render"
    elif "fly-request-id" in seen:
        out["hosting"] = "Fly.io"
    elif "x-railway-edge" in seen or "x-railway-request-id" in seen:
        out["hosting"] = "Railway"
    elif (server == "heroku"
          or "heroku-router" in via
          or "vegur" in via
          or "heroku-nel" in report_to):
        # Heroku: multiple signals; modern apps have `server: Heroku` + `via: 2.0 heroku-router`
        out["hosting"] = "Heroku"
    if "cf-ray" in seen:
        out["cdn"] = "Cloudflare"
    elif "x-amz-cf-id" in seen:
        out["cdn"] = "AWS CloudFront"
    elif "fastly-debug-digest" in seen:
        out["cdn"] = "Fastly"
    if "server" in seen:
        out["server_header"] = seen["server"]
    if "x-powered-by" in seen:
        out["x_powered_by"] = seen["x-powered-by"]
    return out


def detect_api_style(network_summary: dict) -> dict:
    """Detect API style (REST / tRPC / GraphQL / Hasura) from observed paths.

    Reads network-summary.json's entries and matches path patterns.
    """
    out = {}
    if not network_summary:
        return out
    entries = network_summary.get("entries", [])
    if not entries:
        return out

    trpc_count = sum(1 for e in entries if "/api/trpc/" in e.get("path", ""))
    graphql_count = sum(1 for e in entries if e.get("path", "").rstrip("/").endswith("/graphql"))
    hasura_count = sum(1 for e in entries if "/v1/graphql" in e.get("path", ""))
    # REST = api paths that are NOT trpc/graphql
    rest_count = sum(1 for e in entries
                     if "/api/" in e.get("path", "")
                     and "/api/trpc/" not in e.get("path", "")
                     and not e.get("path", "").endswith("/graphql"))

    counts = {"tRPC": trpc_count, "GraphQL": graphql_count, "Hasura": hasura_count, "REST": rest_count}
    counts = {k: v for k, v in counts.items() if v > 0}
    if not counts:
        return out
    # Dominant style = highest count
    dominant = max(counts, key=counts.get)
    out["api_style"] = dominant
    out["api_style_counts"] = counts

    # If tRPC, extract router names (the part before the first dot)
    if dominant == "tRPC":
        routers = set()
        for e in entries:
            path = e.get("path", "")
            m = re.match(r"^/api/trpc/([^?]+)", path)
            if m:
                proc = m.group(1)  # e.g., "agency.talent.root.list"
                router = proc.split(".")[0]
                routers.add(router)
        if routers:
            out["trpc_top_routers"] = sorted(routers)[:15]
    return out


def detect_hosting_from_paths(network_summary: dict) -> dict:
    """Fallback hosting detection from URL paths when response headers aren't available."""
    out = {}
    if not network_summary:
        return out
    entries = network_summary.get("entries", [])
    hosts = network_summary.get("unique_hosts", [])

    if any("/_vercel/insights" in e.get("path", "") for e in entries):
        out["hosting"] = "Vercel"
    if any(h.endswith(".cloudfront.net") for h in hosts):
        out.setdefault("cdn", "AWS CloudFront")
    if any(h.endswith(".cloudflarestorage.com") or h.endswith(".r2.dev") for h in hosts):
        out["object_storage"] = "Cloudflare R2"
    if any(h.endswith(".amazonaws.com") and ".s3" in h for h in hosts):
        out["object_storage"] = "AWS S3"

    return out


def collect_response_headers(study: Path) -> list[dict]:
    """Best-effort: walk raw/network/*.json|*.har for response headers."""
    headers_lists: list[dict] = []
    netdir = study / "raw" / "network"
    if not netdir.exists():
        return headers_lists
    for f in list(netdir.glob("*.json")) + list(netdir.glob("*.har")):
        try:
            data = json.loads(f.read_text())
        except Exception:
            continue
        # HAR
        if isinstance(data, dict) and "log" in data:
            for e in data["log"].get("entries", []):
                hdrs = (e.get("response") or {}).get("headers") or []
                d = {}
                for h in hdrs:
                    if isinstance(h, dict) and "name" in h:
                        d[h["name"]] = h.get("value", "")
                if d:
                    headers_lists.append(d)
        # chrome-devtools dump (list of requests with responseHeaders)
        elif isinstance(data, list):
            for e in data:
                if isinstance(e, dict):
                    hdrs = e.get("responseHeaders") or e.get("response_headers") or {}
                    if isinstance(hdrs, list):
                        d = {h.get("name", ""): h.get("value", "") for h in hdrs if isinstance(h, dict)}
                    elif isinstance(hdrs, dict):
                        d = hdrs
                    else:
                        d = {}
                    if d:
                        headers_lists.append(d)
    return headers_lists


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("study")
    args = p.parse_args()

    study = Path(args.study)
    out: dict = {}

    # 1. HTML-based detection: collect per-file findings then merge with marketing/app distinction
    html_dir = study / "raw" / "html"
    if html_dir.exists():
        priority = ["landing.html", "post-login.html", "login.html"]
        candidates = []
        seen_paths = set()
        for name in priority:
            f = html_dir / name
            if f.exists():
                candidates.append(f)
                seen_paths.add(f)
        for f in sorted(html_dir.glob("*.html")):
            if f not in seen_paths:
                candidates.append(f)

        per_file: list[tuple[str, dict]] = []
        for f in candidates[:8]:
            try:
                html = f.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            per_file.append((f.name, detect_from_html(html)))

        merged: dict = {}
        frameworks_seen: dict[str, str] = {}  # framework name -> first file that detected it
        for fname, detected in per_file:
            for k, v in detected.items():
                if k == "build_signals":
                    merged.setdefault("build_signals", [])
                    for s in v:
                        if s not in merged["build_signals"]:
                            merged["build_signals"].append(s)
                elif k == "frontend_framework":
                    # Collect ALL frameworks seen across pages (marketing site + authed app often differ)
                    if v not in frameworks_seen:
                        frameworks_seen[v] = fname
                elif k not in merged:
                    merged[k] = v

        if frameworks_seen:
            # Primary framework = first detected (usually landing.html → marketing site)
            primary = list(frameworks_seen.keys())[0]
            merged["frontend_framework"] = primary
            # If multiple frameworks detected (common: Astro marketing + Next.js app), surface them
            if len(frameworks_seen) > 1:
                merged["frontend_frameworks_by_file"] = [
                    {"framework": fw, "first_seen_in": fname} for fw, fname in frameworks_seen.items()
                ]
                # Heuristic: if landing.html shows X but login.html/post-login.html shows Y,
                # X is the marketing-site framework and Y is the app framework.
                marketing_fw = None
                app_fw = None
                for fw, fname in frameworks_seen.items():
                    if fname == "landing.html":
                        marketing_fw = fw
                    elif fname in ("login.html", "post-login.html"):
                        app_fw = fw
                if marketing_fw and app_fw and marketing_fw != app_fw:
                    merged["marketing_site_framework"] = marketing_fw
                    merged["app_framework"] = app_fw

        out.update(merged)

    # 2. Header-based detection
    hdrs = collect_response_headers(study)
    out.update(detect_from_headers(hdrs))

    # 3. API style + path-based hosting fallback (driven by network-summary.json)
    summary_path = study / "derived" / "network-summary.json"
    network_summary = {}
    if summary_path.exists():
        try:
            network_summary = json.loads(summary_path.read_text())
        except Exception:
            pass
    out.update(detect_api_style(network_summary))
    # path-based hosting: only fills gaps left by header detection
    path_based = detect_hosting_from_paths(network_summary)
    for k, v in path_based.items():
        if k not in out:
            out[k] = v

    if not out:
        out["frontend_framework"] = "unknown"

    (study / "derived" / "tech-fingerprint.json").write_text(json.dumps(out, indent=2))
    print(f"✓ tech-fingerprint.json: framework={out.get('frontend_framework')}, "
          f"api={out.get('api_style', 'unknown')}, "
          f"hosting={out.get('hosting', 'unknown')}, "
          f"cdn={out.get('cdn', 'unknown')}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
