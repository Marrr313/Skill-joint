#!/usr/bin/env python3
"""Scrub auth/cookies/JWTs/keys/emails from network artifacts.

Reads:
  <study>/raw/network/*.json   (raw captures from chrome-devtools MCP dumps)
  <study>/raw/network/*.har    (if HAR export available)
  <study>/derived/action-trace.jsonl  (in-place if exists)

Writes:
  <study>/derived/network-summary.json  (slim, scrubbed)
  <study>/derived/action-trace.jsonl    (overwritten, scrubbed)

Raw files are NEVER modified.

Usage:
  scrub_network.py <study-folder>
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

JWT_RE = re.compile(r"\beyJ[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{4,}\b")
API_KEY_RE = re.compile(r"\b(?:sk_(?:live|test)_[A-Za-z0-9]{16,}|pk_(?:live|test)_[A-Za-z0-9]{16,}|rk_[A-Za-z0-9]{16,}|xox[bpa]-[A-Za-z0-9-]{10,}|AIza[0-9A-Za-z\-_]{20,})\b")
HEX_KEY_RE = re.compile(r"\b[a-f0-9]{40,}\b")
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
SENSITIVE_FIELDS = {"password", "passwd", "token", "secret", "api_key", "apikey", "access_token", "refresh_token", "session_token", "auth", "authorization"}


def scrub_text(text: str) -> str:
    if not text:
        return text
    text = JWT_RE.sub("<redacted:jwt>", text)
    text = API_KEY_RE.sub("<redacted:apikey>", text)
    text = HEX_KEY_RE.sub("<redacted:hex>", text)
    text = EMAIL_RE.sub("<redacted:email>", text)
    return text


def scrub_headers(headers: dict | list) -> dict | list:
    """Headers may be dict or list-of-dict ({name, value}). Scrub both shapes."""
    if isinstance(headers, list):
        return [scrub_headers(h) for h in headers]
    if not isinstance(headers, dict):
        return headers
    out = {}
    for k, v in headers.items():
        kl = k.lower() if isinstance(k, str) else str(k).lower()
        # list-shape header entry: {name, value}
        if kl == "name" and "value" in headers:
            name_lower = str(headers.get("name", "")).lower()
            value = headers.get("value", "")
            if name_lower in ("authorization", "proxy-authorization"):
                value = "<redacted:bearer>"
            elif name_lower in ("cookie", "set-cookie"):
                value = "<redacted:cookie>"
            elif name_lower in ("x-api-key", "x-auth-token", "x-csrf-token", "x-session-token"):
                value = "<redacted:header>"
            else:
                value = scrub_text(str(value))
            return {"name": headers.get("name"), "value": value}
        if kl in ("authorization", "proxy-authorization"):
            out[k] = "<redacted:bearer>"
        elif kl in ("cookie", "set-cookie"):
            out[k] = "<redacted:cookie>"
        elif kl in ("x-api-key", "x-auth-token", "x-csrf-token", "x-session-token"):
            out[k] = "<redacted:header>"
        else:
            out[k] = scrub_text(v) if isinstance(v, str) else v
    return out


def scrub_body(body):
    if body is None:
        return None
    if isinstance(body, str):
        # Try JSON first
        try:
            parsed = json.loads(body)
            return scrub_json(parsed)
        except (ValueError, TypeError):
            return scrub_text(body)
    if isinstance(body, (dict, list)):
        return scrub_json(body)
    return body


def scrub_json(obj):
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            kl = str(k).lower()
            if kl in SENSITIVE_FIELDS:
                out[k] = "<redacted>"
            elif isinstance(v, (dict, list)):
                out[k] = scrub_json(v)
            elif isinstance(v, str):
                out[k] = scrub_text(v)
            else:
                out[k] = v
        return out
    if isinstance(obj, list):
        return [scrub_json(x) for x in obj]
    if isinstance(obj, str):
        return scrub_text(obj)
    return obj


def slim_entry(entry: dict) -> dict:
    """Reduce a raw chrome-devtools network entry to a slim summary."""
    # chrome-devtools MCP shape: { id, url, method, status, type, size, requestHeaders, responseHeaders, ... }
    # HAR shape: { request: { method, url, headers }, response: { status, content, headers }, ... }
    if "request" in entry and "response" in entry:
        req = entry.get("request", {})
        res = entry.get("response", {})
        url = req.get("url", "")
        method = req.get("method", "")
        status = res.get("status")
        size = (res.get("content", {}) or {}).get("size", 0)
        ctype = (res.get("content", {}) or {}).get("mimeType", "")
    else:
        url = entry.get("url", "")
        method = entry.get("method", "")
        status = entry.get("status")
        size = entry.get("size") or entry.get("encodedDataLength") or 0
        ctype = entry.get("mimeType") or entry.get("contentType") or ""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    return {
        "host": parsed.netloc,
        "path": parsed.path,
        "method": method,
        "status": status,
        "content_type": ctype,
        "size": size,
    }


def process_network_file(path: Path) -> list[dict]:
    """Parse a raw network json/har file into list of scrubbed slim entries."""
    try:
        data = json.loads(path.read_text())
    except Exception as e:
        print(f"warn: {path.name}: {e}", file=sys.stderr)
        return []
    entries = []
    # HAR shape
    if isinstance(data, dict) and "log" in data and "entries" in data["log"]:
        entries = data["log"]["entries"]
    # chrome-devtools list_network_requests shape (array of objects)
    elif isinstance(data, list):
        entries = data
    # chrome-devtools shape with wrapper
    elif isinstance(data, dict) and "requests" in data:
        entries = data["requests"]
    elif isinstance(data, dict) and "items" in data:
        entries = data["items"]
    else:
        # Treat as single-entry
        entries = [data]
    return [slim_entry(e) for e in entries if isinstance(e, dict)]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("study")
    args = p.parse_args()

    study = Path(args.study)
    raw_net = study / "raw" / "network"
    derived = study / "derived"
    derived.mkdir(parents=True, exist_ok=True)

    summary = {"sources": [], "entries": [], "unique_hosts": []}
    if raw_net.exists():
        # Network DUMPS (list of requests). sample_*.network-response files are response BODIES,
        # handled by fingerprint_data_shapes.py instead (they have no URL/method).
        net_files = sorted(raw_net.glob("*.json")) + sorted(raw_net.glob("*.har"))
        for f in net_files:
            slim = process_network_file(f)
            summary["sources"].append({"file": f.name, "entry_count": len(slim)})
            summary["entries"].extend(slim)

        # ALSO ingest endpoints from action-trace.jsonl: most authed-page network signal lives here, not in raw files
        # (the orchestrator usually only saves a slim per-page JSON, not full HAR per page)
        trace_path = derived / "action-trace.jsonl"
        if trace_path.exists():
            trace_count = 0
            for line in trace_path.read_text().splitlines():
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                except Exception:
                    continue
                for ep in entry.get("endpoints", []):
                    if not isinstance(ep, dict):
                        continue
                    # action-trace endpoints already have {host, path, method, status, content_type, size}
                    slim_e = {
                        "host": ep.get("host", ""),
                        "path": ep.get("path", ""),
                        "method": ep.get("method", ""),
                        "status": ep.get("status"),
                        "content_type": ep.get("content_type", ""),
                        "size": ep.get("size", 0),
                    }
                    summary["entries"].append(slim_e)
                    trace_count += 1
            if trace_count:
                summary["sources"].append({"file": "action-trace.jsonl (endpoints)", "entry_count": trace_count})

    # Dedupe entries by (host, path, method)
    seen = {}
    for e in summary["entries"]:
        key = (e["host"], e["path"], e["method"])
        if key in seen:
            seen[key]["seen_count"] = seen[key].get("seen_count", 1) + 1
        else:
            e["seen_count"] = 1
            seen[key] = e
    summary["entries"] = list(seen.values())
    summary["unique_hosts"] = sorted({e["host"] for e in summary["entries"] if e["host"]})

    (derived / "network-summary.json").write_text(json.dumps(summary, indent=2))

    # Scrub action-trace.jsonl in place (rewriting)
    trace_path = derived / "action-trace.jsonl"
    if trace_path.exists():
        scrubbed_lines = []
        for line in trace_path.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except ValueError:
                scrubbed_lines.append(line)
                continue
            scrubbed_lines.append(json.dumps(scrub_json(obj)))
        trace_path.write_text("\n".join(scrubbed_lines) + "\n")

    print(f"✓ network-summary.json: {len(summary['entries'])} deduped entries, "
          f"{len(summary['unique_hosts'])} unique hosts", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
