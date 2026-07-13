from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import uuid
import wave
from pathlib import Path

from rv.audio import _ffmpeg_render_filter_legacy, _target_sample_count, decoded_float_samples, ffmpeg_mix_components, ffmpeg_render_filter, sample_count
from make_fixtures import make_all
from rv.deliver import _mux_candidate, deliver_command
from rv.plan import _micro_chunk_rows, _peak_control_rows as _plan_peak_control_rows, validate_plan
from rv.rails import load_default_rails
from rv.stop import validate_stop
from rv.util import sha256_file, sha256_json
from rv.verify import _dip_rows, _expected_gain_by_time, _gap_rows, _mic_rows, _peak_control_rows, _transition_rows, _true_peak_rows, verify_candidate

ROOT = Path(__file__).resolve().parents[1]
RV = ROOT / "scripts" / "rv.py"


def _workdir(name: str) -> Path:
    if "RV_TEST_TMPDIR" not in os.environ:
        raise AssertionError("RV_TEST_TMPDIR must be set for rv tests")
    base = Path(os.environ["RV_TEST_TMPDIR"]).resolve()
    base.mkdir(parents=True, exist_ok=True)
    target = base / f"rv-workflow-{name}-{uuid.uuid4().hex}"
    target.mkdir()
    return target


def _run(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(RV), *args], check=check, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def _probe_analyze_plan(media: Path, workdir: Path) -> tuple[Path, Path, Path, dict, dict]:
    probe = workdir / "probe.json"
    analysis_path = workdir / "analysis.json"
    plan_path = workdir / "render_plan.json"
    _run(["probe", str(media), "--json-out", str(probe)])
    _run(["analyze", str(media), "--probe", str(probe), "--json-out", str(analysis_path)])
    _run(["plan-init", "--analysis", str(analysis_path), "--out", str(plan_path)])
    analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    return probe, analysis_path, plan_path, analysis, plan


def _fill_good_gains(plan: dict, analysis: dict, *, mic_offset_db: float = 0.0) -> dict:
    del analysis
    for seg in plan["mic_segments"]:
        seg["gain_db"] = round(float(seg["gain_db"]) + mic_offset_db, 3)
        seg["judgment"] = "hold"
        seg["evidence_paths"] = ["analysis.json:regimes"]
    for seg in plan["bed_segments"]:
        seg["gain_db"] = round(float(seg["gain_db"]) + mic_offset_db, 3)
        seg["judgment"] = "hold"
    return plan


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _make_two_lane_source(path: Path, *, duration: float, mic_volume_db: float, bed_volume_db: float | None = None) -> None:
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-nostdin",
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"sine=frequency=997:sample_rate=48000:duration={duration:.6f}",
        "-f",
        "lavfi",
        "-i",
        f"{'anullsrc=r=48000:cl=stereo' if bed_volume_db is None else f'sine=frequency=181:sample_rate=48000:duration={duration:.6f}'}",
        "-filter_complex",
        f"[0:a:0]volume={mic_volume_db:.3f}dB,pan=stereo|c0=c0|c1=c0[mic];[1:a:0]{'' if bed_volume_db is None else f'volume={bed_volume_db:.3f}dB,'}aformat=sample_fmts=s16:channel_layouts=stereo[bed]",
        "-map",
        "[mic]",
        "-map",
        "[bed]",
        "-t",
        f"{duration:.6f}",
        "-c:a",
        "flac",
        str(path),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def _complete_report(
    promotion: dict,
    promotion_path: Path,
    *,
    status: str = "caller-test-ready",
    artifact: str = "caller-test-mux",
    delivery: dict | None = None,
    finalization: str = "NONE",
) -> str:
    candidate_hash = promotion.get("candidate", {}).get("sha256", "")
    failing = [row for row in promotion.get("rows", []) if row.get("status") == "fail"]
    runnable = "NONE" if not failing else f"yes - {failing[0].get('failure_class')}: {failing[0].get('next_action')}"
    render = {}
    render_path = Path(str(promotion.get("render_manifest_path") or ""))
    if render_path.is_file():
        render = json.loads(render_path.read_text(encoding="utf-8"))
    source = (delivery or {}).get("source_path") or render.get("source_path") or "NOT RUN - promotion render lineage unavailable"
    output = delivery.get("output_path") if delivery else "NOT RUN - no delivery manifest"
    analysis_line = f"{promotion.get('analysis_path')} sha256={promotion.get('analysis_sha256')}" if promotion.get("analysis_path") else "NOT RUN - promotion analysis lineage unavailable"
    plan_line = f"{promotion.get('plan_path')} sha256={promotion.get('plan_sha256')}" if promotion.get("plan_path") else "NOT RUN - promotion plan lineage unavailable"
    peak = promotion.get("peak_control", {})
    outcome = promotion.get("outcome", {"class": "pass", "limitation_owner": "NONE", "evidence": [], "recommended_fix": "NONE"})
    informational_rows = [row for row in promotion.get("rows", []) if row.get("status") == "pass" and row.get("failure_class")]
    informational_classes = sorted({str(row["failure_class"]) for row in informational_rows})
    informational = json.dumps({"count": len(informational_rows), "failure_classes": informational_classes}, sort_keys=True)
    bed_proof_rows = [row for row in promotion.get("rows", []) if row.get("type") == "bed_yield_necessity" and isinstance(row.get("proof"), dict)]
    bed_reconciliation = json.dumps(bed_proof_rows[0]["proof"], sort_keys=True) if len(bed_proof_rows) == 1 else "NONE"
    if len(bed_proof_rows) == 1:
        bed_proof = bed_proof_rows[0]["proof"]
        preferred_gap = str(bed_proof.get("preferred_gap_db")) if bed_proof.get("preferred_gap_db") is not None else "NONE"
        delivered_gap = json.dumps(bed_proof.get("common_window_gap_distribution"), sort_keys=True) if isinstance(bed_proof.get("common_window_gap_distribution"), list) else "NONE"
        widening_reason = json.dumps(bed_proof.get("controlling_failure"), sort_keys=True) if isinstance(bed_proof.get("controlling_failure"), dict) else "NONE - deep bed yield not triggered" if bed_proof.get("triggered") is not True else "NONE"
        remaining_lift = str(bed_proof.get("maximum_candidate_safe_uniform_lift_db")) if bed_proof.get("maximum_candidate_safe_uniform_lift_db") is not None else "NOT RUN - deep bed yield not triggered" if bed_proof.get("triggered") is not True else "NONE"
    else:
        preferred_gap = delivered_gap = widening_reason = remaining_lift = "NONE"
    peak_lines = []
    delivery_lines = []
    if delivery and delivery.get("status") == "delivered" and isinstance(delivery.get("mux"), dict):
        mux = delivery["mux"]
        delivery_lines = [
            "- Delivery status: delivered",
            "- Output written: true",
            f"- Remix audio first/default: {str(mux.get('remix_audio_stream_index') == 0 and mux.get('verified_audio_inventory', {}).get('default_audio_stream_indexes') == [0]).lower()}",
            f"- Original audio preserved: {str(mux.get('original_audio_streams_preserved_after_remix') is True).lower()}",
            f"- Video copied: {str(mux.get('video_copied') is True).lower()}",
            f"- Remixed audio hash match: {str(mux.get('extracted_audio_hash_match') is True).lower()}",
        ]
    if peak.get("enabled") is True:
        peak_lines = [
            "- Peak control enabled: true",
            f"- Peak control mechanism: {peak.get('mechanism')}",
            f"- Peak control declared ceiling dBTP: {peak.get('declared_true_peak_ceiling_dbtp')}",
            f"- Peak control pre mic sha256: {peak.get('pre_control_mic_sha256')}",
            f"- Peak control post mic sha256: {peak.get('post_control_mic_sha256')}",
            f"- Peak control worst regime BODY delta dB: {peak.get('worst_per_regime_body_delta_db')}",
            f"- Peak control global duty: {peak.get('global_duty_fraction')}",
            f"- Peak control worst regime duty: {peak.get('worst_regime_duty_fraction')}",
            f"- Peak control max contiguous run seconds: {peak.get('max_contiguous_controlled_run_seconds')}",
        ]
    return "\n".join(
        [
            f"- Run status: {status}",
            f"- Artifact mode: {artifact}",
            f"- Source: {source}",
            f"- Output: {output}",
            f"- Candidate sha256: {candidate_hash}",
            f"- Promotion manifest: {promotion_path} sha256={sha256_json(promotion)} status={promotion.get('status')}",
            f"- Analysis: {analysis_line}",
            f"- Render plan: {plan_line}",
            "- Stop state: NOT RUN - generated after report validation",
            f"- Runnable manifest work remains: {runnable}",
            "- External blocker: NONE",
            f"- Finalization evidence: {finalization}",
            f"- Outcome class: {outcome.get('class')}",
            f"- Limitation owner: {outcome.get('limitation_owner')}",
            f"- Limitation evidence: {json.dumps(outcome.get('evidence', []), sort_keys=True)}",
            f"- Recommended fix: {outcome.get('recommended_fix')}",
            f"- Informational rows: {informational}",
            f"- Bed balance reconciliation: {bed_reconciliation}",
            f"- Preferred mic/bed gap dB: {preferred_gap}",
            f"- Delivered meaningful-bed gap distribution: {delivered_gap}",
            f"- Gap widening reason: {widening_reason}",
            f"- Remaining safe uniform bed lift dB: {remaining_lift}",
            "- Source file preserved: true",
            *peak_lines,
            *delivery_lines,
        ]
    )


