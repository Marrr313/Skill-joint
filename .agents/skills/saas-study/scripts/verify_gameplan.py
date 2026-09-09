#!/usr/bin/env python3
"""Diff GAMEPLAN.md predictions against actual captured evidence.

Reads:
  <study>/GAMEPLAN.md
  <study>/derived/action-trace.jsonl
  <study>/derived/providers.json
  <study>/derived/api-endpoints.json

Writes:
  <study>/GAMEPLAN-EXECUTED.md

This script does NOT parse the gameplan rigidly: it does best-effort regex
extraction of expected providers (Section B.1) and expected endpoint patterns
(Section B.2), then reports hits vs misses based on the actual captures.

Surprises = captured endpoints that didn't match any predicted pattern.

Usage:
  verify_gameplan.py <study-folder>
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path


HEADING_RE = re.compile(r"^(#{1,4})\s+(.+)$", re.M)
ENDPOINT_LINE_RE = re.compile(r"`?(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+([^`\s]+)`?", re.I)
PROVIDER_TABLE_ROW_RE = re.compile(r"^\s*\|\s*\w+[\w\s/-]*\s*\|\s*([^|]+?)\s*\|", re.M)


def step_key(label: str) -> str:
    """Leading identifier of a step heading, lowercased.

    Handles both "Step 3: Feature" and the older "Step 3 - Feature" shapes so a
    hand-authored gameplan keeps matching regardless of which separator it uses.
    """
    return re.split(r"\s*[:\u2013\u2014-]\s+", label, maxsplit=1)[0].strip().lower()


def split_sections(md: str) -> dict[str, str]:
    """Split markdown into top-level (## A. ..., ## B. ...) sections."""
    sections: dict[str, str] = {}
    current_key = None
    current_lines: list[str] = []
    for line in md.splitlines():
        m = re.match(r"^##\s+([A-E])\.\s+(.*)", line)
        if m:
            if current_key is not None:
                sections[current_key] = "\n".join(current_lines)
            current_key = m.group(1)
            current_lines = [line]
        else:
            if current_key is not None:
                current_lines.append(line)
    if current_key is not None:
        sections[current_key] = "\n".join(current_lines)
    return sections


def parse_section_c_steps(section_c_md: str) -> list[dict]:
    """Each step is a ### heading. Extract goal/action/endpoints expected."""
    steps = []
    chunks = re.split(r"^###\s+", section_c_md, flags=re.M)
    for chunk in chunks[1:]:
        first_line, _, rest = chunk.partition("\n")
        step_label = first_line.strip()
        endpoints = []
        for em in ENDPOINT_LINE_RE.finditer(rest):
            endpoints.append((em.group(1).upper(), em.group(2)))
        steps.append({
            "label": step_label,
            "predicted_endpoints": endpoints,
        })
    return steps


def parse_section_b1_providers(section_b_md: str) -> list[str]:
    """Pull provider names from §B.1 table rows (second column)."""
    providers = []
    for m in PROVIDER_TABLE_ROW_RE.finditer(section_b_md):
        val = m.group(1).strip()
        # Skip table-divider rows
        if "---" in val or val.lower() in ("hypothesis", "providers"):
            continue
        # Multi-name cells like "Clerk or Supabase Auth"
        for piece in re.split(r"\s+or\s+|/|,", val):
            piece = piece.strip()
            if piece and piece.lower() != "verify by":
                providers.append(piece)
    return list(dict.fromkeys(providers))


def parse_section_b2_endpoints(section_b_md: str) -> list[tuple]:
    out = []
    # Endpoints in §B.2 typically appear as `POST /api/...` or `GET /api/me`
    for em in ENDPOINT_LINE_RE.finditer(section_b_md):
        out.append((em.group(1).upper(), em.group(2)))
    return out


def endpoint_matches(predicted_path: str, observed_path: str) -> bool:
    """Loose pattern match: predicted is regex-ified with /api/ exact match."""
    # Strip query strings
    observed_path = observed_path.split("?", 1)[0]
    if predicted_path == observed_path:
        return True
    # Convert path params like :id, {id}, * to wildcards
    pat = re.escape(predicted_path)
    pat = pat.replace(r"\:id", r"[^/]+")
    pat = pat.replace(r"\{id\}", r"[^/]+")
    pat = pat.replace(r"\*", r".*")
    return bool(re.fullmatch(pat, observed_path))


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("study")
    args = p.parse_args()

    study = Path(args.study)
    gameplan_path = study / "GAMEPLAN.md"
    trace_path = study / "derived" / "action-trace.jsonl"
    providers_path = study / "derived" / "providers.json"
    endpoints_path = study / "derived" / "api-endpoints.json"

    if not gameplan_path.exists():
        out = "# Gameplan Execution Report\n\n(no GAMEPLAN.md present, was --no-authed used?)\n"
        (study / "GAMEPLAN-EXECUTED.md").write_text(out)
        print("info: no gameplan to verify", file=sys.stderr)
        return 0

    gp = gameplan_path.read_text()
    sections = split_sections(gp)

    steps = parse_section_c_steps(sections.get("C", ""))
    b1_providers = parse_section_b1_providers(sections.get("B", ""))
    b2_endpoints = parse_section_b2_endpoints(sections.get("B", ""))

    # Load captured evidence
    trace_entries: list[dict] = []
    if trace_path.exists():
        for line in trace_path.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                trace_entries.append(json.loads(line))
            except ValueError:
                continue

    providers_detail = []
    if providers_path.exists():
        providers_detail = json.loads(providers_path.read_text()).get("detail", [])
    confirmed_provider_names = {d["provider"] for d in providers_detail}

    all_endpoints: list[tuple] = []
    for e in trace_entries:
        for ep in e.get("endpoints", []):
            all_endpoints.append((ep["method"], ep["host"], ep["path"]))

    # Step verification
    step_results = []
    for step in steps:
        executed = any(
            (e.get("type") == "action" or e.get("type") == "navigate" or e.get("type") == "window")
            and step_key(step["label"]) in (e.get("label", "") + " " + (e.get("note") or "")).lower()
            for e in trace_entries
        )
        # Endpoint hit count
        hits = 0
        for method, path in step["predicted_endpoints"]:
            for m, h, p in all_endpoints:
                if m == method and endpoint_matches(path, p):
                    hits += 1
                    break
        step_results.append({
            "label": step["label"],
            "executed_guess": executed,
            "predicted_count": len(step["predicted_endpoints"]),
            "hit_count": hits,
        })

    # Provider verification
    provider_results = []
    for name in b1_providers:
        confirmed = any(
            name.lower() in c.lower() or c.lower() in name.lower()
            for c in confirmed_provider_names
        )
        provider_results.append({"name": name, "confirmed": confirmed})

    # Endpoint pattern verification (§B.2)
    endpoint_results = []
    for method, path in b2_endpoints:
        observed = False
        for m, h, p in all_endpoints:
            if m == method and endpoint_matches(path, p):
                observed = True
                break
        endpoint_results.append({"method": method, "path": path, "observed": observed})

    # Surprises: observed endpoints that didn't match any predicted pattern
    predicted_set = {(m, p) for m, p in b2_endpoints}
    for step in steps:
        for m, p in step["predicted_endpoints"]:
            predicted_set.add((m, p))
    surprises = []
    for method, host, path in all_endpoints:
        # Skip third-party hosts
        manifest = json.loads((study / "study.json").read_text())
        domain = manifest["domain"]
        if not (host == domain or host.endswith("." + domain)):
            continue
        if any(m == method and endpoint_matches(p, path) for m, p in predicted_set):
            continue
        surprises.append({"method": method, "host": host, "path": path})

    # Dedupe surprises
    seen = set()
    unique_surprises = []
    for s in surprises:
        key = (s["method"], s["host"], s["path"])
        if key not in seen:
            seen.add(key)
            unique_surprises.append(s)

    # Build report
    lines = []
    lines.append(f"# Gameplan Execution Report: {study.parent.name} · {study.name}")
    lines.append("")
    completed_count = sum(1 for r in step_results if r["executed_guess"] or r["hit_count"] > 0)
    lines.append(f"## 1. Steps completed: {completed_count}/{len(step_results)}")
    for r in step_results:
        mark = "✅" if (r["executed_guess"] or r["hit_count"] > 0) else "❌"
        lines.append(f"- {mark} {r['label']}, predicted endpoints: {r['hit_count']}/{r['predicted_count']}")
    lines.append("")

    confirmed_predicted = sum(1 for r in endpoint_results if r["observed"])
    lines.append("## 2. Endpoint predictions")
    lines.append(f"- Predicted {len(endpoint_results)} patterns, confirmed {confirmed_predicted}")
    for r in endpoint_results:
        mark = "✅" if r["observed"] else "❌"
        lines.append(f"  - {mark} `{r['method']} {r['path']}`")
    lines.append("")

    lines.append("## 3. Provider verifications")
    for r in provider_results:
        mark = "✅" if r["confirmed"] else "❌"
        lines.append(f"- {mark} {r['name']}{'  (confirmed)' if r['confirmed'] else '  (not seen)'}")
    lines.append("")

    lines.append("## 4. Surprises (own-host endpoints not predicted in gameplan)")
    if unique_surprises:
        for s in unique_surprises[:20]:
            lines.append(f"- `{s['method']} {s['host']}{s['path']}`")
        if len(unique_surprises) > 20:
            lines.append(f"- (+{len(unique_surprises) - 20} more in derived/api-endpoints.json)")
    else:
        lines.append("- (none, all observed own-host endpoints matched predictions)")
    lines.append("")

    lines.append("## 5. Notes")
    lines.append(f"- Action trace: {len(trace_entries)} entries")
    lines.append(f"- Source: derived/action-trace.jsonl + derived/providers.json + derived/api-endpoints.json")
    lines.append("- Step-completion guess uses label substring match; review manually if it looks wrong.")
    lines.append("")

    (study / "GAMEPLAN-EXECUTED.md").write_text("\n".join(lines))
    print(f"✓ GAMEPLAN-EXECUTED.md: {completed_count}/{len(step_results)} steps, "
          f"{confirmed_predicted}/{len(endpoint_results)} endpoint patterns, "
          f"{len(unique_surprises)} surprises", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
