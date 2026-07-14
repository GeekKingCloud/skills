from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from rv.plan import _recenter_bed_after_macro, confirmed_mic_transition_boundaries, materialize_lane_segments, plan_init_command, validate_plan
from rv.render import _validate_plan_for_render
from rv.util import RvError, read_json, sha256_json


def _analysis(*, split: bool = False) -> dict:
    regimes = [
        {
            "id": "r001",
            "start_seconds": 0.0,
            "end_seconds": 50.0 if split else 1000.0,
            "duration_seconds": 50.0 if split else 1000.0,
            "raw_speech_body_lufs": -20.0,
            "bed_body": {"raw_bed_body_lufs": -31.0},
            "clean_gain_headroom": {"max_clean_gain_before_noise_floor_target_db": 30.0},
        }
    ]
    if split:
        regimes.append(
            {
                "id": "r002",
                "start_seconds": 50.0,
                "end_seconds": 100.0,
                "duration_seconds": 50.0,
                "raw_speech_body_lufs": -20.25,
                "bed_body": {"raw_bed_body_lufs": -31.0},
                "clean_gain_headroom": {"max_clean_gain_before_noise_floor_target_db": 30.0},
            }
        )
    windows = [
        {"id": f"w{idx}", "regime_id": "r001", "start_seconds": point, "end_seconds": point + 1.0, "duration_seconds": 1.0}
        for idx, point in enumerate((100.0, 200.0, 300.0, 400.0))
    ]
    return {
        "schema_version": 1,
        "source_sha256": "source-a",
        "duration_seconds": 100.0 if split else 1000.0,
        "analysis_roles": {"mic_streams": [0], "bed_streams": [1], "excluded_existing_mix_streams": []},
        "lane_profiles": [
            {"audio_stream_index": 0, "speech_shape_ratio": 0.8},
            {"audio_stream_index": 1, "speech_shape_ratio": 0.1},
        ],
        "cross_lane_correlation": {"existing_mix_candidates": []},
        "regimes": regimes,
        "step_candidates": [{"boundary_seconds": 50.0}] if split else [],
        "speech_windows": windows,
    }


def _init_plan(tmp_path: Path, analysis: dict) -> dict:
    analysis_path = tmp_path / "analysis.json"
    plan_path = tmp_path / "render_plan.json"
    analysis_path.write_text(json.dumps(analysis), encoding="utf-8")
    assert plan_init_command(argparse.Namespace(analysis=str(analysis_path), out=str(plan_path))) == 0
    return read_json(plan_path)


def test_four_dispersed_overlays_do_not_fragment_baseline_budget(tmp_path: Path) -> None:
    analysis = _analysis()
    plan = _init_plan(tmp_path, analysis)
    baseline_gain = float(plan["mic_segments"][0]["gain_db"])
    plan["event_overlays"] = [
        {
            "id": f"e{idx}",
            "lane": "mic",
            "start_seconds": point,
            "end_seconds": point + 1.0,
            "gain_delta_db": -3.0,
            "ramp_in_seconds": 0.1,
            "ramp_out_seconds": 0.1,
            "event_reason": f"bounded peak {idx}",
            "event_citation": {"source": "analysis", "ref": f"/speech_windows/{idx}"},
        }
        for idx, point in enumerate((100.0, 200.0, 300.0, 400.0))
    ]

    rows = validate_plan(plan, analysis)
    assert not [row for row in rows if row["status"] == "fail"]
    first = materialize_lane_segments(plan, "mic", analysis)
    second = materialize_lane_segments(plan, "mic", analysis)
    assert len(first) == 9
    assert first == second
    assert sha256_json(first) == sha256_json(second)
    assert [row["id"] for row in first] == [f"mic-m{idx:04d}" for idx in range(1, 10)]
    assert [row["mic_gain_db"] for row in first if row["overlay_ids"]] == [baseline_gain - 3.0] * 4