def test_pinned_rails_regressions_fail_and_best_like_pass() -> None:
    rails = load_default_rails()
    assert rails["processed_mic_active_speech_lufs"]["min"] == -23.0
    analysis = {
        "regimes": [{"id": "r001", "duration_seconds": 60.0, "active_speech_density": 0.5, "clean_gain_headroom": {"margin_db": 20.0}}],
        "speech_windows": [{"regime_id": "r001", "start_seconds": 0.0, "end_seconds": 20.0, "duration_seconds": 20.0}],
        "bed_presence_windows": [{"regime_id": "r001", "start_seconds": 0.0, "end_seconds": 20.0, "bed_present": True}],
    }
    plan = {"segments": [{"regime_id": "r001"}], "rails": {}}
    test2_mic = [{"time_seconds": i / 10, "end_seconds": i / 10 + 0.1, "momentary_lufs": -23.7} for i in range(200)]
    best_mic = [{"time_seconds": i / 10, "end_seconds": i / 10 + 0.1, "momentary_lufs": -20.5} for i in range(200)]
    low_gap_bed = [{"time_seconds": i / 10, "end_seconds": i / 10 + 0.1, "momentary_lufs": -29.1} for i in range(200)]
    best_bed = [{"time_seconds": i / 10, "end_seconds": i / 10 + 0.1, "momentary_lufs": -30.9} for i in range(200)]
    assert any(row["failure_class"] == "mic_below_rail" for row in _mic_rows(plan, analysis, test2_mic, rails))
    assert any(row["failure_class"] == "mic_bed_gap_out_of_rail" for row in _gap_rows(plan, analysis, test2_mic, low_gap_bed, rails))
    assert all(row["status"] == "pass" for row in _mic_rows(plan, analysis, best_mic, rails))
    assert all(row["status"] == "pass" for row in _gap_rows(plan, analysis, best_mic, best_bed, rails))


def test_noncontract_filename_rejected_and_false_stop_rejected(tmp_path: Path) -> None:
    mix = tmp_path / "mix.wav"
    mix.write_bytes(b"not-a-real-wav-but-hashable")
    promotion = {"rows": [], "candidate": {"path": str(mix), "sha256": __import__("hashlib").sha256(mix.read_bytes()).hexdigest()}}
    manifest = tmp_path / "promotion_manifest.json"
    _write_json(manifest, promotion)
    source = tmp_path / "source.mkv"
    source.write_bytes(b"source")
    output = tmp_path / f"{source.stem}-REMIX-VOICEOVER-extra-label.mkv"
    args = type("Args", (), {"manifest": str(manifest), "source": str(source), "output": str(output), "exact_output_request": None, "allow_overwrite": False})()
    try:
        deliver_command(args)
    except Exception as exc:
        assert "output path must be the contract name" in str(exc)
    else:
        raise AssertionError("non-contract filename should be rejected")
    stop_findings = validate_stop(
        "- Run status: iteration-incomplete\n- Artifact mode: scratch-candidate\n- External blocker: none\n",
        {"status": "fail", "rows": [{"status": "fail", "failure_class": "mic_below_rail", "next_action": "raise mic_gain_db and rerun render"}]},
        manifest,
        None,
    )
    assert any(row["code"] == "false_stop_runnable_work" for row in stop_findings)


def test_verify_self_validates_plan_and_render_ignores_tampered_sibling_verdict() -> None:
    workdir = _workdir("selfvalidate")
    fixtures = make_all(workdir)
    media = fixtures["mono_mic_stereo_bed"]
    _, analysis_path, plan_path, analysis, plan = _probe_analyze_plan(media, workdir)
    _fill_good_gains(plan, analysis)
    plan["rails"]["rails_adjustment"] = {"mic_band_center_shift_db": 99.0, "gap_band_shift_db": 0.0, "analysis_evidence_paths": ["analysis.json:regimes"]}
    _write_json(plan_path, plan)
    _write_json(workdir / "plan_validation.json", {"status": "pass", "plan_sha256": __import__("rv.util").util.sha256_json(plan)})
    proc = _run(["render", "--source", str(media), "--plan", str(plan_path), "--outdir", str(workdir / "candidate"), "--manifest-out", str(workdir / "render_manifest.json")], check=False)
    assert proc.returncode == 1
    assert "plan validation did not pass" in proc.stderr

    rows = verify_candidate({"components": {}}, plan, analysis, workdir / "render_manifest.json")
    assert any(row.get("failure_class") == "rails_adjustment_out_of_bounds" for row in rows)


def test_deliver_refuses_source_hash_mismatch_before_mux(tmp_path: Path) -> None:
    source = tmp_path / "source.mka"
    source.write_bytes(b"actual source")
    mix = tmp_path / "mix.wav"
    mix.write_bytes(b"candidate")
    promotion = {
        "status": "pass",
        "source_sha256": "0" * 64,
        "rows": [],
        "candidate": {"path": str(mix), "sha256": __import__("hashlib").sha256(mix.read_bytes()).hexdigest()},
    }
    manifest = tmp_path / "promotion_manifest.json"
    _write_json(manifest, promotion)
    args = type("Args", (), {"manifest": str(manifest), "source": str(source), "output": str(source.with_name("source-REMIX-VOICEOVER.mka")), "exact_output_request": None, "allow_overwrite": False})()
    try:
        deliver_command(args)
    except Exception as exc:
        assert "source hash does not match promotion manifest" in str(exc)
    else:
        raise AssertionError("source hash mismatch should refuse delivery")


def test_deliver_mp4_uses_alac_and_decoded_pcm_hash(tmp_path: Path) -> None:
    source = tmp_path / "clip.mp4"
    mix = tmp_path / "mix.wav"
    subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostdin",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "color=c=black:s=64x64:r=5:d=1",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:sample_rate=48000:duration=1",
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "96k",
            str(source),
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-y", "-f", "lavfi", "-i", "sine=frequency=880:sample_rate=48000:duration=1", "-ac", "2", "-c:a", "pcm_f32le", str(mix)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output = source.with_name("clip-REMIX-VOICEOVER.mp4")
    mux = _mux_candidate(source, mix, output, ["repair test fixture"])
    assert mux["remix_audio_codec"] == "alac"
    assert mux["extracted_audio_hash_match"] is True
    inventory = mux["verified_audio_inventory"]
    assert inventory["audio_stream_count"] == 2
    assert inventory["default_audio_stream_indexes"] == [0]
    assert inventory["preserved_original_audio_streams"][0]["decoded_pcm_match"] is True
    assert inventory["preserved_original_audio_streams"][0]["default_disposition"] == 0


def test_deliver_native_flac_keeps_extension_and_source_untouched(tmp_path: Path) -> None:
    source = tmp_path / "voice.flac"
    mix = tmp_path / "mix.wav"
    subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-y", "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=1", "-ac", "2", "-c:a", "flac", str(source)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-y", "-f", "lavfi", "-i", "sine=frequency=880:sample_rate=48000:duration=1", "-ac", "2", "-c:a", "pcm_f32le", str(mix)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    source_hash = sha256_file(source)
    output = source.with_name("voice-REMIX-VOICEOVER.flac")
    mux = _mux_candidate(source, mix, output, ["repair test fixture"])
    assert output.suffix == source.suffix
    assert mux["remix_audio_codec"] == "flac"
    assert mux["delivery_profile"] == "native-single-program"
    assert mux["original_audio_streams_preserved_after_remix"] is False
    assert mux["source_file_preserved"] is True
    assert mux["extracted_audio_hash_match"] is True
    assert sha256_file(source) == source_hash
    assert mux["verified_audio_inventory"]["audio_stream_count"] == 1
    assert mux["verified_audio_inventory"]["source_file_preserved_beside_output"] is True


