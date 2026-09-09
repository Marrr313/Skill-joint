import json
import subprocess
import sys
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"

def test_scene_aware_extracts_one_frame_per_scene_plus_boundary(tmp_path):
    video = FIXTURES / "two_scene.mp4"
    scenes = tmp_path / "scenes.json"
    scenes.write_text(json.dumps({"scenes": [
        {"start_ms": 0, "end_ms": 1000},
        {"start_ms": 1000, "end_ms": 2000},
    ]}))
    out = tmp_path / "frames"
    out.mkdir()
    result = subprocess.run(
        [sys.executable, "-m", "scripts.scene_aware_sample", str(video), str(scenes), str(out)],
        capture_output=True, text=True, cwd=Path(__file__).parents[1],
    )
    assert result.returncode == 0, result.stderr
    frames = sorted(out.glob("*.jpg"))
    assert len(frames) >= 4
    manifest = json.loads((out / "manifest.json").read_text())
    assert all("scene_idx" in f and "kind" in f for f in manifest["frames"])
