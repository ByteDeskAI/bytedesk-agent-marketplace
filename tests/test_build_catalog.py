import json
import subprocess
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent


def run_build(output: Path) -> dict:
    subprocess.run(
        [sys.executable, str(REPOSITORY_ROOT / "scripts" / "build_catalog.py"), "--output", str(output)],
        cwd=REPOSITORY_ROOT,
        check=True,
    )
    return json.loads(output.read_text())


def test_empty_catalog_is_deterministic(tmp_path: Path) -> None:
    first = run_build(tmp_path / "a" / "index.json")
    second = run_build(tmp_path / "b" / "index.json")
    assert first == second
    assert first == {"entries": []}