def test_validate_stop_rejects_missing_unknown_noneish_and_ready_false_pass(tmp_path: Path) -> None:
    promotion_path = tmp_path / "promotion_manifest.json"
    promotion = {"status": "fail", "rows": [{"status": "fail", "failure_class": "mic_below_rail", "next_action": "raise mic"}]}
    _write_json(promotion_path, promotion)
    assert any(row["code"] == "missing_or_unknown_run_status" for row in validate_stop("- Artifact mode: scratch-candidate\n", promotion, promotion_path, None))
    assert any(row["code"] == "missing_or_unknown_run_status" for row in validate_stop("- Run status: done\n- Artifact mode: scratch-candidate\n", promotion, promotion_path, None))
    noneish = validate_stop("- Run status: iteration-incomplete\n- Artifact mode: scratch-candidate\n- External blocker: n/a\n", {"status": "pass", "rows": []}, promotion_path, None)
    assert any(row["code"] == "iteration_incomplete_missing_external_blocker" for row in noneish)
    ready = validate_stop("- Run status: caller-test-ready\n- Artifact mode: caller-test-mux\n", promotion, promotion_path, None)
    assert any(row["code"] == "false_pass_with_failing_rows" for row in ready)


def test_validate_stop_requires_machine_checkable_report_packet(tmp_path: Path) -> None:
    mix = tmp_path / "mix.wav"
    mix.write_bytes(b"mix")
    promotion_path = tmp_path / "promotion_manifest.json"
    promotion = {"status": "pass", "rows": [], "candidate": {"path": str(mix), "sha256": sha256_file(mix)}, "outcome": {"class": "pass", "limitation_owner": "NONE", "evidence": [], "recommended_fix": "NONE"}}
    _write_json(promotion_path, promotion)
    delivery = {
        "generated_by": "rv-deliver",
        "artifact_mode": "scratch-candidate",
        "promotion_manifest_sha256": __import__("rv.util").util.sha256_json(promotion),
        "candidate": {"sha256": sha256_file(mix)},
        "source_sha256": None,
        "status": "awaiting-overwrite",
        "output_path": str(tmp_path / "out.mkv"),
        "output_written": False,
        "next_action": "approve overwrite",
        "caller_test_mux_allowed_after_overwrite": True,
    }
    skeletal = "- Run status: caller-test-ready\n- Artifact mode: scratch-candidate\n"
    assert any(row["code"] == "missing_report_label" for row in validate_stop(skeletal, promotion, promotion_path, delivery))
    report = _complete_report(promotion, promotion_path, artifact="scratch-candidate", delivery=delivery)
    assert validate_stop(report, promotion, promotion_path, delivery) == []
    wrong_source = report.replace("Source: NOT RUN - promotion render lineage unavailable", "Source: wrong-source.mkv")
    assert any(row["code"] == "report_lineage_mismatch" for row in validate_stop(wrong_source, promotion, promotion_path, delivery))
    wrong_stop = report.replace("Stop state: NOT RUN - generated after report validation", "Stop state: forged-stop.json status=pass")
    assert any(row["code"] == "report_lineage_mismatch" for row in validate_stop(wrong_stop, promotion, promotion_path, delivery))
    placeholder = report + "\nTODO\n"
    assert any(row["code"] == "report_contains_placeholder" for row in validate_stop(placeholder, promotion, promotion_path, delivery))


def test_validate_stop_cross_checks_informational_rows(tmp_path: Path) -> None:
    promotion_path = tmp_path / "promotion_manifest.json"
    promotion = {
        "status": "pass",
        "rows": [
            {"status": "pass", "failure_class": "gap_preference_disclosure"},
            {"status": "pass", "failure_class": "bed_underused_disclosure"},
            {"status": "pass", "failure_class": "gap_preference_disclosure"},
            {"status": "pass"},
        ],
        "candidate": {"sha256": "a" * 64},
    }
    _write_json(promotion_path, promotion)
    report = _complete_report(promotion, promotion_path)
    assert not any(row["code"] == "informational_rows_report_mismatch" for row in validate_stop(report, promotion, promotion_path, None))
    stale = report.replace(
        'Informational rows: {"count": 3, "failure_classes": ["bed_underused_disclosure", "gap_preference_disclosure"]}',
        "Informational rows: NONE",
    )
    assert any(row["code"] == "informational_rows_report_mismatch" for row in validate_stop(stale, promotion, promotion_path, None))


def test_validate_stop_requires_exact_verifier_owned_bed_reconciliation(tmp_path: Path) -> None:
    promotion_path = tmp_path / "promotion_manifest.json"
    proof = {
        "policy": "verifier-owned-uniform-bed-lift-v1",
        "triggered": True,
        "preferred_gap_db": 10.5,
        "common_window_gap_distribution": [{"regime_id": "r001", "p10_db": 8.0, "p50_db": 18.6, "p90_db": 24.0, "measured_seconds": 60.0}],
        "maximum_masking_safe_uniform_lift_db": 0.1,
        "maximum_candidate_safe_uniform_lift_db": 0.0,
        "controlling_failure": {"failure_class": "sustained_masking", "longest_run_seconds": 2.1},
    }
    promotion = {
        "status": "pass",
        "rows": [{"type": "bed_yield_necessity", "status": "pass", "failure_class": "bed_yield_necessity_proven", "proof": proof}],
        "candidate": {"sha256": "b" * 64},
    }
    _write_json(promotion_path, promotion)
    report = _complete_report(promotion, promotion_path)
    assert not any(row["code"] == "bed_balance_reconciliation_report_mismatch" for row in validate_stop(report, promotion, promotion_path, None))
    stale = report.replace(json.dumps(proof, sort_keys=True), "NONE")
    assert any(row["code"] == "bed_balance_reconciliation_report_mismatch" for row in validate_stop(stale, promotion, promotion_path, None))
    duplicate = report + f"\n- Bed balance reconciliation: {json.dumps(proof, sort_keys=True)}\n"
    assert any(row["code"] == "duplicate_report_label" for row in validate_stop(duplicate, promotion, promotion_path, None))
    stale_readable = report.replace("Preferred mic/bed gap dB: 10.5", "Preferred mic/bed gap dB: 18.0")
    assert any(row["code"] == "bed_balance_readable_report_mismatch" for row in validate_stop(stale_readable, promotion, promotion_path, None))
    stale_distribution = report.replace('"p50_db": 18.6', '"p50_db": 10.5')
    assert any(row["code"] == "bed_balance_readable_report_mismatch" for row in validate_stop(stale_distribution, promotion, promotion_path, None))


def test_validate_stop_requires_peak_control_disclosure_and_exact_values(tmp_path: Path) -> None:
    promotion_path = tmp_path / "promotion_manifest.json"
    promotion = {
        "status": "pass",
        "rows": [],
        "candidate": {"sha256": "c" * 64},
        "peak_control": {
            "enabled": True,
            "mechanism": "alimiter",
            "declared_true_peak_ceiling_dbtp": -1.5,
            "pre_control_mic_sha256": "a" * 64,
            "post_control_mic_sha256": "b" * 64,
            "worst_per_regime_body_delta_db": 0.125,
            "global_duty_fraction": 0.02,
            "worst_regime_duty_fraction": 0.04,
            "max_contiguous_controlled_run_seconds": 0.8,
        },
    }
    _write_json(promotion_path, promotion)
    report = _complete_report(promotion, promotion_path)
    assert not any(row["code"].startswith("missing_peak_control") or row["code"] == "peak_control_report_mismatch" for row in validate_stop(report, promotion, promotion_path, None))
    missing = "\n".join(line for line in report.splitlines() if "Peak control global duty:" not in line)
    assert any(row["code"] == "missing_peak_control_report_line" for row in validate_stop(missing, promotion, promotion_path, None))
    wrong = report.replace("Peak control worst regime duty: 0.04", "Peak control worst regime duty: 0.05")
    assert any(row["code"] == "peak_control_report_mismatch" for row in validate_stop(wrong, promotion, promotion_path, None))


def test_validate_stop_rejects_candidate_hash_and_runnable_work_mismatches(tmp_path: Path) -> None:
    promotion_path = tmp_path / "promotion_manifest.json"
    promotion = {"status": "fail", "rows": [{"status": "fail", "failure_class": "mic_below_rail", "next_action": "raise mic"}], "candidate": {"sha256": "a" * 64}}
    _write_json(promotion_path, promotion)
    report = _complete_report(promotion, promotion_path).replace("Candidate sha256: " + ("a" * 64), "Candidate sha256: " + ("b" * 64)).replace("Runnable manifest work remains: yes - mic_below_rail: raise mic", "Runnable manifest work remains: NONE")
    findings = validate_stop(report, promotion, promotion_path, None)
    assert any(row["code"] == "candidate_sha256_mismatch" for row in findings)
    assert any(row["code"] == "runnable_work_report_mismatch" for row in findings)


