from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Any

from .rails import _resolve_analysis_ref, adjusted_rails, clean_gain_allowed_ceiling, clean_gain_default_ceiling, has_regime_clean_gain_headroom_evidence, load_default_rails, validate_adjustment
from .util import RvError, read_json, refuse_output_alias, rounded, sha256_file, sha256_json, utc_now, write_json


def plan_init_command(args: argparse.Namespace) -> int:
    analysis_path = Path(args.analysis)
    out = Path(args.out)
    refuse_output_alias(out, [analysis_path], ["choose a render plan path distinct from analysis.json"], label="render plan output")
    analysis = read_json(analysis_path)
    if analysis.get("media_path"):
        refuse_output_alias(out, [analysis["media_path"]], ["choose a render plan path distinct from the source media"], label="render plan output")
    defaults = load_default_rails()
    roles = analysis.get("confirmed_roles") or analysis.get("analysis_roles") or analysis.get("inferred_roles", {})
    mic_segments: list[dict[str, Any]] = []
    bed_segments: list[dict[str, Any]] = []
    regimes = analysis.get("regimes", [])
    mic_target = _recommended_shared_mic_target(regimes, defaults)
    gap_target = float(defaults["mic_over_bed_gap_db"]["preferred"])
    for idx, regime in enumerate(regimes, start=1):
        clean_headroom = regime.get("clean_gain_headroom", {})
        required_lift = float(clean_headroom.get("reference_gain_to_loudest_regime_db") or 0.0)
        regime_id = regime.get("id", f"r{idx:03d}")
        raw_mic = regime.get("raw_speech_body_lufs")
        mic_gain = round(mic_target - float(raw_mic), 3) if raw_mic is not None else 0.0
        evidence_paths: list[str] = []
        if mic_gain > clean_gain_default_ceiling(defaults):
            evidence_paths.append(f"/regimes/{idx - 1}/clean_gain_headroom")
        mic_segments.append(
            {
                "id": f"m{idx:03d}",
                "analysis_regime_ids": [regime_id],
                "start_seconds": regime.get("start_seconds"),
                "end_seconds": regime.get("end_seconds"),
                "gain_db": mic_gain,
                "ramp_in_seconds": 0.0,
                "ramp_out_seconds": 0.0,
                "judgment": _gain_judgment(mic_gain),
                "evidence_paths": evidence_paths,
                "recommendation": {
                    "shared_target_lufs": mic_target,
                    "analysis_reference_lift_db": rounded(required_lift, 2),
                },
            }
        )
    if roles.get("bed_streams"):
        bed_regimes = analysis.get("bed_regimes") or _bed_regimes_from_mic_measurements(regimes)
        for idx, regime in enumerate(bed_regimes, start=1):
            raw_bed = regime.get("raw_bed_body_lufs")
            regime_id = str(regime.get("id") or f"b{idx:03d}")
            preferred_bed_gain = round((mic_target - gap_target) - float(raw_bed), 3) if raw_bed is not None else 0.0
            preserve_unity = _preserve_unity_bed(regime)
            bed_gain = 0.0 if preserve_unity else _loudest_safe_bed_gain(analysis, regime, mic_segments, preferred_bed_gain, defaults)
            bed_segments.append(
                {
                    "id": f"b{idx:03d}",
                    "analysis_regime_ids": [regime_id],
                    "start_seconds": regime.get("start_seconds"),
                    "end_seconds": regime.get("end_seconds"),
                    "gain_db": bed_gain,
                    "ramp_in_seconds": 0.0,
                    "ramp_out_seconds": 0.0,
                    "judgment": _gain_judgment(bed_gain),
                    "stitching_policy": regime.get("stitching_policy", "stitchable"),
                    "evidence_paths": [],
                    "recommendation": {
                        "shared_mic_target_lufs": mic_target,
                        "preferred_gap_db": gap_target,
                        "preferred_body_gain_db": preferred_bed_gain,
                        "loudest_safe_sustained_gain_db": bed_gain,
                        "stitching_policy": regime.get("stitching_policy", "stitchable"),
                    },
                }
            )
        shared_bed_target = _stitch_bed_targets(bed_segments, bed_regimes)
        bed_segments = _bounded_macro_balance_segments(analysis, bed_segments, bed_regimes, mic_segments, defaults)
        bed_segments, bed_yield_reconciliation = _recenter_bed_after_macro(analysis, bed_segments, bed_regimes, mic_segments, mic_target, gap_target, defaults)
    else:
        shared_bed_target = None
        bed_yield_reconciliation = None
    _add_required_transition_ramps(mic_segments)
    _add_required_transition_ramps(bed_segments)
    plan = {
        "schema_version": 3,
        "generated_at": utc_now(),
        "analysis": {
            "path": str(analysis_path),
            "sha256": sha256_json(analysis),
            "source_sha256": analysis.get("source_sha256"),
            "duration_seconds": analysis.get("duration_seconds"),
        },
        "roles": {
            "mic_streams": roles.get("mic_streams", []),
            "bed_streams": roles.get("bed_streams", []),
            "excluded_existing_mix_streams": roles.get("excluded_existing_mix_streams", []),
            "role_basis": roles.get("role_basis"),
            "role_override": None,
            "role_override_hint": "Plan-level role overrides are unsupported. Rerun analyze with confirmed mic and bed selectors, then rerun plan-init.",
        },
        "rails": {
            "defaults": defaults,
            "adjusted": defaults,
            "rails_adjustment": None,
            "rails_adjustment_hint": "Optional; mic band center shift +/-2 dB, gap shift +/-1.5 dB, with analysis_evidence_paths.",
        },
        "targets": {
            "shared_mic_body_lufs": mic_target,
            "preferred_mic_over_bed_gap_db": gap_target,
            "shared_bed_body_lufs": shared_bed_target,
            "bed_yield_reconciliation": bed_yield_reconciliation,
            "basis": "preferred rails lowered only when an analysis clean-gain ceiling makes the preferred mic target infeasible",
            "constraints": _shared_target_constraints(regimes, defaults, mic_target),
        },
        "mic_segments": mic_segments,
        "bed_segments": bed_segments,
        "event_overlays": [],
        "boundary_overrides": [],
        "boundary_overrides_hint": "Boundary overrides are unsupported. Retain detected mic and bed transitions or rerun analyze with bounded detector parameters.",
        "render": {
            "sample_rate_hz": 48000,
            "channel_layout": "stereo",
            "sample_format": "pcm_f32le",
            "peak_control": _recommended_peak_control(analysis, roles, mic_segments),
            "sum_exactness": "components are rendered separately; mix is ffmpeg amix normalize=0 of the listener-heard mic_component.wav and bed_component.wav",
        },
    }
    write_json(out, plan)
    return 0


def plan_validate_command(args: argparse.Namespace) -> int:
    plan_path = Path(args.plan)
    analysis_path = Path(args.analysis)
    refuse_output_alias(args.json_out, [plan_path, analysis_path], ["choose a plan-validation output distinct from plan and analysis"], label="plan-validation JSON output")
    plan = read_json(plan_path)
    analysis = read_json(analysis_path)
    if analysis.get("media_path"):
        refuse_output_alias(args.json_out, [analysis["media_path"]], ["choose a plan-validation output distinct from the source media"], label="plan-validation JSON output")
    rows = validate_plan(plan, analysis)
    status = "pass" if all(row["status"] == "pass" for row in rows) else "fail"
    payload = {
        "schema_version": 1,
        "generated_at": utc_now(),
        "status": status,
        "plan_path": str(plan_path),
        "plan_sha256": sha256_json(plan),
        "analysis_path": str(analysis_path),
        "analysis_sha256": sha256_json(analysis),
        "rows": rows,
        "lineage": {
            "plan_analysis_sha256": plan.get("analysis", {}).get("sha256"),
            "actual_analysis_sha256": sha256_json(analysis),
            "source_sha256": analysis.get("source_sha256"),
        },
    }
    write_json(args.json_out, payload)
    return 0 if status == "pass" else 1


