#!/usr/bin/env python3
"""Render <study>/derived/action-trace.jsonl into <study>/extracted/action-map.md
(human/LLM-readable form, grouped by page).

Usage:
  render_action_map.py <study-folder>
"""
from __future__ import annotations
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("study")
    args = p.parse_args()

    study = Path(args.study)
    trace = study / "derived" / "action-trace.jsonl"
    out_path = study / "extracted" / "action-map.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if not trace.exists():
        out_path.write_text("# Action Map\n\n(no actions recorded)\n")
        print("info: no action-trace.jsonl", file=sys.stderr)
        return 0

    entries: list[dict] = []
    for line in trace.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except ValueError:
            continue

    # Group by URL (page)
    by_page = defaultdict(list)
    for e in entries:
        page = e.get("url", "(unknown)")
        by_page[page].append(e)

    lines = ["# Action Map", "",
             "Captured during Phase 3 (action mode, navigate, window).",
             f"Total entries: **{len(entries)}**, across **{len(by_page)}** distinct URLs.",
             ""]

    for page, page_entries in sorted(by_page.items()):
        lines.append(f"## {page}")
        lines.append("")
        for e in page_entries:
            etype = e.get("type", "")
            label = e.get("label") or e.get("window_label") or ""
            step = e.get("step")
            heading = f"**{etype}**"
            if step:
                heading += f" · step {step}"
            if label:
                heading += f": {label}"
            lines.append(f"### {heading}")
            endpoints = e.get("endpoints", [])
            if not endpoints:
                lines.append("- (no endpoints captured)")
            else:
                for ep in endpoints:
                    status = ep.get("status")
                    status_str = f" → {status}" if status else ""
                    size = ep.get("size")
                    size_str = f" ({size}B)" if size else ""
                    lines.append(f"- `{ep['method']} {ep['host']}{ep['path']}`{status_str}{size_str}")
            console = e.get("console", [])
            if console:
                lines.append("")
                lines.append("**Console:**")
                for c in console[:5]:
                    lvl = (c.get("level") or c.get("type") or "log") if isinstance(c, dict) else "log"
                    msg = (c.get("text") or c.get("message") or str(c))[:200] if isinstance(c, dict) else str(c)[:200]
                    lines.append(f"- [{lvl}] {msg}")
            note = e.get("note")
            if note:
                lines.append("")
                lines.append(f"> note: {note}")
            lines.append("")

    out_path.write_text("\n".join(lines))
    print(f"✓ action-map.md: {len(entries)} entries across {len(by_page)} pages", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