def test_delivered_final_requires_quoted_caller_finalization_and_written_output(tmp_path: Path) -> None:
    source = tmp_path / "source.mka"
    mix = tmp_path / "mix.wav"
    _make_two_lane_source(source, duration=1.0, mic_volume_db=-12.0, bed_volume_db=-24.0)
    subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-y", "-f", "lavfi", "-i", "sine=frequency=880:sample_rate=48000:duration=1", "-ac", "2", "-c:a", "pcm_f32le", str(mix)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output = tmp_path / "out.mka"
    mux = _mux_candidate(source, mix, output, ["repair test fixture"])
    assert mux["remix_audio_codec"] == "flac"
    assert mux["extracted_audio_hash_match"] is True
    promotion_path = tmp_path / "promotion_manifest.json"
    promotion = {"status": "pass", "rows": [], "source_sha256": sha256_file(source), "candidate": {"path": str(mix), "sha256": sha256_file(mix)}, "outcome": {"class": "pass", "limitation_owner": "NONE", "evidence": [], "recommended_fix": "NONE"}}
    _write_json(promotion_path, promotion)
    delivery = {
        "generated_by": "rv-deliver",
        "artifact_mode": "caller-test-mux",
        "promotion_manifest_sha256": __import__("rv.util").util.sha256_json(promotion),
        "candidate_mix_sha256": sha256_file(mix),
        "source_path": str(source),
        "source_sha256": sha256_file(source),
        "status": "delivered",
        "output_path": str(output),
        "output_sha256": sha256_file(output),
        "output_written": True,
        "mux": mux,
        "contract_name_match": True,
    }
    missing = _complete_report(promotion, promotion_path, status="delivered-final", artifact="final-deliverable", delivery=delivery)
    assert any(row["code"] == "final_without_caller_finalization" for row in validate_stop(missing, promotion, promotion_path, delivery))
    written_false = dict(delivery)
    written_false["output_written"] = False
    quoted = _complete_report(promotion, promotion_path, status="delivered-final", artifact="final-deliverable", delivery=delivery, finalization='"caller approved this as final"')
    assert any(row["code"] == "final_without_caller_finalization" for row in validate_stop(quoted, promotion, promotion_path, written_false))
    assert validate_stop(quoted, promotion, promotion_path, delivery) == []


def test_audition_evidence_never_waives_a_failing_mic_gate(tmp_path: Path) -> None:
    rails = load_default_rails()
    analysis = {
        "source_sha256": "source-a",
        "regimes": [{"id": "r001", "duration_seconds": 60.0, "active_speech_density": 0.5, "raw_speech_body_lufs": -40.0, "clean_gain_headroom": {"max_clean_gain_before_noise_floor_target_db": 12.0, "margin_db": -5.0}}],
        "speech_windows": [{"regime_id": "r001", "start_seconds": 0.0, "end_seconds": 10.0, "duration_seconds": 10.0}],
    }
    raw = tmp_path / "raw.wav"
    processed = tmp_path / "processed.wav"
    for path in (raw, processed):
        with wave.open(str(path), "wb") as handle:
            handle.setnchannels(2)
            handle.setsampwidth(2)
            handle.setframerate(48000)
            handle.writeframes(b"\0\0\0\0" * 480)
    audition = tmp_path / "audition.json"
    _write_json(
        audition,
        {
            "generated_by": "rv-audition",
            "source_sha256": "source-a",
            "analysis_sha256": sha256_json(analysis),
            "candidate_mic_sha256": "candidate-a",
            "regime_id": "r001",
            "raw_sample": {"path": str(raw), "sha256": sha256_file(raw)},
            "processed_sample": {"path": str(processed), "sha256": sha256_file(processed)},
            "review": {"reviewed": True, "reviewed_by": "listener", "commentary_quality": "fair", "noise_background_quality": "fair", "overall_quality": "fair"},
        },
    )
    mic_curve = [{"time_seconds": i / 10, "end_seconds": i / 10 + 0.1, "momentary_lufs": -24.0} for i in range(100)]
    undergained = {"segments": [{"regime_id": "r001", "mic_gain_db": 3.0}]}
    genuine = {"segments": [{"regime_id": "r001", "mic_gain_db": 6.5}]}
    assert any(row.get("failure_class") == "mic_below_rail" for row in _mic_rows(undergained, analysis, mic_curve, rails))
    assert any(row.get("failure_class") == "mic_below_rail" for row in _mic_rows(genuine, analysis, mic_curve, rails))

    raw.write_bytes(b"not audio")
    assert any(row.get("failure_class") == "mic_below_rail" for row in _mic_rows(genuine, analysis, mic_curve, rails))


def test_headroom_backed_deep_capture_drop_gain_validates_renders_and_verifies(tmp_path: Path) -> None:
    source = tmp_path / "deep_drop.mka"
    _make_two_lane_source(source, duration=30.0, mic_volume_db=-32.42, bed_volume_db=-20.0)
    analysis = {
        "source_sha256": sha256_file(source),
        "duration_seconds": 30.0,
        "lane_profiles": [{"audio_stream_index": 0, "speech_shape_ratio": 0.9}, {"audio_stream_index": 1, "speech_shape_ratio": 0.1}],
        "step_candidates": [],
        "regimes": [
            {
                "id": "r001",
                "start_seconds": 0.0,
                "end_seconds": 30.0,
                "duration_seconds": 30.0,
                "raw_speech_body_lufs": -50.0,
                "active_speech_density": 0.67,
                "clean_gain_headroom": {
                    "max_clean_gain_before_noise_floor_target_db": 66.0,
                    "margin_db": 36.0,
                },
            }
        ],
        "speech_windows": [{"id": "w0001", "regime_id": "r001", "start_seconds": 5.0, "end_seconds": 25.0, "duration_seconds": 20.0}],
        "bed_presence_windows": [],
    }
    analysis_path = tmp_path / "analysis.json"
    _write_json(analysis_path, analysis)
    plan = {
        "analysis": {"path": str(analysis_path), "sha256": sha256_json(analysis), "source_sha256": sha256_file(source), "duration_seconds": 30.0},
        "schema_version": 2,
        "roles": {"mic_streams": [0], "bed_streams": [], "excluded_existing_mix_streams": []},
        "rails": {},
        "targets": {"shared_mic_body_lufs": -20.5, "preferred_mic_over_bed_gap_db": 10.5, "shared_bed_body_lufs": None},
        "mic_segments": [
            {
                "id": "m001",
                "analysis_regime_ids": ["r001"],
                "start_seconds": 0.0,
                "end_seconds": 30.0,
                "gain_db": 30.0,
                "ramp_in_seconds": 0.0,
                "ramp_out_seconds": 0.0,
                "judgment": "lift",
                "evidence_paths": ["/regimes/0/clean_gain_headroom/max_clean_gain_before_noise_floor_target_db"],
            }
        ],
        "bed_segments": [],
        "event_overlays": [],
    }
    assert all(row["status"] == "pass" for row in validate_plan(plan, analysis))
    no_citation = json.loads(json.dumps(plan))
    no_citation["mic_segments"][0]["evidence_paths"] = []
    assert any(row["failure_class"] == "mic_gain_ceiling_needs_evidence" for row in validate_plan(no_citation, analysis))
    too_much = json.loads(json.dumps(plan))
    too_much["mic_segments"][0]["gain_db"] = 60.0
    too_much_analysis = json.loads(json.dumps(analysis))
    too_much_analysis["regimes"][0]["clean_gain_headroom"]["max_clean_gain_before_noise_floor_target_db"] = 65.0
    too_much["analysis"]["sha256"] = sha256_json(too_much_analysis)
    assert any(row["failure_class"] == "mic_gain_ceiling_exceeded" for row in validate_plan(too_much, too_much_analysis))

    plan_path = tmp_path / "render_plan.json"
    _write_json(plan_path, plan)
    render_manifest = tmp_path / "render_manifest.json"
    _run(["render", "--source", str(source), "--plan", str(plan_path), "--outdir", str(tmp_path / "candidate"), "--manifest-out", str(render_manifest)])
    promotion = tmp_path / "promotion_manifest.json"
    _run(["verify", "--manifest", str(render_manifest), "--plan", str(plan_path), "--analysis", str(analysis_path), "--json-out", str(promotion)])
    rows = json.loads(promotion.read_text(encoding="utf-8"))["rows"]
    mic_rows = [row for row in rows if row.get("type") == "mic_lufs"]
    assert mic_rows and all(row["status"] == "pass" for row in mic_rows)


def test_mix_render_is_trimmed_to_exact_target_sample_count(tmp_path: Path) -> None:
    duration = 1.337
    mic = tmp_path / "mic.wav"
    bed = tmp_path / "bed.wav"
    mix = tmp_path / "mix.wav"
    subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-y", "-f", "lavfi", "-i", f"sine=frequency=440:sample_rate=48000:duration={duration:.6f}", "-ac", "2", "-c:a", "pcm_f32le", str(mic)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-y", "-f", "lavfi", "-i", f"sine=frequency=220:sample_rate=48000:duration={duration:.6f}", "-ac", "2", "-c:a", "pcm_f32le", str(bed)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    ffmpeg_mix_components(mic, bed, mix, duration, ["repair"])
    assert sample_count(mix) == _target_sample_count(duration)


