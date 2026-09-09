#!/usr/bin/env python3
"""Convert raw/html/*.html into extracted/*.md via trafilatura.

Usage:
  extract_html.py <study-folder>

Skips files already extracted (compares mtime). Idempotent.
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("study")
    args = p.parse_args()

    study = Path(args.study)
    html_dir = study / "raw" / "html"
    out_dir = study / "extracted"
    out_dir.mkdir(parents=True, exist_ok=True)

    if not html_dir.exists():
        print(f"warn: no raw/html/ in {study}", file=sys.stderr)
        return 0

    try:
        import trafilatura  # type: ignore
    except ImportError:
        print("error: trafilatura not installed. Run scripts/install.sh", file=sys.stderr)
        return 1

    count = 0
    skipped = 0
    failed = 0
    for html_file in sorted(html_dir.glob("*.html")):
        out_file = out_dir / (html_file.stem + ".md")
        if out_file.exists() and out_file.stat().st_mtime >= html_file.stat().st_mtime:
            skipped += 1
            continue
        try:
            raw = html_file.read_text(encoding="utf-8", errors="replace")
            extracted = trafilatura.extract(
                raw,
                output_format="markdown",
                include_links=True,
                include_tables=True,
                include_images=False,
                favor_recall=True,
            )
            if not extracted or len(extracted.strip()) < 40:
                # Fall back: bs4 plaintext
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(raw, "lxml")
                for tag in soup(["script", "style", "noscript"]):
                    tag.decompose()
                extracted = soup.get_text("\n", strip=True)
            header = f"<!-- source: raw/html/{html_file.name} -->\n\n"
            out_file.write_text(header + (extracted or "(empty extraction)\n"))
            count += 1
        except Exception as e:
            print(f"error: {html_file.name}: {e}", file=sys.stderr)
            failed += 1
    print(f"✓ extracted {count} new, skipped {skipped}, failed {failed}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