def test_plan_level_boundary_override_cannot_erase_transition_ownership(tmp_path: Path) -> None:
    analysis = _analysis(split=True)
    plan = _init_plan(tmp_path, analysis)
    plan["mic_segments"] = [
        {
            **plan["mic_segments"][0],
            "id": "m-confirmed",
            "analysis_regime_ids": ["r001", "r002"],
            "start_seconds": 0.0,
            "end_seconds": 100.0,
        }
    ]
    plan["boundary_overrides"] = [
        {"lane": "mic", "boundary_seconds": 50.0, "reason": "detector fluctuation inside one plateau", "analysis_evidence_paths": ["/step_candidates/0"]}
    ]

    rows = validate_plan(plan, analysis)
    assert any(row.get("failure_class") == "boundary_override_unsupported" for row in rows)
    assert confirmed_mic_transition_boundaries(plan, analysis) == []
    materialized = materialize_lane_segments(plan, "mic", analysis)
    assert [(row["start_seconds"], row["end_seconds"]) for row in materialized] == [(0.0, 100.0)]


def test_promotion_event_citation_requires_current_source_and_analysis_lineage(tmp_path: Path) -> None:
    analysis = _analysis()
    plan = _init_plan(tmp_path, analysis)
    prior = tmp_path / "prior.json"
    prior.write_text(
        json.dumps(
            {
                "status": "fail",
                "source_sha256": analysis["source_sha256"],
                "analysis_sha256": sha256_json(analysis),
                "rows": [{"status": "fail", "failure_class": "true_peak_exceeded", "event_seconds": 100.0}],
            }
        ),
        encoding="utf-8",
    )
    plan["event_overlays"] = [
        {
            "id": "peak",
            "lane": "mic",
            "start_seconds": 99.5,
            "end_seconds": 100.5,
            "gain_delta_db": -2.0,
            "ramp_in_seconds": 0.1,
            "ramp_out_seconds": 0.1,
            "event_reason": "verified true peak",
            "event_citation": {"source": "promotion_manifest", "path": str(prior), "ref": "/rows/0"},
        }
    ]
    assert not [row for row in validate_plan(plan, analysis) if row["status"] == "fail"]

    foreign = json.loads(prior.read_text(encoding="utf-8"))
    foreign["status"] = "pass"
    foreign["source_sha256"] = "different-source"
    prior.write_text(json.dumps(foreign), encoding="utf-8")
    failures = [row for row in validate_plan(plan, analysis) if row["status"] == "fail"]
    assert any("source lineage differs" in row["measurement"] for row in failures)


def test_legacy_segments_cannot_enter_production_materialization() -> None:
    analysis = {"duration_seconds": 10.0, "regimes": [], "step_candidates": []}
    legacy = {
        "schema_version": 1,
        "segments": [
            {
                "id": "s001",
                "regime_id": "r001",
                "start_seconds": 0.0,
                "end_seconds": 10.0,
                "mic_gain_db": 2.0,
                "bed_gain_db": -4.0,
                "ramp_in_seconds": 0.0,
                "ramp_out_seconds": 0.0,
                "judgment": "lift",
            }
        ],
    }
    with pytest.raises(RvError, match="schema_version 2"):
        materialize_lane_segments(legacy, "mic", analysis)


def test_plan_init_uses_independent_bed_regimes_and_enforces_bed_steps(tmp_path: Path) -> None:
    analysis = _analysis(split=True)
    analysis["bed_regimes"] = [
        {"id": "b001", "start_seconds": 0.0, "end_seconds": 25.0, "raw_bed_body_lufs": -31.0},
        {"id": "b002", "start_seconds": 25.0, "end_seconds": 100.0, "raw_bed_body_lufs": -37.0},
    ]
    analysis["bed_step_candidates"] = [{"boundary_seconds": 25.0, "step_db": -6.0}]
    plan = _init_plan(tmp_path, analysis)
    assert [(row["start_seconds"], row["end_seconds"]) for row in plan["mic_segments"]] == [(0.0, 50.0), (50.0, 100.0)]
    assert [(row["start_seconds"], row["end_seconds"]) for row in plan["bed_segments"]] == [(0.0, 25.0), (25.0, 50.0), (50.0, 100.0)]
    assert not [row for row in validate_plan(plan, analysis) if row["status"] == "fail"]

    plan["bed_segments"] = [{**plan["bed_segments"][0], "end_seconds": 100.0}]
    failures = [row for row in validate_plan(plan, analysis) if row["status"] == "fail"]
    assert any(row["failure_class"] == "bed_segment_spans_detected_step" for row in failures)


