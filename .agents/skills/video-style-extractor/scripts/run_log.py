"""Append step status, cost, warnings to a human-readable run-log.md.

Designed to be called from SKILL.md's procedural workflow. Each major step
pushes a status line; Gemini passes push token+USD cost; warnings are grouped.
"""
import datetime as dt
import json
import sys
from pathlib import Path


def _append(log_path: Path, block: str) -> None:
    header = "" if log_path.exists() else (
        f"# Run log: {dt.datetime.now().isoformat(timespec='seconds')}\n\n"
    )
    log_path.write_text(log_path.read_text() if log_path.exists() else "")
    with log_path.open("a") as f:
        if header:
            f.write(header)
        f.write(block)
        f.write("\n")


def step(log: Path, name: str, status: str, reason: str = "") -> None:
    line = f"- **{name}**: {status}"
    if reason:
        line += f" ({reason})"
    _append(log, line)


def cost(log: Path, pass_name: str, input_tokens: int, output_tokens: int, usd: float) -> None:
    line = (
        f"- `{pass_name}`: in={input_tokens:,} tok, out={output_tokens:,} tok, "
        f"cost=${usd:.4f}"
    )
    _append(log, line)


def warning(log: Path, message: str) -> None:
    _append(log, f"> ⚠️ {message}")


def summary(log: Path, totals: dict) -> None:
    block = "\n## Summary\n\n" + "\n".join(
        f"- **{k}**: {v}" for k, v in totals.items()
    )
    _append(log, block)


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: run_log.py <log> <step|cost|warning|summary> <json>", file=sys.stderr)
        return 2
    log = Path(sys.argv[1])
    action = sys.argv[2]
    payload = json.loads(sys.argv[3])
    if action == "step":
        step(log, **payload)
    elif action == "cost":
        cost(log, **payload)
    elif action == "warning":
        warning(log, **payload)
    elif action == "summary":
        summary(log, **payload)
    else:
        print(f"unknown action: {action}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
