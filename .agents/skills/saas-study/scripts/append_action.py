#!/usr/bin/env python3
"""Append one entry to <study>/derived/action-trace.jsonl.

Called by SKILL.md during Phase 3 after each capture. Accepts JSON strings on the
command line so chrome-devtools MCP outputs can be passed through cleanly.

Usage:
  append_action.py <study> --type <action|navigate|window|skipped|capture> \
      [--step N] [--label LABEL] [--url URL] \
      [--requests-json '<json-array>'] [--console-json '<json-array>'] \
      [--window-label LABEL] [--note "<text>"]
"""
from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


def slim_requests(reqs) -> list[dict]:
    """Reduce raw request objects from chrome-devtools to slim dicts."""
    if not reqs:
        return []
    out = []
    for r in reqs:
        if not isinstance(r, dict):
            continue
        url = r.get("url", "")
        method = r.get("method", "")
        status = r.get("status")
        size = r.get("size") or r.get("encodedDataLength") or 0
        ctype = r.get("mimeType") or r.get("contentType") or ""
        parsed = urlparse(url)
        out.append({
            "method": method,
            "host": parsed.netloc,
            "path": parsed.path,
            "status": status,
            "content_type": ctype,
            "size": size,
        })
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("study")
    p.add_argument("--type", required=True,
                   choices=["action", "navigate", "window", "skipped", "capture"])
    p.add_argument("--step")
    p.add_argument("--label", default="")
    p.add_argument("--url", default="")
    p.add_argument("--requests-json", default="[]")
    p.add_argument("--console-json", default="[]")
    p.add_argument("--window-label", default=None)
    p.add_argument("--note", default=None)
    args = p.parse_args()

    study = Path(args.study)
    derived = study / "derived"
    derived.mkdir(parents=True, exist_ok=True)
    trace = derived / "action-trace.jsonl"

    try:
        requests = json.loads(args.requests_json)
        if not isinstance(requests, list):
            requests = []
    except ValueError:
        requests = []
    try:
        console = json.loads(args.console_json)
        if not isinstance(console, list):
            console = []
    except ValueError:
        console = []

    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "type": args.type,
        "step": args.step,
        "label": args.label,
        "url": args.url,
        "endpoints": slim_requests(requests),
        "console": console,
    }
    if args.window_label:
        entry["window_label"] = args.window_label
    if args.note:
        entry["note"] = args.note

    with trace.open("a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"✓ appended entry (type={args.type}, endpoints={len(entry['endpoints'])})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
