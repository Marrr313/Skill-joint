#!/usr/bin/env python3
"""Render BRIEF.md from manifest + derived JSONs using the Jinja2 template.

Reads:
  <study>/study.json
  <study>/derived/{providers,pricing,tech-fingerprint,api-endpoints,action-trace.jsonl}.json
  <study>/extracted/landing.md           (for tagline)
  templates/BRIEF.md.j2

Writes:
  <study>/BRIEF.md

Usage:
  render_brief.py <study-folder>
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = SKILL_ROOT / "templates" / "BRIEF.md.j2"


def load_json(p: Path, default):
    if p.exists():
        try:
            return json.loads(p.read_text())
        except ValueError:
            return default
    return default


def extract_tagline(landing_md: Path) -> str | None:
    if not landing_md.exists():
        return None
    text = landing_md.read_text()
    # First non-trivial heading or first decent paragraph
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("<!--"):
            continue
        if line.startswith("#"):
            cleaned = re.sub(r"^#+\s*", "", line).strip()
            if 5 < len(cleaned) < 140:
                return cleaned
        elif len(line) > 15 and len(line) < 180 and not line.startswith(("|", "-", "*", ">")):
            return line[:140]
    return None


def derive_features(extracted_dir: Path) -> list[dict]:
    """Derive a feature list from filenames in extracted/."""
    if not extracted_dir.exists():
        return []
    features = []
    skip = {"landing", "about", "pricing", "blog-index", "blog", "changelog",
            "docs-index", "docs", "post-login", "action-map", "robots",
            "sitemap", "terms", "privacy", "security", "contact", "login",
            "signup", "customers"}
    for md in sorted(extracted_dir.glob("*.md")):
        stem = md.stem.lower()
        if stem in skip or stem.startswith("step-"):
            continue
        # Skip nav-junk
        if any(part in stem for part in ("404", "thanks", "legal")):
            continue
        features.append({
            "name": md.stem.replace("-", " ").title(),
            "evidence": f"extracted/{md.name}",
            "path": None,
        })
    return features[:12]


def derive_tech_view(tech: dict) -> dict:
    if not tech:
        return {"detected": "unknown"}
    view = {}
    for k in ("frontend_framework", "css_framework", "api_style", "hosting", "cdn",
              "object_storage", "server_header", "x_powered_by", "next_build_id",
              "generator_meta"):
        if tech.get(k):
            view[k.replace("_", " ").title()] = tech[k]
    if tech.get("trpc_top_routers"):
        view["TRPC Routers"] = ", ".join(tech["trpc_top_routers"])
    if tech.get("api_style_counts"):
        # Pretty-print as "tRPC=31, REST=9"
        view["API Style Counts"] = ", ".join(f"{k}={v}" for k, v in tech["api_style_counts"].items())
    if tech.get("build_signals"):
        view["Build signals"] = ", ".join(tech["build_signals"])
    return view


def derive_shape_findings(shapes: dict) -> list[dict]:
    """Format data-shape fingerprint findings for the brief."""
    if not shapes or not shapes.get("findings"):
        return []
    out = []
    for f in shapes["findings"]:
        out.append({
            "vendor": f["vendor"],
            "category": f["category"],
            "confidence": f["confidence"],
            "score": f.get("best_score", 0),
            "description": f.get("description", ""),
        })
    return out


def derive_authed_surfaces(study: Path) -> list[str]:
    """List authed pages captured."""
    out = []
    html_dir = study / "raw" / "html"
    if not html_dir.exists():
        return out
    for f in sorted(html_dir.glob("*.html")):
        if f.name.startswith("step-") or f.name == "post-login.html":
            out.append(f.stem)
    return out[:20]


def derive_standout_actions(trace_path: Path, max_n: int = 5) -> list[dict]:
    if not trace_path.exists():
        return []
    actions = []
    for line in trace_path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if e.get("type") != "action":
            continue
        if not e.get("endpoints"):
            continue
        actions.append({
            "label": e.get("label") or "(unlabeled)",
            "page": e.get("url", ""),
            "endpoints": e["endpoints"],
        })
    # Sort by number of endpoints (rough interest proxy)
    actions.sort(key=lambda a: -len(a["endpoints"]))
    return actions[:max_n]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("study")
    args = p.parse_args()

    study = Path(args.study)
    manifest = load_json(study / "study.json", {})

    try:
        from jinja2 import Template
    except ImportError:
        print("error: jinja2 not installed. Run scripts/install.sh", file=sys.stderr)
        return 1

    ctx = {
        "domain": manifest.get("domain", "(unknown)"),
        "study_date": manifest.get("study_date", ""),
        "study_version": manifest.get("study_version", "1.0"),
        "stealth_profile": manifest.get("stealth_profile", "balanced"),
        "auth_used": manifest.get("auth_used", False),
        "counts": manifest.get("counts", {}),
        "tagline": extract_tagline(study / "extracted" / "landing.md"),
        "features": derive_features(study / "extracted"),
        "tech": derive_tech_view(load_json(study / "derived" / "tech-fingerprint.json", {})),
        "providers": load_json(study / "derived" / "providers.json", {"summary": {}}),
        "shape_findings": derive_shape_findings(load_json(study / "derived" / "data-shape-fingerprints.json", {})),
        "own_api": load_json(study / "derived" / "api-endpoints.json", {"endpoints_by_host": {}}),
        "pricing": load_json(study / "derived" / "pricing.json", {"tiers": [], "trial": None, "cadence": []}),
        "authed_surfaces": derive_authed_surfaces(study),
        "standout_actions": derive_standout_actions(study / "derived" / "action-trace.jsonl"),
        "analysis_exists": (study / "ANALYSIS.md").exists(),
        "derived_folder_path": f"../{manifest.get('study_date', '')}-derived",
    }

    tpl = Template(TEMPLATE.read_text(), trim_blocks=True, lstrip_blocks=True)
    rendered = tpl.render(**ctx)
    (study / "BRIEF.md").write_text(rendered)
    print(f"✓ BRIEF.md rendered ({len(rendered)} chars)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