def test_plan_init_preserves_low_confidence_bed_at_unity(tmp_path: Path) -> None:
    analysis = _analysis(split=True)
    analysis["bed_regimes"] = [
        {"id": "b001", "start_seconds": 0.0, "end_seconds": 25.0, "raw_bed_body_lufs": -56.351, "stitching_policy": "preserve-unity-low-confidence"},
        {"id": "b002", "start_seconds": 25.0, "end_seconds": 100.0, "raw_bed_body_lufs": -50.0, "stitching_policy": "stitchable"},
    ]
    analysis["bed_step_candidates"] = [{"boundary_seconds": 25.0, "step_db": 25.351}]
    analysis["speech_windows"] = [{"id": "wbed", "regime_id": "r001", "start_seconds": 30.0, "end_seconds": 31.0, "duration_seconds": 1.0, "raw_mic_window_lufs": -20.0}]
    analysis["bed_presence_windows"] = [{"window_id": "wbed", "regime_id": "r001", "start_seconds": 30.0, "end_seconds": 31.0, "duration_seconds": 1.0, "bed_lufs": -50.0, "bed_presence_tier": "meaningful", "meaningful": True}]
    plan = _init_plan(tmp_path, analysis)
    held = plan["bed_segments"][0]
    assert (held["start_seconds"], held["end_seconds"]) == (0.0, 25.0)
    assert held["gain_db"] == 0.0
    assert held["judgment"] == "hold"
    assert held["stitching_policy"] == "preserve-unity-low-confidence"
    assert held["ramp_in_seconds"] == held["ramp_out_seconds"] == 0.0
    assert plan["targets"]["shared_bed_body_lufs"] == -30.0
    assert plan["bed_segments"][1]["ramp_in_seconds"] == 0.25
    assert not [row for row in validate_plan(plan, analysis) if row["status"] == "fail"]

    plan["bed_segments"][0]["gain_db"] = 1.0
    failures = [row for row in validate_plan(plan, analysis) if row["status"] == "fail"]
    assert any(row["failure_class"] == "preserve_unity_bed_modified" for row in failures)


def test_plan_uses_one_sided_ramp_for_sub_12_db_stitchable_to_held_boundary(tmp_path: Path) -> None:
    analysis = _analysis()
    analysis["bed_regimes"] = [
        {"id": "b001", "start_seconds": 0.0, "end_seconds": 25.0, "raw_bed_body_lufs": -40.0, "stitching_policy": "stitchable"},
        {"id": "b002", "start_seconds": 25.0, "end_seconds": 1000.0, "raw_bed_body_lufs": -64.0, "stitching_policy": "preserve-unity-low-confidence"},
    ]
    analysis["bed_step_candidates"] = [{"boundary_seconds": 25.0, "step_db": -24.0}]
    plan = _init_plan(tmp_path, analysis)
    stitchable, held = plan["bed_segments"]
    assert 0.25 < stitchable["gain_db"] < 12.0
    assert stitchable["ramp_out_seconds"] == 0.25
    assert held["ramp_in_seconds"] == held["ramp_out_seconds"] == 0.0
    assert not [row for row in validate_plan(plan, analysis) if row["status"] == "fail"]


