from __future__ import annotations

import json
import os
import subprocess
import sys
import uuid
import csv
import math
from pathlib import Path

from make_fixtures import make_all
from rv.ffio import MONO_UPMIX_COEFFICIENT
from rv.ffio import ebur128_curve
from rv.ffio import _parse_metadata
from rv.analyze import _annotate_bed_regime_policies
from rv.laneprofile import correlation_report
from rv.util import correlation

ROOT = Path(__file__).resolve().parents[1]
RV = ROOT / "scripts" / "rv.py"


def test_low_confidence_bed_policy_uses_full_regime_body_and_contained_windows() -> None:
    regimes = [
        {"id": "b001", "start_seconds": 0.0, "end_seconds": 30.0, "raw_bed_body_lufs": -56.0},
        {"id": "b002", "start_seconds": 30.0, "end_seconds": 60.0, "raw_bed_body_lufs": -56.0},
        {"id": "b003", "start_seconds": 60.0, "end_seconds": 90.0, "raw_bed_body_lufs": -45.0},
        {"id": "b004", "start_seconds": 90.0, "end_seconds": 120.0, "raw_bed_body_lufs": -70.0},
    ]
    windows = [
        {"start_seconds": 5.0, "end_seconds": 10.0, "bed_presence_tier": "absent"},
        {"start_seconds": 35.0, "end_seconds": 40.0, "bed_presence_tier": "marginal"},
        {"start_seconds": 58.0, "end_seconds": 62.0, "bed_presence_tier": "meaningful"},
    ]
    curve = [
        {"time_seconds": float(second), "end_seconds": float(second + 1), "momentary_lufs": -70.0}
        for second in range(120)
    ]
    _annotate_bed_regime_policies(regimes, windows, curve)
    assert regimes[0]["stitching_policy"] == "preserve-unity-low-confidence"
    assert regimes[1]["stitching_policy"] == "stitchable"
    assert regimes[2]["stitching_policy"] == "stitchable"
    assert regimes[3]["stitching_policy"] == "preserve-unity-low-confidence"
    assert regimes[1]["stitching_policy_evidence"]["boundary_censored_speech_windows"] == 1
    assert regimes[2]["stitching_policy_evidence"]["boundary_censored_speech_windows"] == 1


def test_low_confidence_bed_policy_rejects_sparse_full_regime_activity() -> None:
    regimes = [{"id": "b001", "start_seconds": 0.0, "end_seconds": 30.0, "raw_bed_body_lufs": -64.0}]
    curve = [
        {"time_seconds": float(second), "end_seconds": float(second + 1), "momentary_lufs": -20.0 if second == 17 else -70.0}
        for second in range(30)
    ]
    _annotate_bed_regime_policies(regimes, [], curve)
    assert regimes[0]["stitching_policy"] == "hold-unity-indeterminate"
    assert regimes[0]["stitching_policy_evidence"]["curve"]["meaningful_active_seconds"] == 1.0


def test_low_confidence_bed_policy_holds_incomplete_evidence_as_indeterminate() -> None:
    regimes = [{"id": "b001", "start_seconds": 0.0, "end_seconds": 30.0, "raw_bed_body_lufs": -64.0}]
    partial_curve = [
        {"time_seconds": float(second), "end_seconds": float(second + 1), "momentary_lufs": -70.0}
        for second in range(10)
    ]
    _annotate_bed_regime_policies(regimes, [], partial_curve)
    assert regimes[0]["stitching_policy"] == "hold-unity-indeterminate"
    assert regimes[0]["stitching_policy_evidence"]["curve"]["coverage_complete"] is False


