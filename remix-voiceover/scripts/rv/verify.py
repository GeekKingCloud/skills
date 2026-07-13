from __future__ import annotations

import argparse
import csv
import math
import os
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import Any, Callable

from . import plan as plan_contract
from .audio import ffmpeg_mix_components, ffmpeg_peak_control, ffmpeg_render_filter, power_curve_100ms, sample_count, streamed_component_stats
from .ffio import ebur128_curve, ffprobe_json
from .plan import materialized_overrides_and_adjustments, validate_plan
from .probe import _streams
from .rails import adjusted_rails, load_default_rails
from .util import RvError, db_to_power, power_mean_lufs, power_to_db, read_json, refuse_output_alias, rounded, sha256_file, sha256_json, utc_now, weighted_median, write_json


def verify_command(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest)
    plan_path = Path(args.plan)
    analysis_path = Path(args.analysis)
    refuse_output_alias(args.json_out, [manifest_path, plan_path, analysis_path], ["choose a promotion output distinct from render manifest, plan, and analysis"], label="promotion JSON output")
    manifest = read_json(manifest_path)
    plan = read_json(plan_path)
    analysis = read_json(analysis_path)
    protected_media: list[str | Path] = []
    for value in (analysis.get("media_path"), manifest.get("source_path")):
        if value:
            protected_media.append(value)
    for component in manifest.get("components", {}).values():
        if isinstance(component, dict) and component.get("path"):
            protected_media.append(component["path"])
    refuse_output_alias(args.json_out, protected_media, ["choose a promotion output distinct from source and candidate components"], label="promotion JSON output")
    rows = verify_candidate(manifest, plan, analysis, manifest_path)
    rows = _with_action_scopes(rows)
    blocking = [row for row in rows if row["status"] == "fail"]
    outcome = _classify_outcome(rows, plan)
    payload: dict[str, Any] = {
        "schema_version": 1,
        "generated_by": "rv-verify",
        "generated_at": utc_now(),
        "status": "pass" if not blocking else "fail",
        "overall": {
            "status": "pass" if not blocking else "fail-with-work",
            "pass": not blocking,
            "fail_with_work": bool(blocking),
            "fail_terminal_candidates": [],
        },
        "outcome": outcome,
        "render_manifest_path": str(manifest_path),
        "render_manifest_sha256": sha256_json(manifest),
        "plan_path": str(plan_path),
        "plan_sha256": sha256_json(plan),
        "analysis_path": str(analysis_path),
        "analysis_sha256": sha256_json(analysis),
        "source_sha256": manifest.get("source_sha256"),
        "candidate": manifest.get("components", {}).get("mix", {}),
        "peak_control": _peak_control_summary(plan, manifest, rows),
        "rows": rows,
        "overrides_and_adjustments": {
            **materialized_overrides_and_adjustments(plan),
            "non_default_analyze_parameters": [
                {"name": name, "value": row.get("value"), "default": row.get("default")}
                for name, row in analysis.get("parameters", {}).items()
                if isinstance(row, dict) and row.get("overridden")
            ],
        },
    }
    write_json(args.json_out, payload)
    return 0 if payload["status"] == "pass" else 1


