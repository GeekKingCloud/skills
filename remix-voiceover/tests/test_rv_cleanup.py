from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from rv.cleanup import cleanup_command, cleanup_successful_transaction
from rv.util import RvError, sha256_file, sha256_json


def _packet(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    scratch = tmp_path / "remix-voiceover-cleanup-test"
    scratch.mkdir()
    source = tmp_path / "source.mkv"
    output = tmp_path / "source-REMIX-VOICEOVER.mkv"
    source.write_bytes(b"source")
    output.write_bytes(b"delivered")
    report = scratch / "REMIX-VOICEOVER-report.md"
    promotion_path = scratch / "promotion_manifest.json"
    delivery_path = scratch / "delivery.json"
    stop_path = scratch / "stop_state.json"
    report.write_text("report\n", encoding="utf-8")
    promotion = {"generated_by": "rv-verify", "status": "pass"}
    promotion_path.write_text(json.dumps(promotion), encoding="utf-8")
    delivery = {
        "generated_by": "rv-deliver",
        "status": "delivered",
        "output_written": True,
        "source_path": str(source),
        "output_path": str(output),
        "output_sha256": sha256_file(output),
    }
    delivery_path.write_text(json.dumps(delivery), encoding="utf-8")
    stop = {
        "generated_by": "rv-validate-stop",
        "status": "pass",
        "findings": [],
        "report_path": str(report),
        "report_sha256": sha256_file(report),
        "promotion_manifest_path": str(promotion_path),
        "promotion_manifest_sha256": sha256_json(promotion),
        "delivery_manifest_sha256": sha256_json(delivery),
    }
    stop_path.write_text(json.dumps(stop), encoding="utf-8")
    return scratch, delivery_path, stop_path, output


def test_cleanup_removes_only_successful_scratch_and_preserves_output(tmp_path: Path) -> None:
    scratch, delivery, stop, output = _packet(tmp_path)
    summary = cleanup_successful_transaction(scratch, delivery, stop)
    assert not scratch.exists()
    assert output.read_bytes() == b"delivered"
    assert summary["output_sha256"] == sha256_file(output)


def test_cleanup_cli_prints_machine_success(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    scratch, delivery, stop, output = _packet(tmp_path)
    assert cleanup_command(argparse.Namespace(scratch=str(scratch), delivery=str(delivery), stop_state=str(stop))) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "cleaned"
    assert output.exists()


def test_cleanup_refuses_failed_stop_state(tmp_path: Path) -> None:
    scratch, delivery, stop, _ = _packet(tmp_path)
    payload = json.loads(stop.read_text(encoding="utf-8"))
    payload["status"] = "fail"
    stop.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(RvError, match="stop state is not"):
        cleanup_successful_transaction(scratch, delivery, stop)
    assert scratch.exists()


def test_cleanup_refuses_output_inside_scratch(tmp_path: Path) -> None:
    scratch, delivery, stop, _ = _packet(tmp_path)
    payload = json.loads(delivery.read_text(encoding="utf-8"))
    inside = scratch / "final.mkv"
    inside.write_bytes(b"inside")
    payload["output_path"] = str(inside)
    payload["output_sha256"] = sha256_file(inside)
    delivery.write_text(json.dumps(payload), encoding="utf-8")
    stop_payload = json.loads(stop.read_text(encoding="utf-8"))
    stop_payload["delivery_manifest_sha256"] = sha256_json(payload)
    stop.write_text(json.dumps(stop_payload), encoding="utf-8")
    with pytest.raises(RvError, match="output must be outside scratch"):
        cleanup_successful_transaction(scratch, delivery, stop)
    assert scratch.exists()


def test_cleanup_refuses_arbitrary_temp_directory(tmp_path: Path) -> None:
    scratch, delivery, stop, _ = _packet(tmp_path)
    arbitrary = scratch.with_name("unrelated-work")
    scratch.rename(arbitrary)
    with pytest.raises(RvError, match="basename must start"):
        cleanup_successful_transaction(arbitrary, arbitrary / delivery.name, arbitrary / stop.name)
    assert arbitrary.exists()