def test_low_confidence_bed_policy_rejects_internal_curve_holes() -> None:
    regimes = [{"id": "b001", "start_seconds": 0.0, "end_seconds": 100.0, "raw_bed_body_lufs": -64.0}]
    curve = [
        {"time_seconds": index / 10.0, "end_seconds": index / 10.0 + 0.1, "momentary_lufs": -70.0}
        for index in range(1000)
        if not 400 <= index < 410
    ]
    _annotate_bed_regime_policies(regimes, [], curve)
    evidence = regimes[0]["stitching_policy_evidence"]["curve"]
    assert evidence["coverage_ratio"] == 0.99
    assert evidence["maximum_internal_gap_seconds"] == 1.0
    assert evidence["coverage_complete"] is False
    assert regimes[0]["stitching_policy"] == "hold-unity-indeterminate"


def test_low_confidence_bed_policy_rejects_overlapping_curve_rows() -> None:
    regimes = [{"id": "b001", "start_seconds": 0.0, "end_seconds": 30.0, "raw_bed_body_lufs": -64.0}]
    curve = [
        {"time_seconds": index / 10.0, "end_seconds": index / 10.0 + 0.1, "momentary_lufs": -70.0}
        for index in range(300)
    ]
    curve.append({"time_seconds": 10.0, "end_seconds": 10.1, "momentary_lufs": -70.0})
    _annotate_bed_regime_policies(regimes, [], curve)
    evidence = regimes[0]["stitching_policy_evidence"]["curve"]
    assert evidence["overlap_seconds"] == 0.1
    assert evidence["coverage_complete"] is False
    assert regimes[0]["stitching_policy"] == "hold-unity-indeterminate"


def test_absent_intro_curve_shape_is_preserved_without_importing_later_bed() -> None:
    regimes = [
        {"id": "b001", "start_seconds": 0.0, "end_seconds": 29.5, "raw_bed_body_lufs": -64.951},
        {"id": "b002", "start_seconds": 29.5, "end_seconds": 60.0, "raw_bed_body_lufs": -30.0},
    ]
    curve = []
    for index in range(600):
        start = index / 10.0
        curve.append(
            {
                "time_seconds": start,
                "end_seconds": start + 0.1,
                "momentary_lufs": -58.004 if start < 29.5 else -20.0,
            }
        )
    windows = [
        {"start_seconds": float(second), "end_seconds": float(second + 1), "bed_presence_tier": "absent"}
        for second in range(1, 9)
    ]
    _annotate_bed_regime_policies(regimes, windows, curve)
    intro = regimes[0]
    assert intro["stitching_policy"] == "preserve-unity-low-confidence"
    assert intro["stitching_policy_evidence"]["curve"]["coverage_ratio"] == 1.0
    assert intro["stitching_policy_evidence"]["curve"]["maximum_lufs"] == -58.004
    assert regimes[1]["stitching_policy"] == "stitchable"


def _workdir(name: str) -> Path:
    if "RV_TEST_TMPDIR" not in os.environ:
        raise AssertionError("RV_TEST_TMPDIR must be set for rv tests")
    base = Path(os.environ["RV_TEST_TMPDIR"]).resolve()
    base.mkdir(parents=True, exist_ok=True)
    target = base / f"rv-{name}-{uuid.uuid4().hex}"
    target.mkdir()
    return target


def _probe_and_analyze(media: Path, workdir: Path, name: str, *analyze_args: str) -> dict:
    probe = workdir / f"{name}_probe.json"
    analysis = workdir / f"{name}_analysis.json"
    subprocess.run([sys.executable, str(RV), "probe", str(media), "--json-out", str(probe)], check=True)
    subprocess.run([sys.executable, str(RV), "analyze", str(media), "--probe", str(probe), "--json-out", str(analysis), *analyze_args], check=True)
    return json.loads(analysis.read_text(encoding="utf-8"))


