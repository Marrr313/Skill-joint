#!/usr/bin/env python3
"""Decode a chrome-devtools MCP evaluate_script buffered result into raw text.

The chrome-devtools MCP wraps evaluate_script outputs as:
    Script ran on page and returned:
    ```json
    "<json-encoded string>"
    ```
When the result exceeds the inline-response token limit, it spills to a
buffered file at the path printed in the error message. This helper unwraps
the wrapper and returns the inner string (or pretty-printed value if not a
string).

Usage:
    decode_buf.py <buf-path> <out-path>          # default: decode to text
    decode_buf.py <buf-path> <out-path> --b64    # also accept base64-payload variant (from `btoa(...)`)
"""
from __future__ import annotations
import base64
import json
import re
import sys
from pathlib import Path


def decode_buffer(raw: str, b64_fallback: bool = False) -> str:
    """Unwrap the MCP `Script ran on page and returned:\n```json\n...\n``` ` envelope."""
    m = re.search(r"```json\n(.*)\n```\s*\Z", raw, re.DOTALL)
    payload = m.group(1) if m else raw
    try:
        val = json.loads(payload)
    except json.JSONDecodeError:
        # Maybe already plain text
        return payload
    if isinstance(val, str):
        if b64_fallback:
            # Try decoding as base64; on failure, return as-is
            try:
                return base64.b64decode(val).decode("utf-8")
            except Exception:
                return val
        return val
    # Non-string JSON: pretty print
    return json.dumps(val, indent=2)


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: decode_buf.py <buf-path> <out-path> [--b64]", file=sys.stderr)
        return 1
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    b64 = "--b64" in sys.argv[3:]
    if not src.exists():
        print(f"error: {src} does not exist", file=sys.stderr)
        return 1
    raw = src.read_text()
    out = decode_buffer(raw, b64_fallback=b64)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(out)
    print(f"wrote {len(out)} chars to {dst}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
