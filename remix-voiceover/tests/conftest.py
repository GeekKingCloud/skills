from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


@pytest.fixture
def tmp_path() -> Path:
    if "RV_TEST_TMPDIR" not in os.environ:
        raise AssertionError("RV_TEST_TMPDIR must be set for rv tests")
    base = Path(os.environ["RV_TEST_TMPDIR"]).resolve()
    base.mkdir(parents=True, exist_ok=True)
    target = base / f"pytest-{uuid.uuid4().hex}"
    target.mkdir()
    return target
