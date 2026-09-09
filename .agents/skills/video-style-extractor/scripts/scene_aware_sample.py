"""Extract scene keyframes + dense 2fps frames around cut boundaries.

Outputs JPG frames to <out>/ plus <out>/manifest.json describing each frame.
"""
import json
import subprocess
import sys
from pathlib import Path


def _ffmpeg_extract(video: Path, ts_ms: int, out: Path) -> bool:
    cmd = [
        "ffmpeg", "-y", "-ss", f"{ts_ms/1000:.3f}", "-i", str(video),
        "-frames:v", "1", "-q:v", "2", str(out),
    ]
    r = subprocess.run(cmd, capture_output=True)
    return r.returncode == 0 and out.exists()


def sample(video: Path, scenes: list[dict], out_dir: Path, boundary_ms: int = 500) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest: list[dict] = []
    counter = 0
    for idx, scene in enumerate(scenes):
        start, end = scene["start_ms"], scene["end_ms"]
        mid = (start + end) // 2
        fp = out_dir / f"frame_{counter:04d}.jpg"
        if _ffmpeg_extract(video, mid, fp):
            manifest.append({
                "path": fp.name, "ts_ms": mid, "scene_idx": idx, "kind": "keyframe",
            })
            counter += 1
        if idx > 0:
            win_start = max(0, start - boundary_ms)
            win_end = start + boundary_ms
            ts = win_start
            while ts <= win_end:
                fp = out_dir / f"frame_{counter:04d}.jpg"
                if _ffmpeg_extract(video, ts, fp):
                    manifest.append({
                        "path": fp.name, "ts_ms": ts, "scene_idx": idx, "kind": "boundary",
                    })
                    counter += 1
                ts += 500
    (out_dir / "manifest.json").write_text(
        json.dumps({"frames": manifest, "count": len(manifest)}, indent=2)
    )
    return {"count": len(manifest)}


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: scene_aware_sample.py <video> <scenes.json> <out_dir>", file=sys.stderr)
        return 2
    video = Path(sys.argv[1])
    scenes = json.loads(Path(sys.argv[2]).read_text())["scenes"]
    out_dir = Path(sys.argv[3])
    sample(video, scenes, out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
