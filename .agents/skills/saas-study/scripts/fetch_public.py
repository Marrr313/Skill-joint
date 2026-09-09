#!/usr/bin/env python3
"""Phase 1: fetch robots.txt + sitemap.xml over stdlib urllib with browser headers.

Usage:
  fetch_public.py <url> <study-folder>

Writes:
  <study>/raw/public/robots.txt
  <study>/raw/public/sitemap.xml          (if found)
  <study>/derived/public-urls.json        (sitemap-derived URLs scored by interest)
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.pacing import jittered_sleep, load_profile  # noqa: E402

# Interest scoring for URL paths (higher = more important to visit in Phase 2)
# Specific patterns first; fallback heuristic for short single-word slugs at the end.
INTEREST_PATTERNS = [
    (re.compile(r"/pricing/?$", re.I), 10, "pricing"),
    (re.compile(r"/plans/?$", re.I), 10, "pricing"),
    (re.compile(r"/about/?$", re.I), 8, "about"),
    (re.compile(r"/features?/?$", re.I), 7, "features"),
    (re.compile(r"/features?/[^/]+/?$", re.I), 7, "feature_detail"),
    (re.compile(r"/demo/?$", re.I), 7, "demo"),
    (re.compile(r"/docs/?$", re.I), 6, "docs_root"),
    (re.compile(r"/changelog/?$", re.I), 6, "changelog"),
    (re.compile(r"/blog/?$", re.I), 5, "blog_index"),
    (re.compile(r"/customers?/?$", re.I), 5, "customers"),
    (re.compile(r"/login/?$", re.I), 4, "login"),
    (re.compile(r"/signup/?$", re.I), 4, "signup"),
    (re.compile(r"/use-cases?/?$", re.I), 4, "use_cases"),
    (re.compile(r"/integrations?/?$", re.I), 4, "integrations"),
    (re.compile(r"/api/?$", re.I), 4, "api_docs"),
    (re.compile(r"/security/?$", re.I), 3, "security"),
    (re.compile(r"/$", re.I), 9, "landing"),
]

# Words that often appear as top-level slugs for feature pages
# (used by the short-slug fallback to upgrade the score).
FEATURE_SLUG_WORDS = {
    # generic SaaS feature words
    "crm", "deals", "pipeline", "inbox", "messages", "calendar", "tasks",
    "contacts", "people", "team", "members", "billing", "payments", "invoices",
    "reports", "analytics", "insights", "stats", "metrics", "dashboard",
    "automations", "workflows", "templates", "library", "assets", "media",
    "discover", "search", "explore", "studio", "editor", "designer",
    # creator/agency-specific (from withjuly study)
    "roster", "talent", "creators", "decks", "mediakits", "press", "rates",
    # commerce
    "shop", "store", "checkout", "cart", "orders", "products",
    # dev/infra
    "playground", "sandbox", "examples", "guides", "tutorials",
}


def short_slug_score(path: str) -> tuple[int, str]:
    """Fallback: short single-word top-level slug (likely a feature page).
    Returns (score, kind). A score of 0 means not a feature page.
    """
    bits = [b for b in path.split("/") if b]
    if len(bits) != 1:
        return 0, "other"
    slug = bits[0].lower()
    if "." in slug:  # not a slug, probably a file
        return 0, "other"
    if len(slug) > 18:  # too long to be a one-word feature name
        return 0, "other"
    if slug in FEATURE_SLUG_WORDS:
        return 8, "feature"          # explicit hit on known feature word
    if 2 <= len(slug) <= 12 and slug.isalpha():
        return 6, "feature_inferred"  # short alphabetic slug, likely a feature
    return 0, "other"


def slug_for(url: str, kind: str) -> str:
    parsed = urlparse(url)
    if parsed.path in ("", "/"):
        return "landing"
    bits = [b for b in parsed.path.split("/") if b]
    base = "-".join(bits[:3])
    return f"{kind}_{base}" if base else kind


def score_url(url: str) -> tuple[int, str]:
    parsed = urlparse(url)
    path = parsed.path or "/"
    for pat, score, kind in INTEREST_PATTERNS:
        if pat.search(path):
            return score, kind
    # Fallback: catches /crm, /mediakits, /payments, /roster style feature pages
    return short_slug_score(path)


def parse_sitemap(xml_bytes: bytes) -> list[str]:
    """Best-effort sitemap parser (handles urlset + sitemapindex)."""
    urls: list[str] = []
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return urls
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    for loc in root.findall(".//sm:url/sm:loc", ns):
        if loc.text:
            urls.append(loc.text.strip())
    # sitemapindex variant: collect child sitemap URLs (caller can choose to fetch)
    for loc in root.findall(".//sm:sitemap/sm:loc", ns):
        if loc.text:
            urls.append(loc.text.strip())
    # also handle raw <loc> without ns
    if not urls:
        for loc in root.findall(".//loc"):
            if loc.text:
                urls.append(loc.text.strip())
    return urls


def parse_robots(robots_text: str) -> tuple[list[str], list[str]]:
    """Return (sitemaps, disallows for *)."""
    sitemaps: list[str] = []
    disallows: list[str] = []
    in_star = False
    for line in robots_text.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip().lower()
        val = val.strip()
        if key == "sitemap":
            sitemaps.append(val)
        elif key == "user-agent":
            in_star = val == "*"
        elif key == "disallow" and in_star and val:
            disallows.append(val)
    return sitemaps, disallows


def path_allowed(path: str, disallows: list[str]) -> bool:
    return not any(path.startswith(d) for d in disallows)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("url")
    p.add_argument("study")
    args = p.parse_args()

    study = Path(args.study)
    public_dir = study / "raw" / "public"
    derived_dir = study / "derived"
    public_dir.mkdir(parents=True, exist_ok=True)
    derived_dir.mkdir(parents=True, exist_ok=True)

    # Determine profile
    profile_name = (study / ".stealth-profile").read_text().strip() if (study / ".stealth-profile").exists() else "balanced"
    profile = load_profile(profile_name)

    base = args.url if "://" in args.url else f"https://{args.url}"
    parsed = urlparse(base)
    origin = f"{parsed.scheme}://{parsed.netloc}"

    # urllib with realistic Chrome headers. TLS impersonation is not needed for
    # robots.txt / sitemap.xml (these are bot-targeted resources, rarely fingerprinted).
    # Substantive page fetches happen via chrome-devtools MCP in the user's real Chrome.
    import urllib.request
    UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    REQUEST_HEADERS = {
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
    }

    def fetch(url: str) -> tuple[int, bytes, dict]:
        req = urllib.request.Request(url, headers=REQUEST_HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                body = resp.read()
                headers = dict(resp.headers)
                return resp.status, body, headers
        except urllib.error.HTTPError as e:
            print(f"info: {url}: HTTP {e.code}", file=sys.stderr)
            return e.code, b"", {}
        except Exception as e:
            print(f"warn: {url}: {e}", file=sys.stderr)
            return 0, b"", {}

    # 1. robots.txt
    robots_url = urljoin(origin + "/", "robots.txt")
    status, body, _ = fetch(robots_url)
    sitemaps_from_robots: list[str] = []
    disallows: list[str] = []
    if status == 200 and body:
        text = body.decode("utf-8", errors="replace")
        (public_dir / "robots.txt").write_text(text)
        sitemaps_from_robots, disallows = parse_robots(text)
    else:
        print(f"info: robots.txt unavailable (status={status})", file=sys.stderr)

    jittered_sleep(profile, "public_fetch_delay_seconds")

    # 2. sitemap.xml: try robots-declared first, then conventional
    sitemap_candidates = sitemaps_from_robots or [urljoin(origin + "/", "sitemap.xml")]
    all_sitemap_urls: list[str] = []
    sitemap_saved = False
    for sm_url in sitemap_candidates[:3]:  # cap to first 3
        s, b, _ = fetch(sm_url)
        if s == 200 and b:
            if not sitemap_saved:
                (public_dir / "sitemap.xml").write_bytes(b)
                sitemap_saved = True
            urls = parse_sitemap(b)
            all_sitemap_urls.extend(urls)
        jittered_sleep(profile, "public_fetch_delay_seconds")

    # 3. Score URLs and write derived/public-urls.json
    # Always include the landing URL itself
    scored = [{"url": base, "score": 9, "kind": "landing", "slug": "landing", "allowed": True}]
    seen = {base.rstrip("/")}
    for u in all_sitemap_urls:
        if u.rstrip("/") in seen:
            continue
        seen.add(u.rstrip("/"))
        score, kind = score_url(u)
        if score == 0:
            continue
        parsed_u = urlparse(u)
        # Only consider same-origin URLs
        if parsed_u.netloc != parsed.netloc:
            continue
        allowed = path_allowed(parsed_u.path, disallows)
        scored.append({
            "url": u,
            "score": score,
            "kind": kind,
            "slug": slug_for(u, kind),
            "allowed": allowed,
        })

    scored.sort(key=lambda x: (-x["score"], x["url"]))

    out = {
        "origin": origin,
        "robots_disallows": disallows,
        "sitemap_count": len(all_sitemap_urls),
        "urls": scored[:30],  # cap to 30
    }
    (derived_dir / "public-urls.json").write_text(json.dumps(out, indent=2))

    print(f"✓ fetched robots.txt ({'ok' if (public_dir / 'robots.txt').exists() else 'missing'})", file=sys.stderr)
    print(f"✓ fetched sitemap ({'ok' if sitemap_saved else 'missing'}), {len(all_sitemap_urls)} URLs parsed", file=sys.stderr)
    print(f"✓ wrote {len(out['urls'])} scored URLs to derived/public-urls.json", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
