"""Provider table loader + matchers."""
from __future__ import annotations
import fnmatch
import json
from pathlib import Path

REFERENCES = Path(__file__).resolve().parents[2] / "references" / "providers.json"


def load() -> dict:
    return json.loads(REFERENCES.read_text())


def host_matches(host: str, patterns: list[str]) -> bool:
    """fnmatch-style host glob match (case-insensitive)."""
    h = host.lower()
    return any(fnmatch.fnmatch(h, p.lower()) for p in patterns)


def header_matches(headers: dict, patterns: list[str]) -> bool:
    """Header matcher: pattern can be 'name' or 'name: value'.
    Case-insensitive match on header name; if value given, substring match (case-insensitive).
    """
    if not headers:
        return False
    lower_hdrs = {k.lower(): str(v).lower() for k, v in headers.items()}
    for pat in patterns:
        if ":" in pat:
            name, _, value = pat.partition(":")
            name = name.strip().lower()
            value = value.strip().lower()
            if name in lower_hdrs and value in lower_hdrs[name]:
                return True
        else:
            if pat.strip().lower() in lower_hdrs:
                return True
    return False