def test_segment_renderer_is_sample_identical_to_legacy_on_small_plan(tmp_path: Path) -> None:
    source = tmp_path / "tone.wav"
    subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-v", "error", "-y", "-f", "lavfi", "-i", "sine=frequency=997:sample_rate=48000:duration=3", "-ac", "2", "-c:a", "pcm_f32le", str(source)], check=True)
    segments = [
        {"start_seconds": 0.0, "end_seconds": 0.5, "mic_gain_db": 0.0},
        {"start_seconds": 0.5, "end_seconds": 1.0, "mic_gain_db": 3.0, "ramp_in_seconds": 0.2},
        {"start_seconds": 1.0, "end_seconds": 1.5, "mic_gain_db": -2.0, "ramp_out_seconds": 0.2},
        {"start_seconds": 1.5, "end_seconds": 2.0, "mic_gain_db": 4.0, "ramp_in_seconds": 0.1},
        {"start_seconds": 2.0, "end_seconds": 2.5, "mic_gain_db": 1.0},
        {"start_seconds": 2.5, "end_seconds": 3.0, "mic_gain_db": 0.0},
    ]
    legacy = tmp_path / "legacy.wav"
    scalable = tmp_path / "scalable.wav"
    _ffmpeg_render_filter_legacy(source, [0], {0: 2}, segments, "mic_gain_db", legacy, 3.0, ["repair"])
    meta = ffmpeg_render_filter(source, [0], {0: 2}, segments, "mic_gain_db", scalable, 3.0, ["repair"])
    assert meta["renderer"] == "bounded-segment-slices-f32le-concat"
    assert sample_count(legacy) == sample_count(scalable) == 144000
    assert decoded_float_samples(legacy, ["repair"]) == decoded_float_samples(scalable, ["repair"])


def test_segment_renderer_handles_three_hundred_segment_plan(tmp_path: Path) -> None:
    duration = 3.0
    source = tmp_path / "tone.wav"
    subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-v", "error", "-y", "-f", "lavfi", "-i", f"sine=frequency=440:sample_rate=48000:duration={duration}", "-ac", "2", "-c:a", "pcm_f32le", str(source)], check=True)
    segments = [
        {
            "id": f"e{idx:03d}",
            "role": "exception",
            "event_reason": f"synthetic event {idx}",
            "start_seconds": idx / 100.0,
            "end_seconds": (idx + 1) / 100.0,
            "mic_gain_db": float((idx % 3) - 1),
        }
        for idx in range(300)
    ]
    output = tmp_path / "many.wav"
    meta = ffmpeg_render_filter(source, [0], {0: 2}, segments, "mic_gain_db", output, duration, ["repair"])
    assert meta["segment_count"] == 300
    assert sample_count(output) == _target_sample_count(duration)


def test_zero_db_to_thirteen_db_ramp_renders_interpolation(tmp_path: Path) -> None:
    source = tmp_path / "tone.wav"
    subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-y", "-f", "lavfi", "-i", "sine=frequency=1000:sample_rate=48000:duration=3", "-ac", "2", str(source)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out = tmp_path / "ramped.wav"
    segments = [
        {"start_seconds": 0.0, "end_seconds": 1.0, "mic_gain_db": 0.0},
        {"start_seconds": 1.0, "end_seconds": 3.0, "mic_gain_db": 13.0, "ramp_in_seconds": 1.0},
    ]
    ffmpeg_render_filter(source, [0], {0: 2}, segments, "mic_gain_db", out, 3.0, ["repair"])
    samples = decoded_float_samples(out, ["repair"])
    def rms_at(start: float, end: float) -> float:
        lo = int(start * 48000 * 2)
        hi = int(end * 48000 * 2)
        vals = samples[lo:hi]
        return (sum(v * v for v in vals) / len(vals)) ** 0.5
    early = rms_at(0.4, 0.5)
    mid = rms_at(1.45, 1.55)
    late = rms_at(2.4, 2.5)
    assert early < mid < late


def test_ramped_plan_has_no_dip_but_unplanned_dip_still_fails(tmp_path: Path) -> None:
    raw_csv = tmp_path / "raw.csv"
    raw_csv.write_text("time_seconds,end_seconds,momentary_lufs\n" + "".join(f"{i/10:.1f},{i/10+0.1:.1f},-30.0\n" for i in range(30)), encoding="utf-8")
    segments = [{"start_seconds": 0.0, "end_seconds": 3.0, "mic_gain_db": 13.0, "ramp_in_seconds": 1.0}]
    expected = _expected_gain_by_time(segments, "mic_gain_db")
    mic_curve = [{"time_seconds": i / 10, "end_seconds": i / 10 + 0.1, "momentary_lufs": -30.0 + expected(i / 10)} for i in range(30)]
    plan = {
        "schema_version": 2,
        "roles": {"mic_streams": [0], "bed_streams": []},
        "mic_segments": [{"id": "m001", "start_seconds": 0.0, "end_seconds": 3.0, "gain_db": 13.0, "ramp_in_seconds": 1.0}],
        "bed_segments": [],
        "event_overlays": [],
        "targets": {},
    }
    analysis = {"curve_sidecars": {"0": str(raw_csv)}}
    assert all(row["status"] == "pass" for row in _dip_rows(plan, analysis, mic_curve, load_default_rails()))
    dipped = [dict(row) for row in mic_curve]
    for row in dipped:
        if 1.2 <= row["time_seconds"] < 1.6:
            row["momentary_lufs"] -= 8.0
    assert any(row.get("failure_class") == "applied_gain_dip_artifact" for row in _dip_rows(plan, analysis, dipped, load_default_rails()))


def test_gap_and_coverage_floor_public_rows() -> None:
    rails = load_default_rails()
    plan = {"segments": [{"regime_id": "r001"}], "rails": {}}
    analysis = {
        "regimes": [{"id": "r001", "duration_seconds": 60.0, "active_speech_density": 0.5, "clean_gain_headroom": {"margin_db": 20.0}}],
        "speech_windows": [
            {"regime_id": "r001", "start_seconds": 0.0, "end_seconds": 10.5, "duration_seconds": 10.5},
            {"regime_id": "r001", "start_seconds": 10.5, "end_seconds": 21.0, "duration_seconds": 10.5},
        ],
        "bed_presence_windows": [
            {"window_id": "w1", "regime_id": "r001", "start_seconds": 0.0, "end_seconds": 10.5, "duration_seconds": 10.5, "bed_present": True, "bed_lufs": -24.0},
            {"window_id": "w2", "regime_id": "r001", "start_seconds": 10.5, "end_seconds": 21.0, "duration_seconds": 10.5, "bed_present": True, "bed_lufs": -31.0},
        ],
    }
    mic_curve = [{"time_seconds": i / 10, "end_seconds": i / 10 + 0.1, "momentary_lufs": -20.5} for i in range(210)]
    bed_curve = [{"time_seconds": i / 10, "end_seconds": i / 10 + 0.1, "momentary_lufs": (-23.5 if i < 105 else -31.0)} for i in range(210)]
    assert any(row.get("failure_class") == "mic_bed_gap_out_of_rail" for row in _gap_rows(plan, analysis, mic_curve, bed_curve, rails))
    thin_curve = [{"time_seconds": i / 10, "end_seconds": i / 10 + 0.1, "momentary_lufs": -101.0} for i in range(210)]
    assert any(row.get("failure_class") == "insufficient_speech_coverage" for row in _mic_rows(plan, analysis, thin_curve, rails))
    unstable = [
        {"time_seconds": i / 10, "end_seconds": i / 10 + 0.1, "momentary_lufs": (-20.5 if i < 105 else -27.0)}
        for i in range(210)
    ]
    assert any(row.get("failure_class") == "expressive_window_variation_disclosure" and row["status"] == "pass" for row in _mic_rows(plan, analysis, unstable, rails))
    hot_curve = [{"time_seconds": i / 10, "end_seconds": i / 10 + 0.1, "momentary_lufs": -16.0} for i in range(210)]
    assert any(row.get("failure_class") == "mic_above_rail" for row in _mic_rows(plan, analysis, hot_curve, rails))
    sparse = dict(analysis)
    sparse["regimes"] = [{"id": "r001", "duration_seconds": 600.0, "active_speech_density": 0.01, "clean_gain_headroom": {"margin_db": 20.0}}]
    sparse["speech_windows"] = [{"regime_id": "r001", "start_seconds": 0.0, "end_seconds": 1.0, "duration_seconds": 1.0}]
    assert any(row.get("failure_class") == "sparse-speech" and row["status"] == "pass" for row in _mic_rows(plan, sparse, mic_curve[:10], rails))
    assert any(row.get("failure_class") == "processed_mic_body_unmeasurable" for row in _mic_rows(plan, analysis, [], rails))