def validate_plan(plan: dict[str, Any], analysis: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    rows.extend(_schema_rows(plan))
    if rows:
        return rows
    duration = float(analysis.get("duration_seconds") or plan.get("analysis", {}).get("duration_seconds") or 0.0)
    if plan.get("analysis", {}).get("sha256") != sha256_json(analysis):
        rows.append(_fail("stale_analysis_hash", "plan analysis sha256 does not match analysis.json", "rerun: python remix-voiceover/scripts/rv.py plan-init --analysis <analysis.json> --out <render_plan.json>"))
    rows.extend(_finite_rows(plan))
    if any(row["failure_class"] == "non_finite_plan_value" for row in rows):
        return rows
    rows.extend(_role_rows(plan, analysis))
    rows.extend(_v2_coverage_rows(plan, analysis, duration))
    rows.extend(_v2_event_rows(plan, analysis))
    rows.extend(_v2_step_rows(plan, analysis))
    rows.extend(_v2_bed_step_rows(plan, analysis))
    rows.extend(_v2_gain_rows(plan, analysis))
    rows.extend(_preserve_unity_bed_rows(plan, analysis))
    rows.extend(_boundary_override_rows(plan, analysis))
    rows.extend(_peak_control_rows(plan))
    defaults = load_default_rails()
    rows.extend(validate_adjustment(defaults, plan.get("rails", {}).get("rails_adjustment"), analysis))
    rows.extend(_target_rows(plan, analysis, adjusted_rails(defaults, plan.get("rails", {}).get("rails_adjustment"))))
    if not any(row["status"] == "fail" for row in rows):
        rows.append(_pass("plan_contract", "render plan covers duration, matches analysis hash, roles pass cross-exam, gains and rails are inside bounds", "validated"))
    return rows


def _peak_control_rows(plan: dict[str, Any]) -> list[dict[str, Any]]:
    config = plan.get("render", {}).get("peak_control")
    if config is None:
        return []
    if not isinstance(config, dict):
        return [_fail("invalid_peak_control", "render.peak_control must be an object or null", "remove render.peak_control or declare enabled, true_peak_ceiling_dbtp, and mechanism=alimiter")]
    enabled = config.get("enabled")
    if not isinstance(enabled, bool):
        return [_fail("invalid_peak_control", "render.peak_control.enabled must be boolean", "set render.peak_control.enabled to true or false")]
    if not enabled:
        return []
    if config.get("mechanism") != "alimiter":
        return [_fail("invalid_peak_control", "enabled peak control mechanism must be alimiter", "set render.peak_control.mechanism to alimiter")]
    ceiling = config.get("true_peak_ceiling_dbtp")
    try:
        numeric = float(ceiling)
    except (TypeError, ValueError):
        numeric = math.nan
    if not math.isfinite(numeric) or numeric < -24.0 or numeric > -1.0:
        return [_fail("invalid_peak_control", f"peak-control ceiling {ceiling!r} is outside -24.0..-1.0 dBTP", "set render.peak_control.true_peak_ceiling_dbtp inside -24.0..-1.0")]
    return []


_SEGMENT_NUMERIC_BOUNDS = {
    "start_seconds": (0.0, 1e7),
    "end_seconds": (0.0, 1e7),
    "mic_gain_db": (-120.0, 60.0),
    "bed_gain_db": (-120.0, 60.0),
    "ramp_in_seconds": (0.0, 600.0),
    "ramp_out_seconds": (0.0, 600.0),
}

_ALLOWED_JUDGMENTS = {"lift", "trim", "hold", "local-support"}


def _is_v2(plan: dict[str, Any]) -> bool:
    return int(plan.get("schema_version") or 1) >= 2 and isinstance(plan.get("mic_segments"), list) and isinstance(plan.get("bed_segments"), list)


def _is_v3(plan: dict[str, Any]) -> bool:
    return int(plan.get("schema_version") or 1) >= 3 and _is_v2(plan)


def _schema_rows(plan: dict[str, Any]) -> list[dict[str, Any]]:
    raw_version = plan.get("schema_version")
    try:
        version = int(raw_version)
    except (TypeError, ValueError):
        version = None
    if version not in {2, 3}:
        failure_class = "v2_schema_downgrade" if version == 1 else "unsupported_plan_schema"
        return [_fail(failure_class, f"production plans must declare schema_version 2 or 3; got {raw_version!r}", "rerun plan-init to create the current render plan schema")]
    missing = [key for key in ("mic_segments", "bed_segments", "event_overlays") if not isinstance(plan.get(key), list)]
    if not isinstance(plan.get("targets"), dict):
        missing.append("targets")
    if missing:
        return [_fail("invalid_v2_schema", f"declared schema v2 is missing required surfaces: {', '.join(missing)}", "rerun plan-init; do not downgrade through the legacy mirror")]
    return []


def _v2_sections_hash(mic_segments: list[dict[str, Any]], bed_segments: list[dict[str, Any]], event_overlays: list[dict[str, Any]]) -> str:
    return sha256_json({"mic_segments": mic_segments, "bed_segments": bed_segments, "event_overlays": event_overlays})


def _recommended_shared_mic_target(regimes: list[dict[str, Any]], rails: dict[str, Any]) -> float:
    mic_rails = rails["processed_mic_active_speech_lufs"]
    preferred = float(mic_rails["preferred"])
    reachable: list[float] = []
    for regime in regimes:
        body = regime.get("raw_speech_body_lufs")
        if body is None:
            continue
        reachable.append(float(body) + clean_gain_allowed_ceiling(regime, rails))
    if not reachable:
        return preferred
    return round(min(preferred, min(reachable)), 3)


def _shared_target_constraints(regimes: list[dict[str, Any]], rails: dict[str, Any], target: float) -> list[dict[str, Any]]:
    constraints: list[dict[str, Any]] = []
    for regime in regimes:
        body = regime.get("raw_speech_body_lufs")
        if body is None:
            continue
        reachable = float(body) + clean_gain_allowed_ceiling(regime, rails)
        if abs(reachable - target) <= 0.01:
            constraints.append({"regime_id": regime.get("id"), "raw_body_lufs": float(body), "clean_gain_ceiling_db": clean_gain_allowed_ceiling(regime, rails), "reachable_target_lufs": rounded(reachable, 3)})
    return constraints


def _target_rows(plan: dict[str, Any], analysis: dict[str, Any], rails: dict[str, Any]) -> list[dict[str, Any]]:
    if not _is_v2(plan):
        return []
    target = plan.get("targets", {}).get("shared_mic_body_lufs") if isinstance(plan.get("targets"), dict) else None
    try:
        actual = float(target)
    except (TypeError, ValueError):
        return [_fail("invalid_shared_mic_target", f"shared mic target {target!r} is not numeric", "rerun plan-init or set a finite feasibility-derived target")]
    expected = _recommended_shared_mic_target(analysis.get("regimes", []), rails)
    rows: list[dict[str, Any]] = []
    if not math.isfinite(actual) or abs(actual - expected) > 0.01:
        rows.append(_fail("invalid_shared_mic_target", f"declared shared mic target {actual} LUFS differs from highest safe analysis-derived target {expected} LUFS", "rerun plan-init; use bounded rails_adjustment for caller calibration instead of hand-authoring an arbitrary target"))
        return rows
    tolerance = float(rails.get("mic_stitching_v2", {}).get("target_tolerance_db", 1.5))
    regimes = {str(row.get("id")): row for row in analysis.get("regimes", [])}
    for segment in plan.get("mic_segments", []):
        gain = float(segment.get("gain_db") or 0.0)
        for regime_id in segment.get("analysis_regime_ids", []):
            regime = regimes.get(str(regime_id), {})
            body = regime.get("raw_speech_body_lufs")
            if body is None:
                continue
            achieved = float(body) + gain
            if abs(achieved - actual) > tolerance:
                rows.append(_fail("mic_baseline_misses_shared_target", f"mic segment {segment.get('id')} would place {regime_id} at {achieved:.3f} LUFS instead of shared target {actual:.3f}", "set the baseline gain from shared target minus raw regime BODY, within the stitching tolerance"))
    if plan.get("roles", {}).get("bed_streams"):
        bed_regimes = analysis.get("bed_regimes") or _bed_regimes_from_mic_measurements(analysis.get("regimes", []))
        expected_bed = _expected_shared_bed_target(analysis, bed_regimes, plan.get("mic_segments", []), actual, rails)
        declared_bed = plan.get("targets", {}).get("shared_bed_body_lufs")
        try:
            declared_bed_value = float(declared_bed)
        except (TypeError, ValueError):
            declared_bed_value = math.nan
        if expected_bed is None:
            if declared_bed is not None:
                rows.append(_fail("invalid_shared_bed_target", f"all bed regimes are preserved at unity but shared bed target is {declared_bed!r}", "rerun plan-init and keep targets.shared_bed_body_lufs null"))
        elif not math.isfinite(declared_bed_value) or abs(declared_bed_value - expected_bed) > 0.01:
            rows.append(_fail("invalid_shared_bed_target", f"declared shared bed target {declared_bed!r} differs from loudest safe stitched target {expected_bed}", "rerun plan-init; lower bed with evidence-backed yield rather than hand-authoring the target"))
        bed_by_id = {str(row.get("id")): row for row in bed_regimes}
        bed_bodies = {regime_id: row.get("raw_bed_body_lufs") for regime_id, row in bed_by_id.items()}
        bed_tolerance = float(rails.get("bed_stitching_v2", {}).get("target_tolerance_db", 1.5))
        for segment in plan.get("bed_segments", []):
            regime_id = str((segment.get("analysis_regime_ids") or [""])[0])
            if _preserve_unity_bed(bed_by_id.get(regime_id, {})):
                continue
            body = bed_bodies.get(regime_id)
            if body is not None and math.isfinite(declared_bed_value):
                recommendation = segment.get("recommendation") if isinstance(segment.get("recommendation"), dict) else {}
                parent_gain = recommendation.get("parent_baseline_gain_db")
                achieved = float(body) + float(parent_gain if parent_gain is not None else segment.get("gain_db") or 0.0)
                if abs(achieved - declared_bed_value) > bed_tolerance:
                    rows.append(_fail("bed_baseline_misses_shared_target", f"bed segment {segment.get('id')} would place {regime_id} at {achieved:.3f} LUFS instead of stitched target {declared_bed_value:.3f}", "set the bed baseline from shared bed target minus raw bed regime BODY"))
                correction = float(recommendation.get("macro_balance_correction_db") or 0.0)
                maximum = float(rails.get("macro_balance_consistency", {}).get("maximum_bed_correction_db", 1.5))
                if abs(correction) > maximum + 0.001:
                    rows.append(_fail("macro_balance_correction_exceeded", f"bed segment {segment.get('id')} correction {correction:.3f} dB exceeds +/-{maximum:.3f} dB", "rerun plan-init or keep the macro balance correction inside the bounded rail"))
                if parent_gain is not None:
                    recovery = float(recommendation.get("global_safety_recovery_db") or 0.0) if _is_v3(plan) else 0.0
                    expected_gain = float(parent_gain) + correction + recovery
                    actual_gain = float(segment.get("gain_db") or 0.0)
                    if abs(actual_gain - expected_gain) > 0.01:
                        rows.append(_fail("macro_balance_gain_mismatch", f"bed segment {segment.get('id')} gain {actual_gain:.3f} dB differs from parent {float(parent_gain):.3f} plus correction {correction:.3f} plus global recovery {recovery:.3f}", "rerun plan-init; do not detach the rendered bed gain from its bounded macro correction and global recovery"))
        if _is_v3(plan):
            rows.extend(_bed_yield_plan_rows(plan, analysis, bed_regimes, actual, rails))
    return rows


def _bed_yield_plan_rows(
    plan: dict[str, Any],
    analysis: dict[str, Any],
    bed_regimes: list[dict[str, Any]],
    mic_target: float,
    rails: dict[str, Any],
) -> list[dict[str, Any]]:
    stitchable_segments = [segment for segment in plan.get("bed_segments", []) if not _preserve_unity_bed(segment)]
    if not stitchable_segments:
        return []
    reconciliation = plan.get("targets", {}).get("bed_yield_reconciliation")
    if not isinstance(reconciliation, dict):
        return [_fail("missing_bed_yield_reconciliation", "schema-3 bed plan has no targets.bed_yield_reconciliation", "rerun plan-init")]
    try:
        declared_recovery = float(reconciliation.get("global_safety_recovery_db"))
    except (TypeError, ValueError):
        return [_fail("invalid_bed_yield_reconciliation", "global_safety_recovery_db is not numeric", "rerun plan-init")]
    gap_target = float(plan.get("targets", {}).get("preferred_mic_over_bed_gap_db", rails["mic_over_bed_gap_db"]["preferred"]))
    bodies = {str(row.get("id")): row.get("raw_bed_body_lufs") for row in bed_regimes}
    missing_body_segments = [
        str(segment.get("id"))
        for segment in stitchable_segments
        if bodies.get(str((segment.get("analysis_regime_ids") or [""])[0])) is None
    ]
    policy = reconciliation.get("policy")
    if missing_body_segments:
        rows: list[dict[str, Any]] = []
        if policy != "no-recovery-unmeasured-stitchable-bed-v1" or abs(declared_recovery) > 0.001:
            rows.append(_fail("unmeasured_bed_recovery", f"stitchable bed segments {missing_body_segments} lack raw BODY evidence but reconciliation policy is {policy!r} with recovery {declared_recovery:.3f} dB", "rerun plan-init; unmeasured stitchable bed disables global recovery"))
        for segment in stitchable_segments:
            recommendation = segment.get("recommendation") if isinstance(segment.get("recommendation"), dict) else {}
            segment_recovery = float(recommendation.get("global_safety_recovery_db") or 0.0)
            if abs(segment_recovery) > 0.001:
                rows.append(_fail("unmeasured_bed_recovery", f"bed segment {segment.get('id')} applies {segment_recovery:.3f} dB global recovery while {missing_body_segments} lack BODY evidence", "rerun plan-init; keep global recovery at 0 dB"))
        return rows
    if policy == "no-recovery-unmeasured-stitchable-bed-v1":
        return [_fail("stale_unmeasured_bed_policy", "plan declares unmeasured-bed recovery suppression but every stitchable segment has BODY evidence", "rerun plan-init from current analysis")]
    remaining: list[tuple[float, str, float]] = []
    rows: list[dict[str, Any]] = []
    for segment in plan.get("bed_segments", []):
        if _preserve_unity_bed(segment):
            continue
        regime_id = str((segment.get("analysis_regime_ids") or [""])[0])
        raw_body = bodies.get(regime_id)
        if raw_body is None:
            continue
        recommendation = segment.get("recommendation") if isinstance(segment.get("recommendation"), dict) else {}
        segment_recovery = float(recommendation.get("global_safety_recovery_db") or 0.0)
        if abs(segment_recovery - declared_recovery) > 0.01:
            rows.append(_fail("bed_yield_recovery_mismatch", f"bed segment {segment.get('id')} recovery {segment_recovery:.3f} dB differs from declared global recovery {declared_recovery:.3f} dB", "rerun plan-init; apply one uniform recovery to every stitchable bed segment"))
        preferred_gain = _segment_preferred_bed_gain(segment, mic_target, gap_target, float(raw_body))
        safe_ceiling = _loudest_safe_bed_gain(analysis, segment, plan.get("mic_segments", []), preferred_gain, rails)
        actual_gain = float(segment.get("gain_db") or 0.0)
        slack = safe_ceiling - actual_gain
        if slack < -0.011:
            rows.append(_fail("bed_gain_exceeds_safe_ceiling", f"bed segment {segment.get('id')} gain {actual_gain:.3f} dB exceeds masking-safe ceiling {safe_ceiling:.3f} dB", "lower the global bed recovery and rerun render/verify"))
        remaining.append((max(0.0, slack), str(segment.get("id")), safe_ceiling))
    if remaining:
        available, controlling_id, safe_ceiling = min(remaining, key=lambda item: item[0])
        maximum = float(rails.get("bed_retention", {}).get("maximum_unexplained_recoverable_lift_db", 0.11))
        if available > maximum + 0.001:
            rows.append(_fail("bed_yield_not_minimal", f"schema-3 plan leaves {available:.3f} dB uniform masking-safe bed lift unused; controlling segment {controlling_id} ceiling {safe_ceiling:.3f} dB", "rerun plan-init or increase the declared global bed recovery by the verifier-named amount"))
    return rows


def _expected_shared_bed_target(
    analysis: dict[str, Any],
    bed_regimes: list[dict[str, Any]],
    mic_segments: list[dict[str, Any]],
    mic_target: float,
    rails: dict[str, Any],
) -> float | None:
    preferred_gap = float(rails["mic_over_bed_gap_db"]["preferred"])
    targets: list[float] = []
    for regime in bed_regimes:
        if _preserve_unity_bed(regime):
            continue
        raw_bed = regime.get("raw_bed_body_lufs")
        if raw_bed is None:
            continue
        preferred_gain = (mic_target - preferred_gap) - float(raw_bed)
        safe_gain = _loudest_safe_bed_gain(analysis, regime, mic_segments, preferred_gain, rails)
        targets.append(float(raw_bed) + safe_gain)
    return rounded(min(targets), 3) if targets else None


def _gain_judgment(gain: float) -> str:
    if gain > 0.25:
        return "lift"
    if gain < -0.25:
        return "trim"
    return "hold"


def _add_required_transition_ramps(segments: list[dict[str, Any]], *, threshold_db: float = 12.0, ramp_seconds: float = 0.25) -> None:
    """Make generated large capture-state jumps valid without blunting recovery."""
    for previous, current in zip(segments, segments[1:]):
        delta = abs(float(current.get("gain_db") or 0.0) - float(previous.get("gain_db") or 0.0))
        previous_held = _preserve_unity_bed(previous)
        current_held = _preserve_unity_bed(current)
        boundary_threshold = 0.25 if previous_held != current_held else threshold_db
        if delta <= boundary_threshold:
            continue
        if not previous_held:
            previous["ramp_out_seconds"] = max(float(previous.get("ramp_out_seconds") or 0.0), ramp_seconds)
        if not current_held:
            current["ramp_in_seconds"] = max(float(current.get("ramp_in_seconds") or 0.0), ramp_seconds)


def _loudest_safe_bed_gain(
    analysis: dict[str, Any],
    bed_regime: dict[str, Any],
    mic_segments: list[dict[str, Any]],
    preferred_gain: float,
    rails: dict[str, Any],
) -> float:
    """Lower a bed baseline only as far as sustained masking requires."""
    start = float(bed_regime.get("start_seconds") or 0.0)
    end = float(bed_regime.get("end_seconds") or 0.0)
    speech_by_id = {str(row.get("id")): row for row in analysis.get("speech_windows", [])}
    overlaps: list[tuple[float, float, float]] = []
    for bed_window in analysis.get("bed_presence_windows", []):
        tier = bed_window.get("bed_presence_tier")
        if tier not in {None, "meaningful"} or bed_window.get("meaningful") is False:
            continue
        win_start = float(bed_window.get("start_seconds") or 0.0)
        win_end = float(bed_window.get("end_seconds") or win_start)
        midpoint = win_start + (win_end - win_start) / 2.0
        if not (start <= midpoint < end):
            continue
        speech = speech_by_id.get(str(bed_window.get("window_id")), {})
        raw_mic = speech.get("raw_mic_window_lufs")
        raw_bed = bed_window.get("bed_lufs")
        if raw_mic is None or raw_bed is None:
            continue
        mic_gain = next(
            (
                float(segment.get("gain_db") or 0.0)
                for segment in mic_segments
                if float(segment.get("start_seconds") or 0.0) <= midpoint < float(segment.get("end_seconds") or 0.0)
            ),
            0.0,
        )
        overlaps.append((win_start, win_end, float(raw_mic) + mic_gain - float(raw_bed)))
    if not overlaps:
        return round(preferred_gain, 3)
    config = rails.get("sustained_masking", {})
    minimum = float(config.get("house_minimum_gap_db", 8.0))
    fraction_limit = float(config.get("maximum_duration_fraction_below_minimum", 0.1))
    run_limit = float(config.get("maximum_contiguous_seconds_below_minimum", 2.0))
    adjacency = float(config.get("window_adjacency_tolerance_seconds", 0.15))
    candidate = float(preferred_gain)
    while candidate >= -120.0:
        below = [(a, b) for a, b, raw_gap in overlaps if raw_gap - candidate < minimum]
        total = sum(max(0.0, b - a) for a, b, _ in overlaps)
        below_duration = sum(max(0.0, b - a) for a, b in below)
        longest = _longest_interval_run(below, adjacency)
        if (below_duration / total if total > 0 else 0.0) <= fraction_limit and longest <= run_limit:
            return round(candidate, 3)
        candidate = rounded(candidate - 0.1, 3)
    return -120.0


def _longest_interval_run(intervals: list[tuple[float, float]], adjacency: float) -> float:
    best = 0.0
    run_start: float | None = None
    run_end: float | None = None
    for start, end in sorted(intervals):
        if run_start is None or run_end is None or start > run_end + adjacency:
            run_start, run_end = start, end
        else:
            run_end = max(run_end, end)
        best = max(best, run_end - run_start)
    return best


def _stitch_bed_targets(bed_segments: list[dict[str, Any]], bed_regimes: list[dict[str, Any]]) -> float | None:
    bodies = {str(row.get("id")): row.get("raw_bed_body_lufs") for row in bed_regimes}
    safe_targets: list[float] = []
    for segment in bed_segments:
        if _preserve_unity_bed(segment):
            continue
        regime_id = str((segment.get("analysis_regime_ids") or [""])[0])
        body = bodies.get(regime_id)
        if body is not None:
            safe_targets.append(float(body) + float(segment.get("gain_db") or 0.0))
    if not safe_targets:
        return None
    shared = min(safe_targets)
    for segment in bed_segments:
        if _preserve_unity_bed(segment):
            continue
        regime_id = str((segment.get("analysis_regime_ids") or [""])[0])
        body = bodies.get(regime_id)
        if body is None:
            continue
        segment["gain_db"] = rounded(shared - float(body), 3)
        recommendation = segment.get("recommendation") if isinstance(segment.get("recommendation"), dict) else {}
        recommendation["shared_bed_body_lufs"] = rounded(shared, 3)
        segment["recommendation"] = recommendation
        segment["judgment"] = _gain_judgment(float(segment["gain_db"]))
    return rounded(shared, 3)


def _bounded_macro_balance_segments(
    analysis: dict[str, Any],
    parent_segments: list[dict[str, Any]],
    bed_regimes: list[dict[str, Any]],
    mic_segments: list[dict[str, Any]],
    rails: dict[str, Any],
) -> list[dict[str, Any]]:
    """Apply small, sustained bed corrections after the independent capture map is stitched."""
    mic_regimes = analysis.get("regimes", [])
    config = rails.get("macro_balance_consistency", {})
    maximum = float(config.get("maximum_bed_correction_db", 1.5))
    minimum_seconds = float(config.get("minimum_balance_section_seconds", 120.0))
    minimum_windows = int(config.get("minimum_meaningful_windows", 10))
    meaningful_counts: dict[str, int] = {}
    for window in analysis.get("bed_presence_windows", []):
        if window.get("bed_presence_tier") not in {None, "meaningful"} or window.get("meaningful") is False:
            continue
        regime_id = str(window.get("regime_id") or "")
        meaningful_counts[regime_id] = meaningful_counts.get(regime_id, 0) + 1
    if len(mic_regimes) < 2 or maximum <= 0.0:
        return parent_segments

    bodies = {str(row.get("id")): row.get("raw_bed_body_lufs") for row in bed_regimes}
    sections: list[dict[str, Any]] = []
    for parent in parent_segments:
        if _preserve_unity_bed(parent):
            sections.append(parent)
            continue
        parent_start = float(parent.get("start_seconds") or 0.0)
        parent_end = float(parent.get("end_seconds") or 0.0)
        parent_id = str((parent.get("analysis_regime_ids") or [""])[0])
        parent_body = bodies.get(parent_id)
        parent_gain = float(parent.get("gain_db") or 0.0)
        overlaps = [
            regime
            for regime in mic_regimes
            if float(regime.get("end_seconds") or 0.0) > parent_start + 0.001
            and float(regime.get("start_seconds") or 0.0) < parent_end - 0.001
        ]
        if not overlaps:
            sections.append(dict(parent))
            continue
        for regime in overlaps:
            start = max(parent_start, float(regime.get("start_seconds") or 0.0))
            end = min(parent_end, float(regime.get("end_seconds") or 0.0))
            regime_id = str(regime.get("id") or "")
            regime_bed = regime.get("bed_body") if isinstance(regime.get("bed_body"), dict) else {}
            section_body = regime_bed.get("raw_bed_body_lufs")
            full_mic_regime = abs(start - float(regime.get("start_seconds") or 0.0)) <= 0.001 and abs(end - float(regime.get("end_seconds") or 0.0)) <= 0.001
            eligible = (
                full_mic_regime
                and section_body is not None
                and parent_body is not None
                and end - start >= minimum_seconds
                and meaningful_counts.get(regime_id, 0) >= minimum_windows
            )
            correction = 0.0
            if eligible:
                desired_gain = float(parent_body) + parent_gain - float(section_body)
                correction = max(-maximum, min(maximum, desired_gain - parent_gain))
                section = {"start_seconds": start, "end_seconds": end}
                safe_gain = _loudest_safe_bed_gain(analysis, section, mic_segments, parent_gain + correction, rails)
                correction = min(correction, safe_gain - parent_gain)
            gain = rounded(parent_gain + correction, 3)
            recommendation = dict(parent.get("recommendation") or {})
            recommendation.update(
                {
                    "parent_bed_regime_id": parent_id,
                    "balance_regime_id": regime_id,
                    "parent_baseline_gain_db": rounded(parent_gain, 3),
                    "macro_balance_correction_db": rounded(gain - parent_gain, 3),
                    "section_raw_bed_body_lufs": rounded(section_body, 3),
                    "correction_eligible": eligible,
                }
            )
            sections.append(
                {
                    **parent,
                    "id": f"b{len(sections) + 1:03d}",
                    "start_seconds": rounded(start, 3),
                    "end_seconds": rounded(end, 3),
                    "gain_db": gain,
                    "judgment": _gain_judgment(gain),
                    "balance_regime_ids": [regime_id],
                    "recommendation": recommendation,
                }
            )
    return sections


def _recenter_bed_after_macro(
    analysis: dict[str, Any],
    segments: list[dict[str, Any]],
    bed_regimes: list[dict[str, Any]],
    mic_segments: list[dict[str, Any]],
    mic_target: float,
    gap_target: float,
    rails: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    """Recover uniform bed headroom created by bounded post-baseline corrections."""
    bodies = {str(row.get("id")): row.get("raw_bed_body_lufs") for row in bed_regimes}
    constraints: list[dict[str, Any]] = []
    unmeasured: list[str] = []
    for segment in segments:
        if _preserve_unity_bed(segment):
            continue
        regime_id = str((segment.get("analysis_regime_ids") or [""])[0])
        raw_body = bodies.get(regime_id)
        if raw_body is None:
            unmeasured.append(str(segment.get("id")))
            continue
        preferred_gain = _segment_preferred_bed_gain(segment, mic_target, gap_target, float(raw_body))
        safe_ceiling = _loudest_safe_bed_gain(analysis, segment, mic_segments, preferred_gain, rails)
        current_gain = float(segment.get("gain_db") or 0.0)
        constraints.append(
            {
                "segment_id": segment.get("id"),
                "safe_gain_ceiling_db": rounded(safe_ceiling, 3),
                "pre_recovery_gain_db": rounded(current_gain, 3),
                "recoverable_lift_db": rounded(max(0.0, safe_ceiling - current_gain), 3),
            }
        )
    if unmeasured:
        for segment in segments:
            if _preserve_unity_bed(segment):
                continue
            recommendation = dict(segment.get("recommendation") or {})
            recommendation["global_safety_recovery_db"] = 0.0
            segment["recommendation"] = recommendation
        return segments, {
            "policy": "no-recovery-unmeasured-stitchable-bed-v1",
            "global_safety_recovery_db": 0.0,
            "planner_recovery_reserve_db": float(rails.get("bed_retention", {}).get("planner_recovery_reserve_db", 0.1)),
            "controlling_segment_id": None,
            "unmeasured_segment_ids": unmeasured,
            "pre_recovery_constraints": constraints,
        }
    if not constraints:
        return segments, None
    config = rails.get("bed_retention", {})
    reserve = float(config.get("planner_recovery_reserve_db", 0.1))
    step = float(config.get("counterfactual_step_db", 0.1))
    available = min(float(row["recoverable_lift_db"]) for row in constraints)
    recovery = max(0.0, available - reserve)
    if step > 0.0:
        recovery = math.floor((recovery + 1e-9) / step) * step
    recovery = rounded(recovery, 3)
    for segment in segments:
        if _preserve_unity_bed(segment):
            continue
        segment["gain_db"] = rounded(float(segment.get("gain_db") or 0.0) + recovery, 3)
        segment["judgment"] = _gain_judgment(float(segment["gain_db"]))
        recommendation = dict(segment.get("recommendation") or {})
        recommendation["global_safety_recovery_db"] = recovery
        segment["recommendation"] = recommendation
    controlling = min(constraints, key=lambda row: float(row["recoverable_lift_db"]))
    return segments, {
        "policy": "uniform-post-macro-counterfactual-v1",
        "global_safety_recovery_db": recovery,
        "planner_recovery_reserve_db": reserve,
        "controlling_segment_id": controlling.get("segment_id"),
        "pre_recovery_constraints": constraints,
    }


def _segment_preferred_bed_gain(segment: dict[str, Any], mic_target: float, gap_target: float, parent_raw_body: float) -> float:
    recommendation = segment.get("recommendation") if isinstance(segment.get("recommendation"), dict) else {}
    correction = float(recommendation.get("macro_balance_correction_db") or 0.0)
    return (mic_target - gap_target) - parent_raw_body + correction


def _preserve_unity_bed(value: dict[str, Any]) -> bool:
    return value.get("stitching_policy") in {"preserve-unity-low-confidence", "hold-unity-indeterminate"}


def _preserve_unity_bed_rows(plan: dict[str, Any], analysis: dict[str, Any]) -> list[dict[str, Any]]:
    regimes = {str(row.get("id")): row for row in analysis.get("bed_regimes", [])}
    segments = plan.get("bed_segments", [])
    overlays = [row for row in plan.get("event_overlays", []) if row.get("lane") == "bed"]
    rows: list[dict[str, Any]] = []
    held_ids = {regime_id for regime_id, regime in regimes.items() if _preserve_unity_bed(regime)}
    for segment in segments:
        segment_ids = {str(value) for value in segment.get("analysis_regime_ids", [])}
        if _preserve_unity_bed(segment) and (
            len(segment_ids) != 1
            or not segment_ids <= held_ids
            or segment.get("stitching_policy") != regimes[next(iter(segment_ids))].get("stitching_policy")
        ):
            rows.append(_fail("preserve_unity_bed_modified", f"bed segment {segment.get('id')} declares preserve-unity for a stitchable regime", "rerun plan-init"))
    for regime_id in held_ids:
        regime = regimes[regime_id]
        owned = [segment for segment in segments if regime_id in {str(value) for value in segment.get("analysis_regime_ids", [])}]
        valid = len(owned) == 1
        segment = owned[0] if owned else {}
        valid = valid and abs(float(segment.get("start_seconds") or 0.0) - float(regime.get("start_seconds") or 0.0)) <= 0.001
        valid = valid and abs(float(segment.get("end_seconds") or 0.0) - float(regime.get("end_seconds") or 0.0)) <= 0.001
        valid = valid and _preserve_unity_bed(segment)
        valid = valid and abs(float(segment.get("gain_db") or 0.0)) <= 0.001
        valid = valid and abs(float(segment.get("ramp_in_seconds") or 0.0)) <= 0.001 and abs(float(segment.get("ramp_out_seconds") or 0.0)) <= 0.001
        valid = valid and segment.get("judgment") == "hold"
        start = float(regime.get("start_seconds") or 0.0)
        end = float(regime.get("end_seconds") or start)
        touching_overlay = any(float(row.get("start_seconds") or 0.0) < end and float(row.get("end_seconds") or 0.0) > start for row in overlays)
        if not valid or touching_overlay:
            rows.append(_fail("preserve_unity_bed_modified", f"bed regime {regime_id} must remain one exact 0 dB hold segment with no ramps or overlays", "rerun plan-init and leave the low-confidence bed regime unchanged"))
    return rows


def _recommended_peak_control(analysis: dict[str, Any], roles: dict[str, Any], mic_segments: list[dict[str, Any]]) -> dict[str, Any] | None:
    selected = {int(value) for value in roles.get("mic_streams", [])}
    peaks = [
        float(row["maximum_true_peak_dbtp"])
        for row in analysis.get("lane_profiles", [])
        if int(row.get("audio_stream_index", -1)) in selected and row.get("maximum_true_peak_dbtp") is not None
    ]
    if not peaks or not mic_segments:
        return None
    estimated = max(peaks) + max(float(row.get("gain_db") or 0.0) for row in mic_segments)
    if estimated <= -1.0:
        return None
    return {
        "enabled": True,
        "true_peak_ceiling_dbtp": -1.5,
        "mechanism": "alimiter",
        "basis": "conservative raw mic true-peak plus maximum planned baseline gain estimate exceeds the delivery ceiling; verifier duty and body-shape gates remain authoritative",
        "estimated_uncontrolled_true_peak_dbtp": rounded(estimated, 3),
    }


def _bed_regimes_from_mic_measurements(regimes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Compatibility fallback for analyses produced before independent bed regimes."""
    rows: list[dict[str, Any]] = []
    for idx, regime in enumerate(regimes, start=1):
        bed = regime.get("bed_body") if isinstance(regime.get("bed_body"), dict) else {}
        rows.append(
            {
                "id": f"b{idx:03d}",
                "start_seconds": regime.get("start_seconds"),
                "end_seconds": regime.get("end_seconds"),
                "raw_bed_body_lufs": bed.get("raw_bed_body_lufs"),
                "source": "mic-regime-derived-bed-measurement-fallback",
            }
        )
    return rows


def materialize_lane_segments(plan: dict[str, Any], lane: str, analysis: dict[str, Any]) -> list[dict[str, Any]]:
    """Compile one authored lane into deterministic flat renderer segments."""
    if lane not in {"mic", "bed"}:
        raise RvError(f"unknown plan lane {lane!r}; expected mic or bed", [])
    schema_failures = _schema_rows(plan)
    if schema_failures:
        raise RvError(schema_failures[0]["measurement"], [schema_failures[0]["next_action"]])
    baseline_key = f"{lane}_segments"
    baselines = sorted(plan.get(baseline_key, []), key=lambda row: (float(row.get("start_seconds") or 0.0), str(row.get("id") or "")))
    overlays = sorted(
        [row for row in plan.get("event_overlays", []) if row.get("lane") == lane],
        key=lambda row: (float(row.get("start_seconds") or 0.0), float(row.get("end_seconds") or 0.0), str(row.get("id") or "")),
    )
    boundaries = {float(row.get("start_seconds") or 0.0) for row in baselines}
    boundaries.update(float(row.get("end_seconds") or 0.0) for row in baselines)
    for overlay in overlays:
        boundaries.add(float(overlay.get("start_seconds") or 0.0))
        boundaries.add(float(overlay.get("end_seconds") or 0.0))
    points = sorted(boundaries)
    field = f"{lane}_gain_db"
    materialized: list[dict[str, Any]] = []
    for start, end in zip(points, points[1:]):
        if end <= start:
            continue
        midpoint = start + (end - start) / 2.0
        baseline = next((row for row in baselines if float(row.get("start_seconds") or 0.0) <= midpoint < float(row.get("end_seconds") or 0.0)), None)
        if baseline is None:
            continue
        active = [row for row in overlays if float(row.get("start_seconds") or 0.0) <= midpoint < float(row.get("end_seconds") or 0.0)]
        gain = float(baseline.get("gain_db") or 0.0) + sum(float(row.get("gain_delta_db") or 0.0) for row in active)
        ramp_in = float(baseline.get("ramp_in_seconds") or 0.0) if abs(start - float(baseline.get("start_seconds") or 0.0)) <= 0.001 else 0.0
        ramp_out = float(baseline.get("ramp_out_seconds") or 0.0) if abs(end - float(baseline.get("end_seconds") or 0.0)) <= 0.001 else 0.0
        for overlay in active:
            if abs(start - float(overlay.get("start_seconds") or 0.0)) <= 0.001:
                ramp_in = max(ramp_in, float(overlay.get("ramp_in_seconds") or 0.0))
            if abs(end - float(overlay.get("end_seconds") or 0.0)) <= 0.001:
                ramp_out = max(ramp_out, float(overlay.get("ramp_out_seconds") or 0.0))
        overlay_ids = [str(row.get("id") or "?") for row in active]
        materialized.append(
            {
                "id": f"{lane}-m{len(materialized) + 1:04d}",
                "confirmed_segment_id": baseline.get("id"),
                "analysis_regime_ids": list(baseline.get("analysis_regime_ids") or []),
                "regime_id": baseline.get("id"),
                "overlay_ids": overlay_ids,
                "start_seconds": rounded(start, 6),
                "end_seconds": rounded(end, 6),
                field: rounded(gain, 6),
                "ramp_in_seconds": rounded(ramp_in, 6),
                "ramp_out_seconds": rounded(ramp_out, 6),
                "judgment": baseline.get("judgment"),
                "evidence_paths": list(baseline.get("evidence_paths") or []),
            }
        )
    return materialized


def confirmed_mic_transition_boundaries(plan: dict[str, Any], analysis: dict[str, Any]) -> list[dict[str, Any]]:
    if not _is_v2(plan):
        return list(analysis.get("step_candidates", []))
    confirmed: list[dict[str, Any]] = []
    for step in analysis.get("step_candidates", []):
        boundary = float(step["boundary_seconds"])
        if any(abs(float(seg.get("start_seconds") or -999.0) - boundary) <= 0.25 or abs(float(seg.get("end_seconds") or -999.0) - boundary) <= 0.25 for seg in plan.get("mic_segments", [])):
            confirmed.append(step)
    return confirmed


def _finite_rows(plan: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    checks: list[tuple[str, str, Any, tuple[float, float]]] = []
    for lane_key in ("mic_segments", "bed_segments"):
        for seg in plan.get(lane_key, []):
            seg_id = str(seg.get("id", "?"))
            for field in ("start_seconds", "end_seconds", "ramp_in_seconds", "ramp_out_seconds"):
                if seg.get(field) is not None:
                    checks.append((f"{lane_key}[{seg_id}]", field, seg.get(field), _SEGMENT_NUMERIC_BOUNDS[field]))
            if seg.get("gain_db") is not None:
                checks.append((f"{lane_key}[{seg_id}]", "gain_db", seg.get("gain_db"), (-120.0, 60.0)))
    for overlay in plan.get("event_overlays", []):
        overlay_id = str(overlay.get("id", "?"))
        for field in ("start_seconds", "end_seconds", "ramp_in_seconds", "ramp_out_seconds"):
            if overlay.get(field) is not None:
                checks.append((f"event_overlays[{overlay_id}]", field, overlay.get(field), _SEGMENT_NUMERIC_BOUNDS[field]))
        if overlay.get("gain_delta_db") is not None:
            checks.append((f"event_overlays[{overlay_id}]", "gain_delta_db", overlay.get("gain_delta_db"), (-60.0, 60.0)))
    adjustment = plan.get("rails", {}).get("rails_adjustment") or {}
    for field in ("mic_band_center_shift_db", "gap_band_shift_db"):
        if adjustment.get(field) is not None:
            # Finiteness only; range enforcement belongs to validate_adjustment.
            checks.append(("rails.rails_adjustment", field, adjustment.get(field), (-1e6, 1e6)))
    for where, field, value, (low, high) in checks:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            numeric = math.nan
        if not math.isfinite(numeric) or numeric < low or numeric > high:
            rows.append(_fail("non_finite_plan_value", f"{where}.{field} = {value!r} is not a finite number inside {low}..{high}", f"set {where}.{field} to a finite value inside {low}..{high}, then rerun plan-validate"))
    return rows


def _role_rows(plan: dict[str, Any], analysis: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    roles = plan.get("roles", {})
    mic_streams = [int(x) for x in roles.get("mic_streams", [])]
    bed_streams = [int(x) for x in roles.get("bed_streams", [])]
    analysis_roles = analysis.get("confirmed_roles") or analysis.get("analysis_roles") or analysis.get("inferred_roles", {})
    analysis_mic = sorted(int(x) for x in analysis_roles.get("mic_streams", []))
    analysis_bed = sorted(int(x) for x in analysis_roles.get("bed_streams", []))
    if analysis_roles and (sorted(mic_streams) != analysis_mic or sorted(bed_streams) != analysis_bed):
        rows.append(
            _fail(
                "plan_roles_mismatch_analysis",
                f"plan mic/bed roles {sorted(mic_streams)}/{sorted(bed_streams)} differ from analysis roles {analysis_mic}/{analysis_bed}",
                "rerun analyze with --mic-streams/--bed-streams and re-init the plan",
            )
        )
    override = roles.get("role_override")
    override_validation = _validate_role_override(override, analysis)
    rows.extend(override_validation)
    profiles = {int(row["audio_stream_index"]): row for row in analysis.get("lane_profiles", [])}
    if not mic_streams:
        rows.append(_fail("missing_mic_role", "plan roles.mic_streams is empty", "rerun analyze with confirmed --mic-streams and --bed-streams, then rerun plan-init and plan-validate"))
        return rows
    if analysis.get("role_confirmation") == "caller/agent-confirmed" and not override_validation:
        return rows
    for candidate in analysis.get("cross_lane_correlation", {}).get("existing_mix_candidates", []):
        idx = int(candidate.get("audio_stream_index", -1))
        if idx in mic_streams and candidate.get("existing_mix_signature"):
            rows.append(_fail("mic_role_has_mix_signature", f"selected mic lane {idx} correlates like a fitted mix", "rerun analyze with confirmed mic and bed selectors, then rerun plan-init"))
    selected_shape = max(float(profiles.get(idx, {}).get("speech_shape_ratio") or 0.0) for idx in mic_streams)
    for idx, profile in profiles.items():
        if idx not in mic_streams and idx not in bed_streams:
            continue
        shape = float(profile.get("speech_shape_ratio") or 0.0)
        if idx not in mic_streams and shape > selected_shape + 0.05:
            rows.append(_fail("unselected_lane_more_speech_shaped", f"lane {idx} speech_shape_ratio {shape} exceeds selected mic {selected_shape}", "rerun analyze with confirmed mic and bed selectors, then rerun plan-init"))
    return rows


def _validate_role_override(override: Any, analysis: dict[str, Any]) -> list[dict[str, Any]]:
    del analysis
    if override is None:
        return []
    return [_fail("role_override_unsupported", "plan-level role overrides are disabled because they cannot replace source-derived role confirmation", "rerun analyze with both --mic-streams and --bed-streams, then rerun plan-init")]


def _v2_coverage_rows(plan: dict[str, Any], analysis: dict[str, Any], duration: float) -> list[dict[str, Any]]:
    rows = _lane_coverage_rows("mic", plan.get("mic_segments", []), duration)
    bed_required = bool(plan.get("roles", {}).get("bed_streams", []))
    if bed_required or plan.get("bed_segments"):
        rows.extend(_lane_coverage_rows("bed", plan.get("bed_segments", []), duration))
    return rows


def _lane_coverage_rows(lane: str, segments: Any, duration: float) -> list[dict[str, Any]]:
    if not isinstance(segments, list) or not segments:
        return [_fail("missing_segments", f"schema-v2 {lane}_segments has no baseline coverage", f"add continuous {lane}_segments coverage and rerun plan-validate")]
    rows: list[dict[str, Any]] = []
    ordered = sorted(segments, key=lambda row: float(row.get("start_seconds") or -1.0))
    cursor = 0.0
    for seg in ordered:
        start = float(seg.get("start_seconds") or 0.0)
        end = float(seg.get("end_seconds") or 0.0)
        if start > cursor + 0.001:
            rows.append(_fail("coverage_gap", f"{lane} baseline gap {cursor:.3f}..{start:.3f}", f"make {lane}_segments continuous, then rerun plan-validate"))
        if start < cursor - 0.001:
            rows.append(_fail("coverage_overlap", f"{lane} baseline overlap at {start:.3f}; previous end {cursor:.3f}", f"remove overlap from {lane}_segments, then rerun plan-validate"))
        if end <= start:
            rows.append(_fail("invalid_segment_duration", f"{lane} segment {seg.get('id')} end <= start", "set end_seconds greater than start_seconds"))
        cursor = max(cursor, end)
    if duration and cursor < duration - 0.25:
        rows.append(_fail("coverage_gap", f"{lane} baseline tail gap {cursor:.3f}..{duration:.3f}", f"extend final {lane} baseline to analysis duration"))
    if duration and cursor > duration + 0.25:
        rows.append(_fail("coverage_overlap", f"{lane} baseline extends beyond duration to {cursor:.3f}; duration {duration:.3f}", f"trim final {lane} baseline to analysis duration"))
    return rows


def _v2_step_rows(plan: dict[str, Any], analysis: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    segments = plan.get("mic_segments", [])
    for step in analysis.get("step_candidates", []):
        boundary = float(step["boundary_seconds"])
        has_boundary = any(abs(float(seg.get("start_seconds") or -999.0) - boundary) <= 0.25 or abs(float(seg.get("end_seconds") or -999.0) - boundary) <= 0.25 for seg in segments)
        spanning = next((seg for seg in segments if float(seg.get("start_seconds") or 0.0) + 0.25 < boundary < float(seg.get("end_seconds") or 0.0) - 0.25), None)
        if has_boundary:
            continue
        if spanning is not None:
            rows.append(_fail("segment_spans_detected_step", f"mic segment {spanning.get('id')} spans analysis step {boundary:.3f}s", "split the mic baseline at the detected step, then rerun plan-validate"))
        else:
            rows.append(_fail("missing_step_boundary", f"analysis step {boundary:.3f}s has no mic baseline boundary", "align a mic baseline boundary to the detected step, then rerun plan-validate"))
    return rows


def _v2_bed_step_rows(plan: dict[str, Any], analysis: dict[str, Any]) -> list[dict[str, Any]]:
    if not plan.get("roles", {}).get("bed_streams"):
        return []
    segments = plan.get("bed_segments", [])
    rows: list[dict[str, Any]] = []
    for step in analysis.get("bed_step_candidates", []):
        boundary = float(step["boundary_seconds"])
        if any(
            abs(float(seg.get("start_seconds") or -999.0) - boundary) <= 0.25
            or abs(float(seg.get("end_seconds") or -999.0) - boundary) <= 0.25
            for seg in segments
        ):
            continue
        rows.append(
            _fail(
                "bed_segment_spans_detected_step",
                f"bed baseline has no boundary at independent bed step {boundary:.3f}s",
                "split bed_segments at the detected bed step, then rerun plan-validate",
            )
        )
    return rows


def _v2_event_rows(plan: dict[str, Any], analysis: dict[str, Any]) -> list[dict[str, Any]]:
    config = load_default_rails()["plan_structure"]
    events = plan.get("event_overlays", [])
    if not isinstance(events, list):
        return [_fail("invalid_event_overlays", "event_overlays must be a list", "replace event_overlays with a list and rerun plan-validate")]
    rows: list[dict[str, Any]] = []
    by_owner: dict[tuple[str, str], list[dict[str, Any]]] = {}
    normalized_reasons: dict[str, list[str]] = {}
    for event in events:
        event_id = str(event.get("id") or "?")
        lane = str(event.get("lane") or "")
        if lane not in {"mic", "bed"}:
            rows.append(_fail("invalid_event_overlay", f"event {event_id} lane {lane!r} is not mic or bed", "set event lane to mic or bed"))
            continue
        start = float(event.get("start_seconds") or 0.0)
        end = float(event.get("end_seconds") or 0.0)
        if end <= start:
            rows.append(_fail("invalid_segment_duration", f"event {event_id} end <= start", "set event end_seconds greater than start_seconds"))
            continue
        baselines = plan.get(f"{lane}_segments", [])
        owners = [seg for seg in baselines if start >= float(seg.get("start_seconds") or 0.0) - 0.001 and end <= float(seg.get("end_seconds") or 0.0) + 0.001]
        if len(owners) != 1:
            rows.append(_fail("event_overlay_crosses_baseline", f"event {event_id} is not wholly owned by exactly one {lane} baseline", "split or move the event so it stays inside one baseline"))
            continue
        owner = owners[0]
        by_owner.setdefault((lane, str(owner.get("id") or "?")), []).append(event)
        reason = str(event.get("event_reason") or "").strip()
        if not reason:
            rows.append(_fail("event_overlay_missing_evidence", f"event {event_id} lacks event_reason", "add a distinct reason and event_citation"))
        else:
            normalized_reasons.setdefault(" ".join(reason.lower().split()), []).append(event_id)
        bounds, error = _resolve_event_citation(event.get("event_citation"), analysis)
        if error:
            rows.append(_fail("event_overlay_missing_evidence", f"event {event_id} citation {error}", "cite an analysis event or a same-lineage promotion row"))
        elif bounds is not None:
            neighborhood = float(config["event_neighborhood_seconds"])
            if start < bounds[0] - neighborhood - 1e-9 or end > bounds[1] + neighborhood + 1e-9:
                rows.append(_fail("event_overlay_outside_citation", f"event {event_id} {start:.3f}..{end:.3f}s is outside +/-{neighborhood:g}s of cited {bounds[0]:.3f}..{bounds[1]:.3f}s", "move the event or cite the correct source event"))
    repeated = [ids for ids in normalized_reasons.values() if len(ids) > 1]
    if repeated:
        rows.append(_fail("event_overlay_duplicate_reason", f"event overlays repeat non-distinct reasons: {', '.join(item for group in repeated for item in group)}", "give each residual event a distinct source-grounded reason"))
    max_count = int(config["max_event_segments_per_regime"])
    max_fraction = float(config["max_event_duration_fraction_per_regime"])
    for (lane, owner_id), owned in by_owner.items():
        baseline = next(seg for seg in plan[f"{lane}_segments"] if str(seg.get("id") or "?") == owner_id)
        duration = _segment_duration(baseline)
        event_duration = sum(_segment_duration(event) for event in owned)
        if len(owned) > max_count:
            rows.append(_fail("micro_chunked_plan", f"{lane} baseline {owner_id} has {len(owned)} overlays; maximum is {max_count}", "merge repeated event repairs into the baseline"))
        if duration <= 0.0 or event_duration / duration > max_fraction + 1e-12:
            rows.append(_fail("micro_chunked_plan", f"{lane} baseline {owner_id} overlay duration {event_duration:.3f}/{duration:.3f}s exceeds fraction {max_fraction:.4f}", "reduce overlays to bounded residual events"))
        ordered = sorted(owned, key=lambda event: float(event.get("start_seconds") or 0.0))
        for left, right in zip(ordered, ordered[1:]):
            if float(right.get("start_seconds") or 0.0) < float(left.get("end_seconds") or 0.0) - 0.001:
                rows.append(_fail("event_overlay_overlap", f"{lane} overlays {left.get('id')} and {right.get('id')} overlap", "merge or separate overlapping overlays"))
    total_duration = float(analysis.get("duration_seconds") or 0.0)
    total_event = sum(_segment_duration(event) for event in events if isinstance(event, dict))
    if total_duration > 0.0 and total_event / total_duration > float(config["max_event_duration_fraction_total"]) + 1e-12:
        rows.append(_fail("micro_chunked_plan", f"plan overlay duration {total_event:.3f}/{total_duration:.3f}s exceeds total fraction {float(config['max_event_duration_fraction_total']):.4f}", "reduce overlays to bounded residual events"))
    return rows


def _v2_gain_rows(plan: dict[str, Any], analysis: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    defaults = load_default_rails()
    default_ceiling = clean_gain_default_ceiling(defaults)
    regimes = {str(regime.get("id")): regime for regime in analysis.get("regimes", [])}
    for lane in ("mic", "bed"):
        segments = sorted(plan.get(f"{lane}_segments", []), key=lambda row: float(row.get("start_seconds") or 0.0))
        for seg in segments:
            if seg.get("gain_db") is None:
                rows.append(_fail("todo_gain", f"{lane} segment {seg.get('id')} gain_db is null", f"set {lane}_segments {seg.get('id')} gain_db"))
                continue
            if not seg.get("judgment"):
                rows.append(_fail("missing_judgment", f"{lane} segment {seg.get('id')} judgment is null", "record lift, trim, hold, or local-support"))
            elif seg.get("judgment") not in _ALLOWED_JUDGMENTS:
                rows.append(_fail("invalid_judgment", f"{lane} segment {seg.get('id')} judgment {seg.get('judgment')!r} is invalid", f"use one of {sorted(_ALLOWED_JUDGMENTS)}"))
            gain = float(seg.get("gain_db") or 0.0)
            if lane == "mic" and gain > default_ceiling:
                if "source_limit" in seg:
                    rows.append(_fail("unsupported_source_limit", f"mic segment {seg.get('id')} contains obsolete source_limit authoring", "remove source_limit; diagnostic audition evidence cannot waive a failing gate"))
                refs = _segment_evidence_refs(seg)
                for regime_id in seg.get("analysis_regime_ids", []):
                    regime = regimes.get(str(regime_id), {})
                    if not has_regime_clean_gain_headroom_evidence(analysis, regime_id, refs):
                        rows.append(_fail("mic_gain_ceiling_needs_evidence", f"mic segment {seg.get('id')} gain {gain} dB exceeds default {default_ceiling} dB without {regime_id} headroom evidence", "cite every crossed regime clean_gain_headroom or lower the gain"))
                    elif gain > clean_gain_allowed_ceiling(regime, defaults):
                        rows.append(_fail("mic_gain_ceiling_exceeded", f"mic segment {seg.get('id')} gain {gain} dB exceeds clean ceiling for {regime_id}", "lower gain, make the bed yield, or choose a bounded lower shared target"))
        for prev, cur in zip(segments, segments[1:]):
            if prev.get("gain_db") is None or cur.get("gain_db") is None:
                continue
            jump = abs(float(cur["gain_db"]) - float(prev["gain_db"]))
            if jump > 12.0 and not (float(prev.get("ramp_out_seconds") or 0.0) > 0.0 or float(cur.get("ramp_in_seconds") or 0.0) > 0.0):
                rows.append(_fail("unramped_gain_step", f"{lane} {prev.get('id')}->{cur.get('id')} gain jump {jump:.2f} dB", "add a ramp at the confirmed boundary"))
    for lane in ("mic", "bed"):
        field = f"{lane}_gain_db"
        for segment in materialize_lane_segments(plan, lane, analysis):
            gain = float(segment.get(field) or 0.0)
            if gain < -120.0 or gain > 60.0:
                rows.append(_fail("non_finite_plan_value", f"materialized {lane} gain {gain} dB is outside -120..60", "reduce baseline or overlay gain"))
    return rows


def _coverage_rows(plan: dict[str, Any], analysis: dict[str, Any], duration: float) -> list[dict[str, Any]]:
    segments = sorted(plan.get("segments", []), key=lambda row: float(row.get("start_seconds") or -1.0))
    rows: list[dict[str, Any]] = []
    if not segments:
        return [_fail("missing_segments", "plan has no segments", "rerun plan-init or add full-duration segments to render_plan.json")]
    cursor = 0.0
    for seg in segments:
        start = float(seg.get("start_seconds") or 0.0)
        end = float(seg.get("end_seconds") or 0.0)
        if start > cursor + 0.001:
            rows.append(_fail("coverage_gap", f"gap {cursor:.3f}..{start:.3f}", "edit render_plan.json segments so coverage is continuous, then rerun plan-validate"))
        if start < cursor - 0.001:
            rows.append(_fail("coverage_overlap", f"overlap at {start:.3f}; previous end {cursor:.3f}", "edit render_plan.json to remove overlapping segments, then rerun plan-validate"))
        if end <= start:
            rows.append(_fail("invalid_segment_duration", f"{seg.get('id')} end <= start", "set each segment end_seconds greater than start_seconds"))
        cursor = max(cursor, end)
    if duration and cursor < duration - 0.25:
        rows.append(_fail("coverage_gap", f"tail gap {cursor:.3f}..{duration:.3f}", "extend the final segment to the analysis duration and rerun plan-validate"))
    return rows


def _micro_chunk_rows(plan: dict[str, Any], analysis: dict[str, Any]) -> list[dict[str, Any]]:
    if not analysis.get("regimes"):
        return []
    config = load_default_rails()["plan_structure"]
    minimum_seconds = float(config["minimum_non_exception_segment_seconds"])
    max_per_regime = int(config["max_non_exception_segments_per_regime"])
    max_events_per_regime = int(config["max_event_segments_per_regime"])
    max_event_fraction_per_regime = float(config["max_event_duration_fraction_per_regime"])
    max_events_per_plan_per_regime = int(config["max_event_segments_per_plan_per_regime"])
    max_event_fraction_total = float(config["max_event_duration_fraction_total"])
    event_neighborhood = float(config["event_neighborhood_seconds"])
    exempt_roles = {str(role) for role in config["event_exempt_roles"]}
    segments = plan.get("segments", [])
    rows: list[dict[str, Any]] = []
    regimes = {str(regime.get("id")): regime for regime in analysis.get("regimes", [])}
    ordinary_by_regime: dict[str, list[dict[str, Any]]] = {regime_id: [] for regime_id in regimes}
    events_by_regime: dict[str, list[dict[str, Any]]] = {regime_id: [] for regime_id in regimes}
    ownership_failures: list[str] = []
    for seg in segments:
        regime_id = str(seg.get("regime_id") or "")
        regime = regimes.get(regime_id)
        if regime is None or not _segment_owned_by_regime(seg, regime):
            ownership_failures.append(str(seg.get("id") or "?"))
            continue
        destination = events_by_regime if str(seg.get("role") or "") in exempt_roles else ordinary_by_regime
        destination[regime_id].append(seg)
    if ownership_failures:
        rows.append(_fail("micro_chunked_plan", f"segments lack valid per-regime time ownership: {', '.join(ownership_failures[:8])}", "set each segment regime_id and keep its full time span inside that analysis regime, then rerun plan-validate"))

    for regime_id, ordinary in ordinary_by_regime.items():
        if len(ordinary) > max_per_regime:
            rows.append(_fail("micro_chunked_plan", f"{regime_id} has {len(ordinary)} ordinary segments; maximum is {max_per_regime} per regime", "move the mic/bed repair into the regime baseline and merge ordinary slices, then rerun plan-validate"))
        short = [seg for seg in ordinary if _segment_duration(seg) < minimum_seconds]
        if short:
            labels = ", ".join(str(seg.get("id") or "?") for seg in short[:8])
            rows.append(_fail("micro_chunked_plan", f"{regime_id} ordinary segments shorter than {minimum_seconds:g}s: {labels}", "merge micro-chunks into the regime baseline; reserve bounded exceptions for cited residual events"))

    all_events = [seg for owned in events_by_regime.values() for seg in owned]
    for regime_id, events in events_by_regime.items():
        regime = regimes[regime_id]
        regime_duration = _regime_duration(regime)
        event_duration = sum(_segment_duration(seg) for seg in events)
        if len(events) > max_events_per_regime:
            rows.append(_fail("micro_chunked_plan", f"{regime_id} has {len(events)} event segments; maximum is {max_events_per_regime}", "move repeated repair into the per-regime mic/bed baseline and keep only residual cited events"))
        fraction = event_duration / regime_duration if regime_duration > 0.0 else math.inf
        if fraction > max_event_fraction_per_regime + 1e-12:
            rows.append(_fail("micro_chunked_plan", f"{regime_id} event duration {event_duration:.3f}/{regime_duration:.3f}s = {fraction:.4f}; maximum is {max_event_fraction_per_regime:.4f}", "move sustained repair into the per-regime baseline and reduce exceptions to residual event windows"))

    regime_count = len(regimes)
    plan_count_limit = regime_count * max_events_per_plan_per_regime
    total_duration = float(analysis.get("duration_seconds") or sum(_regime_duration(regime) for regime in regimes.values()))
    total_event_duration = sum(_segment_duration(seg) for seg in all_events)
    total_event_fraction = total_event_duration / total_duration if total_duration > 0.0 else math.inf
    if len(all_events) > plan_count_limit:
        rows.append(_fail("micro_chunked_plan", f"plan has {len(all_events)} event segments; maximum is {regime_count} regimes x {max_events_per_plan_per_regime} = {plan_count_limit}", "move repeated repair into per-regime baselines and retain only residual cited events"))
    if total_event_fraction > max_event_fraction_total + 1e-12:
        rows.append(_fail("micro_chunked_plan", f"plan event duration {total_event_duration:.3f}/{total_duration:.3f}s = {total_event_fraction:.4f}; maximum is {max_event_fraction_total:.4f}", "move sustained repair into per-regime baselines and reduce whole-plan exception duration"))

    normalized_reasons: dict[str, list[str]] = {}
    for seg in all_events:
        reason = str(seg.get("event_reason") or "").strip()
        if not reason:
            rows.append(_fail("micro_chunked_plan", f"exception/transition segment {seg.get('id') or '?'} lacks event_reason", "add a specific event_reason plus event_citation, or merge it into the regime baseline"))
        else:
            normalized_reasons.setdefault(" ".join(reason.lower().split()), []).append(str(seg.get("id") or "?"))
        citation = seg.get("event_citation")
        event_bounds, error = _resolve_event_citation(citation, analysis)
        if error:
            rows.append(_fail("micro_chunked_plan", f"{seg.get('id') or '?'} event_citation {error}", "cite a structured analysis event or prior passing promotion-manifest row with a resolvable event time"))
        elif event_bounds is not None:
            start, end = float(seg.get("start_seconds") or 0.0), float(seg.get("end_seconds") or 0.0)
            event_start, event_end = event_bounds
            if start < event_start - event_neighborhood - 1e-9 or end > event_end + event_neighborhood + 1e-9:
                rows.append(_fail("micro_chunked_plan", f"{seg.get('id') or '?'} at {start:.3f}..{end:.3f}s is farther than +/-{event_neighborhood:g}s from cited event {event_start:.3f}..{event_end:.3f}s", "move the exception to the cited event neighborhood or cite the correct event"))
    repeated = [labels for labels in normalized_reasons.values() if len(labels) > 1]
    if repeated:
        labels = ", ".join(label for group in repeated for label in group[:4])
        rows.append(_fail("micro_chunked_plan", f"event segments repeat generic/non-specific event_reason text: {labels}", "give each residual event a distinct source-grounded reason or merge repeated repairs into the regime baseline"))
    return rows


def _segment_duration(seg: dict[str, Any]) -> float:
    return max(0.0, float(seg.get("end_seconds") or 0.0) - float(seg.get("start_seconds") or 0.0))


def _regime_duration(regime: dict[str, Any]) -> float:
    explicit = regime.get("duration_seconds")
    if explicit is not None:
        return max(0.0, float(explicit))
    return max(0.0, float(regime.get("end_seconds") or 0.0) - float(regime.get("start_seconds") or 0.0))


def _segment_owned_by_regime(seg: dict[str, Any], regime: dict[str, Any]) -> bool:
    if regime.get("start_seconds") is None or regime.get("end_seconds") is None:
        return False
    start = float(seg.get("start_seconds") or 0.0)
    end = float(seg.get("end_seconds") or 0.0)
    return start >= float(regime["start_seconds"]) - 0.001 and end <= float(regime["end_seconds"]) + 0.001


def _resolve_event_citation(citation: Any, analysis: dict[str, Any]) -> tuple[tuple[float, float] | None, str | None]:
    if not isinstance(citation, dict):
        return None, "must be an object with source and ref"
    source = citation.get("source")
    ref = citation.get("ref")
    if not isinstance(ref, str) or not ref:
        return None, "lacks a non-empty ref"
    try:
        if source == "analysis":
            if not (ref.startswith("/step_candidates/") or ref.startswith("step_candidates[") or ref.startswith("/speech_windows/") or ref.startswith("speech_windows[")):
                return None, "must resolve to analysis step_candidates or speech_windows"
            event = _resolve_analysis_ref(analysis, ref)
        elif source == "promotion_manifest":
            manifest_path = citation.get("path")
            if not manifest_path or not Path(str(manifest_path)).is_file():
                return None, "prior promotion manifest path is missing"
            prior = read_json(str(manifest_path))
            if prior.get("source_sha256") != analysis.get("source_sha256"):
                return None, "promotion manifest source lineage differs from current analysis"
            if prior.get("analysis_sha256") != sha256_json(analysis):
                return None, "promotion manifest analysis lineage differs from current analysis"
            if not (ref.startswith("/rows/") or ref.startswith("rows[")):
                return None, "must resolve to a prior promotion manifest row"
            event = _resolve_analysis_ref(prior, ref)
        else:
            return None, "source must be analysis or promotion_manifest"
    except (KeyError, IndexError, TypeError, ValueError, RvError):
        return None, "does not resolve"
    bounds = _event_bounds(event)
    return (bounds, None) if bounds is not None else (None, "resolved value lacks structured event time")


def _event_bounds(event: Any) -> tuple[float, float] | None:
    if not isinstance(event, dict):
        return None
    for field in ("event_seconds", "boundary_seconds", "time_seconds", "peak_time_seconds"):
        if event.get(field) is not None:
            point = float(event[field])
            return point, point
    if event.get("start_seconds") is not None and event.get("end_seconds") is not None:
        return float(event["start_seconds"]), float(event["end_seconds"])
    return None


def _step_rows(plan: dict[str, Any], analysis: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    segments = plan.get("segments", [])
    for step in analysis.get("step_candidates", []):
        boundary = float(step["boundary_seconds"])
        has_boundary = any(abs(float(seg.get("start_seconds") or -999.0) - boundary) <= 0.25 or abs(float(seg.get("end_seconds") or -999.0) - boundary) <= 0.25 for seg in segments)
        if not has_boundary:
            rows.append(_fail("missing_step_boundary", f"analysis step {boundary:.3f}s has no segment boundary", "split render_plan.json at each analysis step"))
        for seg in segments:
            start = float(seg.get("start_seconds") or 0.0)
            end = float(seg.get("end_seconds") or 0.0)
            if start + 0.25 < boundary < end - 0.25:
                rows.append(_fail("segment_spans_detected_step", f"{seg.get('id')} spans analysis step {boundary:.3f}s", "split the segment at the detected step"))
    return rows


def _gain_rows(plan: dict[str, Any], analysis: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    defaults = load_default_rails()
    ceiling = clean_gain_default_ceiling(defaults)
    regimes = {regime.get("id"): regime for regime in analysis.get("regimes", [])}
    segments = sorted(plan.get("segments", []), key=lambda row: float(row.get("start_seconds") or 0.0))
    for seg in segments:
        for field in ("mic_gain_db", "bed_gain_db"):
            if seg.get(field) is None:
                rows.append(_fail("todo_gain", f"{seg.get('id')} {field} is null", f"edit render_plan.json {seg.get('id')}.{field}, then rerun plan-validate"))
        if not seg.get("judgment"):
            rows.append(_fail("missing_judgment", f"{seg.get('id')} judgment is null", "record lift, trim, hold, or local-support judgment, then rerun plan-validate"))
        elif seg.get("judgment") not in _ALLOWED_JUDGMENTS:
            rows.append(_fail("invalid_judgment", f"{seg.get('id')} judgment {seg.get('judgment')!r} is not one of {sorted(_ALLOWED_JUDGMENTS)}", "record lift, trim, hold, or local-support judgment, then rerun plan-validate"))
        mic_gain = seg.get("mic_gain_db")
        if mic_gain is not None:
            gain = float(mic_gain)
            if gain > ceiling:
                evidence_refs = _segment_evidence_refs(seg)
                regime = regimes.get(seg.get("regime_id"), {})
                has_headroom_evidence = has_regime_clean_gain_headroom_evidence(analysis, seg.get("regime_id"), evidence_refs)
                if not has_headroom_evidence:
                    rows.append(_fail("mic_gain_ceiling_needs_evidence", f"{seg.get('id')} mic gain {gain} dB exceeds default {ceiling} dB without a citation to {seg.get('regime_id')} clean_gain_headroom", "cite this regime's analysis clean_gain_headroom in segment evidence_paths or lower the gain"))
                else:
                    allowed = clean_gain_allowed_ceiling(regime, defaults)
                    if gain > allowed:
                        rows.append(_fail("mic_gain_ceiling_exceeded", f"{seg.get('id')} mic gain {gain} dB exceeds evidence-backed clean ceiling {allowed:.3f} dB for {seg.get('regime_id')}", "lower mic gain to the regime clean headroom ceiling, make the bed yield, or choose a bounded lower shared target"))
    for prev, cur in zip(segments, segments[1:]):
        if prev.get("mic_gain_db") is None or cur.get("mic_gain_db") is None:
            continue
        jump = abs(float(cur["mic_gain_db"]) - float(prev["mic_gain_db"]))
        if jump > 12.0 and not (float(prev.get("ramp_out_seconds") or 0.0) > 0.0 or float(cur.get("ramp_in_seconds") or 0.0) > 0.0):
            rows.append(_fail("unramped_gain_step", f"{prev.get('id')}->{cur.get('id')} mic gain jump {jump:.2f} dB", "add ramp_out_seconds or ramp_in_seconds at the boundary, then rerun plan-validate"))
    return rows


def _segment_evidence_refs(seg: dict[str, Any]) -> list[Any]:
    refs: list[Any] = []
    evidence_paths = seg.get("evidence_paths")
    if isinstance(evidence_paths, list):
        refs.extend(evidence_paths)
    return refs


def _boundary_override_rows(plan: dict[str, Any], analysis: dict[str, Any]) -> list[dict[str, Any]]:
    del analysis
    if plan.get("boundary_overrides"):
        return [_fail("boundary_override_unsupported", "boundary overrides are disabled because arbitrary evidence could erase a real capture transition", "keep the detected mic/bed boundary or rerun analyze with bounded parameters")]
    return []


def materialized_overrides_and_adjustments(plan: dict[str, Any]) -> dict[str, Any]:
    roles = plan.get("roles", {})
    role_override = roles.get("role_override")
    boundary_overrides = plan.get("boundary_overrides", [])
    rails_adjustment = plan.get("rails", {}).get("rails_adjustment")
    return {
        "role_override": _materialize_role_override(role_override),
        "boundary_overrides": [_materialize_boundary_override(row) for row in boundary_overrides],
        "rails_adjustment": rails_adjustment,
    }


def _materialize_role_override(override: Any) -> Any:
    if not isinstance(override, dict):
        return override
    materialized = dict(override)
    evidence = override.get("isolated_sample_manifests")
    if isinstance(evidence, list):
        materialized["isolated_sample_files"] = _file_evidence(evidence)
    return materialized


def _materialize_boundary_override(override: Any) -> Any:
    if not isinstance(override, dict):
        return override
    materialized = dict(override)
    evidence = override.get("evidence_paths")
    if isinstance(evidence, list):
        materialized["evidence_files"] = _file_evidence(evidence)
    return materialized


def _file_evidence(paths: list[Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw in paths:
        path = Path(str(raw)).expanduser()
        resolved = path.resolve(strict=False)
        row: dict[str, Any] = {"path": str(raw), "resolved_path": str(resolved), "exists": path.is_file()}
        if path.is_file():
            row["sha256"] = sha256_file(path)
        rows.append(row)
    return rows


def _existing_file(path: Any) -> bool:
    return Path(str(path)).expanduser().is_file()


def _role_sample_next_action() -> str:
    return "render isolated samples, for example: ffmpeg -hide_banner -nostdin -y -i <source> -map 0:a:<stream> -t 20 -c:a pcm_s16le <scratch>/isolated-stream-<stream>.wav, then cite those files"


def _fail(failure_class: str, measurement: str, next_action: str) -> dict[str, Any]:
    return {"type": "plan_validation", "measurement": measurement, "target": "DESIGN.md render-plan contract", "status": "fail", "failure_class": failure_class, "next_action": next_action}


def _pass(row_type: str, measurement: str, target: str) -> dict[str, Any]:
    return {"type": row_type, "measurement": measurement, "target": target, "status": "pass", "failure_class": None, "next_action": "none"}
