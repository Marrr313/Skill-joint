import json
import subprocess
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"

def test_scene_detect_produces_valid_json(tmp_path):
    video = FIXTURES / "two_scene.mp4"
    out = tmp_path / "scenes.json"
    result = subprocess.run(
        ["python", "-m", "scripts.scene_detect", str(video), str(out)],
        capture_output=True, text=True, cwd=Path(__file__).parents[1],
    )
    assert result.returncode == 0, result.stderr
    data = json.loads(out.read_text())
    assert "scenes" in data
    assert len(data["scenes"]) >= 2
    for s in data["scenes"]:
        assert "start_ms" in s and "end_ms" in s
        assert s["end_ms"] > s["start_ms"]
