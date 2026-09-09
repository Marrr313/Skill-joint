#!/usr/bin/env python3
"""Heuristic pricing extraction from raw/html/pricing*.html.

Reads:
  <study>/raw/html/pricing.html (or pricing-*.html, plans.html, etc.)
  <study>/extracted/pricing.md  (fallback if html-based extraction fails)

Writes:
  <study>/derived/pricing.json

Usage:
  extract_pricing.py <study-folder>

Note: pricing pages vary wildly. This is best-effort. The structured output should
always be cross-checked against extracted/pricing.md (Tier 2 read).
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

PRICE_RE = re.compile(r"(?:\$|€|£)\s?(\d{1,4}(?:[.,]\d{2})?)\s*(?:/(mo|month|yr|year)|\bper\b\s+(month|year|mo|yr|seat|user))?", re.I)
TIER_NAME_HINTS = re.compile(r"\b(free|starter|basic|pro|plus|premium|business|team|enterprise|scale|growth|standard|advanced|ultimate|hobby|individual)\b", re.I)
TRIAL_RE = re.compile(r"(\d+)\s*[-\s]*day(?:s)?\s+(?:free\s+)?trial", re.I)
CADENCE_RE = re.compile(r"\b(monthly|yearly|annually|annual|per month|per year)\b", re.I)
CREDIT_RE = re.compile(r"(\d{1,5}(?:,\d{3})*)\s*credits?(?:/(?:mo|month|yr|year))?", re.I)


def find_pricing_html(study: Path) -> Path | None:
    html_dir = study / "raw" / "html"
    if not html_dir.exists():
        return None
    for name in ("pricing.html", "plans.html"):
        f = html_dir / name
        if f.exists():
            return f
    for f in html_dir.glob("*pricing*.html"):
        return f
    for f in html_dir.glob("*plans*.html"):
        return f
    return None


def find_pricing_md(study: Path) -> Path | None:
    md_dir = study / "extracted"
    if not md_dir.exists():
        return None
    for name in ("pricing.md", "plans.md"):
        f = md_dir / name
        if f.exists():
            return f
    for f in md_dir.glob("*pricing*.md"):
        return f
    return None


def extract_tiers_from_html(html: str) -> list[dict]:
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return []
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    tiers: list[dict] = []
    # Look for repeated card-like containers with a price + tier name
    candidates = soup.find_all(["div", "article", "section", "li"])
    for c in candidates:
        text = c.get_text(" ", strip=True)
        if len(text) < 20 or len(text) > 1500:
            continue
        price_match = PRICE_RE.search(text)
        name_match = TIER_NAME_HINTS.search(text)
        if not (price_match and name_match):
            continue
        # Avoid huge ancestors that contain multiple tiers
        if len(c.find_all(["h2", "h3"])) > 3:
            continue
        # Tier name: nearest heading text
        heading_el = c.find(["h1", "h2", "h3", "h4"])
        tier_name = (heading_el.get_text(strip=True) if heading_el else name_match.group(1).title())[:50]
        # Avoid duplicate tier-name capture
        if any(t["name"].lower() == tier_name.lower() for t in tiers):
            continue
        # Features: bullet-ish text within card
        features = []
        for li in c.find_all("li")[:12]:
            t = li.get_text(" ", strip=True)
            if 3 < len(t) < 200:
                features.append(t)
        # All prices in card
        all_prices = []
        for m in PRICE_RE.finditer(text):
            amt = m.group(1)
            cadence = (m.group(2) or m.group(3) or "").lower()
            cadence = "month" if cadence.startswith("m") else ("year" if cadence.startswith(("y", "a")) else "")
            all_prices.append({"amount": amt, "cadence": cadence})
        # Credit hints
        credits = None
        cm = CREDIT_RE.search(text)
        if cm:
            credits = cm.group(1).replace(",", "")

        tier = {
            "name": tier_name,
            "prices": all_prices[:3],
            "price_monthly": next((p["amount"] for p in all_prices if p["cadence"] == "month"), all_prices[0]["amount"] if all_prices else None),
            "price_yearly": next((p["amount"] for p in all_prices if p["cadence"] == "year"), None),
            "credits": credits,
            "features": features[:8],
        }
        tiers.append(tier)
        if len(tiers) >= 6:
            break
    return tiers


def extract_meta_from_text(text: str) -> dict:
    out = {}
    tm = TRIAL_RE.search(text)
    if tm:
        out["trial"] = f"{tm.group(1)}-day"
    cadences = sorted({m.group(1).lower() for m in CADENCE_RE.finditer(text)})
    if cadences:
        out["cadence"] = cadences
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("study")
    args = p.parse_args()

    study = Path(args.study)
    out = {"tiers": [], "trial": None, "cadence": [], "source": None}

    html_path = find_pricing_html(study)
    if html_path:
        html = html_path.read_text(encoding="utf-8", errors="replace")
        out["tiers"] = extract_tiers_from_html(html)
        out.update(extract_meta_from_text(html))
        out["source"] = f"raw/html/{html_path.name}"
    else:
        md_path = find_pricing_md(study)
        if md_path:
            md = md_path.read_text()
            # Very lightweight tier extraction from markdown
            for line in md.splitlines():
                pm = PRICE_RE.search(line)
                nm = TIER_NAME_HINTS.search(line)
                if pm and nm:
                    out["tiers"].append({
                        "name": nm.group(1).title(),
                        "price_monthly": pm.group(1),
                        "price_yearly": None,
                        "features": [],
                    })
            out.update(extract_meta_from_text(md))
            out["source"] = f"extracted/{md_path.name}"

    (study / "derived" / "pricing.json").write_text(json.dumps(out, indent=2))
    print(f"✓ pricing.json: {len(out['tiers'])} tiers detected "
          f"(source={out['source'] or 'none'})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
