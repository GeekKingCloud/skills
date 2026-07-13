from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from rv.deliver import _validate_promotion_chain, deliver_command
from rv.audition import audition_command
from rv.plan import plan_init_command, validate_plan
from rv.rails import load_default_rails
from rv.stop import _delivery_ok, validate_stop
from rv.util import RvError, sha256_file, sha256_json


def _minimal_plan(analysis: dict, mic_gain: object) -> dict:
    return {
        "schema_version": 2,
        "analysis": {"sha256": sha256_json(analysis), "duration_seconds": 10.0},
        "roles": {"mic_streams": [0], "bed_streams": [1]},
        "rails": {},
        "targets": {},
        "mic_segments": [
            {
                "id": "seg1",
                "analysis_regime_ids": ["r001"],
                "start_seconds": 0.0,
                "end_seconds": 10.0,
                "judgment": "hold",
                "gain_db": mic_gain,
            }
        ],
        "bed_segments": [],
        "event_overlays": [],
        "boundary_overrides": [],
    }


def test_audition_rejects_candidate_not_bound_to_render_manifest(tmp_path: Path) -> None:
    source = tmp_path / "source.mka"
    source.write_bytes(b"source")
    analysis = {
        "media_path": str(source),
        "source_sha256": sha256_file(source),
        "duration_seconds": 10.0,
        "confirmed_roles": {"mic_streams": [0], "bed_streams": [], "excluded_existing_mix_streams": []},
        "role_confirmation": "caller/agent-confirmed",
        "lane_profiles": [{"audio_stream_index": 0, "speech_shape_ratio": 1.0, "maximum_true_peak_dbtp": -20.0}],
        "regimes": [{"id": "r001", "start_seconds": 0.0, "end_seconds": 10.0, "raw_speech_body_lufs": -20.5, "clean_gain_headroom": {"max_clean_gain_before_noise_floor_target_db": 20.0}}],
        "speech_windows": [],
        "step_candidates": [],
        "bed_regimes": [],
        "bed_step_candidates": [],
    }
    analysis_path = tmp_path / "analysis.json"
    analysis_path.write_text(json.dumps(analysis), encoding="utf-8")
    plan_path = tmp_path / "plan.json"
    plan_init_command(argparse.Namespace(analysis=str(analysis_path), out=str(plan_path)))
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    rendered = tmp_path / "rendered-mic.wav"
    rendered.write_bytes(b"rendered")
    supplied = tmp_path / "unrelated-mic.wav"
    supplied.write_bytes(b"unrelated")
    manifest_path = tmp_path / "render.json"
    manifest_path.write_text(json.dumps({
        "generated_by": "rv-render", "status": "rendered", "source_sha256": analysis["source_sha256"],
        "plan_sha256": sha256_json(plan), "analysis_sha256": sha256_json(analysis),
        "components": {"mic": {"path": str(rendered), "sha256": sha256_file(rendered)}},
    }), encoding="utf-8")
    args = argparse.Namespace(
        source=str(source), candidate_mic=str(supplied), manifest=str(manifest_path), plan=str(plan_path), analysis=str(analysis_path),
        regime_id="r001", start=0.0, duration=1.0, outdir=str(tmp_path / "audition"), json_out=str(tmp_path / "audition.json"),
        reviewed=False, reviewed_by=None, commentary_quality=None, background_quality=None, overall_quality=None,
    )
    with pytest.raises(RvError, match="not the current render-manifest mic component"):
        audition_command(args)


@pytest.mark.parametrize("bad_gain", ["nan", "inf", "-inf", 1e12, -500.0])
def test_non_finite_or_absurd_gain_fails_plan_validation(bad_gain: object) -> None:
    analysis = {"duration_seconds": 10.0, "lane_profiles": [], "step_candidates": [], "regimes": []}
    plan = _minimal_plan(analysis, bad_gain)
    rows = validate_plan(plan, analysis)
    classes = {row["failure_class"] for row in rows if row["status"] == "fail"}
    assert "non_finite_plan_value" in classes