def test_analyze_detects_drop_recovery_and_writes_schema() -> None:
    workdir = _workdir("drop")
    fixtures = make_all(workdir)
    data = _probe_and_analyze(fixtures["speech_drop_video"], workdir, "drop", "--min-plateau-seconds", "60")
    assert data["source_lineage"]["hash_verified"] is True
    assert data["inferred_roles"]["mic_streams"] == [0]
    assert data["regimes"]
    assert data["step_candidates"]
    assert any(step["direction"] == "drop" and abs(step["step_db"]) >= 10.0 for step in data["step_candidates"])
    quiet_windows = [win for win in data["speech_windows"] if 35.0 <= win["start_seconds"] < 85.0]
    assert quiet_windows
    assert all(Path(path).exists() for path in data["curve_sidecars"].values())
    first_regime = data["regimes"][0]
    for field in ("raw_speech_body_lufs", "active_speech_seconds", "active_speech_density", "noise_floor_lufs", "clean_gain_headroom"):
        assert field in first_regime
    assert data["bed_presence"]
    assert data["bed_presence_windows"]
    assert all("id" in win for win in data["speech_windows"])
    assert all({"window_id", "start_seconds", "end_seconds", "bed_present", "bed_presence_tier", "meaningful", "bed_lufs", "basis"} <= set(row) for row in data["bed_presence_windows"])
    assert all(row["bed_presence_tier"] in {"meaningful", "marginal", "absent"} for row in data["bed_presence_windows"])
    assert all("meaningful_threshold_lufs" in row["presence_rule"] for row in data["bed_presence_windows"])
    assert any(win["active_duration_seconds"] <= win["duration_seconds"] for win in data["speech_windows"])
    assert all(isinstance(win["raw_mic_window_lufs"], (int, float)) for win in data["speech_windows"])
    assert all("raw direct-mic" in win["raw_mic_window_lufs_basis"] for win in data["speech_windows"])
    assert "duration_tolerance_note" in data["method"]
    assert "dense_regime_note" in data["method"]

    with Path(data["curve_sidecars"]["0"]).open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    deltas = [round(float(rows[idx + 1]["time_seconds"]) - float(rows[idx]["time_seconds"]), 3) for idx in range(min(20, len(rows) - 1))]
    assert deltas
    assert all(abs(delta - 0.1) <= 0.001 for delta in deltas)

    mic = next(row for row in data["lane_profiles"] if row["audio_stream_index"] == 0)
    final_curve_i = float(rows[-1]["integrated_lufs"])
    assert mic["integrated_lufs"] == round(final_curve_i, 3)
    assert "ungated_power_mean_lufs" in mic
    assert abs(mic["integrated_lufs"] - mic["ungated_power_mean_lufs"]) > 1.0


def test_analyze_mono_mic_stereo_bed_and_audio_only() -> None:
    workdir = _workdir("mono")
    fixtures = make_all(workdir)
    mono = _probe_and_analyze(fixtures["mono_mic_stereo_bed"], workdir, "mono")
    assert mono["container_kind"] == "audio-only"
    mic = next(row for row in mono["lane_profiles"] if row["audio_stream_index"] == mono["inferred_roles"]["mic_streams"][0])
    assert mic["canonical_decode"]["mono_upmix_coefficient_per_channel"] == MONO_UPMIX_COEFFICIENT
    audio_only = _probe_and_analyze(fixtures["audio_only"], workdir, "audio")
    assert audio_only["container_kind"] == "audio-only"


def test_existing_mix_signature_is_flagged() -> None:
    workdir = _workdir("mix")
    fixtures = make_all(workdir)
    data = _probe_and_analyze(fixtures["existing_mix_signature"], workdir, "mix")
    flags = data["cross_lane_correlation"]["existing_mix_candidates"]
    mix_flag = [row for row in flags if row["audio_stream_index"] == 2]
    assert mix_flag, flags
    assert mix_flag[0]["existing_mix_signature"] is True
    mic_flag = [row for row in flags if row["audio_stream_index"] == 0]
    assert mic_flag
    assert mic_flag[0]["existing_mix_signature"] is False
    assert data["inferred_roles"]["mic_streams"] == [0]
    assert 2 not in data["inferred_roles"]["bed_streams"]
    assert data["inferred_roles"]["bed_streams"] == [1]
    assert data["role_conflicts"]
    assert data["role_conflicts"][0]["requires_resolution"] is True


