from __future__ import annotations

import math
import wave
from array import array
from pathlib import Path

import pytest

from rv.rails import load_default_rails
from rv.speech import AnalyzeParameters, detect_level_regimes
from rv.util import RvError
from rv.verify import _bed_stitching_rows, _classify_outcome, _counterfactual_peak_safe_lift, _dip_rows, _duration_weighted_gap_quantile, _gap_rows, _mic_rows, _remove_counterfactual_scratch, _require_counterfactual_resources, _stitchable_gap_groups, _with_action_scopes


def _curve(duration: float, value_at) -> list[dict]:
    return [
        {
            "time_seconds": idx / 10.0,
            "end_seconds": idx / 10.0 + 0.1,
            "momentary_lufs": float(value_at(idx / 10.0)),
        }
        for idx in range(int(duration * 10))
    ]


def _gap_analysis(window_seconds: float = 0.5, count: int = 20) -> dict:
    windows = [
        {
            "window_id": f"w{idx:03d}",
            "regime_id": "r001",
            "start_seconds": idx * window_seconds,
            "end_seconds": (idx + 1) * window_seconds,
            "duration_seconds": window_seconds,
            "bed_present": True,
            "bed_presence_tier": "meaningful",
            "bed_lufs": -30.5,
        }
        for idx in range(count)
    ]
    return {
        "regimes": [{"id": "r001", "bed_body": {"raw_bed_body_lufs": -30.5}}],
        "bed_presence_windows": windows,
    }


def test_brief_jump_scare_is_legal_but_sustained_masking_fails() -> None:
    rails = load_default_rails()
    analysis = _gap_analysis()
    plan = {"segments": [{"regime_id": "r001", "bed_gain_db": 0.0}]}
    mic = _curve(10.0, lambda _: -20.5)

    jump_scare = _curve(10.0, lambda t: -24.5 if 4.0 <= t < 4.5 else -30.5)
    jump_row = next(row for row in _gap_rows(plan, analysis, mic, jump_scare, rails) if row["type"] == "mic_bed_gap")
    assert jump_row["status"] == "pass"
    assert "(0.050)" in jump_row["measurement"]
    assert "0.500s" in jump_row["measurement"]

    sustained = _curve(10.0, lambda t: -24.5 if 3.0 <= t < 6.0 else -30.5)
    sustained_row = next(row for row in _gap_rows(plan, analysis, mic, sustained, rails) if row["type"] == "mic_bed_gap")
    assert sustained_row["status"] == "fail"
    assert sustained_row["failure_class"] == "mic_bed_gap_out_of_rail"
    assert "(0.300)" in sustained_row["measurement"]
    assert "3.000s" in sustained_row["measurement"]


def test_quiet_bed_is_legal_and_retention_disclosure_never_blocks() -> None:
    rails = load_default_rails()
    analysis = _gap_analysis()
    mic = _curve(10.0, lambda _: -20.5)
    quiet_bed = _curve(10.0, lambda _: -50.5)

    justified = {
        "bed_segments": [
            {
                "id": "b001",
                "analysis_regime_ids": ["r001"],
                "gain_db": -20.0,
                "judgment": "mic-priority-yield",
            }
        ]
    }
    justified_rows = _gap_rows(justified, analysis, mic, quiet_bed, rails)
    assert all(row["status"] == "pass" for row in justified_rows)
    justified_retention = next(row for row in justified_rows if row["type"] == "bed_retention")
    assert justified_retention["failure_class"] == "bed_underused_disclosure"
    assert "verifier-owned bed_yield_necessity" in justified_retention["measurement"]

    unnecessary = {
        "bed_segments": [
            {
                "id": "b001",
                "analysis_regime_ids": ["r001"],
                "gain_db": -20.0,
                "judgment": "hold",
            }
        ]
    }
    unnecessary_rows = _gap_rows(unnecessary, analysis, mic, quiet_bed, rails)
    retention = next(row for row in unnecessary_rows if row["type"] == "bed_retention")
    assert retention["status"] == "pass"
    assert retention["failure_class"] == "bed_underused_disclosure"
    assert retention["next_action"] == "none"
    assert not any(row.get("failure_class") == "background_collapse" for row in unnecessary_rows)