def test_plan_rejects_ramp_or_overlay_inside_preserved_unity_bed(tmp_path: Path) -> None:
    analysis = _analysis()
    analysis["bed_regimes"] = [{"id": "b001", "start_seconds": 0.0, "end_seconds": 1000.0, "raw_bed_body_lufs": -70.0, "stitching_policy": "preserve-unity-low-confidence"}]
    analysis["bed_step_candidates"] = []
    plan = _init_plan(tmp_path, analysis)
    assert plan["targets"]["shared_bed_body_lufs"] is None
    assert not [row for row in validate_plan(plan, analysis) if row["status"] == "fail"]

    plan["bed_segments"][0]["ramp_in_seconds"] = 0.25
    plan["event_overlays"] = [{"id": "e1", "lane": "bed", "start_seconds": 10.0, "end_seconds": 11.0, "gain_delta_db": 1.0}]
    failures = [row for row in validate_plan(plan, analysis) if row["status"] == "fail"]
    assert any(row["failure_class"] == "preserve_unity_bed_modified" for row in failures)


def test_plan_rejects_forged_preserve_policy_without_regime_ownership(tmp_path: Path) -> None:
    analysis = _analysis()
    plan = _init_plan(tmp_path, analysis)
    segment = plan["bed_segments"][0]
    segment["analysis_regime_ids"] = []
    segment["stitching_policy"] = "preserve-unity-low-confidence"
    segment["gain_db"] = 0.0
    segment["judgment"] = "hold"
    failures = [row for row in validate_plan(plan, analysis) if row["status"] == "fail"]
    assert any(row["failure_class"] == "preserve_unity_bed_modified" for row in failures)


def test_plan_init_applies_only_bounded_macro_bed_corrections(tmp_path: Path) -> None:
    analysis = _analysis(split=True)
    analysis["duration_seconds"] = 300.0
    analysis["regimes"] = [
        {"id": "r001", "start_seconds": 0.0, "end_seconds": 150.0, "duration_seconds": 150.0, "raw_speech_body_lufs": -20.0, "bed_body": {"raw_bed_body_lufs": -30.0}, "clean_gain_headroom": {"max_clean_gain_before_noise_floor_target_db": 30.0}},
        {"id": "r002", "start_seconds": 150.0, "end_seconds": 300.0, "duration_seconds": 150.0, "raw_speech_body_lufs": -20.0, "bed_body": {"raw_bed_body_lufs": -40.0}, "clean_gain_headroom": {"max_clean_gain_before_noise_floor_target_db": 30.0}},
    ]
    analysis["step_candidates"] = [{"boundary_seconds": 150.0}]
    analysis["bed_regimes"] = [{"id": "b001", "start_seconds": 0.0, "end_seconds": 300.0, "raw_bed_body_lufs": -35.0}]
    analysis["bed_step_candidates"] = []
    analysis["speech_windows"] = []
    analysis["bed_presence_windows"] = []
    for index in range(24):
        regime_id = "r001" if index < 12 else "r002"
        start = index * 12.0 if index < 12 else 150.0 + (index - 12) * 12.0
        window_id = f"w{index:03d}"
        analysis["speech_windows"].append({"id": window_id, "regime_id": regime_id, "start_seconds": start, "end_seconds": start + 1.0, "duration_seconds": 1.0, "raw_mic_window_lufs": -20.0})
        analysis["bed_presence_windows"].append({"window_id": window_id, "regime_id": regime_id, "start_seconds": start, "end_seconds": start + 1.0, "duration_seconds": 1.0, "bed_lufs": -35.0, "bed_presence_tier": "meaningful", "meaningful": True})
    plan = _init_plan(tmp_path, analysis)
    assert [(row["start_seconds"], row["end_seconds"]) for row in plan["bed_segments"]] == [(0.0, 150.0), (150.0, 300.0)]
    corrections = [row["recommendation"]["macro_balance_correction_db"] for row in plan["bed_segments"]]
    assert corrections == [-1.5, 1.5]
    assert not [row for row in validate_plan(plan, analysis) if row["status"] == "fail"]

    plan["bed_segments"][1]["gain_db"] += 0.5
    failures = [row for row in validate_plan(plan, analysis) if row["status"] == "fail"]
    assert any(row["failure_class"] == "macro_balance_gain_mismatch" for row in failures)