def test_confirmed_roles_drive_analysis_and_plan_role_mismatch_fails() -> None:
    workdir = _workdir("confirmed-roles")
    fixtures = make_all(workdir)
    media = fixtures["existing_mix_signature"]
    probe = workdir / "probe.json"
    analysis_path = workdir / "analysis.json"
    plan_path = workdir / "render_plan.json"
    subprocess.run([sys.executable, str(RV), "probe", str(media), "--json-out", str(probe)], check=True)
    subprocess.run(
        [
            sys.executable,
            str(RV),
            "analyze",
            str(media),
            "--probe",
            str(probe),
            "--json-out",
            str(analysis_path),
            "--mic-streams",
            "0:a:0",
            "--bed-streams",
            "0:a:1",
        ],
        check=True,
    )
    data = json.loads(analysis_path.read_text(encoding="utf-8"))
    assert data["role_confirmation"] == "caller/agent-confirmed"
    assert data["confirmed_roles"]["mic_streams"] == [0]
    assert data["confirmed_roles"]["bed_streams"] == [1]
    assert data["confirmed_roles"]["excluded_existing_mix_streams"] == [2]
    assert data["role_conflicts"] == []
    assert data["regimes"] and all("bed_body" in regime for regime in data["regimes"])

    subprocess.run([sys.executable, str(RV), "plan-init", "--analysis", str(analysis_path), "--out", str(plan_path)], check=True)
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    assert plan["roles"]["mic_streams"] == [0]
    assert plan["roles"]["bed_streams"] == [1]
    plan["roles"]["bed_streams"] = [1, 2]
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    validation = workdir / "plan_validation.json"
    proc = subprocess.run(
        [sys.executable, str(RV), "plan-validate", "--plan", str(plan_path), "--analysis", str(analysis_path), "--json-out", str(validation)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert proc.returncode == 1
    rows = json.loads(validation.read_text(encoding="utf-8"))["rows"]
    mismatch = next(row for row in rows if row.get("failure_class") == "plan_roles_mismatch_analysis")
    assert mismatch["next_action"] == "rerun analyze with --mic-streams/--bed-streams and re-init the plan"


def test_confirmed_roles_reject_streams_outside_fresh_inventory() -> None:
    workdir = _workdir("bad-confirmed-roles")
    fixtures = make_all(workdir)
    media = fixtures["audio_only"]
    probe = workdir / "probe.json"
    subprocess.run([sys.executable, str(RV), "probe", str(media), "--json-out", str(probe)], check=True)
    proc = subprocess.run(
        [sys.executable, str(RV), "analyze", str(media), "--probe", str(probe), "--json-out", str(workdir / "analysis.json"), "--mic-streams", "99", "--bed-streams", "1"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert proc.returncode == 1
    assert "absent from fresh ffprobe inventory" in proc.stderr


def test_lineage_mismatch_refuses_with_repair_commands() -> None:
    workdir = _workdir("lineage")
    fixtures = make_all(workdir)
    probe = workdir / "probe.json"
    subprocess.run([sys.executable, str(RV), "probe", str(fixtures["audio_only"]), "--json-out", str(probe)], check=True)
    proc = subprocess.run(
        [sys.executable, str(RV), "analyze", str(fixtures["mono_mic_stereo_bed"]), "--probe", str(probe), "--json-out", str(workdir / "analysis.json")],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert proc.returncode == 1
    assert "source hash mismatch" in proc.stderr
    assert "Repair commands:" in proc.stderr
    assert "rv.py probe" in proc.stderr


def test_forged_probe_inventory_refuses_deleted_stream_and_channel_forgery() -> None:
    workdir = _workdir("forged")
    fixtures = make_all(workdir)
    original = workdir / "probe.json"
    subprocess.run([sys.executable, str(RV), "probe", str(fixtures["existing_mix_signature"]), "--json-out", str(original)], check=True)
    base = json.loads(original.read_text(encoding="utf-8"))
    for name, mutate in (
        ("deleted", lambda data: data["audio_streams"].pop()),
        ("channels", lambda data: data["audio_streams"][0].__setitem__("channels", 99)),
    ):
        forged = json.loads(json.dumps(base))
        mutate(forged)
        forged_path = workdir / f"{name}_probe.json"
        forged_path.write_text(json.dumps(forged), encoding="utf-8")
        proc = subprocess.run(
            [
                sys.executable,
                str(RV),
                "analyze",
                str(fixtures["existing_mix_signature"]),
                "--probe",
                str(forged_path),
                "--json-out",
                str(workdir / f"{name}_analysis.json"),
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert proc.returncode == 1
        assert "probe inventory mismatch" in proc.stderr
        assert "Repair commands:" in proc.stderr


def test_single_lane_input_analyzes_as_single_program_repair() -> None:
    workdir = _workdir("single")
    fixtures = make_all(workdir)
    probe = workdir / "single_probe.json"
    subprocess.run([sys.executable, str(RV), "probe", str(fixtures["single_lane"]), "--json-out", str(probe)], check=True)
    analysis_path = workdir / "analysis.json"
    subprocess.run(
        [sys.executable, str(RV), "analyze", str(fixtures["single_lane"]), "--probe", str(probe), "--json-out", str(analysis_path)],
        check=True,
    )
    analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
    assert analysis["analysis_mode"] == "single-program-repair"
    assert analysis["analysis_roles"]["mic_streams"] == [0]
    assert analysis["analysis_roles"]["bed_streams"] == []
    assert analysis["role_conflicts"] == []
    assert analysis["bed_regimes"] == []
    assert analysis["bed_step_candidates"] == []

    confirmed_path = workdir / "confirmed_analysis.json"
    subprocess.run(
        [
            sys.executable,
            str(RV),
            "analyze",
            str(fixtures["single_lane"]),
            "--probe",
            str(probe),
            "--json-out",
            str(confirmed_path),
            "--mic-streams",
            "0",
            "--bed-streams",
            "",
        ],
        check=True,
    )
    confirmed = json.loads(confirmed_path.read_text(encoding="utf-8"))
    assert confirmed["confirmed_roles"]["mic_streams"] == [0]
    assert confirmed["confirmed_roles"]["bed_streams"] == []


def test_multi_lane_confirmed_roles_refuse_empty_bed() -> None:
    workdir = _workdir("multi-empty-bed")
    fixtures = make_all(workdir)
    probe = workdir / "probe.json"
    subprocess.run([sys.executable, str(RV), "probe", str(fixtures["audio_only"]), "--json-out", str(probe)], check=True)
    proc = subprocess.run(
        [
            sys.executable,
            str(RV),
            "analyze",
            str(fixtures["audio_only"]),
            "--probe",
            str(probe),
            "--json-out",
            str(workdir / "analysis.json"),
            "--mic-streams",
            "0",
            "--bed-streams",
            "",
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert proc.returncode == 1
    assert "empty --bed-streams only" in proc.stderr


def test_three_direct_lanes_never_auto_sum_leftovers_into_bed() -> None:
    from rv.analyze import _infer_roles

    profiles = [
        {"audio_stream_index": 0, "speech_shape_ratio": 0.90},
        {"audio_stream_index": 1, "speech_shape_ratio": 0.30},
        {"audio_stream_index": 2, "speech_shape_ratio": 0.10},
    ]
    roles, conflicts = _infer_roles(profiles, [])
    assert conflicts and conflicts[0]["type"] == "ambiguous_direct_lane_roles"
    assert roles["bed_streams"] == []
    assert roles["unknown_streams"] == [0, 1, 2]


def test_amplified_duplicate_is_not_classified_as_existing_mix() -> None:
    curves = {
        0: [{"momentary_lufs": 10 * math.log10(1.0 + (idx % 5))} for idx in range(30)],
        1: [{"momentary_lufs": 10 * math.log10(4.0 * (1.0 + (idx % 5)))} for idx in range(30)],
        2: [{"momentary_lufs": -50.0 + (idx % 2)} for idx in range(30)],
    }
    report = correlation_report(curves)
    duplicate = next(row for row in report["existing_mix_candidates"] if row["audio_stream_index"] == 1)
    assert duplicate["fit_r2"] >= 0.99
    assert duplicate["existing_mix_signature"] is False


def test_nan_rows_do_not_poison_aligned_correlation_or_mix_regression() -> None:
    assert correlation([1.0, math.nan, 3.0], [2.0, 999.0, 6.0]) == 1.0

    powers: dict[int, list[float]] = {0: [], 1: [], 2: []}
    for idx in range(30):
        left = 1.0 + (idx % 5)
        right = 0.5 + ((idx * 3) % 7)
        powers[0].append(left)
        powers[1].append(right)
        powers[2].append(left + right)
    powers[0][3] = math.nan
    powers[1][9] = math.nan
    powers[2][17] = math.nan
    curves = {
        lane: [{"momentary_lufs": (10.0 * math.log10(value)) if math.isfinite(value) else math.nan} for value in values]
        for lane, values in powers.items()
    }
    report = correlation_report(curves)
    mix = next(row for row in report["existing_mix_candidates"] if row["audio_stream_index"] == 2)
    assert mix["existing_mix_signature"] is True
    assert mix["correlation_with_fitted_sum_of_other_lanes"] is not None
    assert all(value is None or math.isfinite(value) for row in report["matrix"].values() for value in row.values())

    all_missing = correlation_report({lane: [{"momentary_lufs": math.nan} for _ in range(5)] for lane in range(3)})
    assert not any(row["existing_mix_signature"] for row in all_missing["existing_mix_candidates"])


def test_ambiguous_two_lane_inventory_is_fail_closed_until_confirmed() -> None:
    workdir = _workdir("ambiguous")
    fixtures = make_all(workdir)
    media = workdir / "ambiguous_two_lane.mka"
    subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostdin",
            "-y",
            "-i",
            str(fixtures["single_lane"]),
            "-map",
            "0:a:0",
            "-map",
            "0:a:0",
            "-c:a",
            "flac",
            str(media),
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    data = _probe_and_analyze(media, workdir, "ambiguous")
    assert any(row["type"] == "ambiguous_direct_lane_roles" for row in data["role_conflicts"])
    assert data["analysis_roles"]["mic_streams"] == []
    assert data["analysis_roles"]["bed_streams"] == []
    assert data["analysis_roles"]["unknown_streams"] == [0, 1]
    assert data["inferred_roles"]["bed_streams"] == []


def test_bed_level_transitions_are_independent_from_mic_speech_regimes() -> None:
    workdir = _workdir("bed-steps")
    media = workdir / "bed_steps.mka"
    subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostdin",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=997:sample_rate=48000:duration=90",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=181:sample_rate=48000:duration=90",
            "-filter_complex",
            "[0:a:0]volume=0.04,pan=stereo|c0=c0|c1=c0[mic];[1:a:0]volume='if(lt(t,30),0.08,if(lt(t,60),0.02,0.08))':eval=frame,pan=stereo|c0=c0|c1=c0[bed]",
            "-map",
            "[mic]",
            "-map",
            "[bed]",
            "-c:a",
            "flac",
            str(media),
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    probe = workdir / "probe.json"
    analysis_path = workdir / "analysis.json"
    subprocess.run([sys.executable, str(RV), "probe", str(media), "--json-out", str(probe)], check=True)
    subprocess.run(
        [
            sys.executable,
            str(RV),
            "analyze",
            str(media),
            "--probe",
            str(probe),
            "--json-out",
            str(analysis_path),
            "--mic-streams",
            "0",
            "--bed-streams",
            "1",
            "--min-plateau-seconds",
            "20",
            "--step-min-db",
            "6",
        ],
        check=True,
    )
    data = json.loads(analysis_path.read_text(encoding="utf-8"))
    assert data["step_candidates"] == []
    assert len(data["bed_regimes"]) == 3
    boundaries = [row["boundary_seconds"] for row in data["bed_step_candidates"]]
    assert len(boundaries) == 2
    assert abs(boundaries[0] - 30.0) <= 1.0
    assert abs(boundaries[1] - 60.0) <= 1.0
    assert data["bed_step_candidates"][0]["direction"] == "drop"
    assert data["bed_step_candidates"][1]["direction"] == "rise"


def test_cli_bounds_violation_refuses() -> None:
    workdir = _workdir("bounds")
    fixtures = make_all(workdir)
    probe = workdir / "probe.json"
    subprocess.run([sys.executable, str(RV), "probe", str(fixtures["audio_only"]), "--json-out", str(probe)], check=True)
    proc = subprocess.run(
        [
            sys.executable,
            str(RV),
            "analyze",
            str(fixtures["audio_only"]),
            "--probe",
            str(probe),
            "--json-out",
            str(workdir / "analysis.json"),
            "--step-min-db",
            "100",
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert proc.returncode == 1
    assert "step_min_db=100.0 outside bounds" in proc.stderr


def test_known_997hz_minus_23_dbfs_sine_measures_about_minus_23_lufs() -> None:
    workdir = _workdir("sine")
    sine = workdir / "sine_997_minus23.wav"
    subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostdin",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=997:duration=3:sample_rate=48000",
            "-af",
            "volume=-1.92dB",
            str(sine),
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    curve = ebur128_curve(sine, 0, 1, workdir / "sine_curve.csv", [f'python remix-voiceover/scripts/rv.py analyze "{sine}" --probe "{workdir / "probe.json"}" --json-out "{workdir / "analysis.json"}"'])
    measured = curve["rows"][-1]["integrated_lufs"]
    assert -23.5 <= measured <= -22.5

    stereo = workdir / "sine_997_minus23_stereo.wav"
    subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostdin",
            "-y",
            "-i",
            str(sine),
            "-af",
            f"pan=stereo|c0={MONO_UPMIX_COEFFICIENT:.16f}*c0|c1={MONO_UPMIX_COEFFICIENT:.16f}*c0",
            str(stereo),
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stereo_curve = ebur128_curve(stereo, 0, 2, workdir / "stereo_curve.csv", [f'python remix-voiceover/scripts/rv.py analyze "{stereo}" --probe "{workdir / "probe.json"}" --json-out "{workdir / "analysis.json"}"'])
    assert abs(curve["rows"][-1]["integrated_lufs"] - stereo_curve["rows"][-1]["integrated_lufs"]) <= 0.2


def test_metadata_parser_rejects_missing_m_and_bad_pts_does_not_merge() -> None:
    rows, missing, frames = _parse_metadata(
        "\n".join(
            [
                "frame:1 pts:1 pts_time:0.100",
                "lavfi.r128.M=-20.0",
                "lavfi.r128.S=-20.0",
                "lavfi.r128.I=-20.0",
                "frame:2 pts:2 pts_time:N/A",
                "lavfi.r128.M=-5.0",
                "frame:3 pts:3 pts_time:0.300",
                "lavfi.r128.S=-30.0",
            ]
        )
    )
    assert frames == 3
    assert missing == 1
    assert len(rows) == 1
    assert rows[0]["momentary_lufs"] == -20.0
