import json
import subprocess
import sys
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"

def test_detects_10fps_from_30fps_source(tmp_path):
    out = tmp_path / "fps.json"
    result = subprocess.run(
        [sys.executable, "-m", "scripts.native_fps_detect",
         str(FIXTURES / "pixel_10fps.mp4"), str(out)],
        capture_output=True, text=True, cwd=Path(__file__).parents[1],
    )
    assert result.returncode == 0, result.stderr
    data = json.loads(out.read_text())
    assert 8 <= data["native_animation_fps"] <= 12
    assert data["confidence"] == "high"