def test_post_macro_recenter_recovers_only_uniform_masking_safe_slack() -> None:
    rails = {
        "mic_over_bed_gap_db": {"min": 8.0},
        "sustained_masking": {
            "house_minimum_gap_db": 8.0,
            "maximum_duration_fraction_below_minimum": 0.1,
            "maximum_contiguous_seconds_below_minimum": 2.0,
            "window_adjacency_tolerance_seconds": 0.15,
        },
        "bed_retention": {"planner_recovery_reserve_db": 0.1, "counterfactual_step_db": 0.1},
    }
    analysis = {
        "speech_windows": [
            {"id": "w1", "raw_mic_window_lufs": -20.5},
            {"id": "w2", "raw_mic_window_lufs": -20.5},
            {"id": "w3", "raw_mic_window_lufs": -20.5},
        ],
        "bed_presence_windows": [
            {"window_id": "w1", "bed_presence_tier": "meaningful", "start_seconds": 10.0, "end_seconds": 11.0, "bed_lufs": -29.5},
            {"window_id": "w2", "bed_presence_tier": "meaningful", "start_seconds": 110.0, "end_seconds": 111.0, "bed_lufs": -18.5},
            {"window_id": "w3", "bed_presence_tier": "meaningful", "start_seconds": 210.0, "end_seconds": 211.0, "bed_lufs": -30.5},
        ],
    }
    mic_segments = [{"start_seconds": 0.0, "end_seconds": 300.0, "gain_db": 0.0}]
    bed_regimes = [{"id": "b001", "raw_bed_body_lufs": -30.0}]
    segments = [
        {"id": "b1", "analysis_regime_ids": ["b001"], "start_seconds": 0.0, "end_seconds": 100.0, "gain_db": -10.0, "recommendation": {"preferred_body_gain_db": -1.0, "macro_balance_correction_db": 0.0}},
        {"id": "b2", "analysis_regime_ids": ["b001"], "start_seconds": 100.0, "end_seconds": 200.0, "gain_db": -11.0, "recommendation": {"preferred_body_gain_db": -1.0, "macro_balance_correction_db": -1.0}},
        {"id": "b3", "analysis_regime_ids": ["b001"], "start_seconds": 200.0, "end_seconds": 300.0, "gain_db": -8.5, "recommendation": {"preferred_body_gain_db": -1.0, "macro_balance_correction_db": 1.5}},
    ]
    recentered, proof = _recenter_bed_after_macro(analysis, segments, bed_regimes, mic_segments, -20.5, 10.5, rails)
    assert proof is not None
    assert proof["global_safety_recovery_db"] == 0.9
    assert [row["gain_db"] for row in recentered] == [-9.1, -10.1, -7.6]
    assert [row["gain_db"] - recentered[0]["gain_db"] for row in recentered] == [0.0, -1.0, 1.5]


def test_post_macro_recenter_is_disabled_when_stitchable_body_is_unmeasured() -> None:
    rails = {"bed_retention": {"planner_recovery_reserve_db": 0.1, "counterfactual_step_db": 0.1}}
    segments = [
        {"id": "b1", "analysis_regime_ids": ["b001"], "start_seconds": 0.0, "end_seconds": 10.0, "gain_db": -4.0, "recommendation": {}},
        {"id": "b2", "analysis_regime_ids": ["b002"], "start_seconds": 10.0, "end_seconds": 20.0, "gain_db": -5.0, "recommendation": {}},
    ]
    recentered, proof = _recenter_bed_after_macro({}, segments, [{"id": "b001", "raw_bed_body_lufs": -30.0}, {"id": "b002", "raw_bed_body_lufs": None}], [], -20.5, 10.5, rails)
    assert [row["gain_db"] for row in recentered] == [-4.0, -5.0]
    assert proof is not None
    assert proof["policy"] == "no-recovery-unmeasured-stitchable-bed-v1"
    assert proof["global_safety_recovery_db"] == 0.0
    assert proof["unmeasured_segment_ids"] == ["b2"]


