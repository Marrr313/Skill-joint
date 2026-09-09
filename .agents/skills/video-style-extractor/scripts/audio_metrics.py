"""ffmpeg loudnorm two-pass: extract LUFS integrated, LRA, true peak."""
import json
import re
import subprocess
import sys
from pathlib import Path


def measure(video: Path) -> dict:
    cmd = [
        "ffmpeg", "-nostats", "-i", str(video),
        "-af", "loudnorm=print_format=json",
        "-f", "null", "-",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    stderr = r.stderr
    m = re.search(r"\{[\s\S]*?\}", stderr)
    if not m:
        return {"error": "loudnorm output not found", "stderr_tail": stderr[-500:]}
    data = json.loads(m.group(0))
    return {
        "integrated_lufs": float(data["input_i"]),
        "loudness_range": float(data["input_lra"]),
        "true_peak_db": float(data["input_tp"]),
        "threshold_lufs": float(data["input_thresh"]),
    }


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: audio_metrics.py <video> <out.json>", file=sys.stderr)
        return 2
    Path(sys.argv[2]).write_text(json.dumps(measure(Path(sys.argv[1])), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