def test_deliver_refuses_output_equal_to_source(tmp_path: Path) -> None:
    source = tmp_path / "clip.mkv"
    source.write_bytes(b"source-bytes")
    mix = tmp_path / "mix.wav"
    mix.write_bytes(b"mix-bytes")
    manifest = tmp_path / "promotion_manifest.json"
    promotion = {
        "rows": [],
        "candidate": {"path": str(mix), "sha256": sha256_file(mix)},
        "source_sha256": sha256_file(source),
    }
    manifest.write_text(json.dumps(promotion), encoding="utf-8")
    args = argparse.Namespace(
        manifest=str(manifest),
        source=str(source),
        output=str(source),
        exact_output_request="caller literally asked to overwrite the source",
        allow_overwrite=True,
    )
    with pytest.raises(RvError, match="never be overwritten"):
        deliver_command(args)


def test_deliver_refuses_output_equal_to_candidate(tmp_path: Path) -> None:
    source = tmp_path / "clip.mkv"
    source.write_bytes(b"source-bytes")
    mix = tmp_path / "mix.wav"
    mix.write_bytes(b"mix-bytes")
    manifest = tmp_path / "promotion_manifest.json"
    promotion = {
        "rows": [],
        "candidate": {"path": str(mix), "sha256": sha256_file(mix)},
        "source_sha256": sha256_file(source),
    }
    manifest.write_text(json.dumps(promotion), encoding="utf-8")
    args = argparse.Namespace(
        manifest=str(manifest),
        source=str(source),
        output=str(mix),
        exact_output_request="quote",
        allow_overwrite=True,
    )
    with pytest.raises(RvError, match="never be overwritten"):
        deliver_command(args)


def test_delivery_ok_rejects_empty_output_path_without_crash(tmp_path: Path) -> None:
    promotion = {"candidate": {"sha256": "abc"}, "source_sha256": "src"}
    delivery = {
        "promotion_manifest_sha256": sha256_json(promotion),
        "candidate": {"sha256": "abc"},
        "source_sha256": "src",
        "status": "delivered",
        "output_path": "",
        "output_sha256": "whatever",
        "mux": {"extracted_audio_hash_match": True},
        "contract_name_match": True,
    }
    assert _delivery_ok(delivery, promotion, tmp_path / "promotion_manifest.json") is False


def test_delivery_ok_rejects_claims_without_rv_deliver_provenance(tmp_path: Path) -> None:
    promotion = {"candidate": {"sha256": "abc"}, "source_sha256": "src"}
    forged = {
        "promotion_manifest_sha256": sha256_json(promotion),
        "candidate_mix_sha256": "abc",
        "source_sha256": "src",
        "status": "awaiting-overwrite",
        "artifact_mode": "scratch-candidate",
        "output_path": str(tmp_path / "out.mkv"),
        "output_written": False,
        "next_action": "approve overwrite",
        "caller_test_mux_allowed_after_overwrite": True,
    }
    assert _delivery_ok(forged, promotion, tmp_path / "promotion_manifest.json") is False


def test_stop_binds_artifact_mode_to_run_and_delivery_state(tmp_path: Path) -> None:
    promotion_path = tmp_path / "promotion.json"
    promotion = {"status": "pass", "rows": [], "candidate": {"sha256": "abc"}, "outcome": {"class": "pass"}}
    report = "Run status: caller-test-ready\nArtifact mode: final-deliverable\n"
    findings = validate_stop(report, promotion, promotion_path, None)
    assert any(row["code"] == "artifact_status_mismatch" for row in findings)
    report = "Run status: caller-test-ready\nArtifact mode: mystery\n"
    findings = validate_stop(report, promotion, promotion_path, None)
    assert any(row["code"] == "missing_or_unknown_artifact_mode" for row in findings)