def _with_action_scopes(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    toolkit_failures = {"true_peak_unmeasured"}
    for row in rows:
        if row.get("action_scope") is None:
            if row.get("status") == "pass":
                row["action_scope"] = "none"
            elif row.get("failure_class") in toolkit_failures:
                row["action_scope"] = "toolkit-change"
            else:
                row["action_scope"] = "current-plan"
    return rows


def _classify_outcome(rows: list[dict[str, Any]], plan: dict[str, Any]) -> dict[str, Any]:
    blocking = [row for row in rows if row.get("status") == "fail"]
    if blocking:
        scopes = {str(row.get("action_scope") or "current-plan") for row in blocking}
        if scopes <= {"toolkit-change"}:
            outcome_class, owner = "toolkit-limited", "toolkit"
        elif scopes <= {"external", "caller-action"}:
            outcome_class, owner = "external-blocked", "external" if "external" in scopes else "caller"
        elif all(row.get("failure_class") == "source_terminal" for row in blocking):
            outcome_class, owner = "source-terminal", "source"
        else:
            outcome_class, owner = "tuning-required", "current-plan"
        evidence = [
            {
                "type": row.get("type"),
                "failure_class": row.get("failure_class"),
                "action_scope": row.get("action_scope"),
                "measurement": row.get("measurement"),
            }
            for row in blocking
        ]
        return {
            "class": outcome_class,
            "limitation_owner": owner,
            "evidence": evidence,
            "recommended_fix": str(blocking[0].get("next_action") or "inspect failing verifier rows"),
        }
    targets = plan.get("targets") if isinstance(plan.get("targets"), dict) else {}
    target = targets.get("shared_mic_body_lufs")
    defaults = load_default_rails()
    preferred = defaults["processed_mic_active_speech_lufs"]["preferred"]
    if target is not None and float(target) < float(preferred) - 0.001:
        constraints = targets.get("constraints") if isinstance(targets.get("constraints"), list) else []
        adjustment = plan.get("rails", {}).get("rails_adjustment") if isinstance(plan.get("rails"), dict) else None
        quality_limited = bool(adjustment) and not constraints
        return {
            "class": "target-limited",
            "limitation_owner": "quality-safety" if quality_limited else "source",
            "evidence": [{"shared_mic_body_lufs": float(target), "preferred_mic_body_lufs": float(preferred), "constraining_regimes": constraints, "rails_adjustment": adjustment}],
            "recommended_fix": (
                "NONE - candidate passes at a bounded lower shared target chosen to satisfy quality and peak-control gates"
                if quality_limited
                else "NONE - candidate passes at the highest shared target supported by the weakest regime"
            ),
        }
    return {"class": "pass", "limitation_owner": "NONE", "evidence": [], "recommended_fix": "NONE"}


def verify_candidate(manifest: dict[str, Any], plan: dict[str, Any], analysis: dict[str, Any], manifest_path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    repair = _repair(manifest_path, plan)
    for plan_row in validate_plan(plan, analysis):
        if plan_row.get("status") == "fail":
            rows.append(
                _fail(
                    plan_row.get("failure_class", "plan_validation_failed"),
                    f"verify-side plan validation failed: {plan_row.get('measurement')}",
                    plan_row.get("next_action") or "repair render_plan.json and rerun plan-validate, render, verify",
                    row_type="plan_validation",
                )
            )
    components = manifest.get("components", {})
    mic_path = Path(components.get("mic", {}).get("path", ""))
    bed_path = Path(components.get("bed", {}).get("path", ""))
    mix_path = Path(components.get("mix", {}).get("path", ""))
    peak_control_enabled = (plan.get("render", {}).get("peak_control") or {}).get("enabled") is True
    component_paths = [("mic", mic_path), ("bed", bed_path), ("mix", mix_path)]
    mic_raw_path: Path | None = None
    if peak_control_enabled:
        mic_raw_path = Path(components.get("mic_raw", {}).get("path", ""))
        component_paths.append(("mic_raw", mic_raw_path))
    for label, path in component_paths:
        expected = components.get(label, {}).get("sha256")
        raw_path = components.get(label, {}).get("path")
        actual = sha256_file(path) if raw_path and path.exists() and path.is_file() else None
        rows.append(_row("hash", f"{label} sha256 {actual}", expected, actual is not None and expected is not None and actual == expected, "hash_mismatch", f"rerun render: {'; '.join(repair)}"))
    if manifest.get("plan_sha256") != sha256_json(plan):
        rows.append(_fail("stale_plan_hash", "render manifest plan_sha256 does not match render_plan.json", f"rerun render: {'; '.join(repair)}", row_type="lineage"))
    if manifest.get("analysis_sha256") != sha256_json(analysis):
        rows.append(_fail("stale_analysis_hash", "render manifest analysis_sha256 does not match analysis.json", "rerun plan-init, plan-validate, render, and verify", row_type="lineage"))
    if manifest.get("source_sha256") != analysis.get("source_sha256"):
        rows.append(_fail("stale_source_hash", "render manifest source_sha256 does not match analysis source_sha256", "rerun probe, analyze, plan-init, plan-validate, render, and verify", row_type="lineage"))
    if int(plan.get("schema_version") or 1) >= 2:
        automation = manifest.get("materialized_automation") if isinstance(manifest.get("materialized_automation"), dict) else {}
        for lane in ("mic", "bed"):
            compiled = _materialized_lane_segments(plan, lane, analysis)
            recorded = automation.get(lane) if isinstance(automation.get(lane), dict) else {}
            expected_hash = sha256_json(compiled)
            ok = recorded.get("sha256") == expected_hash and recorded.get("segment_count") == len(compiled)
            rows.append(
                _row(
                    "lineage",
                    f"{lane} materialized automation sha256 {recorded.get('sha256')}; segment count {recorded.get('segment_count')}",
                    f"{expected_hash}; segment count {len(compiled)}",
                    ok,
                    "stale_materialized_automation",
                    "rerun render and verify with the current plan compiler",
                )
            )
    if any(row["status"] == "fail" for row in rows if row["type"] in {"hash", "lineage"}):
        return rows
    rows.extend(_derived_component_rows(manifest, plan, analysis, mic_path, bed_path, mic_raw_path, repair))
    if any(row["status"] == "fail" for row in rows if row["type"] == "component_derivation"):
        return rows
    counts = {label: sample_count(path) for label, path in component_paths}
    max_delta = max(abs(counts["mic"] - counts["bed"]), abs(counts["mix"] - counts["mic"]), abs(counts.get("mic_raw", counts["mic"]) - counts["mic"]))
    rows.append(_row("length", f"sample counts {counts}", "component lengths equal within +/-1 sample", max_delta <= 1, "component_length_mismatch", "rerun render after confirming pad/trim duration"))
    stats = streamed_component_stats(mic_path, bed_path, mix_path, repair)
    null_peak = float(stats["null_peak"])
    epsilon = float(load_default_rails()["null_test"]["epsilon_peak"])
    rows.append(_row("null_test", f"peak residual {null_peak:.9f}", f"<= {epsilon}", null_peak <= epsilon, "null_test_failed", "rerun render; mix must be amix normalize=0 from current components"))
    rails_defaults = load_default_rails()
    sample_peak_limit = float(rails_defaults["true_peak_dbtp"]["max"])
    for label, peak in stats["peaks"].items():
        peak_db = 20.0 * math.log10(peak) if peak > 0 else -120.0
        peak_time = float(stats.get("peak_times_seconds", {}).get(label, 0.0))
        rows.append(_row("sample_peak", f"{label} sample peak {peak_db:.3f} dBFS at {peak_time:.3f}s", f"secondary sample peak <= {sample_peak_limit} dBFS", peak_db <= sample_peak_limit, "sample_peak_exceeded", _peak_next_action(plan, label, peak_time, "sample")))

    curve_dir = manifest_path.parent / f"{manifest_path.stem}_verify_curves"
    mic_curve = ebur128_curve(mic_path, 0, 2, curve_dir / "mic_component_momentary.csv", repair)["rows"]
    bed_curve = ebur128_curve(bed_path, 0, 2, curve_dir / "bed_component_momentary.csv", repair)["rows"]
    mix_curve = ebur128_curve(mix_path, 0, 2, curve_dir / "mix_momentary.csv", repair)["rows"]
    if peak_control_enabled and mic_raw_path is not None:
        mic_raw_curve = ebur128_curve(mic_raw_path, 0, 2, curve_dir / "mic_component_raw_momentary.csv", repair)["rows"]
        raw_power = power_curve_100ms(mic_raw_path, repair)
        post_power = power_curve_100ms(mic_path, repair)
        rows.extend(_peak_control_rows(analysis, mic_raw_curve, mic_curve, raw_power, post_power))
    rails = adjusted_rails(rails_defaults, plan.get("rails", {}).get("rails_adjustment"))
    peak_curves = {"mic": mic_curve, "mix": mix_curve}
    if plan.get("roles", {}).get("bed_streams"):
        peak_curves["bed"] = bed_curve
    rows.extend(_true_peak_rows(peak_curves, rails, plan))
    rows.extend(_mic_rows(plan, analysis, mic_curve, rails))
    rows.extend(_bed_stitching_rows(plan, analysis, bed_curve, rails))
    counterfactual_bed_segments = _counterfactual_bed_lift_segments(plan, analysis)
    peak_resolver = lambda masking_lift: _counterfactual_peak_safe_lift(
        mic_path,
        bed_path,
        float(manifest.get("duration_seconds") or analysis.get("duration_seconds") or 0.0),
        masking_lift,
        float(rails["bed_retention"].get("counterfactual_step_db", 0.1)),
        float(rails["true_peak_dbtp"]["max"]),
        repair,
        manifest_path.parent,
        counterfactual_bed_segments,
        int(rails["bed_retention"].get("maximum_counterfactual_peak_attempts", 10)),
        int(rails["bed_retention"].get("maximum_counterfactual_scratch_bytes", 68719476736)),
        float(rails["bed_retention"].get("maximum_counterfactual_media_seconds", 172800.0)),
        int(rails["bed_retention"].get("counterfactual_media_passes_per_attempt", 6)),
        float(rails["bed_retention"].get("counterfactual_disk_safety_factor", 1.25)),
    )
    rows.extend(_gap_rows(plan, analysis, mic_curve, bed_curve, rails, candidate_safe_lift_resolver=peak_resolver))
    rows.extend(_transition_rows(plan, analysis, mic_curve, rails))
    rows.extend(_dip_rows(plan, analysis, mic_curve, rails))
    mix_i = mix_curve[-1].get("integrated_lufs") if mix_curve else None
    rows.append({"type": "mix_integrated_lufs", "measurement": f"mix integrated LUFS {mix_i}", "target": "informational only", "status": "pass", "failure_class": None, "next_action": "none"})
    return rows


def _derived_component_rows(
    manifest: dict[str, Any],
    plan: dict[str, Any],
    analysis: dict[str, Any],
    mic_path: Path,
    bed_path: Path,
    mic_raw_path: Path | None,
    repair: list[str],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    source = Path(str(analysis.get("media_path") or manifest.get("source_path") or ""))
    if not source.is_file() or sha256_file(source) != analysis.get("source_sha256"):
        return [_fail("component_not_derived_from_plan", "verifier source path is missing or does not match analysis source_sha256", "rerun probe/analyze from the source, then plan-validate/render/verify", row_type="component_derivation")]
    peak_config = plan.get("render", {}).get("peak_control") or {}
    peak_enabled = peak_config.get("enabled") is True
    duration = float(plan.get("analysis", {}).get("duration_seconds") or analysis.get("duration_seconds") or 0.0)
    roles = plan.get("roles", {})
    actual_probe = ffprobe_json(source, repair)
    audio_streams = [row for row in _streams(actual_probe) if row["codec_type"] == "audio"]
    channel_counts = {int(row["audio_stream_index"]): int(row.get("channels") or 2) for row in audio_streams}
    temp_root = Path(os.environ.get("RV_TEST_TMPDIR") or tempfile.gettempdir()) / "rv-verifier-owned"
    temp_root.mkdir(parents=True, exist_ok=True)
    temp_dir = temp_root / f"derive-{uuid.uuid4().hex}"
    temp_dir.mkdir()
    try:
        derived_pre = temp_dir / "mic_component_pre_control.wav"
        derived_post = temp_dir / "mic_component_post_control.wav"
        derived_bed = temp_dir / "bed_component.wav"
        mic_segments = _materialized_lane_segments(plan, "mic", analysis)
        bed_segments = _materialized_lane_segments(plan, "bed", analysis)
        ffmpeg_render_filter(source, [int(x) for x in roles.get("mic_streams", [])], channel_counts, mic_segments, "mic_gain_db", derived_pre, duration, repair)
        ffmpeg_render_filter(source, [int(x) for x in roles.get("bed_streams", [])], channel_counts, bed_segments, "bed_gain_db", derived_bed, duration, repair)
        expected_bed = sha256_file(derived_bed)
        rows.append(_row("component_derivation", f"bed candidate {sha256_file(bed_path)}; verifier-derived {expected_bed}", "candidate bed must equal source+plan derivation", sha256_file(bed_path) == expected_bed, "component_not_derived_from_plan", "discard substituted/processed bed and rerun render/verify"))
        if peak_enabled:
            if mic_raw_path is None:
                rows.append(_fail("component_not_derived_from_plan", "enabled peak control lacks candidate pre-control mic", "rerun render/verify", row_type="component_derivation"))
                return rows
            expected_pre = sha256_file(derived_pre)
            actual_pre = sha256_file(mic_raw_path)
            rows.append(_row("component_derivation", f"pre-control mic candidate {actual_pre}; verifier-derived {expected_pre}", "candidate pre-control mic must equal source+plan derivation", actual_pre == expected_pre, "component_not_derived_from_plan", "discard substituted pre-control mic and rerun render/verify"))
            derived_peak_meta = ffmpeg_peak_control(mic_raw_path, derived_post, duration, float(peak_config["true_peak_ceiling_dbtp"]), repair)
            expected_post = sha256_file(derived_post)
            actual_post = sha256_file(mic_path)
            rows.append(_row("component_derivation", f"post-control mic candidate {actual_post}; verifier-reapplied limiter {expected_post}", "candidate post-control mic must equal fixed limiter applied to candidate pre-control mic at the plan ceiling", actual_post == expected_post, "component_not_derived_from_plan", "discard substituted post-control mic and rerun render/verify"))
            actual_peak_meta = manifest.get("peak_control")
            rows.append(_row("component_derivation", f"peak-control metadata {actual_peak_meta}", f"fixed verifier metadata {derived_peak_meta}", actual_peak_meta == derived_peak_meta, "component_not_derived_from_plan", "restore the plan-declared fixed limiter metadata by rerunning render/verify"))
        else:
            expected_mic = sha256_file(derived_pre)
            actual_mic = sha256_file(mic_path)
            rows.append(_row("component_derivation", f"mic candidate {actual_mic}; verifier-derived {expected_mic}", "candidate mic must equal source+plan derivation", actual_mic == expected_mic, "component_not_derived_from_plan", "discard substituted/processed mic and rerun render/verify"))
            rows.append(_row("component_derivation", f"peak-control metadata {manifest.get('peak_control')}", "no peak-control metadata when the plan disables peak control", manifest.get("peak_control") is None, "component_not_derived_from_plan", "remove undeclared peak processing by rerunning render/verify"))
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
    return rows


def _mic_rows(
    plan: dict[str, Any],
    analysis: dict[str, Any],
    mic_curve: list[dict[str, Any]],
    rails: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    measured_bodies: list[dict[str, Any]] = []
    lo = float(rails["processed_mic_active_speech_lufs"]["min"])
    hi = float(rails["processed_mic_active_speech_lufs"]["max"])
    target_basis = "adjusted house BODY rail"
    shared_target = _shared_mic_target(plan)
    if shared_target is not None:
        stitch_defaults = rails.get("mic_stitching_v2", {})
        target_tolerance = float(stitch_defaults.get("target_tolerance_db", 1.5))
        lo = shared_target - target_tolerance
        hi = shared_target + target_tolerance
        target_basis = "plan targets.shared_mic_body_lufs"
    tolerance = float(rails["window_tolerance_db"])
    window_lo = lo - tolerance
    window_hi = hi + tolerance
    coverage_floor = rails["coverage_floor"]
    for regime in analysis.get("regimes", []):
        windows = [win for win in analysis.get("speech_windows", []) if win.get("regime_id") == regime.get("id")]
        active = sum(float(win.get("duration_seconds") or 0.0) for win in windows)
        raw_density = float(regime.get("active_speech_density") or 0.0)
        min_active = max(float(coverage_floor["minimum_active_speech_seconds"]), float(regime.get("duration_seconds") or 0.0) * float(coverage_floor["minimum_regime_fraction"]))
        if active < min_active and raw_density < float(coverage_floor["sparse_speech_density_floor"]):
            rows.append({"type": "sparse-speech", "regime_id": regime.get("id"), "measurement": f"{regime.get('id')} raw active speech {active:.3f}s; raw density {raw_density:.4f}", "target": "caller packet informational sparse-source disclosure", "status": "pass", "failure_class": "sparse-speech", "next_action": "none"})
            continue
        processed_active = 0.0
        processed_windows = 0
        window_values: list[tuple[dict[str, Any], float | None]] = []
        for win in windows:
            value = _window_lufs(mic_curve, float(win["start_seconds"]), float(win["end_seconds"]))
            window_values.append((win, value))
            if value is not None and value > -100.0:
                processed_active += float(win.get("duration_seconds") or 0.0)
                processed_windows += 1
        if windows and all(value is None for _, value in window_values):
            rows.append(_fail("processed_mic_body_unmeasurable", f"{regime.get('id')} processed mic body is not measurable over raw speech windows", "check render lineage/component routing and rerun render/verify", row_type="mic_lufs"))
            continue
        presence_ratio = processed_active / active if active > 0 else 0.0
        if active < min_active or presence_ratio < float(coverage_floor["raw_density_ratio_floor"]):
            rows.append(_fail("insufficient_speech_coverage", f"{regime.get('id')} processed speech coverage {presence_ratio:.3f} ({processed_active:.3f}/{active:.3f}s); raw density {raw_density:.4f}", "fix detector/render coverage and rerun analyze or verify", row_type="mic_lufs"))
            continue
        in_band = 0.0
        measured: list[tuple[float, float]] = []
        for win, value in window_values:
            if value is not None:
                measured.append((value, float(win.get("duration_seconds") or 0.0)))
                if window_lo <= value <= window_hi:
                    in_band += float(win.get("duration_seconds") or 0.0)
        body = weighted_median(measured)
        if body is None:
            rows.append(_fail("processed_mic_body_unmeasurable", f"{regime.get('id')} processed mic body is not measurable over raw speech windows", "check render lineage/component routing and rerun render/verify", row_type="mic_lufs"))
            continue
        fraction = in_band / active if active > 0 else 1.0
        body_ok = body is not None and lo <= body <= hi
        if body < lo:
            failure = "mic_below_rail"
            next_action = f"raise the owning mic_segments[].gain_db for {regime.get('id')} in render_plan.json, then run plan-validate, render, verify"
        elif body > hi:
            failure = "mic_above_rail"
            next_action = f"trim the owning mic_segments[].gain_db for {regime.get('id')} in render_plan.json, then run plan-validate, render, verify"
        else:
            failure = None
            next_action = "none"
        status = "pass" if body_ok else "fail"
        failure_class = None if body_ok else str(failure)
        mic_row = {
                "type": "mic_lufs",
                "regime_id": regime.get("id"),
                "measurement": f"processed mic BODY {rounded(body, 3)} LUFS; active {active:.3f}s",
                "target": f"strict BODY {lo}..{hi} LUFS on the listener-heard mic component from {target_basis}",
                "status": status,
                "failure_class": failure_class,
                "next_action": "none" if status == "pass" else next_action,
            }
        rows.append(mic_row)
        measured_bodies.append(
            {
                "regime_id": regime.get("id"),
                "start_seconds": float(regime.get("start_seconds") or 0.0),
                "body_lufs": float(body),
            }
        )
        gross_floor = float(rails["mic_window_coverage"]["gross_floor"])
        rows.append(
            {
                "type": "mic_window_coverage",
                "regime_id": regime.get("id"),
                "measurement": f"processed mic in-band fraction {fraction:.3f}; active {active:.3f}s",
                "target": f"informational only; house reference {gross_floor:.3f} inside widened window band {window_lo}..{window_hi} LUFS",
                "status": "pass",
                "failure_class": None if fraction >= gross_floor else "expressive_window_variation_disclosure",
                "next_action": "none",
            }
        )
    rows.extend(_mic_stitching_rows(plan, measured_bodies, rails))
    return rows


def _mic_stitching_rows(plan: dict[str, Any], measured_bodies: list[dict[str, Any]], rails: dict[str, Any]) -> list[dict[str, Any]]:
    targets = plan.get("targets") if isinstance(plan.get("targets"), dict) else {}
    legacy = plan.get("mic_stitching") if isinstance(plan.get("mic_stitching"), dict) else {}
    if not legacy and isinstance(plan.get("rails"), dict) and isinstance(plan["rails"].get("mic_stitching"), dict):
        legacy = plan["rails"]["mic_stitching"]
    target_raw = targets.get("shared_mic_body_lufs")
    if target_raw is None:
        target_raw = legacy.get("shared_target_lufs", legacy.get("target_lufs"))
    if target_raw is None:
        return []
    target = float(target_raw)
    defaults = rails.get("mic_stitching_v2", {})
    target_tolerance = float(legacy.get("target_tolerance_db", defaults.get("target_tolerance_db", 1.5)))
    adjacent_limit = float(legacy.get("maximum_adjacent_body_delta_db", defaults.get("maximum_adjacent_body_delta_db", 1.5)))
    spread_limit = float(legacy.get("maximum_body_spread_db", defaults.get("maximum_body_spread_db", 2.0)))
    confirmed_ids = {
        str(regime_id)
        for segment in _raw_lane_segments(plan, "mic")
        for regime_id in (segment.get("analysis_regime_ids") or ([segment.get("regime_id")] if segment.get("regime_id") is not None else []))
    }
    selected = [row for row in measured_bodies if not confirmed_ids or str(row.get("regime_id")) in confirmed_ids]
    selected.sort(key=lambda row: float(row.get("start_seconds") or 0.0))
    missing = sorted(confirmed_ids - {str(row.get("regime_id")) for row in selected})
    if not selected or missing:
        return [
            _fail(
                "mic_stitch_measurement_missing",
                f"shared target {target:.3f} LUFS has measured regimes {[row.get('regime_id') for row in selected]}; missing {missing}",
                "repair confirmed mic segment/regime mapping or speech measurement, then rerun verify",
                row_type="mic_stitching",
            )
        ]
    bodies = [float(row["body_lufs"]) for row in selected]
    deviations = [abs(body - target) for body in bodies]
    worst_deviation = max(deviations)
    rows = [
        _row(
            "mic_stitch_target",
            f"shared target {target:.3f} LUFS; confirmed regime bodies {[(row.get('regime_id'), rounded(row.get('body_lufs'), 3)) for row in selected]}; worst deviation {worst_deviation:.3f} dB",
            f"every confirmed macro body within +/-{target_tolerance:.3f} dB of the plan shared target",
            worst_deviation <= target_tolerance,
            "mic_stitch_target_missed",
            "adjust confirmed mic segment baselines toward targets.shared_mic_body_lufs, then rerun render/verify",
        )
    ]
    adjacent = [
        (selected[idx - 1].get("regime_id"), selected[idx].get("regime_id"), abs(bodies[idx] - bodies[idx - 1]))
        for idx in range(1, len(selected))
    ]
    worst_adjacent = max((delta for _, _, delta in adjacent), default=0.0)
    rows.append(
        _row(
            "mic_stitch_adjacent",
            f"adjacent confirmed macro body deltas {[(left, right, rounded(delta, 3)) for left, right, delta in adjacent]}",
            f"maximum adjacent BODY delta <= {adjacent_limit:.3f} dB",
            worst_adjacent <= adjacent_limit,
            "mic_stitch_adjacent_jump",
            "realign adjacent confirmed mic segment baselines and preserve expressive event overlays, then rerun render/verify",
        )
    )
    spread = max(bodies) - min(bodies)
    rows.append(
        _row(
            "mic_stitch_spread",
            f"confirmed macro BODY spread {spread:.3f} dB across {len(bodies)} regime(s)",
            f"full confirmed BODY spread <= {spread_limit:.3f} dB",
            spread <= spread_limit,
            "mic_stitch_body_spread",
            "realign the shared mic baseline across confirmed macro segments, then rerun render/verify",
        )
    )
    return rows


def _bed_stitching_rows(plan: dict[str, Any], analysis: dict[str, Any], bed_curve: list[dict[str, Any]], rails: dict[str, Any]) -> list[dict[str, Any]]:
    if not plan.get("roles", {}).get("bed_streams"):
        return []
    regimes = analysis.get("bed_regimes", [])
    held_policies = {"preserve-unity-low-confidence", "hold-unity-indeterminate"}
    stitchable = [regime for regime in regimes if regime.get("stitching_policy") not in held_policies]
    held = [regime for regime in regimes if regime.get("stitching_policy") in held_policies]
    targets = plan.get("targets") if isinstance(plan.get("targets"), dict) else {}
    target_raw = targets.get("shared_bed_body_lufs")
    if target_raw is None and stitchable:
        return [_fail("missing_shared_bed_target", "separate-bed plan has no targets.shared_bed_body_lufs", "rerun plan-init", row_type="bed_stitch_target")]
    target = float(target_raw) if target_raw is not None else None
    config = rails.get("bed_stitching_v2", {})
    target_tolerance = float(config.get("target_tolerance_db", 1.5))
    adjacent_limit = float(config.get("maximum_adjacent_body_delta_db", 1.5))
    spread_limit = float(config.get("maximum_body_spread_db", 2.0))
    preserve_tolerance = float(config.get("preserve_unity_processed_body_tolerance_db", 0.1))
    measured: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    for regime in held:
        body = _robust_curve_body(bed_curve, float(regime.get("start_seconds") or 0.0), float(regime.get("end_seconds") or 0.0))
        raw_body = regime.get("raw_bed_body_lufs")
        if body is None and raw_body is None:
            delta = 0.0
            measurement = f"{regime.get('id')} preserved-unity bed remains unmeasurable silence"
        elif body is None or raw_body is None:
            rows.append(_fail("preserved_unity_bed_body_changed", f"{regime.get('id')} raw/processed bed BODY measurability changed", "rerun plan-init/render; preserve the low-confidence bed regime at exact unity", row_type="bed_stitch_target"))
            continue
        else:
            delta = abs(float(body) - float(raw_body))
            measurement = f"{regime.get('id')} preserved-unity raw/processed bed BODY delta {delta:.3f} dB"
        if delta > preserve_tolerance:
            rows.append(_fail("preserved_unity_bed_body_changed", measurement, "rerun plan-init/render; preserve the low-confidence bed regime at exact unity", row_type="bed_stitch_target"))
        else:
            rows.append({"type": "bed_stitch_target", "regime_id": regime.get("id"), "measurement": measurement, "target": f"unity-preserved BODY delta <= {preserve_tolerance:.3f} dB", "status": "pass", "failure_class": "bed_preserved_unity_low_confidence", "next_action": "none"})
    for index, regime in enumerate(regimes):
        if regime.get("stitching_policy") in held_policies:
            continue
        body = _robust_curve_body(bed_curve, float(regime.get("start_seconds") or 0.0), float(regime.get("end_seconds") or 0.0))
        if body is None:
            rows.append(_fail("processed_bed_body_unmeasurable", f"{regime.get('id')} processed bed body is unmeasurable", "check bed routing and rerun render/verify", row_type="bed_stitch_target"))
            continue
        assert target is not None
        ok = abs(body - target) <= target_tolerance
        rows.append(_row("bed_stitch_target", f"{regime.get('id')} processed bed BODY {body:.3f} LUFS", f"shared bed target {target:.3f} +/- {target_tolerance:.3f} dB", ok, "bed_stitch_target_missed", "repair the independent bed baseline from the shared mic-priority bed target"))
        measured.append({"regime_id": regime.get("id"), "regime_index": index, "start_seconds": float(regime.get("start_seconds") or 0.0), "body_lufs": body})
    measured.sort(key=lambda row: row["start_seconds"])
    for left, right in zip(measured, measured[1:]):
        if int(right["regime_index"]) != int(left["regime_index"]) + 1:
            continue
        delta = abs(float(right["body_lufs"]) - float(left["body_lufs"]))
        rows.append(_row("bed_stitch_adjacent", f"{left['regime_id']}->{right['regime_id']} processed bed BODY delta {delta:.3f} dB", f"<= {adjacent_limit:.3f} dB", delta <= adjacent_limit, "bed_stitch_adjacent_jump", "align adjacent independent bed baselines without flattening events inside them"))
    if measured:
        spread = max(float(row["body_lufs"]) for row in measured) - min(float(row["body_lufs"]) for row in measured)
        rows.append(_row("bed_stitch_spread", f"processed bed BODY spread {spread:.3f} dB across {len(measured)} regime(s)", f"<= {spread_limit:.3f} dB", spread <= spread_limit, "bed_stitch_body_spread", "align all independent bed baselines to the shared mic-priority bed target"))
    else:
        rows.append({"type": "bed_stitch_spread", "measurement": f"all {len(held)} bed regime(s) preserved at unity", "target": "no shared bed target when every regime is low-confidence", "status": "pass", "failure_class": "all_bed_regimes_preserved_unity", "next_action": "none"})
    return rows


def _robust_curve_body(curve: list[dict[str, Any]], start: float, end: float) -> float | None:
    return weighted_median(
        (float(row["momentary_lufs"]), max(0.0, float(row.get("end_seconds") or row["time_seconds"]) - float(row["time_seconds"])))
        for row in curve
        if start <= float(row["time_seconds"]) < end and math.isfinite(float(row["momentary_lufs"])) and float(row["momentary_lufs"]) > -119.0
    )


def _shared_mic_target(plan: dict[str, Any]) -> float | None:
    targets = plan.get("targets") if isinstance(plan.get("targets"), dict) else {}
    raw = targets.get("shared_mic_body_lufs")
    if raw is None:
        legacy = plan.get("mic_stitching") if isinstance(plan.get("mic_stitching"), dict) else {}
        if not legacy and isinstance(plan.get("rails"), dict) and isinstance(plan["rails"].get("mic_stitching"), dict):
            legacy = plan["rails"]["mic_stitching"]
        raw = legacy.get("shared_target_lufs", legacy.get("target_lufs"))
    return None if raw is None else float(raw)


def _gap_rows(
    plan: dict[str, Any],
    analysis: dict[str, Any],
    mic_curve: list[dict[str, Any]],
    bed_curve: list[dict[str, Any]],
    rails: dict[str, Any],
    maximum_candidate_safe_lift_db: float | None = None,
    candidate_safe_lift_resolver: Callable[[float], float] | None = None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    macro_gaps: list[tuple[str, float]] = []
    gap_groups: dict[str, list[tuple[float, dict[str, Any], float]]] = {}
    targets = plan.get("targets") if isinstance(plan.get("targets"), dict) else {}
    preferred = float(targets.get("preferred_mic_over_bed_gap_db", rails["mic_over_bed_gap_db"]["preferred"]))
    masking = rails.get("sustained_masking", {})
    house_minimum = float(masking.get("house_minimum_gap_db", rails["mic_over_bed_gap_db"]["min"]))
    fraction_limit = float(masking.get("maximum_duration_fraction_below_minimum", 0.1))
    contiguous_limit = float(masking.get("maximum_contiguous_seconds_below_minimum", 2.0))
    adjacency = float(masking.get("window_adjacency_tolerance_seconds", 0.15))
    explicit_no_bed = "roles" in plan and isinstance(plan.get("roles"), dict) and not plan.get("roles", {}).get("bed_streams")
    for regime in analysis.get("regimes", []):
        gaps: list[tuple[float, dict[str, Any], float]] = []
        total = 0
        present = 0
        marginal = 0
        absent = 0
        holes: list[dict[str, Any]] = []
        for win in analysis.get("bed_presence_windows", []):
            if win.get("regime_id") != regime.get("id"):
                continue
            total += 1
            tier = _bed_presence_tier(win, regime)
            if tier == "marginal":
                marginal += 1
            elif tier == "absent":
                absent += 1
            if tier != "meaningful":
                continue
            present += 1
            duration = float(win.get("duration_seconds") or (float(win["end_seconds"]) - float(win["start_seconds"])))
            mic = _window_lufs(mic_curve, float(win["start_seconds"]), float(win["end_seconds"]))
            bed = _window_lufs(bed_curve, float(win["start_seconds"]), float(win["end_seconds"]))
            if mic is not None and bed is not None:
                gap = mic - bed
                gaps.append((gap, win, duration))
            elif float(win.get("bed_lufs") or -120.0) > -60.0:
                holes.append(win)
        rows.append({"type": "bed_window_classification", "regime_id": regime.get("id"), "measurement": f"meaningful {present}/{total}; marginal {marginal}/{total}; absent {absent}/{total}", "target": "informational bed-presence tiers; gap gates bind only on meaningful windows", "status": "pass", "failure_class": None, "next_action": "none"})
        if explicit_no_bed:
            rows.append({"type": "mic_bed_gap", "regime_id": regime.get("id"), "measurement": "plan roles declare no bed lane", "target": "no masking gate when no bed is selected", "status": "pass", "failure_class": "no-bed", "next_action": "none"})
            rows.append(_bed_retention_row(plan, regime, None, preferred, rails, explicit_no_bed=True))
            continue
        if holes:
            first = holes[0]
            rows.append(_fail("unexplained_bed_present_gap_hole", f"{regime.get('id')} bed-present speech window {first.get('window_id')} {first.get('start_seconds')}..{first.get('end_seconds')} lacks measurable processed mic/bed", "fix processed component routing or verifier measurement hole, then rerun verify", row_type="mic_bed_gap"))
            continue
        if not gaps:
            rows.append({"type": "mic_bed_gap", "regime_id": regime.get("id"), "measurement": f"meaningful-bed coverage {present}/{total}; marginal excluded {marginal}; no meaningful-bed speech windows", "target": "no sustained masking gate without measurable meaningful-bed overlap", "status": "pass", "failure_class": "sparse-bed" if total else None, "next_action": "none"})
            rows.append(_bed_retention_row(plan, regime, None, preferred, rails))
            continue
        total_duration = sum(duration for _, _, duration in gaps)
        below = [(gap, win, duration) for gap, win, duration in gaps if gap < house_minimum]
        below_duration = sum(duration for _, _, duration in below)
        below_fraction = below_duration / total_duration if total_duration > 0 else 0.0
        longest_run, run_start, run_end = _longest_low_gap_run(below, adjacency)
        ok = below_fraction <= fraction_limit and longest_run <= contiguous_limit
        gap_row = _row(
            "mic_bed_gap",
            f"{regime.get('id')} below-house-minimum exposure {below_duration:.3f}/{total_duration:.3f}s ({below_fraction:.3f}); longest contiguous run {longest_run:.3f}s at {run_start}..{run_end}; meaningful coverage {present}/{total}; marginal excluded {marginal}",
            f"duration fraction below {house_minimum} dB <= {fraction_limit:.3f} and longest run <= {contiguous_limit:.3f}s",
            ok,
            "mic_bed_gap_out_of_rail",
            f"lower the {regime.get('id')} sustained bed baseline after mic stitching; preserve brief expressive bed events, then rerun render/verify",
        )
        gap_row.update({"regime_id": regime.get("id"), "start_seconds": run_start, "end_seconds": run_end})
        rows.append(gap_row)
        median_gap = _duration_weighted_median(gaps)
        gap_groups[str(regime.get("id"))] = gaps
        macro_gaps.append((str(regime.get("id")), median_gap))
        rows.append(
            {
                "type": "mic_bed_gap_preference",
                "regime_id": regime.get("id"),
                "measurement": f"{regime.get('id')} duration-weighted median meaningful-bed gap {median_gap:.3f} dB",
                "target": f"house preference {preferred:.3f} dB; informational, with no upper-gap promotion failure",
                "status": "pass",
                "failure_class": None if abs(median_gap - preferred) <= float(rails["window_tolerance_db"]) else "gap_preference_disclosure",
                "next_action": "none",
            }
        )
        rows.append(_bed_retention_row(plan, regime, median_gap, preferred, rails))
    if len(macro_gaps) >= 2:
        spread = max(gap for _, gap in macro_gaps) - min(gap for _, gap in macro_gaps)
        preferred_spread = float(rails.get("macro_balance_consistency", {}).get("maximum_informational_gap_spread_db", 4.0))
        rows.append(
            {
                "type": "mic_bed_gap_consistency",
                "measurement": f"macro meaningful-bed median gaps {[(regime_id, rounded(gap, 3)) for regime_id, gap in macro_gaps]}; spread {spread:.3f} dB",
                "target": f"prefer macro gap spread <= {preferred_spread:.3f} dB after bounded correction; informational, never a promotion blocker",
                "status": "pass",
                "failure_class": None if spread <= preferred_spread else "macro_gap_spread_disclosure",
                "next_action": "none",
            }
        )
    if int(plan.get("schema_version") or 1) >= 2 and not explicit_no_bed:
        necessity = _bed_yield_necessity_row(
            plan,
            _stitchable_gap_groups(plan, analysis, gap_groups),
            preferred,
            rails,
            maximum_candidate_safe_lift_db=maximum_candidate_safe_lift_db,
            candidate_safe_lift_resolver=candidate_safe_lift_resolver,
            unmeasured_segment_ids=_unmeasured_stitchable_bed_segment_ids(plan, analysis),
        )
        rows.append(necessity)
    return rows


def _bed_yield_necessity_row(
    plan: dict[str, Any],
    gap_groups: dict[str, list[tuple[float, dict[str, Any], float]]],
    preferred: float,
    rails: dict[str, Any],
    maximum_candidate_safe_lift_db: float | None = None,
    candidate_safe_lift_resolver: Callable[[float], float] | None = None,
    unmeasured_segment_ids: list[str] | None = None,
) -> dict[str, Any]:
    config = rails.get("bed_retention", {})
    disclosure = float(config.get("disclosure_gap_above_preferred_db", 6.0))
    epsilon = float(config.get("negative_gain_epsilon_db", 0.1))
    step = float(config.get("counterfactual_step_db", 0.1))
    maximum_lift = float(config.get("maximum_counterfactual_lift_db", 30.0))
    allowed = float(config.get("maximum_unexplained_recoverable_lift_db", 0.11))
    masking = rails.get("sustained_masking", {})
    minimum = float(masking.get("house_minimum_gap_db", rails["mic_over_bed_gap_db"]["min"]))
    fraction_limit = float(masking.get("maximum_duration_fraction_below_minimum", 0.1))
    run_limit = float(masking.get("maximum_contiguous_seconds_below_minimum", 2.0))
    adjacency = float(masking.get("window_adjacency_tolerance_seconds", 0.15))
    gains = [float(row.get("gain_db", row.get("bed_gain_db", 0.0)) or 0.0) for row in _raw_lane_segments(plan, "bed")]
    distributions: list[dict[str, Any]] = []
    medians: list[float] = []
    for regime_id, gaps in sorted(gap_groups.items()):
        if not gaps:
            continue
        median = _duration_weighted_median(gaps)
        medians.append(median)
        distributions.append(
            {
                "regime_id": regime_id,
                "p10_db": rounded(_duration_weighted_gap_quantile(gaps, 0.10), 3),
                "p50_db": rounded(median, 3),
                "p90_db": rounded(_duration_weighted_gap_quantile(gaps, 0.90), 3),
                "measured_seconds": rounded(sum(item[2] for item in gaps), 3),
            }
        )
    triggered = bool(medians) and any(gain < -epsilon for gain in gains) and max(medians) > preferred + disclosure
    proof: dict[str, Any] = {
        "policy": "verifier-owned-uniform-bed-lift-v1",
        "triggered": triggered,
        "preferred_gap_db": rounded(preferred, 3),
        "planned_bed_gains_db": [rounded(value, 3) for value in gains],
        "common_window_gap_distribution": distributions,
        "counterfactual_step_db": step,
        "maximum_allowed_unexplained_lift_db": allowed,
        "candidate_peak_evaluation": "actual-counterfactual-bed-and-mix" if candidate_safe_lift_resolver is not None else "caller-supplied-test-bound" if maximum_candidate_safe_lift_db is not None else "not-run",
        "unmeasured_stitchable_segment_ids": list(unmeasured_segment_ids or []),
    }
    if unmeasured_segment_ids and any(gain < -epsilon for gain in gains):
        proof.update({"maximum_masking_safe_uniform_lift_db": None, "maximum_candidate_safe_uniform_lift_db": None, "controlling_failure": None, "candidate_peak_evaluation": "not-run-unmeasured-stitchable-bed"})
        return {
            "type": "bed_yield_necessity",
            "measurement": f"verifier cannot prove a global recovery while stitchable bed segments {unmeasured_segment_ids} lack BODY evidence",
            "target": "all stitchable bed segments measured before global recovery proof",
            "status": "fail",
            "failure_class": "unmeasured_bed_recovery_evidence_required",
            "next_action": "rerun analyze to obtain bed BODY evidence or classify the indeterminate sections as held, then rerun plan-init/plan-validate/render/verify; do not edit bed gains",
            "proof": proof,
        }
    if not triggered:
        proof.update({"maximum_masking_safe_uniform_lift_db": 0.0, "controlling_failure": None})
        return {"type": "bed_yield_necessity", "measurement": "deep deliberate bed yield not triggered", "target": "counterfactual proof required only for deliberate attenuation with a materially wide measured gap", "status": "pass", "failure_class": None, "next_action": "none", "proof": proof}

    feasible = 0.0
    controlling: dict[str, Any] | None = None
    candidate = step
    while candidate <= maximum_lift + 1e-9:
        failure = _counterfactual_masking_failure(gap_groups, candidate, minimum, fraction_limit, run_limit, adjacency)
        if failure is not None:
            controlling = failure
            break
        feasible = candidate
        candidate = rounded(candidate + step, 6)
    if candidate_safe_lift_resolver is not None:
        candidate_safe = candidate_safe_lift_resolver(feasible)
    else:
        candidate_safe = feasible if maximum_candidate_safe_lift_db is None else min(feasible, max(0.0, maximum_candidate_safe_lift_db))
    proof.update({"maximum_masking_safe_uniform_lift_db": rounded(feasible, 3), "maximum_candidate_safe_uniform_lift_db": rounded(candidate_safe, 3), "controlling_failure": controlling})
    ok = candidate_safe <= allowed + 0.001
    return {
        "type": "bed_yield_necessity",
        "measurement": f"verifier-owned counterfactual leaves {candidate_safe:.3f} dB candidate-safe uniform bed lift ({feasible:.3f} dB masking-safe); controlling failure {controlling}",
        "target": f"recoverable uniform lift <= {allowed:.3f} dB",
        "status": "pass" if ok else "fail",
        "failure_class": "bed_yield_necessity_proven" if ok else "bed_yield_not_minimal",
        "next_action": "none" if ok else f"increase every stitchable bed segment uniformly by {candidate_safe:.3f} dB, update targets.bed_yield_reconciliation, then rerun plan-validate/render/verify",
        "proof": proof,
    }


def _stitchable_gap_groups(
    plan: dict[str, Any],
    analysis: dict[str, Any],
    gap_groups: dict[str, list[tuple[float, dict[str, Any], float]]],
) -> dict[str, list[tuple[float, dict[str, Any], float]]]:
    window_end = max(
        (float(window.get("end_seconds") or 0.0) for gaps in gap_groups.values() for _, window, _ in gaps),
        default=0.0,
    )
    duration = float(analysis.get("duration_seconds") or window_end)
    segments = [segment for segment in _counterfactual_bed_lift_segments(plan, analysis) if segment.get("counterfactual_lift_eligible") is True]
    if not segments:
        return {}
    filtered: dict[str, list[tuple[float, dict[str, Any], float]]] = {}
    for regime_id, gaps in gap_groups.items():
        kept: list[tuple[float, dict[str, Any], float]] = []
        for gap, window, window_duration in gaps:
            start = float(window.get("start_seconds") or 0.0)
            end = float(window.get("end_seconds") or (start + window_duration))
            if any(
                start >= float(segment.get("start_seconds") or 0.0) - 1e-9
                and end <= float(segment.get("end_seconds") if segment.get("end_seconds") is not None else duration) + 1e-9
                for segment in segments
            ):
                kept.append((gap, window, window_duration))
        if kept:
            filtered[regime_id] = kept
    return filtered


def _counterfactual_peak_safe_lift(
    mic_path: Path,
    bed_path: Path,
    duration_seconds: float,
    masking_safe_lift_db: float,
    step_db: float,
    peak_limit_dbtp: float,
    repair: list[str],
    scratch_parent: Path,
    bed_segments: list[dict[str, Any]],
    maximum_attempts: int,
    maximum_scratch_bytes: int,
    maximum_media_seconds: float,
    media_passes_per_attempt: int,
    disk_safety_factor: float,
) -> float:
    if masking_safe_lift_db <= 0.0:
        return 0.0
    if step_db <= 0.0 or maximum_attempts <= 0 or maximum_scratch_bytes <= 0 or maximum_media_seconds <= 0.0 or media_passes_per_attempt <= 0 or disk_safety_factor < 1.0:
        raise RvError("bed-yield counterfactual work bounds are invalid", repair)
    _require_counterfactual_resources(scratch_parent, duration_seconds, maximum_scratch_bytes, disk_safety_factor, repair)
    maximum_index = max(0, int(math.floor((masking_safe_lift_db + 1e-9) / step_db)))
    results: dict[int, bool] = {0: True}
    attempt_count = 0
    root = scratch_parent / f".rv-bed-yield-peak-{uuid.uuid4().hex}"
    root.mkdir(parents=True, exist_ok=False)
    try:

        def passes(index: int) -> bool:
            nonlocal attempt_count
            if index in results:
                return results[index]
            if attempt_count >= maximum_attempts:
                raise RvError(f"bed-yield peak counterfactual exceeded its {maximum_attempts}-attempt work budget", repair)
            if (attempt_count + 1) * duration_seconds * media_passes_per_attempt > maximum_media_seconds + 1e-9:
                raise RvError(f"bed-yield peak counterfactual exceeded its {maximum_media_seconds:.0f}-second decoded-media work budget", repair)
            attempt_count += 1
            lift = rounded(index * step_db, 6)
            attempt = root / f"lift-{index:04d}"
            attempt.mkdir(parents=True, exist_ok=True)
            try:
                lifted_bed = attempt / "bed.wav"
                mix = attempt / "mix.wav"
                automation = [
                    {
                        **segment,
                        "bed_gain_db": lift if segment.get("counterfactual_lift_eligible") is True else 0.0,
                    }
                    for segment in bed_segments
                ]
                ffmpeg_render_filter(bed_path, [0], {0: 2}, automation, "bed_gain_db", lifted_bed, duration_seconds, repair)
                ffmpeg_mix_components(mic_path, lifted_bed, mix, duration_seconds, repair)
                true_peak_ok = True
                for label, path in (("bed", lifted_bed), ("mix", mix)):
                    curve = ebur128_curve(path, 0, 2, attempt / f"{label}_peak.csv", repair)["rows"]
                    measured = [float(row.get("true_peak_dbtp", -120.0)) for row in curve if float(row.get("true_peak_dbtp", -120.0)) > -119.0]
                    if not measured:
                        raise RvError("bed-yield counterfactual true peak was not measurable", repair)
                    true_peak_ok = true_peak_ok and max(measured) <= peak_limit_dbtp + 1e-9
                results[index] = true_peak_ok
                return results[index]
            finally:
                _remove_counterfactual_scratch(attempt, repair)

        if passes(maximum_index):
            return rounded(maximum_index * step_db, 6)
        low = 0
        high = maximum_index
        while low + 1 < high:
            middle = (low + high) // 2
            if passes(middle):
                low = middle
            else:
                high = middle
        return rounded(low * step_db, 6)
    finally:
        _remove_counterfactual_scratch(root, repair)


def _remove_counterfactual_scratch(path: Path, repair: list[str]) -> None:
    if path.exists():
        shutil.rmtree(path, ignore_errors=False)
    if path.exists():
        raise RvError(f"bed-yield counterfactual scratch cleanup failed: {path}", repair)


def _require_counterfactual_resources(parent: Path, duration_seconds: float, maximum_scratch_bytes: int, safety_factor: float, repair: list[str]) -> None:
    stereo_f32_bytes = max(0, math.ceil(duration_seconds * 48000.0)) * 2 * 4
    estimated_bytes = stereo_f32_bytes * 4
    required_free_bytes = math.ceil(estimated_bytes * safety_factor)
    if estimated_bytes > maximum_scratch_bytes:
        raise RvError(f"bed-yield counterfactual estimated scratch {estimated_bytes} bytes exceeds its {maximum_scratch_bytes}-byte budget", repair)
    free_bytes = shutil.disk_usage(parent).free
    if free_bytes < required_free_bytes:
        raise RvError(f"bed-yield counterfactual requires {required_free_bytes} free bytes with safety margin; only {free_bytes} available", repair)


def _counterfactual_bed_lift_segments(plan: dict[str, Any], analysis: dict[str, Any]) -> list[dict[str, Any]]:
    bed_regimes = analysis.get("bed_regimes") or analysis.get("regimes") or []
    bodies: dict[str, Any] = {}
    for row in bed_regimes:
        if not isinstance(row, dict):
            continue
        body = row.get("raw_bed_body_lufs")
        if body is None and isinstance(row.get("bed_body"), dict):
            body = row["bed_body"].get("raw_bed_body_lufs")
        bodies[str(row.get("id"))] = body
    segments: list[dict[str, Any]] = []
    for raw in _raw_lane_segments(plan, "bed"):
        segment = dict(raw)
        regime_id = str((segment.get("analysis_regime_ids") or [""])[0])
        segment["counterfactual_lift_eligible"] = not plan_contract._preserve_unity_bed(segment) and bodies.get(regime_id) is not None
        segments.append(segment)
    return segments


def _unmeasured_stitchable_bed_segment_ids(plan: dict[str, Any], analysis: dict[str, Any]) -> list[str]:
    return [
        str(segment.get("id"))
        for segment in _counterfactual_bed_lift_segments(plan, analysis)
        if not plan_contract._preserve_unity_bed(segment) and segment.get("counterfactual_lift_eligible") is not True
    ]


def _counterfactual_masking_failure(
    gap_groups: dict[str, list[tuple[float, dict[str, Any], float]]],
    lift_db: float,
    minimum_gap: float,
    fraction_limit: float,
    run_limit: float,
    adjacency: float,
) -> dict[str, Any] | None:
    for regime_id, gaps in sorted(gap_groups.items()):
        total = sum(duration for _, _, duration in gaps)
        below = [(gap, win, duration) for gap, win, duration in gaps if gap - lift_db < minimum_gap]
        below_duration = sum(duration for _, _, duration in below)
        fraction = below_duration / total if total > 0.0 else 0.0
        longest, start, end = _longest_low_gap_run(below, adjacency)
        if fraction > fraction_limit or longest > run_limit:
            return {"regime_id": regime_id, "tested_lift_db": rounded(lift_db, 3), "below_fraction": rounded(fraction, 6), "longest_run_seconds": rounded(longest, 3), "start_seconds": start, "end_seconds": end}
    return None


def _duration_weighted_median(gaps: list[tuple[float, dict[str, Any], float]]) -> float:
    return _duration_weighted_gap_quantile(gaps, 0.5)


def _duration_weighted_gap_quantile(gaps: list[tuple[float, dict[str, Any], float]], q: float) -> float:
    ordered = sorted(gaps, key=lambda item: item[0])
    total = sum(max(0.0, duration) for _, _, duration in ordered)
    threshold = total * min(1.0, max(0.0, q))
    elapsed = 0.0
    for gap, _, duration in ordered:
        elapsed += max(0.0, duration)
        if elapsed >= threshold:
            return float(gap)
    return float(ordered[-1][0])


def _longest_low_gap_run(gaps: list[tuple[float, dict[str, Any], float]], adjacency: float) -> tuple[float, float | None, float | None]:
    ordered = sorted(gaps, key=lambda item: float(item[1].get("start_seconds") or 0.0))
    best_duration = 0.0
    best_start: float | None = None
    best_end: float | None = None
    run_start: float | None = None
    run_end: float | None = None
    for _, win, duration in ordered:
        start = float(win.get("start_seconds") or 0.0)
        end = float(win.get("end_seconds") or (start + duration))
        if run_start is None or run_end is None or start > run_end + adjacency:
            run_start = start
            run_end = end
        else:
            run_end = max(run_end, end)
        run_duration = max(0.0, run_end - run_start)
        if run_duration > best_duration:
            best_duration = run_duration
            best_start = run_start
            best_end = run_end
    return best_duration, best_start, best_end


def _bed_retention_row(
    plan: dict[str, Any],
    regime: dict[str, Any],
    median_gap: float | None,
    preferred: float,
    rails: dict[str, Any],
    *,
    explicit_no_bed: bool = False,
) -> dict[str, Any]:
    config = rails.get("bed_retention", {})
    disclosure_delta = float(config.get("disclosure_gap_above_preferred_db", 6.0))
    gain_epsilon = float(config.get("negative_gain_epsilon_db", 0.1))
    regime_id = regime.get("id")
    regime_start = float(regime.get("start_seconds") or 0.0)
    regime_end = float(regime.get("end_seconds") or regime_start)
    matching = [
        seg
        for seg in _raw_lane_segments(plan, "bed")
        if seg.get("regime_id") == regime_id
        or regime_id in (seg.get("analysis_regime_ids") or [])
        or (
            float(seg.get("start_seconds") or 0.0) < regime_end
            and float(seg.get("end_seconds") or 0.0) > regime_start
        )
    ]
    gains = [float(seg.get("gain_db", seg.get("bed_gain_db", 0.0)) or 0.0) for seg in matching]
    attenuated = any(gain < -gain_epsilon for gain in gains)
    underused = median_gap is not None and median_gap > preferred + disclosure_delta and attenuated
    if explicit_no_bed:
        detail = "no bed selected by plan roles"
    elif underused:
        detail = "wide measured gap observed; verifier-owned bed_yield_necessity owns any necessity claim"
    else:
        detail = "no unnecessary-muting condition detected"
    return {
        "type": "bed_retention",
        "regime_id": regime_id,
        "measurement": f"{regime_id} median gap {rounded(median_gap, 3)} dB; planned bed gains {gains}; {detail}",
        "target": "informational bed-retention/optimality disclosure; bed may yield without an upper-gap failure",
        "status": "pass",
        "failure_class": "bed_underused_disclosure" if underused else None,
        "next_action": "none",
    }


def _transition_rows(plan: dict[str, Any], analysis: dict[str, Any], mic_curve: list[dict[str, Any]], rails: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    lo = float(rails["processed_mic_active_speech_lufs"]["min"])
    hi = float(rails["processed_mic_active_speech_lufs"]["max"])
    tolerance = float(rails["window_tolerance_db"])
    window_lo = lo - tolerance
    window_hi = hi + tolerance
    limit = float(rails["transition_recovery"]["active_speech_seconds"])
    for step in plan_contract.confirmed_mic_transition_boundaries(plan, analysis):
        boundary = float(step["boundary_seconds"])
        elapsed = 0.0
        recovered_at: float | None = None
        for win in analysis.get("speech_windows", []):
            if float(win["start_seconds"]) < boundary:
                continue
            value = _window_lufs(mic_curve, float(win["start_seconds"]), float(win["end_seconds"]))
            elapsed += float(win.get("duration_seconds") or 0.0)
            if value is not None and window_lo <= value <= window_hi:
                recovered_at = elapsed
                break
            if elapsed > limit:
                break
        if elapsed == 0.0:
            rows.append({"type": "transition_recovery", "measurement": f"step {boundary:.3f}s has no subsequent speech windows", "target": "informational no-speech-after-step; transition cannot be measured", "status": "pass", "failure_class": "no-speech-after-step", "next_action": "none"})
            continue
        ok = recovered_at is not None and recovered_at <= limit
        transition_row = _row("transition_recovery", f"step {boundary:.3f}s recovered at active-speech {rounded(recovered_at, 3)}s", f"within first {limit}s active speech after analysis-detected step using widened window band {window_lo}..{window_hi} LUFS", ok, "transition_recovery_late", f"repair transition after analysis step {boundary:.3f}s; detected boundaries remain verifier checkpoints")
        transition_row["event_seconds"] = boundary
        rows.append(transition_row)
    return rows


def _dip_rows(plan: dict[str, Any], analysis: dict[str, Any], mic_curve: list[dict[str, Any]], rails: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    raw_path = analysis.get("curve_sidecars", {}).get(str(plan.get("roles", {}).get("mic_streams", [0])[0]))
    if not raw_path:
        return rows
    raw_curve = _read_curve(raw_path)
    materialized = _materialized_lane_segments(plan, "mic", analysis)
    expected = _expected_gain_by_time(materialized, "mic_gain_db")
    dip_cfg = rails.get("artifact_detection", {})
    threshold_db = float(dip_cfg.get("minimum_unexplained_dip_db", 6.0))
    min_duration = float(dip_cfg.get("minimum_duration_seconds", 0.2))
    active_dip_start: float | None = None
    active_dip_end: float | None = None
    active_direction: str | None = None
    worst = 0.0
    for mic, raw in zip(mic_curve, raw_curve):
        t = float(mic["time_seconds"])
        if _declared_transition_neighborhood(t, materialized):
            if active_dip_start is not None:
                _append_dip_row(rows, active_dip_start, active_dip_end or t, worst, min_duration, active_direction or "dip")
                active_dip_start = None
                active_direction = None
                worst = 0.0
            continue
        if t < 0.5:
            continue
        if float(raw["momentary_lufs"]) <= -100.0:
            continue
        expected_gain = expected(t)
        measured_gain = float(mic["momentary_lufs"]) - float(raw["momentary_lufs"])
        miss = expected_gain - measured_gain
        direction = "dip" if miss >= threshold_db else ("boost" if miss <= -threshold_db else None)
        if direction is not None and (active_direction is None or direction == active_direction):
            active_dip_start = t if active_dip_start is None else active_dip_start
            active_dip_end = float(mic["end_seconds"])
            active_direction = direction
            worst = max(worst, abs(miss))
        elif direction is not None:
            prior_start = t if active_dip_start is None else active_dip_start
            prior_end = t if active_dip_end is None else active_dip_end
            _append_dip_row(rows, prior_start, prior_end, worst, min_duration, active_direction or "dip")
            active_dip_start = t
            active_dip_end = float(mic["end_seconds"])
            active_direction = direction
            worst = abs(miss)
        elif active_dip_start is not None:
            _append_dip_row(rows, active_dip_start, active_dip_end or t, worst, min_duration, active_direction or "dip")
            active_dip_start = None
            active_direction = None
            worst = 0.0
    if active_dip_start is not None:
        _append_dip_row(rows, active_dip_start, active_dip_end or active_dip_start, worst, min_duration, active_direction or "dip")
    if not rows:
        rows.append({"type": "gain_dip_artifact", "measurement": f"no unexplained applied-gain shape deviation >={threshold_db:g} dB lasting >={min_duration:g}s", "target": "processed-minus-raw follows declared gain without reshaping source expression", "status": "pass", "failure_class": None, "next_action": "none"})
    return rows


def _declared_transition_neighborhood(t: float, segments: list[dict[str, Any]], *, meter_memory_seconds: float = 0.5) -> bool:
    for left, right in zip(segments, segments[1:]):
        boundary = float(left.get("end_seconds") or right.get("start_seconds") or 0.0)
        if float(left.get("ramp_out_seconds") or 0.0) <= 0.0 and float(right.get("ramp_in_seconds") or 0.0) <= 0.0:
            continue
        span = meter_memory_seconds + max(float(left.get("ramp_out_seconds") or 0.0), float(right.get("ramp_in_seconds") or 0.0))
        if boundary - span <= t <= boundary + span:
            return True
    return False


def _append_dip_row(rows: list[dict[str, Any]], start: float, end: float, worst: float, min_duration: float, direction: str) -> None:
    duration = end - start
    if duration >= min_duration:
        failure = "applied_gain_dip_artifact" if direction == "dip" else "applied_gain_shape_artifact"
        rows.append(_fail(failure, f"unexplained applied-gain {direction} {worst:.2f} dB from {start:.3f}..{end:.3f}s", "remove undeclared gain shaping or add a plan-explained ramp/overlay, then rerun render/verify", row_type="gain_dip_artifact"))


def _window_lufs(rows: list[dict[str, Any]], start: float, end: float) -> float | None:
    return power_mean_lufs([float(row["momentary_lufs"]) for row in rows if start <= float(row["time_seconds"]) < end])


def _true_peak_rows(curves: dict[str, list[dict[str, Any]]], rails: dict[str, Any], plan: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    limit = float(rails["true_peak_dbtp"]["max"])
    for label, curve in curves.items():
        values = [float(row.get("true_peak_dbtp", -120.0)) for row in curve if float(row.get("true_peak_dbtp", -120.0)) > -119.0]
        if not values:
            rows.append(_fail("true_peak_unmeasured", f"{label} true peak not reported by ffmpeg ebur128", "upgrade ffmpeg or rerun verify with ebur128 peak=true support", row_type="true_peak"))
            continue
        peak_row = max(curve, key=lambda row: float(row.get("true_peak_dbtp", -120.0)))
        peak = float(peak_row.get("true_peak_dbtp", -120.0))
        peak_time = float(peak_row.get("time_seconds", 0.0))
        peak_result = _row("true_peak", f"{label} true peak {peak:.3f} dBTP near {peak_time:.3f}s", f"<= {limit} dBTP", peak <= limit, "true_peak_exceeded", _peak_next_action(plan or {}, label, peak_time, "true"))
        peak_result.update({"component": label, "event_seconds": peak_time, "true_peak_dbtp": rounded(peak, 6)})
        rows.append(peak_result)
    return rows


def _bed_presence_tier(win: dict[str, Any], regime: dict[str, Any]) -> str:
    tier = win.get("bed_presence_tier")
    if tier in {"meaningful", "marginal", "absent"}:
        return str(tier)
    if "meaningful" in win:
        return "meaningful" if win.get("meaningful") else ("marginal" if win.get("bed_present") else "absent")
    bed_body = regime.get("bed_body", {}).get("raw_bed_body_lufs") if isinstance(regime.get("bed_body"), dict) else None
    bed_lufs = win.get("bed_lufs")
    if bed_body is not None and bed_lufs is not None:
        meaningful_threshold = max(float(bed_body) - 10.0, -45.0)
        if float(bed_lufs) >= meaningful_threshold:
            return "meaningful"
        return "marginal" if win.get("bed_present") else "absent"
    return "meaningful" if win.get("bed_present") else "absent"


def _peak_control_rows(
    analysis: dict[str, Any],
    pre_body_curve: list[dict[str, Any]],
    post_body_curve: list[dict[str, Any]],
    pre_power_curve: list[dict[str, Any]],
    post_power_curve: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    del pre_body_curve, post_body_curve
    rows: list[dict[str, Any]] = []
    config = load_default_rails()["peak_control_accounting"]
    attenuation_threshold = float(config["controlled_attenuation_threshold_db"])
    body_delta_limit = float(config["max_body_energy_delta_db_per_regime"])
    global_duty_limit = float(config["max_global_duty_fraction"])
    regime_duty_limit = float(config["max_regime_duty_fraction"])
    contiguous_limit = float(config["max_contiguous_controlled_seconds"])
    attenuation_limit = float(config["max_per_bin_attenuation_db"])
    speech_windows = analysis.get("speech_windows", [])
    windows_by_regime = {
        str(regime.get("id")): [win for win in speech_windows if win.get("regime_id") == regime.get("id")]
        for regime in analysis.get("regimes", [])
    }
    post_by_bin = {(round(float(row["time_seconds"]), 6), round(float(row["end_seconds"]), 6)): row for row in post_power_curve}
    regime_stats = {
        regime_id: {"active": 0.0, "changed": 0.0, "pre_energy": 0.0, "post_energy": 0.0}
        for regime_id in windows_by_regime
    }
    active_seconds = 0.0
    changed_seconds = 0.0
    max_attenuation = 0.0
    max_attenuation_time = 0.0
    max_attenuation_regime: str | None = None
    contiguous = 0.0
    max_contiguous = 0.0
    previous_control_end: float | None = None
    for pre in pre_power_curve:
        key = (round(float(pre["time_seconds"]), 6), round(float(pre["end_seconds"]), 6))
        post = post_by_bin.get(key)
        if post is None:
            continue
        start = float(pre["time_seconds"])
        end = float(pre["end_seconds"])
        overlap = _window_overlap_seconds(start, end, speech_windows)
        if overlap <= 0.0:
            continue
        active_seconds += overlap
        pre_db = power_to_db(float(pre.get("power") or 0.0))
        post_db = power_to_db(float(post.get("power") or 0.0))
        attenuation = max(0.0, pre_db - post_db)
        controlled = attenuation > attenuation_threshold + 1e-9
        if controlled:
            changed_seconds += overlap
            if previous_control_end is not None and start <= previous_control_end + 1e-6:
                contiguous += overlap
            else:
                contiguous = overlap
            previous_control_end = end
            max_contiguous = max(max_contiguous, contiguous)
        else:
            contiguous = 0.0
            previous_control_end = None
        if attenuation > max_attenuation:
            max_attenuation = attenuation
            max_attenuation_time = start
        for regime_id, windows in windows_by_regime.items():
            regime_overlap = _window_overlap_seconds(start, end, windows)
            if regime_overlap <= 0.0:
                continue
            stats = regime_stats[regime_id]
            stats["active"] += regime_overlap
            stats["pre_energy"] += float(pre.get("power") or 0.0) * regime_overlap
            stats["post_energy"] += float(post.get("power") or 0.0) * regime_overlap
            if controlled:
                stats["changed"] += regime_overlap
            if attenuation >= max_attenuation - 1e-12:
                max_attenuation_regime = regime_id

    for regime_id, stats in regime_stats.items():
        active = float(stats["active"])
        pre_body = power_to_db(float(stats["pre_energy"]) / active) if active > 0.0 else None
        post_body = power_to_db(float(stats["post_energy"]) / active) if active > 0.0 else None
        delta = abs(float(post_body) - float(pre_body)) if pre_body is not None and post_body is not None else math.inf
        body_row = _row("peak_control_body_delta", f"{regime_id} matched-bin pre {rounded(pre_body, 3)} dB; post {rounded(post_body, 3)} dB; silence-inclusive absolute delta {rounded(delta, 3)} dB", f"per-regime matched-bin BODY energy |post - pre| <= {body_delta_limit} dB", delta <= body_delta_limit + 1e-12, "peak_control_reshaped_body", "first raise the declared ceiling only up to the hard true-peak rail; if control remains broad, lower the shared mic target through an evidence-backed rails adjustment or use cited structural event trims, then rerun")
        body_row.update({"regime_id": regime_id, "body_delta_db": rounded(delta, 6), "pre_body_energy_db": rounded(pre_body, 6), "post_body_energy_db": rounded(post_body, 6)})
        rows.append(body_row)
        regime_duty = float(stats["changed"]) / active if active > 0.0 else 0.0
        duty_row = _row("peak_control_regime_duty", f"{regime_id} 100 ms attenuation >{attenuation_threshold} dB for {float(stats['changed']):.3f}/{active:.3f}s active speech; fraction {regime_duty:.4f}", f"per-regime control duty <= {regime_duty_limit}", regime_duty <= regime_duty_limit + 1e-12, "peak_control_duty_exceeded", "raise the declared peak-control ceiling or replace regime-concentrated limiting with structural event trims")
        duty_row.update({"regime_id": regime_id, "duty_fraction": rounded(regime_duty, 6)})
        rows.append(duty_row)
    duty = changed_seconds / active_seconds if active_seconds > 0.0 else 0.0
    global_row = _row("peak_control_duty", f"100 ms attenuation >{attenuation_threshold} dB for {changed_seconds:.3f}/{active_seconds:.3f}s active speech; fraction {duty:.4f}", f"global control duty <= {global_duty_limit}", duty <= global_duty_limit + 1e-12, "peak_control_duty_exceeded", "raise the declared peak-control ceiling or replace broad limiting with structural event trims, then rerun render/verify")
    global_row["duty_fraction"] = rounded(duty, 6)
    rows.append(global_row)
    contiguous_row = _row("peak_control_contiguous_run", f"maximum contiguous controlled active-speech run {max_contiguous:.3f}s", f"<= {contiguous_limit}s", max_contiguous <= contiguous_limit + 1e-12, "peak_control_contiguous_run_exceeded", "lower the shared mic target through an evidence-backed rails adjustment or replace sustained control with a cited structural event repair")
    contiguous_row["max_contiguous_seconds"] = rounded(max_contiguous, 6)
    rows.append(contiguous_row)
    attenuation_row = _row("peak_control_bin_attenuation", f"maximum matched-bin attenuation {max_attenuation:.3f} dB at {max_attenuation_time:.3f}s in {max_attenuation_regime}", f"<= {attenuation_limit} dB per 100 ms bin", max_attenuation <= attenuation_limit + 1e-12, "peak_control_reshaped_body", "raise the peak-control ceiling; deeper attenuation is not bounded peak shaving")
    attenuation_row.update({"max_attenuation_db": rounded(max_attenuation, 6), "event_seconds": rounded(max_attenuation_time, 6), "regime_id": max_attenuation_regime})
    rows.append(attenuation_row)
    rows.append({"type": "peak_control_post_control_basis", "measurement": "body, coverage, gap, transition, applied-gain dip, sample-peak, and true-peak gates use mic_component.wav after declared peak control", "target": "listener-heard post-control mic is the verification basis", "status": "pass", "failure_class": None, "next_action": "none"})
    return rows


def _window_overlap_seconds(start: float, end: float, windows: list[dict[str, Any]]) -> float:
    intervals = sorted(
        (max(start, float(win["start_seconds"])), min(end, float(win["end_seconds"])))
        for win in windows
        if min(end, float(win["end_seconds"])) > max(start, float(win["start_seconds"]))
    )
    total = 0.0
    cursor_start: float | None = None
    cursor_end: float | None = None
    for lo, hi in intervals:
        if cursor_start is None:
            cursor_start, cursor_end = lo, hi
        elif lo <= float(cursor_end) + 1e-12:
            cursor_end = max(float(cursor_end), hi)
        else:
            total += float(cursor_end) - float(cursor_start)
            cursor_start, cursor_end = lo, hi
    if cursor_start is not None:
        total += float(cursor_end) - float(cursor_start)
    return total


def _peak_control_summary(plan: dict[str, Any], manifest: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    config = plan.get("render", {}).get("peak_control") or {}
    enabled = config.get("enabled") is True
    if not enabled:
        return {"enabled": False}
    body = [row for row in rows if row.get("type") == "peak_control_body_delta" and row.get("body_delta_db") is not None]
    global_duty = next((row for row in rows if row.get("type") == "peak_control_duty"), {})
    regime_duty = [row for row in rows if row.get("type") == "peak_control_regime_duty" and row.get("duty_fraction") is not None]
    contiguous = next((row for row in rows if row.get("type") == "peak_control_contiguous_run"), {})
    components = manifest.get("components", {})
    return {
        "enabled": True,
        "mechanism": config.get("mechanism"),
        "declared_true_peak_ceiling_dbtp": float(config["true_peak_ceiling_dbtp"]),
        "pre_control_mic_sha256": components.get("mic_raw", {}).get("sha256"),
        "post_control_mic_sha256": components.get("mic", {}).get("sha256"),
        "worst_per_regime_body_delta_db": max((float(row["body_delta_db"]) for row in body), default=None),
        "global_duty_fraction": global_duty.get("duty_fraction"),
        "worst_regime_duty_fraction": max((float(row["duty_fraction"]) for row in regime_duty), default=None),
        "max_contiguous_controlled_run_seconds": contiguous.get("max_contiguous_seconds"),
    }


def _peak_next_action(plan: dict[str, Any], label: str, peak_time: float, peak_kind: str) -> str:
    enabled = (plan.get("render", {}).get("peak_control") or {}).get("enabled") is True
    if enabled and label in {"mic", "mix"}:
        return f"first lower/tune the declared mic peak-control ceiling for the {label} {peak_kind}-peak near {peak_time:.3f}s; second add a structural event trim with event_reason, then rerun plan-validate/render/verify"
    return f"add a structural exception trim over the offending {label} event near {peak_time:.3f}s with event_reason, then rerun plan-validate/render/verify"


def _read_curve(path: str | Path) -> list[dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _expected_gain_by_time(segments: list[dict[str, Any]], field: str):
    ordered = sorted(segments, key=lambda row: float(row.get("start_seconds") or 0.0))

    def gain_at(t: float) -> float:
        for pos, seg in enumerate(ordered):
            start = float(seg["start_seconds"])
            end = float(seg["end_seconds"])
            if not (start <= t < end):
                continue
            gain = _gain_value(seg, field, 0.0)
            prev = ordered[pos - 1] if pos > 0 else None
            next_seg = ordered[pos + 1] if pos + 1 < len(ordered) else None
            prev_gain = _gain_value(prev, field, gain) if prev is not None else gain
            if prev is not None and float(prev.get("ramp_out_seconds") or 0.0) > 0.0:
                prev_gain = gain
            next_gain = _gain_value(next_seg, field, gain) if next_seg is not None else gain
            ramp_in = max(0.0, min(float(seg.get("ramp_in_seconds") or 0.0), max(0.0, end - start)))
            ramp_out = max(0.0, min(float(seg.get("ramp_out_seconds") or 0.0), max(0.0, end - start - ramp_in)))
            if ramp_in > 0.0 and start <= t < start + ramp_in:
                return prev_gain + (gain - prev_gain) * ((t - start) / ramp_in)
            if ramp_out > 0.0 and end - ramp_out <= t < end:
                return gain + (next_gain - gain) * ((t - (end - ramp_out)) / ramp_out)
            return gain
        return 0.0

    return gain_at


def _gain_value(segment: dict[str, Any] | None, field: str, fallback: float) -> float:
    if segment is None:
        return fallback
    value = segment.get(field)
    return fallback if value is None else float(value)


def _raw_lane_segments(plan: dict[str, Any], lane: str) -> list[dict[str, Any]]:
    v2_key = f"{lane}_segments"
    if isinstance(plan.get(v2_key), list):
        return [row for row in plan[v2_key] if isinstance(row, dict)]
    return [row for row in plan.get("segments", []) if isinstance(row, dict)]


def _materialized_lane_segments(plan: dict[str, Any], lane: str, analysis: dict[str, Any]) -> list[dict[str, Any]]:
    materializer = getattr(plan_contract, "materialize_lane_segments", None)
    if callable(materializer):
        return materializer(plan, lane, analysis)
    gain_field = f"{lane}_gain_db"
    out: list[dict[str, Any]] = []
    for raw in _raw_lane_segments(plan, lane):
        row = dict(raw)
        if gain_field not in row and row.get("gain_db") is not None:
            row[gain_field] = row["gain_db"]
        out.append(row)
    return out


def _row(row_type: str, measurement: str, target: str, ok: bool, failure_class: str, next_action: str) -> dict[str, Any]:
    return {"type": row_type, "measurement": measurement, "target": target, "status": "pass" if ok else "fail", "failure_class": None if ok else failure_class, "next_action": "none" if ok else next_action}


def _fail(failure_class: str, measurement: str, next_action: str, *, row_type: str) -> dict[str, Any]:
    return {"type": row_type, "measurement": measurement, "target": "DESIGN.md verify contract", "status": "fail", "failure_class": failure_class, "next_action": next_action}


def _repair(manifest_path: Path, plan: dict[str, Any]) -> list[str]:
    plan_path = plan.get("path") or "<render_plan.json>"
    analysis = plan.get("analysis", {}).get("path", "<analysis.json>")
    return [
        f'python remix-voiceover/scripts/rv.py plan-validate --plan "{plan_path}" --analysis "{analysis}" --json-out "<plan_validation.json>"',
        f'python remix-voiceover/scripts/rv.py render --source "<source>" --plan "{plan_path}" --outdir "{manifest_path.parent}" --manifest-out "{manifest_path}"',
        f'python remix-voiceover/scripts/rv.py verify --manifest "{manifest_path}" --plan "{plan_path}" --analysis "{analysis}" --json-out "<promotion_manifest.json>"',
    ]