def test_plan_init_adds_short_ramps_for_large_capture_state_jumps(tmp_path: Path) -> None:
    analysis = _analysis(split=True)
    analysis["regimes"][0]["raw_speech_body_lufs"] = -40.0
    analysis["regimes"][1]["raw_speech_body_lufs"] = -20.0
    plan = _init_plan(tmp_path, analysis)
    assert plan["mic_segments"][0]["ramp_out_seconds"] == 0.25
    assert plan["mic_segments"][1]["ramp_in_seconds"] == 0.25
    assert not any(row["failure_class"] == "unramped_gain_step" for row in validate_plan(plan, analysis))


def test_plan_init_enables_bounded_peak_control_when_gain_estimate_overflows(tmp_path: Path) -> None:
    analysis = _analysis()
    analysis["lane_profiles"][0]["maximum_true_peak_dbtp"] = -0.4
    plan = _init_plan(tmp_path, analysis)
    assert plan["render"]["peak_control"]["enabled"] is True
    assert plan["render"]["peak_control"]["mechanism"] == "alimiter"
    assert plan["render"]["peak_control"]["true_peak_ceiling_dbtp"] == -1.5


def test_plan_init_emits_only_authoritative_v2_lane_surfaces(tmp_path: Path) -> None:
    analysis = _analysis()
    plan = _init_plan(tmp_path, analysis)
    assert "segments" not in plan
    assert "compatibility" not in plan
    serialized = json.dumps(plan, sort_keys=True)
    assert "source_limit" not in serialized
    assert "legacy" not in serialized
    assert materialize_lane_segments(plan, "mic", analysis)[0]["mic_gain_db"] == plan["mic_segments"][0]["gain_db"]


def test_declared_v2_requires_all_authoritative_surfaces(tmp_path: Path) -> None:
    analysis = _analysis()
    plan = _init_plan(tmp_path, analysis)
    del plan["mic_segments"]
    failures = [row for row in validate_plan(plan, analysis) if row["status"] == "fail"]
    assert any(row["failure_class"] == "invalid_v2_schema" for row in failures)


def test_v2_plan_cannot_downgrade_through_legacy_mirror(tmp_path: Path) -> None:
    analysis = _analysis()
    plan = _init_plan(tmp_path, analysis)
    plan["schema_version"] = 1
    failures = [row for row in validate_plan(plan, analysis) if row["status"] == "fail"]
    assert any(row["failure_class"] == "v2_schema_downgrade" for row in failures)


def test_genuine_schema_v1_plan_is_rejected_from_production_validation() -> None:
    analysis = {"duration_seconds": 10.0}
    legacy = {
        "schema_version": 1,
        "analysis": {"sha256": sha256_json(analysis), "duration_seconds": 10.0},
        "segments": [{"start_seconds": 0.0, "end_seconds": 10.0, "mic_gain_db": 0.0, "bed_gain_db": -6.0}],
    }
    failures = [row for row in validate_plan(legacy, analysis) if row["status"] == "fail"]
    assert [row["failure_class"] for row in failures] == ["v2_schema_downgrade"]
    render_validation = _validate_plan_for_render(Path("legacy.json"), legacy, Path("analysis.json"), analysis)
    assert render_validation["status"] == "fail"
    assert render_validation["rows"][0]["failure_class"] == "v2_schema_downgrade"


def test_arbitrarily_inaudible_shared_target_is_rejected(tmp_path: Path) -> None:
    analysis = _analysis()
    plan = _init_plan(tmp_path, analysis)
    plan["targets"]["shared_mic_body_lufs"] = -99.0
    for segment in plan["mic_segments"]:
        segment["gain_db"] = -79.0
    failures = [row for row in validate_plan(plan, analysis) if row["status"] == "fail"]
    assert any(row["failure_class"] == "invalid_shared_mic_target" for row in failures)