def test_promotion_replay_rejects_forged_verifier_owned_summaries(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import copy
    import rv.verify as verify_module

    mix = tmp_path / "mix.wav"
    mix.write_bytes(b"candidate")
    source_hash = "s" * 64
    analysis = {"source_sha256": source_hash, "parameters": {}}
    plan = {
        "schema_version": 1,
        "analysis": {"sha256": sha256_json(analysis), "source_sha256": source_hash},
        "roles": {"mic_streams": [0], "bed_streams": []},
        "rails": {},
        "boundary_overrides": [],
        "render": {"peak_control": {"enabled": False}},
    }
    render = {
        "generated_by": "rv-render",
        "status": "rendered",
        "source_sha256": source_hash,
        "plan_sha256": sha256_json(plan),
        "analysis_sha256": sha256_json(analysis),
        "components": {"mix": {"path": str(mix), "sha256": sha256_file(mix)}},
    }
    analysis_path = tmp_path / "analysis.json"
    plan_path = tmp_path / "plan.json"
    render_path = tmp_path / "render.json"
    for path, payload in ((analysis_path, analysis), (plan_path, plan), (render_path, render)):
        path.write_text(json.dumps(payload), encoding="utf-8")
    required = {"hash", "lineage", "component_derivation", "length", "null_test", "sample_peak", "true_peak", "mic_lufs", "gain_dip_artifact"}
    rows = [{"type": row_type, "status": "pass", "failure_class": None, "next_action": "none", "action_scope": "none"} for row_type in sorted(required)]
    monkeypatch.setattr(verify_module, "verify_candidate", lambda *args: copy.deepcopy(rows))
    promotion = {
        "generated_by": "rv-verify",
        "status": "pass",
        "overall": {"status": "pass", "pass": True, "fail_with_work": False, "fail_terminal_candidates": []},
        "outcome": {"class": "pass", "limitation_owner": "NONE", "evidence": [], "recommended_fix": "NONE"},
        "render_manifest_path": str(render_path),
        "render_manifest_sha256": sha256_json(render),
        "plan_path": str(plan_path),
        "plan_sha256": sha256_json(plan),
        "analysis_path": str(analysis_path),
        "analysis_sha256": sha256_json(analysis),
        "source_sha256": source_hash,
        "candidate": render["components"]["mix"],
        "peak_control": {"enabled": False},
        "rows": rows,
        "overrides_and_adjustments": {"role_override": None, "boundary_overrides": [], "rails_adjustment": None, "non_default_analyze_parameters": []},
    }
    _validate_promotion_chain(promotion)
    forged_peak = copy.deepcopy(promotion)
    forged_peak["peak_control"] = {"enabled": True, "mechanism": "magic"}
    with pytest.raises(RvError, match="peak_control differs"):
        _validate_promotion_chain(forged_peak)
    forged_surfaces = copy.deepcopy(promotion)
    forged_surfaces["overrides_and_adjustments"]["rails_adjustment"] = {"forged": True}
    with pytest.raises(RvError, match="overrides_and_adjustments differs"):
        _validate_promotion_chain(forged_surfaces)


def test_render_refuses_source_named_mix_inside_outdir_before_overwrite(tmp_path: Path) -> None:
    from make_fixtures import make_all

    workdir = tmp_path / "work"
    workdir.mkdir()
    source_fixture = make_all(workdir)["mono_mic_stereo_bed"]
    candidate = workdir / "candidate"
    candidate.mkdir()
    source = candidate / "mix.wav"
    source.write_bytes(source_fixture.read_bytes())
    before = sha256_file(source)
    rv = Path(__file__).resolve().parents[1] / "scripts" / "rv.py"
    probe = workdir / "probe.json"
    analysis_path = workdir / "analysis.json"
    plan_path = workdir / "render_plan.json"
    validation = workdir / "plan_validation.json"
    import subprocess

    subprocess.run([sys.executable, str(rv), "probe", str(source), "--json-out", str(probe)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    subprocess.run([sys.executable, str(rv), "analyze", str(source), "--probe", str(probe), "--json-out", str(analysis_path)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    subprocess.run([sys.executable, str(rv), "plan-init", "--analysis", str(analysis_path), "--out", str(plan_path)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    for seg in plan["mic_segments"]:
        seg["judgment"] = "hold"
    for seg in plan["bed_segments"]:
        seg["judgment"] = "hold"
    plan_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    subprocess.run([sys.executable, str(rv), "plan-validate", "--plan", str(plan_path), "--analysis", str(analysis_path), "--json-out", str(validation)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    proc = subprocess.run(
        [sys.executable, str(rv), "render", "--source", str(source), "--plan", str(plan_path), "--outdir", str(candidate), "--manifest-out", str(candidate / "render_manifest.json")],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert proc.returncode == 1
    assert "would overwrite or alias the source" in proc.stderr
    assert "rendering mic component" not in proc.stderr
    assert sha256_file(source) == before


def test_render_refuses_manifest_output_aliasing_mix_component(tmp_path: Path) -> None:
    from rv.render import _refuse_output_aliases

    source = tmp_path / "source.mkv"
    plan_path = tmp_path / "plan.json"
    analysis_path = tmp_path / "analysis.json"
    candidate = tmp_path / "candidate"
    mix = candidate / "mix.wav"
    with pytest.raises(Exception, match="overwrite or alias output mix.wav"):
        _refuse_output_aliases(
            source,
            mix,
            [candidate / "mic_component.wav", candidate / "bed_component.wav", mix],
            [plan_path, analysis_path],
            {},
        )


def test_atomic_json_write_and_alias_guard_preserve_protected_input(tmp_path: Path) -> None:
    from rv.util import refuse_output_alias, write_json

    protected = tmp_path / "source.mkv"
    protected.write_bytes(b"source")
    with pytest.raises(Exception, match="overwrite or alias protected input"):
        refuse_output_alias(protected, [protected], ["choose another output"], label="test JSON")
    assert protected.read_bytes() == b"source"
    output = tmp_path / "state.json"
    write_json(output, {"status": "pass"})
    assert json.loads(output.read_text(encoding="utf-8"))["status"] == "pass"
    assert not list(tmp_path.glob(".state.json.*.tmp"))


def test_atomic_csv_write_replaces_hardlink_without_truncating_referent(tmp_path: Path) -> None:
    import os

    from rv.util import write_csv

    protected = tmp_path / "protected.bin"
    protected.write_bytes(b"do-not-touch")
    output = tmp_path / "curve.csv"
    os.link(protected, output)

    write_csv(output, [{"time": 1, "level": -20}], ["time", "level"])

    assert protected.read_bytes() == b"do-not-touch"
    assert output.read_text(encoding="utf-8").splitlines() == ["time,level", "1,-20"]
    assert not os.path.samefile(protected, output)
    assert not list(tmp_path.glob(".curve.csv.*.tmp"))


def test_atomic_csv_temp_creation_does_not_follow_preexisting_link(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import os
    from types import SimpleNamespace

    import rv.util as util

    protected = tmp_path / "protected.bin"
    protected.write_bytes(b"do-not-touch")
    output = tmp_path / "curve.csv"
    hostile_temp = tmp_path / ".curve.csv.hostile.tmp"
    os.link(protected, hostile_temp)
    identifiers = iter((SimpleNamespace(hex="hostile"), SimpleNamespace(hex="fresh")))
    monkeypatch.setattr(util.uuid, "uuid4", lambda: next(identifiers))

    util.write_csv(output, [{"time": 1}], ["time"])

    assert protected.read_bytes() == b"do-not-touch"
    assert hostile_temp.read_bytes() == b"do-not-touch"
    assert output.read_text(encoding="utf-8").splitlines() == ["time", "1"]


def test_atomic_csv_write_replaces_symlink_without_truncating_referent(tmp_path: Path) -> None:
    import os

    from rv.util import write_csv

    protected = tmp_path / "protected.bin"
    protected.write_bytes(b"do-not-touch")
    output = tmp_path / "curve.csv"
    try:
        output.symlink_to(protected)
    except OSError as exc:
        pytest.skip(f"symlinks unavailable on this host: {exc}")

    write_csv(output, [{"time": 1}], ["time"])

    assert protected.read_bytes() == b"do-not-touch"
    assert not output.is_symlink()
    assert output.read_text(encoding="utf-8").splitlines() == ["time", "1"]


def test_plan_level_role_override_is_unsupported(tmp_path: Path) -> None:
    analysis = {
        "duration_seconds": 10.0,
        "source_sha256": "src",
        "lane_profiles": [
            {"audio_stream_index": 0, "speech_shape_ratio": 0.1},
            {"audio_stream_index": 1, "speech_shape_ratio": 0.9},
        ],
        "cross_lane_correlation": {"existing_mix_candidates": []},
        "step_candidates": [],
        "regimes": [],
    }
    plan = _minimal_plan(analysis, 0.0)
    plan["roles"]["role_override"] = {"reason": "manual role proof", "isolated_sample_manifests": [str(tmp_path / "missing.json")]}
    rows = validate_plan(plan, analysis)
    assert any(row["failure_class"] == "role_override_unsupported" for row in rows)


def test_plan_level_boundary_override_is_unsupported(tmp_path: Path) -> None:
    analysis = {"duration_seconds": 10.0, "lane_profiles": [], "step_candidates": [], "regimes": []}
    plan = _minimal_plan(analysis, 0.0)
    plan["boundary_overrides"] = [{"boundary_seconds": 5.0, "reason": "false step", "evidence_paths": [str(tmp_path / "missing.png")]}]
    rows = validate_plan(plan, analysis)
    assert any(row["failure_class"] == "boundary_override_unsupported" for row in rows)


def test_rails_adjustment_evidence_must_resolve_inside_current_analysis() -> None:
    analysis = {"duration_seconds": 10.0, "lane_profiles": [], "step_candidates": [], "regimes": [{"raw_speech_body_lufs": -31.0}]}
    plan = _minimal_plan(analysis, 0.0)
    plan["rails"]["rails_adjustment"] = {"mic_band_center_shift_db": 1.0, "gap_band_shift_db": 0.0, "analysis_evidence_paths": ["regimes[99].raw_speech_body_lufs", "/regimes/0/missing"]}
    rows = validate_plan(plan, analysis)
    assert any(row["failure_class"] == "rails_adjustment_missing_evidence" for row in rows)
    plan["rails"]["rails_adjustment"]["analysis_evidence_paths"] = ["regimes[0].raw_speech_body_lufs", "/regimes/0/raw_speech_body_lufs"]
    rows = validate_plan(plan, analysis)
    assert not any(row["failure_class"] == "rails_adjustment_missing_evidence" for row in rows)


def _complete_report(candidate_hash: str, **overrides: str) -> str:
    fields = {
        "Run status": "blocked-terminal",
        "Artifact mode": "scratch-candidate",
        "Source": "C:/media/clip.mkv sha256=src",
        "Output": "NONE",
        "Candidate sha256": candidate_hash,
        "Promotion manifest": "C:/scratch/promotion_manifest.json",
        "Analysis": "C:/scratch/analysis.json",
        "Render plan": "C:/scratch/render_plan.json",
        "Stop state": "C:/scratch/stop_state.json",
        "Runnable manifest work remains": "NONE",
        "External blocker": "terminal source evidence recorded",
        "Informational rows": '{"count": 0, "failure_classes": []}',
    }
    fields.update(overrides)
    return "\n".join(f"{label}: {value}" for label, value in fields.items()) + "\n"


def test_validate_stop_rejects_blank_required_values(tmp_path: Path) -> None:
    from rv.stop import validate_stop

    promotion = {"status": "pass", "rows": [], "candidate": {"sha256": "abc"}, "overrides_and_adjustments": {}}
    report = _complete_report("abc", **{"Source": "   ", "Stop state": " "})
    findings = validate_stop(report, promotion, tmp_path / "promotion_manifest.json", None)
    codes = {f["code"] for f in findings}
    assert "missing_report_value" in codes


def test_placeholder_scan_skips_verbatim_caller_quote_lines(tmp_path: Path) -> None:
    from rv.stop import validate_stop

    promotion = {"status": "pass", "rows": [], "candidate": {"sha256": "abc"}, "overrides_and_adjustments": {}}
    ok_report = _complete_report("abc") + 'Exact output request: "please write to <that> path"\n'
    findings = validate_stop(ok_report, promotion, tmp_path / "promotion_manifest.json", None)
    assert not any(f["code"] == "report_contains_placeholder" for f in findings)
    bad_report = _complete_report("abc") + "Notes: fill in <placeholder> later\n"
    findings = validate_stop(bad_report, promotion, tmp_path / "promotion_manifest.json", None)
    assert any(f["code"] == "report_contains_placeholder" for f in findings)


def test_invalid_segment_judgment_fails_plan_validation() -> None:
    analysis = {"duration_seconds": 10.0, "lane_profiles": [], "step_candidates": [], "regimes": []}
    plan = _minimal_plan(analysis, 0.0)
    plan["mic_segments"][0]["judgment"] = "vibes"
    rows = validate_plan(plan, analysis)
    assert any(row["failure_class"] == "invalid_judgment" for row in rows)


def test_analyze_parameters_reject_non_finite_values() -> None:
    from rv.speech import build_parameters

    with pytest.raises(ValueError, match="outside bounds"):
        build_parameters({"min_plateau_seconds": float("nan")})
    with pytest.raises(ValueError, match="outside bounds"):
        build_parameters({"step_min_db": float("inf")})