def test_widened_window_coverage_keeps_body_strict_and_transitions_consistent() -> None:
    rails = load_default_rails()
    windows = [
        {"id": f"w{idx}", "regime_id": "r001", "start_seconds": float(idx), "end_seconds": float(idx + 1), "duration_seconds": 1.0}
        for idx in range(11)
    ]
    analysis = {
        "regimes": [{"id": "r001", "duration_seconds": 60.0, "active_speech_density": 0.5, "clean_gain_headroom": {"margin_db": 20.0}}],
        "speech_windows": windows,
        "step_candidates": [{"boundary_seconds": 0.0}],
    }
    plan = {"segments": [{"regime_id": "r001"}], "rails": {}}
    curve = [
        {"time_seconds": idx / 10.0, "end_seconds": idx / 10.0 + 0.1, "momentary_lufs": (-20.5 if idx < 80 else -25.5)}
        for idx in range(110)
    ]
    mic_rows = _mic_rows(plan, analysis, curve, rails)
    assert all(row["status"] == "pass" for row in mic_rows)
    coverage = next(row for row in mic_rows if row["type"] == "mic_window_coverage")
    assert "widened window band" in coverage["target"]
    assert all(row["status"] == "pass" for row in _transition_rows(plan, analysis, curve, rails))

    low_body = [dict(row, momentary_lufs=-25.5) for row in curve]
    assert any(row.get("failure_class") == "mic_below_rail" for row in _mic_rows(plan, analysis, low_body, rails))


def test_mic_coverage_is_informational_even_below_house_reference() -> None:
    rails = load_default_rails()
    plan = {"segments": [{"regime_id": "r001"}], "rails": {}}
    windows = [
        {"id": f"w{idx}", "regime_id": "r001", "start_seconds": float(idx), "end_seconds": float(idx + 1), "duration_seconds": 1.0}
        for idx in range(11)
    ]
    analysis = {"regimes": [{"id": "r001", "duration_seconds": 60.0, "active_speech_density": 0.5}], "speech_windows": windows}
    fraction_818 = [
        {"time_seconds": idx / 10.0, "end_seconds": idx / 10.0 + 0.1, "momentary_lufs": (-20.5 if idx < 90 else -27.0)}
        for idx in range(110)
    ]
    coverage = next(row for row in _mic_rows(plan, analysis, fraction_818, rails) if row["type"] == "mic_window_coverage")
    assert coverage["status"] == "pass"
    assert "0.818" in coverage["measurement"]

    analysis["speech_windows"] = windows[:10]
    fraction_600 = [
        {"time_seconds": idx / 10.0, "end_seconds": idx / 10.0 + 0.1, "momentary_lufs": (-20.5 if idx < 60 else -27.0)}
        for idx in range(100)
    ]
    coverage = next(row for row in _mic_rows(plan, analysis, fraction_600, rails) if row["type"] == "mic_window_coverage")
    assert coverage["status"] == "pass"
    assert coverage["failure_class"] == "expressive_window_variation_disclosure"
    assert "0.600" in coverage["measurement"]


def test_gap_binds_on_sustained_masking_and_never_on_quiet_bed() -> None:
    rails = load_default_rails()
    windows = [
        {"window_id": f"w{idx}", "regime_id": "r001", "start_seconds": float(idx), "end_seconds": float(idx + 1), "duration_seconds": 1.0, "bed_present": True, "bed_presence_tier": "meaningful", "bed_lufs": -30.5}
        for idx in range(15)
    ]
    analysis = {
        "regimes": [{"id": "r001", "bed_body": {"raw_bed_body_lufs": -30.5}}],
        "bed_presence_windows": windows,
    }
    plan = {"segments": [{"regime_id": "r001"}]}
    mic = [{"time_seconds": idx / 10.0, "end_seconds": idx / 10.0 + 0.1, "momentary_lufs": -20.5} for idx in range(150)]

    windows[14]["bed_presence_tier"] = "marginal"
    one_wide_bed = []
    for idx in range(150):
        window = idx // 10
        one_wide_bed.append({"time_seconds": idx / 10.0, "end_seconds": idx / 10.0 + 0.1, "momentary_lufs": (-37.799 if window == 14 else -30.5)})
    wide_rows = _gap_rows(plan, analysis, mic, one_wide_bed, rails)
    gap_row = next(row for row in wide_rows if row["type"] == "mic_bed_gap")
    assert gap_row["status"] == "pass"
    classification = next(row for row in wide_rows if row["type"] == "bed_window_classification")
    assert "marginal 1/15" in classification["measurement"]
    assert not any(row["type"] == "background_collapse" for row in wide_rows)

    windows[14]["bed_presence_tier"] = "meaningful"
    one_masking_bed = []
    for idx in range(150):
        window = idx // 10
        one_masking_bed.append({"time_seconds": idx / 10.0, "end_seconds": idx / 10.0 + 0.1, "momentary_lufs": (-24.8 if window == 14 else -30.5)})
    masking_rows = _gap_rows(plan, analysis, mic, one_masking_bed, rails)
    masking = next(row for row in masking_rows if row["type"] == "mic_bed_gap")
    assert masking["status"] == "pass"
    assert "1.000s" in masking["measurement"]

    for index in (12, 13, 14):
        windows[index]["bed_presence_tier"] = "meaningful"
    sustained_bed = []
    for idx in range(150):
        window = idx // 10
        sustained_bed.append({"time_seconds": idx / 10.0, "end_seconds": idx / 10.0 + 0.1, "momentary_lufs": (-24.8 if window >= 12 else -30.5)})
    sustained = next(row for row in _gap_rows(plan, analysis, mic, sustained_bed, rails) if row["type"] == "mic_bed_gap")
    assert sustained["status"] == "fail"
    assert "3.000s" in sustained["measurement"]

    collapsed_bed = [{"time_seconds": idx / 10.0, "end_seconds": idx / 10.0 + 0.1, "momentary_lufs": -37.5} for idx in range(150)]
    collapsed_rows = _gap_rows(plan, analysis, mic, collapsed_bed, rails)
    assert not any(row["status"] == "fail" for row in collapsed_rows)
    assert any(row["type"] == "bed_retention" and row["status"] == "pass" for row in collapsed_rows)


def test_peak_control_accounting_is_silence_inclusive_and_locally_bounded() -> None:
    def analysis_for(regimes: list[tuple[str, float, float]]) -> dict:
        return {
            "regimes": [{"id": regime_id} for regime_id, _, _ in regimes],
            "speech_windows": [{"regime_id": regime_id, "start_seconds": start, "end_seconds": end, "duration_seconds": end - start} for regime_id, start, end in regimes],
        }

    def powers(values: list[float]) -> list[dict]:
        return [{"time_seconds": idx / 10.0, "end_seconds": idx / 10.0 + 0.1, "power": value} for idx, value in enumerate(values)]

    analysis = analysis_for([("r001", 0.0, 100.0)])
    pre = [1.0] * 1000
    post = list(pre)
    post[0] = 10 ** (-0.6 / 10.0)
    passing = _peak_control_rows(analysis, [], [], powers(pre), powers(post))
    assert all(row["status"] == "pass" for row in passing)
    assert any(row["type"] == "peak_control_duty" and "0.0010" in row["measurement"] for row in passing)

    muted = list(pre)
    muted[:29] = [0.0] * 29
    muted_rows = _peak_control_rows(analysis, [], [], powers(pre), powers(muted))
    body = next(row for row in muted_rows if row["type"] == "peak_control_body_delta")
    assert body["body_delta_db"] > 0.12
    assert any(row.get("failure_class") == "peak_control_reshaped_body" for row in muted_rows)
    assert any(row.get("failure_class") == "peak_control_contiguous_run_exceeded" for row in muted_rows)

    severe = list(pre)
    for idx in range(0, 986, 35):
        severe[idx] = 10 ** (-12.0 / 10.0)
    severe_rows = _peak_control_rows(analysis, [], [], powers(pre), powers(severe))
    assert any(row["type"] == "peak_control_bin_attenuation" and row["status"] == "fail" for row in severe_rows)

    concentrated_analysis = analysis_for([("r001", 0.0, 10.0), ("r002", 10.0, 100.0)])
    concentrated = list(pre)
    for idx in range(0, 58, 2):
        concentrated[idx] = 10 ** (-1.0 / 10.0)
    concentrated_rows = _peak_control_rows(concentrated_analysis, [], [], powers(pre), powers(concentrated))
    assert next(row for row in concentrated_rows if row["type"] == "peak_control_duty")["status"] == "pass"
    assert any(row["type"] == "peak_control_regime_duty" and row.get("regime_id") == "r001" and row["status"] == "fail" for row in concentrated_rows)

    threshold_analysis = analysis_for([("r001", 0.0, 20.0), ("r002", 20.0, 40.0)])
    threshold_pre = [1.0] * 400
    threshold_post = list(threshold_pre)
    for idx in range(0, 200, 20):
        threshold_post[idx] = 10 ** (-6.0 / 10.0)
    for idx in (200, 300):
        threshold_post[idx] = 10 ** (-6.0 / 10.0)
    threshold_rows = _peak_control_rows(threshold_analysis, [], [], powers(threshold_pre), powers(threshold_post))
    assert all(row["status"] == "pass" for row in threshold_rows)

    post_peak = [{"time_seconds": 1.0, "true_peak_dbtp": -1.5}]
    assert all(row["status"] == "pass" for row in _true_peak_rows({"mic": post_peak}, load_default_rails()))