def test_schema3_deep_yield_requires_verifier_owned_minimality() -> None:
    rails = load_default_rails()
    analysis = _gap_analysis()
    mic = _curve(10.0, lambda _: -20.5)
    plan = {
        "schema_version": 3,
        "targets": {"preferred_mic_over_bed_gap_db": 10.5},
        "bed_segments": [{"id": "b001", "analysis_regime_ids": ["r001"], "gain_db": -10.0, "judgment": "mic-priority-yield", "bed_yield_reason": "trust me", "recommendation": {"loudest_safe_sustained_gain_db": -10.0, "preferred_body_gain_db": 0.0}}],
    }

    minimal_bed = _curve(10.0, lambda t: -28.5 if 3.0 <= t < 6.0 else -40.5)
    minimal_rows = _gap_rows(plan, analysis, mic, minimal_bed, rails)
    necessity = next(row for row in minimal_rows if row["type"] == "bed_yield_necessity")
    assert necessity["status"] == "pass"
    assert necessity["failure_class"] == "bed_yield_necessity_proven"
    assert necessity["proof"]["maximum_masking_safe_uniform_lift_db"] <= 0.1

    underused_bed = _curve(10.0, lambda t: -29.5 if 3.0 <= t < 6.0 else -41.5)
    underused_rows = _gap_rows(plan, analysis, mic, underused_bed, rails)
    necessity = next(row for row in underused_rows if row["type"] == "bed_yield_necessity")
    assert necessity["status"] == "fail"
    assert necessity["failure_class"] == "bed_yield_not_minimal"
    assert necessity["proof"]["maximum_masking_safe_uniform_lift_db"] >= 1.0
    assert all(row["status"] == "pass" for row in underused_rows if row["type"] == "bed_retention")


def test_schema2_cannot_downgrade_around_verifier_owned_yield_proof() -> None:
    rails = load_default_rails()
    plan = {
        "schema_version": 2,
        "targets": {"preferred_mic_over_bed_gap_db": 10.5},
        "bed_segments": [{"id": "b001", "analysis_regime_ids": ["r001"], "gain_db": -10.0, "judgment": "mic-priority-yield", "bed_yield_reason": "trust me"}],
    }
    rows = _gap_rows(plan, _gap_analysis(), _curve(10.0, lambda _: -20.5), _curve(10.0, lambda _: -41.5), rails)
    necessity = next(row for row in rows if row["type"] == "bed_yield_necessity")
    assert necessity["status"] == "fail"
    assert necessity["failure_class"] == "bed_yield_not_minimal"


def test_candidate_peak_headroom_bounds_uniform_yield_repair() -> None:
    rails = load_default_rails()
    plan = {
        "schema_version": 3,
        "targets": {"preferred_mic_over_bed_gap_db": 10.5},
        "bed_segments": [{"id": "b001", "analysis_regime_ids": ["r001"], "gain_db": -10.0}],
    }
    rows = _gap_rows(plan, _gap_analysis(), _curve(10.0, lambda _: -20.5), _curve(10.0, lambda _: -41.5), rails, maximum_candidate_safe_lift_db=0.05)
    necessity = next(row for row in rows if row["type"] == "bed_yield_necessity")
    assert necessity["status"] == "pass"
    assert necessity["proof"]["maximum_masking_safe_uniform_lift_db"] >= 1.0
    assert necessity["proof"]["maximum_candidate_safe_uniform_lift_db"] == 0.05


def test_unmeasured_stitchable_bed_requests_evidence_not_impossible_gain_edit() -> None:
    rails = load_default_rails()
    analysis = _gap_analysis()
    analysis["bed_regimes"] = [{"id": "r001", "raw_bed_body_lufs": None}]
    plan = {
        "schema_version": 3,
        "targets": {"preferred_mic_over_bed_gap_db": 10.5},
        "bed_segments": [{"id": "b001", "analysis_regime_ids": ["r001"], "gain_db": -10.0, "stitching_policy": "stitchable"}],
    }
    rows = _gap_rows(plan, analysis, _curve(10.0, lambda _: -20.5), _curve(10.0, lambda _: -41.5), rails)
    necessity = next(row for row in rows if row["type"] == "bed_yield_necessity")
    assert necessity["status"] == "fail"
    assert necessity["failure_class"] == "unmeasured_bed_recovery_evidence_required"
    assert "do not edit bed gains" in necessity["next_action"]


