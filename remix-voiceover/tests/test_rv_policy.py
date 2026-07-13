from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from rv import rails
from rv.rails import audio_policy_path, load_default_rails


POLICY_CONTRACT_SHA256 = "0978fee8a47cea4497fb311eec899b195235d4c849df92c8464ead8aaf2c34fd"


def _without_traces(value):
    if isinstance(value, dict):
        return {key: _without_traces(item) for key, item in value.items() if key != "trace" and not key.endswith("_trace")}
    if isinstance(value, list):
        return [_without_traces(item) for item in value]
    return value


def _contract_digest(policy: dict) -> str:
    canonical = json.dumps(_without_traces(policy), sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(canonical).hexdigest()


def test_audio_policy_is_runtime_owned_and_loadable(tmp_path: Path, monkeypatch) -> None:
    path = audio_policy_path()

    assert path == Path(rails.__file__).resolve().with_name("audio-policy.json")
    assert path.is_file()
    monkeypatch.chdir(tmp_path)
    assert _contract_digest(load_default_rails()) == POLICY_CONTRACT_SHA256


def test_copied_runtime_package_requires_its_sibling_audio_policy(tmp_path: Path) -> None:
    skill = tmp_path / "skill"
    package = skill / "scripts" / "rv"
    package.parent.mkdir(parents=True)
    shutil.copytree(Path(rails.__file__).resolve().parent, package, ignore=shutil.ignore_patterns("__pycache__"))
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    env = dict(os.environ)
    env["PYTHONPATH"] = str(skill / "scripts")
    command = [sys.executable, "-c", "from rv.rails import load_default_rails; assert load_default_rails()['schema_version'] == 1"]

    subprocess.run(command, cwd=elsewhere, env=env, check=True, capture_output=True, text=True, timeout=30)

    package.joinpath("audio-policy.json").unlink()
    legacy = skill / "assets"
    legacy.mkdir()
    legacy.joinpath("default-rails.json").write_text("{}", encoding="utf-8")
    missing = subprocess.run(command, cwd=elsewhere, env=env, check=False, capture_output=True, text=True, timeout=30)

    assert missing.returncode != 0
    assert "audio-policy.json" in missing.stderr