def test_peak_control_plan_schema_is_bounded_and_declared() -> None:
    valid = {"render": {"peak_control": {"enabled": True, "true_peak_ceiling_dbtp": -1.5, "mechanism": "alimiter"}}}
    assert _plan_peak_control_rows(valid) == []
    invalid = {"render": {"peak_control": {"enabled": True, "true_peak_ceiling_dbtp": -0.5, "mechanism": "compressor"}}}
    assert any(row.get("failure_class") == "invalid_peak_control" for row in _plan_peak_control_rows(invalid))


def test_micro_chunk_guard_enforces_per_regime_ownership_and_event_budgets(tmp_path: Path) -> None:
    analysis = {
        "duration_seconds": 200.0,
        "regimes": [
            {"id": "r001", "start_seconds": 0.0, "end_seconds": 100.0, "duration_seconds": 100.0},
            {"id": "r002", "start_seconds": 100.0, "end_seconds": 200.0, "duration_seconds": 100.0},
        ],
        "step_candidates": [{"boundary_seconds": 4.0}, {"boundary_seconds": 104.0}],
    }
    ordinary = [
        {"id": f"s{idx}", "regime_id": "r001", "role": "recoverable", "start_seconds": idx * 20.0, "end_seconds": (idx + 1) * 20.0}
        for idx in range(4)
    ]
    rows = _micro_chunk_rows({"segments": ordinary}, analysis)
    assert any(row.get("failure_class") == "micro_chunked_plan" and "r001 has 4 ordinary" in row["measurement"] for row in rows)

    short = [{"id": "short", "regime_id": "r001", "role": "recoverable", "start_seconds": 0.0, "end_seconds": 7.999}]
    rows = _micro_chunk_rows({"segments": short}, analysis)
    assert any("shorter than 8s" in row["measurement"] for row in rows)

    events = [
        {"id": f"e{idx}", "regime_id": "r001", "role": "exception", "event_reason": f"source peak {idx}", "event_citation": {"source": "analysis", "ref": "/step_candidates/0"}, "start_seconds": idx / 10.0, "end_seconds": (idx + 1) / 10.0}
        for idx in range(20)
    ]
    assert any("r001 has 20 event segments" in row["measurement"] for row in _micro_chunk_rows({"segments": events}, analysis))

    thousand = [dict(events[0], id=f"x{idx}", event_reason=f"tiny source peak {idx}", start_seconds=idx / 10000.0, end_seconds=(idx + 1) / 10000.0) for idx in range(1000)]
    assert any("1000 event segments" in row["measurement"] for row in _micro_chunk_rows({"segments": thousand}, analysis))

    repeated = [
        {"id": f"g{idx}", "regime_id": "r001", "role": "exception", "event_reason": "generic repair", "event_citation": {"source": "analysis", "ref": "/step_candidates/0"}, "start_seconds": float(idx), "end_seconds": float(idx) + 0.5}
        for idx in range(2)
    ]
    assert any("repeat generic/non-specific" in row["measurement"] for row in _micro_chunk_rows({"segments": repeated}, analysis))

    far = [{"id": "far", "regime_id": "r001", "role": "exception", "event_reason": "far source peak", "event_citation": {"source": "analysis", "ref": "/step_candidates/0"}, "start_seconds": 50.0, "end_seconds": 50.5}]
    assert any("farther than +/-5s" in row["measurement"] for row in _micro_chunk_rows({"segments": far}, analysis))

    threshold = [
        {"id": f"p{idx}", "regime_id": "r001", "role": "exception", "event_reason": f"bounded residual {idx}", "event_citation": {"source": "analysis", "ref": "/step_candidates/0"}, "start_seconds": idx * (8.0 / 6.0), "end_seconds": (idx + 1) * (8.0 / 6.0)}
        for idx in range(6)
    ]
    assert _micro_chunk_rows({"segments": threshold}, analysis) == []

    prior = tmp_path / "prior_promotion.json"
    analysis["source_sha256"] = "source-a"
    _write_json(prior, {"status": "pass", "source_sha256": "source-a", "analysis_sha256": sha256_json(analysis), "rows": [{"type": "true_peak", "event_seconds": 104.0, "status": "pass"}]})
    prior_event = [{"id": "prior", "regime_id": "r002", "role": "exception", "event_reason": "prior verified peak", "event_citation": {"source": "promotion_manifest", "path": str(prior), "ref": "/rows/0"}, "start_seconds": 100.0, "end_seconds": 108.0}]
    assert _micro_chunk_rows({"segments": prior_event}, analysis) == []


def test_e2e_pipeline_passes_delivers_and_validates_stop() -> None:
    workdir = _workdir("e2e")
    fixtures = make_all(workdir)
    media = fixtures["mono_mic_stereo_bed"]
    _, analysis_path, plan_path, analysis, plan = _probe_analyze_plan(media, workdir)
    _fill_good_gains(plan, analysis)
    plan["render"]["peak_control"] = {"enabled": True, "true_peak_ceiling_dbtp": -1.5, "mechanism": "alimiter"}
    _write_json(plan_path, plan)
    validation = workdir / "plan_validation.json"
    _run(["plan-validate", "--plan", str(plan_path), "--analysis", str(analysis_path), "--json-out", str(validation)])
    render_manifest = workdir / "render_manifest.json"
    _run(["render", "--source", str(media), "--plan", str(plan_path), "--outdir", str(workdir / "candidate"), "--manifest-out", str(render_manifest)])
    rendered = json.loads(render_manifest.read_text(encoding="utf-8"))
    assert rendered["components"]["mic_raw"]["sha256"]
    assert rendered["components"]["mic"]["sha256"]
    assert rendered["peak_control"]["attack_ms"] == 5.0
    assert rendered["peak_control"]["release_ms"] == 50.0
    assert rendered["peak_control"]["oversample_rate_hz"] == 192000
    promotion = workdir / "promotion_manifest.json"
    _run(["verify", "--manifest", str(render_manifest), "--plan", str(plan_path), "--analysis", str(analysis_path), "--json-out", str(promotion)])
    data = json.loads(promotion.read_text(encoding="utf-8"))
    assert data["overall"]["status"] == "pass"
    assert {"component_derivation", "peak_control_body_delta", "peak_control_duty", "peak_control_regime_duty", "peak_control_contiguous_run", "peak_control_bin_attenuation", "peak_control_post_control_basis"} <= {row["type"] for row in data["rows"]}
    assert data["peak_control"]["mechanism"] == "alimiter"
    assert data["peak_control"]["pre_control_mic_sha256"] == rendered["components"]["mic_raw"]["sha256"]
    assert data["peak_control"]["post_control_mic_sha256"] == rendered["components"]["mic"]["sha256"]

    tampered_manifest = workdir / "render_manifest_tampered_peak_metadata.json"
    tampered_rendered = json.loads(json.dumps(rendered))
    tampered_rendered["peak_control"]["attack_ms"] = 9.0
    _write_json(tampered_manifest, tampered_rendered)
    tampered_promotion = workdir / "promotion_tampered_peak_metadata.json"
    assert _run(["verify", "--manifest", str(tampered_manifest), "--plan", str(plan_path), "--analysis", str(analysis_path), "--json-out", str(tampered_promotion)], check=False).returncode == 1
    assert any(row.get("failure_class") == "component_not_derived_from_plan" for row in json.loads(tampered_promotion.read_text(encoding="utf-8"))["rows"])

    second_plan = json.loads(plan_path.read_text(encoding="utf-8"))
    second_plan["rails"]["rails_adjustment"] = {"mic_band_center_shift_db": 1.0, "gap_band_shift_db": 0.0, "analysis_evidence_paths": ["/regimes/0/raw_speech_body_lufs"]}
    second_plan["targets"]["shared_mic_body_lufs"] += 1.0
    if second_plan["targets"].get("shared_bed_body_lufs") is not None:
        second_plan["targets"]["shared_bed_body_lufs"] += 1.0
    for seg in second_plan["mic_segments"]:
        seg["gain_db"] += 1.0
    for seg in second_plan["bed_segments"]:
        seg["gain_db"] += 1.0
    second_plan_path = workdir / "render_plan_plus1.json"
    _write_json(second_plan_path, second_plan)
    _run(["plan-validate", "--plan", str(second_plan_path), "--analysis", str(analysis_path), "--json-out", str(workdir / "plan_validation.json")])
    second_manifest = workdir / "render_manifest_plus1.json"
    _run(["render", "--source", str(media), "--plan", str(second_plan_path), "--outdir", str(workdir / "candidate_plus1"), "--manifest-out", str(second_manifest)])
    assert json.loads(render_manifest.read_text(encoding="utf-8"))["components"]["mix"]["sha256"] != json.loads(second_manifest.read_text(encoding="utf-8"))["components"]["mix"]["sha256"]

    output = media.with_name(f"{media.stem}-REMIX-VOICEOVER{media.suffix}")
    missing_proof = json.loads(json.dumps(data))
    missing_proof["rows"] = [row for row in missing_proof["rows"] if row.get("type") != "bed_yield_necessity"]
    missing_proof_path = workdir / "promotion_missing_bed_proof.json"
    _write_json(missing_proof_path, missing_proof)
    missing_proc = _run(["deliver", "--manifest", str(missing_proof_path), "--source", str(media), "--output", str(output)], check=False)
    assert missing_proc.returncode == 1
    assert "row inventory is incomplete" in missing_proc.stderr

    duplicate_proof = json.loads(json.dumps(data))
    duplicate_proof["rows"].append(next(row for row in duplicate_proof["rows"] if row.get("type") == "bed_yield_necessity"))
    duplicate_proof_path = workdir / "promotion_duplicate_bed_proof.json"
    _write_json(duplicate_proof_path, duplicate_proof)
    duplicate_proc = _run(["deliver", "--manifest", str(duplicate_proof_path), "--source", str(media), "--output", str(output)], check=False)
    assert duplicate_proc.returncode == 1
    assert "exactly one bed_yield_necessity" in duplicate_proc.stderr

    malformed_proof = json.loads(json.dumps(data))
    next(row for row in malformed_proof["rows"] if row.get("type") == "bed_yield_necessity")["proof"] = {"policy": "forged"}
    malformed_proof_path = workdir / "promotion_malformed_bed_proof.json"
    _write_json(malformed_proof_path, malformed_proof)
    malformed_proc = _run(["deliver", "--manifest", str(malformed_proof_path), "--source", str(media), "--output", str(output)], check=False)
    assert malformed_proc.returncode == 1
    assert "incomplete verifier-owned proof" in malformed_proc.stderr

    _run(["deliver", "--manifest", str(promotion), "--source", str(media), "--output", str(output)])
    delivery = json.loads((workdir / "delivery.json").read_text(encoding="utf-8"))
    report = workdir / "REMIX-VOICEOVER-report.md"
    report.write_text(_complete_report(data, promotion, delivery=delivery), encoding="utf-8")
    stop = workdir / "stop_state.json"
    _run(["validate-stop", "--report", str(report), "--manifest", str(promotion), "--delivery", str(workdir / "delivery.json"), "--json-out", str(stop)])
    assert json.loads(stop.read_text(encoding="utf-8"))["status"] == "pass"