def test_held_bed_windows_do_not_control_stitchable_counterfactual() -> None:
    plan = {
        "schema_version": 3,
        "bed_segments": [
            {"id": "b001", "analysis_regime_ids": ["br001"], "start_seconds": 0.0, "end_seconds": 5.0, "gain_db": 0.0, "stitching_policy": "preserve-unity-low-confidence"},
            {"id": "b002", "analysis_regime_ids": ["br002"], "start_seconds": 5.0, "end_seconds": 10.0, "gain_db": -5.0, "stitching_policy": "stitchable"},
        ],
    }
    groups = {
        "r001": [
            (4.0, {"start_seconds": 1.0, "end_seconds": 2.0}, 1.0),
            (6.0, {"start_seconds": 4.5, "end_seconds": 5.5}, 1.0),
            (20.0, {"start_seconds": 6.0, "end_seconds": 7.0}, 1.0),
        ]
    }
    analysis = {"duration_seconds": 10.0, "bed_regimes": [{"id": "br001", "raw_bed_body_lufs": None}, {"id": "br002", "raw_bed_body_lufs": -30.0}]}
    filtered = _stitchable_gap_groups(plan, analysis, groups)
    assert [row[0] for row in filtered["r001"]] == [20.0]


def test_gap_distribution_quantiles_are_duration_weighted() -> None:
    gaps = [(0.0, {}, 0.1), (10.0, {}, 9.9)]
    assert _duration_weighted_gap_quantile(gaps, 0.1) == 10.0
    assert _duration_weighted_gap_quantile(gaps, 0.5) == 10.0


def test_peak_counterfactual_does_not_lift_held_interval(tmp_path: Path) -> None:
    mic = tmp_path / "mic.wav"
    bed = tmp_path / "bed.wav"
    for path, sample_at in (
        (mic, lambda _: 0),
        (bed, lambda index: int((19000 if index < 48000 else 1000) * math.sin(2.0 * math.pi * 440.0 * index / 48000.0))),
    ):
        samples = array("h")
        for index in range(96000):
            value = sample_at(index)
            samples.extend((value, value))
        with wave.open(str(path), "wb") as stream:
            stream.setnchannels(2)
            stream.setsampwidth(2)
            stream.setframerate(48000)
            stream.writeframes(samples.tobytes())
    segments = [
        {"start_seconds": 0.0, "end_seconds": 1.0, "counterfactual_lift_eligible": False},
        {"start_seconds": 1.0, "end_seconds": 2.0, "counterfactual_lift_eligible": True},
    ]
    safe = _counterfactual_peak_safe_lift(mic, bed, 2.0, 6.0, 0.1, -1.0, ["repair"], tmp_path, segments, 10, 68719476736, 172800.0, 6, 1.25)
    assert safe == 6.0
    assert list(tmp_path.glob(".rv-bed-yield-peak-*")) == []


