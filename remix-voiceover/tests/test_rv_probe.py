from __future__ import annotations

import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

from make_fixtures import make_all

ROOT = Path(__file__).resolve().parents[1]
RV = ROOT / "scripts" / "rv.py"


def _workdir(name: str) -> Path:
    if "RV_TEST_TMPDIR" not in os.environ:
        raise AssertionError("RV_TEST_TMPDIR must be set for rv tests")
    base = Path(os.environ["RV_TEST_TMPDIR"]).resolve()
    base.mkdir(parents=True, exist_ok=True)
    target = base / f"rv-{name}-{uuid.uuid4().hex}"
    target.mkdir()
    return target


def test_probe_video_and_audio_only() -> None:
    workdir = _workdir("probe")
    fixtures = make_all(workdir)
    for key, expected_kind in (("speech_drop_video", "video"), ("audio_only", "audio-only")):
        out = workdir / f"{key}_probe.json"
        subprocess.run([sys.executable, str(RV), "probe", str(fixtures[key]), "--json-out", str(out)], check=True)
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["container_kind"] == expected_kind
        assert data["source_sha256"]
        assert len(data["audio_streams"]) >= 2
        assert data["supported_shape"]["supported"] is True

    single = workdir / "single_probe.json"
    subprocess.run([sys.executable, str(RV), "probe", str(fixtures["single_lane"]), "--json-out", str(single)], check=True)
    single_data = json.loads(single.read_text(encoding="utf-8"))
    assert len(single_data["audio_streams"]) == 1
    assert single_data["supported_shape"]["supported"] is True
    assert single_data["supported_shape"]["mode"] == "single-program-repair"


def test_later_subcommands_are_registered_with_required_args() -> None:
    proc = subprocess.run([sys.executable, str(RV), "verify"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert proc.returncode == 2
    assert "--manifest" in proc.stderr
    assert "--plan" in proc.stderr