def test_bad_plan_verify_fails_with_mic_below_rail_next_actions() -> None:
    workdir = _workdir("badplan")
    fixtures = make_all(workdir)
    media = fixtures["mono_mic_stereo_bed"]
    _, analysis_path, plan_path, analysis, plan = _probe_analyze_plan(media, workdir)
    _fill_good_gains(plan, analysis, mic_offset_db=-12.0)
    _write_json(plan_path, plan)
    validation = workdir / "plan_validation.json"
    proc = _run(["plan-validate", "--plan", str(plan_path), "--analysis", str(analysis_path), "--json-out", str(validation)], check=False)
    assert proc.returncode == 1
    rows = json.loads(validation.read_text(encoding="utf-8"))["rows"]
    assert any(row.get("failure_class") == "mic_baseline_misses_shared_target" for row in rows)


def test_rehashed_component_substitutions_and_mix_processing_are_rejected() -> None:
    workdir = _workdir("dip")
    fixtures = make_all(workdir)
    media = fixtures["automation_dip_source"]
    _, analysis_path, plan_path, analysis, plan = _probe_analyze_plan(media, workdir)
    _fill_good_gains(plan, analysis)
    _write_json(plan_path, plan)
    _run(["plan-validate", "--plan", str(plan_path), "--analysis", str(analysis_path), "--json-out", str(workdir / "plan_validation.json")])
    render_manifest = workdir / "render_manifest.json"
    _run(["render", "--source", str(media), "--plan", str(plan_path), "--outdir", str(workdir / "candidate"), "--manifest-out", str(render_manifest)])
    manifest = json.loads(render_manifest.read_text(encoding="utf-8"))
    mic = Path(manifest["components"]["mic"]["path"])
    bed = Path(manifest["components"]["bed"]["path"])
    mix = Path(manifest["components"]["mix"]["path"])
    original_mic = workdir / "original_mic.wav"
    original_bed = workdir / "original_bed.wav"
    original_mix = workdir / "original_mix.wav"
    shutil.copy2(mic, original_mic)
    shutil.copy2(bed, original_bed)
    shutil.copy2(mix, original_mix)
    dipped_mic = workdir / "candidate" / "mic_component_dipped.wav"
    subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostdin",
            "-y",
            "-i",
            str(mic),
            "-af",
            "volume=0.1:enable='between(t,5.0,5.4)'",
            "-c:a",
            "pcm_f32le",
            str(dipped_mic),
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    dipped_mic.replace(mic)
    subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostdin",
            "-y",
            "-i",
            str(mic),
            "-i",
            str(bed),
            "-filter_complex",
            "[0:a:0][1:a:0]amix=inputs=2:normalize=0[out]",
            "-map",
            "[out]",
            "-c:a",
            "pcm_f32le",
            str(mix),
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    digest = __import__("hashlib")
    manifest["components"]["mic"]["sha256"] = digest.sha256(mic.read_bytes()).hexdigest()
    manifest["components"]["mix"]["sha256"] = digest.sha256(mix.read_bytes()).hexdigest()
    _write_json(render_manifest, manifest)
    promotion = workdir / "promotion_manifest.json"
    _run(["verify", "--manifest", str(render_manifest), "--plan", str(plan_path), "--analysis", str(analysis_path), "--json-out", str(promotion)], check=False)
    rows = json.loads(promotion.read_text(encoding="utf-8"))["rows"]
    assert any(row.get("failure_class") == "component_not_derived_from_plan" for row in rows)

    shutil.copy2(original_mic, mic)
    shutil.copy2(original_bed, bed)
    shutil.copy2(original_mix, mix)
    manifest = json.loads(render_manifest.read_text(encoding="utf-8"))
    limited_bed = workdir / "candidate" / "bed_component_limited.wav"
    subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-y", "-i", str(bed), "-af", "volume=8,alimiter=limit=0.1:level=false", "-c:a", "pcm_f32le", str(limited_bed)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    limited_bed.replace(bed)
    ffmpeg_mix_components(mic, bed, mix, float(manifest["duration_seconds"]), ["repair"])
    manifest["components"]["mic"]["sha256"] = sha256_file(mic)
    manifest["components"]["bed"]["sha256"] = sha256_file(bed)
    manifest["components"]["mix"]["sha256"] = sha256_file(mix)
    _write_json(render_manifest, manifest)
    bed_promotion = workdir / "promotion_bed_substitution.json"
    assert _run(["verify", "--manifest", str(render_manifest), "--plan", str(plan_path), "--analysis", str(analysis_path), "--json-out", str(bed_promotion)], check=False).returncode == 1
    assert any(row.get("failure_class") == "component_not_derived_from_plan" for row in json.loads(bed_promotion.read_text(encoding="utf-8"))["rows"])

    shutil.copy2(original_bed, bed)
    shutil.copy2(original_mix, mix)
    manifest["components"]["bed"]["sha256"] = sha256_file(bed)
    limited_mix = workdir / "candidate" / "mix_limited.wav"
    subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-y", "-i", str(mix), "-af", "volume=8,alimiter=limit=0.1:level=false", "-c:a", "pcm_f32le", str(limited_mix)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    limited_mix.replace(mix)
    manifest["components"]["mix"]["sha256"] = sha256_file(mix)
    _write_json(render_manifest, manifest)
    mix_promotion = workdir / "promotion_mix_processing.json"
    assert _run(["verify", "--manifest", str(render_manifest), "--plan", str(plan_path), "--analysis", str(analysis_path), "--json-out", str(mix_promotion)], check=False).returncode == 1
    assert any(row.get("failure_class") == "null_test_failed" for row in json.loads(mix_promotion.read_text(encoding="utf-8"))["rows"])