def test_counterfactual_resource_preflight_rejects_insufficient_disk(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(RvError, match="estimated scratch .* exceeds"):
        _require_counterfactual_resources(tmp_path, 60.0, 1, 1.25, ["repair"])
    usage = type("Usage", (), {"free": 1})()
    monkeypatch.setattr("rv.verify.shutil.disk_usage", lambda _: usage)
    with pytest.raises(RvError, match="requires .* free bytes"):
        _require_counterfactual_resources(tmp_path, 60.0, 68719476736, 1.25, ["repair"])


def test_counterfactual_cleanup_failure_is_not_silent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    scratch = tmp_path / ".rv-bed-yield-peak-test"
    scratch.mkdir()
    monkeypatch.setattr("rv.verify.shutil.rmtree", lambda *args, **kwargs: None)
    with pytest.raises(RvError, match="scratch cleanup failed"):
        _remove_counterfactual_scratch(scratch, ["repair"])


def test_counterfactual_media_work_budget_blocks_before_render(tmp_path: Path) -> None:
    with pytest.raises(RvError, match="decoded-media work budget"):
        _counterfactual_peak_safe_lift(tmp_path / "mic.wav", tmp_path / "bed.wav", 2.0, 1.0, 0.1, -1.0, ["repair"], tmp_path, [], 10, 68719476736, 11.9, 6, 1.25)
    assert list(tmp_path.glob(".rv-bed-yield-peak-*")) == []


def test_schema3_naturally_quiet_unattenuated_bed_does_not_trigger_yield_gate() -> None:
    rails = load_default_rails()
    analysis = _gap_analysis()
    plan = {"schema_version": 3, "targets": {"preferred_mic_over_bed_gap_db": 10.5}, "bed_segments": [{"id": "b001", "analysis_regime_ids": ["r001"], "gain_db": 0.0}]}
    rows = _gap_rows(plan, analysis, _curve(10.0, lambda _: -20.5), _curve(10.0, lambda _: -50.5), rails)
    necessity = next(row for row in rows if row["type"] == "bed_yield_necessity")
    assert necessity["status"] == "pass"
    assert necessity["proof"]["triggered"] is False


def test_macro_gap_spread_is_visible_but_never_blocks() -> None:
    rails = load_default_rails()
    analysis = _stitch_analysis()
    analysis["bed_presence_windows"] = [
        {"window_id": "w1", "regime_id": "r001", "start_seconds": 0.0, "end_seconds": 20.0, "duration_seconds": 20.0, "bed_presence_tier": "meaningful", "meaningful": True},
        {"window_id": "w2", "regime_id": "r002", "start_seconds": 20.0, "end_seconds": 40.0, "duration_seconds": 20.0, "bed_presence_tier": "meaningful", "meaningful": True},
    ]
    plan = {**_stitch_plan(), "roles": {"bed_streams": [1]}, "bed_segments": []}
    mic = _curve(40.0, lambda _: -20.0)
    bed = _curve(40.0, lambda t: -40.0 if t < 20.0 else -47.0)
    row = next(item for item in _gap_rows(plan, analysis, mic, bed, rails) if item["type"] == "mic_bed_gap_consistency")
    assert row["status"] == "pass"
    assert row["failure_class"] == "macro_gap_spread_disclosure"
    assert "spread 7.000 dB" in row["measurement"]


def test_explicit_no_bed_role_accepts_silence() -> None:
    rails = load_default_rails()
    analysis = _gap_analysis()
    plan = {"roles": {"bed_streams": []}, "bed_segments": []}
    mic = _curve(10.0, lambda _: -20.5)
    silence = _curve(10.0, lambda _: -120.0)
    rows = _gap_rows(plan, analysis, mic, silence, rails)
    assert all(row["status"] == "pass" for row in rows)
    assert any(row.get("failure_class") == "no-bed" for row in rows)


def test_bed_stitching_preserves_low_confidence_regime_and_skips_its_boundary() -> None:
    rails = load_default_rails()
    analysis = {
        "bed_regimes": [
            {"id": "b001", "start_seconds": 0.0, "end_seconds": 20.0, "raw_bed_body_lufs": -56.0, "stitching_policy": "preserve-unity-low-confidence"},
            {"id": "b002", "start_seconds": 20.0, "end_seconds": 40.0, "raw_bed_body_lufs": -31.0, "stitching_policy": "stitchable"},
        ]
    }
    plan = {"roles": {"bed_streams": [1]}, "targets": {"shared_bed_body_lufs": -31.0}}
    bed = _curve(40.0, lambda t: -56.0 if t < 20.0 else -31.0)
    rows = _bed_stitching_rows(plan, analysis, bed, rails)
    assert all(row["status"] == "pass" for row in rows)
    assert any(row.get("failure_class") == "bed_preserved_unity_low_confidence" for row in rows)
    assert not any(row["type"] == "bed_stitch_adjacent" for row in rows)

    changed = _curve(40.0, lambda t: -55.0 if t < 20.0 else -31.0)
    failures = _bed_stitching_rows(plan, analysis, changed, rails)
    assert any(row.get("failure_class") == "preserved_unity_bed_body_changed" for row in failures)


def test_all_low_confidence_bed_regimes_need_no_shared_target() -> None:
    rails = load_default_rails()
    analysis = {"bed_regimes": [{"id": "b001", "start_seconds": 0.0, "end_seconds": 20.0, "raw_bed_body_lufs": -56.0, "stitching_policy": "preserve-unity-low-confidence"}]}
    plan = {"roles": {"bed_streams": [1]}, "targets": {"shared_bed_body_lufs": None}}
    rows = _bed_stitching_rows(plan, analysis, _curve(20.0, lambda _: -56.0), rails)
    assert all(row["status"] == "pass" for row in rows)
    assert any(row.get("failure_class") == "all_bed_regimes_preserved_unity" for row in rows)


def _stitch_analysis() -> dict:
    return {
        "regimes": [
            {"id": "r001", "start_seconds": 0.0, "end_seconds": 20.0, "duration_seconds": 20.0, "active_speech_density": 1.0, "clean_gain_headroom": {"margin_db": 20.0}},
            {"id": "r002", "start_seconds": 20.0, "end_seconds": 40.0, "duration_seconds": 20.0, "active_speech_density": 1.0, "clean_gain_headroom": {"margin_db": 20.0}},
        ],
        "speech_windows": [
            {"regime_id": "r001", "start_seconds": 0.0, "end_seconds": 20.0, "duration_seconds": 20.0},
            {"regime_id": "r002", "start_seconds": 20.0, "end_seconds": 40.0, "duration_seconds": 20.0},
        ],
    }


def _stitch_plan() -> dict:
    return {
        "schema_version": 2,
        "targets": {"shared_mic_body_lufs": -20.5, "preferred_mic_over_bed_gap_db": 10.5},
        "mic_segments": [
            {"id": "m001", "analysis_regime_ids": ["r001"], "start_seconds": 0.0, "end_seconds": 20.0, "gain_db": 0.0},
            {"id": "m002", "analysis_regime_ids": ["r002"], "start_seconds": 20.0, "end_seconds": 40.0, "gain_db": 0.0},
        ],
    }


def test_v2_shared_target_enforces_adjacent_and_full_body_spread() -> None:
    rails = load_default_rails()
    analysis = _stitch_analysis()
    plan = _stitch_plan()

    stitched = _curve(40.0, lambda t: -20.0 if t < 20.0 else -21.0)
    stitched_rows = [row for row in _mic_rows(plan, analysis, stitched, rails) if row["type"].startswith("mic_stitch")]
    assert {row["type"] for row in stitched_rows} == {"mic_stitch_target", "mic_stitch_adjacent", "mic_stitch_spread"}
    assert all(row["status"] == "pass" for row in stitched_rows)

    broken = _curve(40.0, lambda t: -20.0 if t < 20.0 else -23.0)
    broken_rows = [row for row in _mic_rows(plan, analysis, broken, rails) if row["type"].startswith("mic_stitch")]
    failures = {row.get("failure_class") for row in broken_rows if row["status"] == "fail"}
    assert failures == {"mic_stitch_target_missed", "mic_stitch_adjacent_jump", "mic_stitch_body_spread"}


def test_applied_gain_shape_has_no_long_duration_loophole(tmp_path: Path) -> None:
    raw_csv = tmp_path / "raw.csv"
    raw_csv.write_text(
        "time_seconds,end_seconds,momentary_lufs\n"
        + "".join(f"{idx / 10:.1f},{idx / 10 + 0.1:.1f},-30.0\n" for idx in range(50)),
        encoding="utf-8",
    )
    analysis = {"curve_sidecars": {"0": str(raw_csv)}}
    plan = {
        "roles": {"mic_streams": [0]},
        "schema_version": 2,
        "mic_segments": [{"start_seconds": 0.0, "end_seconds": 5.0, "gain_db": 10.0}],
        "bed_segments": [],
        "event_overlays": [],
        "targets": {},
    }
    reshaped = _curve(5.0, lambda t: -14.0 if 1.0 <= t < 4.0 else -20.0)
    rows = _dip_rows(plan, analysis, reshaped, load_default_rails())
    assert any(row.get("failure_class") == "applied_gain_shape_artifact" for row in rows)


def test_outcome_classifier_preserves_failure_ownership() -> None:
    plan = {"targets": {"shared_mic_body_lufs": -20.5}}
    tuning = _with_action_scopes([{"type": "mic_lufs", "status": "fail", "failure_class": "mic_below_rail", "next_action": "raise gain"}])
    assert _classify_outcome(tuning, plan)["class"] == "tuning-required"

    toolkit = [{"type": "plan", "status": "fail", "failure_class": "unsupported_automation", "next_action": "extend compiler", "action_scope": "toolkit-change"}]
    classified = _classify_outcome(toolkit, plan)
    assert classified["class"] == "toolkit-limited"
    assert classified["limitation_owner"] == "toolkit"

    target_limited = _classify_outcome([], {"targets": {"shared_mic_body_lufs": -22.0}})
    assert target_limited["class"] == "target-limited"

    unmeasured = _with_action_scopes([{"type": "true_peak", "status": "fail", "failure_class": "true_peak_unmeasured", "next_action": "install compatible ffmpeg"}])
    assert _classify_outcome(unmeasured, plan)["class"] == "toolkit-limited"


def test_one_shout_cannot_hide_nine_quiet_ordinary_windows() -> None:
    rails = load_default_rails()
    windows = [
        {"id": f"w{idx}", "regime_id": "r001", "start_seconds": float(idx), "end_seconds": float(idx + 1), "duration_seconds": 1.0}
        for idx in range(10)
    ]
    analysis = {"regimes": [{"id": "r001", "duration_seconds": 10.0, "active_speech_density": 1.0}], "speech_windows": windows}
    plan = {"segments": [{"regime_id": "r001"}], "rails": {}}
    curve = _curve(10.0, lambda t: -10.74 if t >= 9.0 else -25.74)
    rows = _mic_rows(plan, analysis, curve, rails)
    body = next(row for row in rows if row["type"] == "mic_lufs")
    assert body["status"] == "fail"
    assert body["failure_class"] == "mic_below_rail"


def test_twenty_db_bed_capture_drop_fails_independent_stitching() -> None:
    rails = load_default_rails()
    analysis = {
        "bed_regimes": [
            {"id": "b001", "start_seconds": 0.0, "end_seconds": 10.0},
            {"id": "b002", "start_seconds": 10.0, "end_seconds": 20.0},
        ]
    }
    plan = {"roles": {"bed_streams": [1]}, "targets": {"shared_bed_body_lufs": -30.0}}
    curve = _curve(20.0, lambda t: -30.0 if t < 10.0 else -50.0)
    rows = _bed_stitching_rows(plan, analysis, curve, rails)
    assert any(row.get("failure_class") == "bed_stitch_target_missed" for row in rows)
    assert any(row.get("failure_class") == "bed_stitch_adjacent_jump" for row in rows)
    assert any(row.get("failure_class") == "bed_stitch_body_spread" for row in rows)


def test_brief_bed_event_does_not_create_a_sustained_capture_regime() -> None:
    rows = _curve(90.0, lambda t: -10.0 if 44.0 <= t < 45.0 else -30.0)
    result = detect_level_regimes(rows, AnalyzeParameters())
    assert result["bed_step_candidates"] == []
    assert len(result["bed_regimes"]) == 1
    assert result["bed_regimes"][0]["raw_bed_body_lufs"] == -30.0


def test_thirty_second_expressive_bed_passage_is_not_a_macro_capture_regime() -> None:
    rows = _curve(390.0, lambda t: -5.0 if 180.0 <= t < 210.0 else -20.0)
    result = detect_level_regimes(rows, AnalyzeParameters())

    assert result["bed_step_candidates"] == []
    assert len(result["bed_regimes"]) == 1
    assert result["bed_regimes"][0]["start_seconds"] == 0.0
    assert result["bed_regimes"][0]["end_seconds"] == 390.0


def test_sixty_second_expressive_bed_passage_is_not_a_macro_capture_regime_by_default() -> None:
    rows = _curve(420.0, lambda t: -5.0 if 180.0 <= t < 240.0 else -20.0)
    result = detect_level_regimes(rows, AnalyzeParameters())
    assert result["bed_step_candidates"] == []
    assert len(result["bed_regimes"]) == 1
