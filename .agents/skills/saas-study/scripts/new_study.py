#!/usr/bin/env python3
"""Initialize a new study folder.

Usage:
  new_study.py <url> [--stealth balanced] [--library-root PATH]
                     [--no-authed] [--no-screenshots]

The library root defaults to ./saas-library in the current working directory
(override with --library-root or the SAAS_STUDY_LIBRARY environment variable).

Writes:
  <library-root>/<domain>/<YYYY-MM-DD>/
    .gitignore, study.json (skeleton), .stealth-profile,
    raw/{html,network,public}/, screenshots/, extracted/, derived/, notes/

Also writes <library-root>/.gitignore if first study.
Prints the study folder path to stdout (for capture as $STUDY).
"""
from __future__ import annotations
import argparse
import json
import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = SKILL_ROOT / "templates"


def derive_domain(url: str) -> str:
    parsed = urlparse(url if "://" in url else f"https://{url}")
    host = (parsed.hostname or url).lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("url")
    p.add_argument("--stealth", default="balanced",
                   choices=["fast", "balanced", "high"])
    p.add_argument("--library-root", default=os.environ.get("SAAS_STUDY_LIBRARY", "./saas-library"),
                   help="Where study folders are written "
                        "(default: ./saas-library in the current working directory, "
                        "or $SAAS_STUDY_LIBRARY if set)")
    p.add_argument("--no-authed", action="store_true")
    p.add_argument("--no-screenshots", action="store_true")
    args = p.parse_args()

    domain = derive_domain(args.url)
    if not domain or "." not in domain:
        print(f"error: could not parse domain from {args.url!r}", file=sys.stderr)
        return 2

    library_root = Path(os.path.expanduser(args.library_root))
    library_root.mkdir(parents=True, exist_ok=True)

    # Root .gitignore (first-study creation only)
    root_gi = library_root / ".gitignore"
    if not root_gi.exists():
        root_gi.write_text(
            "# saas-library is local-only by default.\n"
            "# To commit a specific study, delete its .gitignore override.\n"
            "*\n"
            "!.gitignore\n"
            "!README.md\n"
        )

    today = date.today().isoformat()
    study_dir = library_root / domain / today
    derived_dir = library_root / domain / f"{today}-derived"  # SIBLING, for transformations/templates

    # Same-domain re-study warning (skill-level: we just write a marker; SKILL.md prompts)
    existing_today = study_dir.exists()

    for sub in ("raw/html", "raw/network", "raw/public", "raw/screenshots-original",
                "screenshots", "extracted", "derived", "notes"):
        (study_dir / sub).mkdir(parents=True, exist_ok=True)

    # Per-study .gitignore
    (study_dir / ".gitignore").write_text(
        (TEMPLATES / "gitignore-study.txt").read_text()
    )

    # SIBLING -derived/ folder for transformations (templates, design remixes, build plans).
    # Keeps the raw study pure observation; transformations live here.
    derived_dir.mkdir(parents=True, exist_ok=True)
    derived_readme = derived_dir / "README.md"
    if not derived_readme.exists():
        derived_readme.write_text(
            f"# {domain}: derived work\n\n"
            f"Sibling to `../{today}/` (the raw study). **This folder holds transformations**: "
            f"templates extracted from the study, design remixes, build plans, opinion-layered analysis, etc.\n\n"
            "Keep the dated raw-study folder pure observation. Put any modifications, opinions, "
            "or generated assets here.\n\n"
            "## Suggested files\n\n"
            "- `templates/`: HTML/component templates extracted from the study\n"
            "- `tokens.css`: design tokens lifted from observed CSS\n"
            "- `build-plan.md`: your opinionated path to clone the product\n"
            "- `index.html`: gallery linking all templates\n\n"
            f"The raw study lives at `../{today}/BRIEF.md` and `../{today}/ANALYSIS.md`.\n"
        )

    # Stealth profile marker
    (study_dir / ".stealth-profile").write_text(args.stealth + "\n")

    # Skeleton study.json
    manifest = {
        "domain": domain,
        "url": args.url,
        "study_date": today,
        "study_version": "1.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "stealth_profile": args.stealth,
        "auth_used": False,  # updated by SKILL.md / write_manifest.py after Phase 3
        "no_authed_flag": args.no_authed,
        "no_screenshots_flag": args.no_screenshots,
        "duration_seconds": None,
        "artifacts": {},
        "counts": {
            "screenshots": 0,
            "html_pages": 0,
            "public_pages": 0,
            "authed_pages": 0,
            "unique_hosts": 0,
            "providers_detected": 0,
            "endpoints_observed": 0,
        },
    }
    (study_dir / "study.json").write_text(json.dumps(manifest, indent=2))

    # Empty user-notes scaffold
    notes_path = study_dir / "notes" / "user-notes.md"
    if not notes_path.exists():
        notes_path.write_text("# User notes: " + domain + " (" + today + ")\n\n")

    # Print path for SKILL.md to capture
    print(str(study_dir))
    if existing_today:
        print(f"warn: study folder for {domain} already exists for {today}, reusing", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
