from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Any

from .ffio import ebur128_curve, ffprobe_json, repair_analyze
from .laneprofile import correlation_report, profile_lane
from .probe import _duration, _streams
from .speech import BED_MEANINGFUL_FLOOR_LUFS, build_parameters, detect_level_regimes, detect_speech_and_regimes
from .util import RvError, db_to_power, quantile, read_json, refuse_output_alias, rounded, sha256_file, sha256_json, utc_now, write_json


def analyze_command(args: argparse.Namespace) -> int:
    media = Path(args.media)
    probe_path = Path(args.probe)
    json_out = Path(args.json_out)
    repair = repair_analyze(media, probe_path, json_out)
    refuse_output_alias(json_out, [media, probe_path], repair, label="analysis JSON output")
    probe = read_json(probe_path)
    source_hash = sha256_file(media)
    if source_hash != probe.get("source_sha256"):
        raise RvError(
            f"source hash mismatch: media sha256 {source_hash} != probe sha256 {probe.get('source_sha256')}",
            repair,
        )
    actual_probe = ffprobe_json(media, repair)
    actual_streams = _streams(actual_probe)
    actual_audio_streams = [row for row in actual_streams if row["codec_type"] == "audio"]
    actual_video_streams = [row for row in actual_streams if row["codec_type"] == "video"]
    _refuse_inventory_mismatch(probe.get("audio_streams", []), actual_audio_streams, repair)
    if not actual_audio_streams:
        raise RvError(
            "unsupported audio inventory: analyze requires at least 1 audio lane from fresh ffprobe; found 0",
            repair,
        )
    try:
        params, parameter_report = build_parameters(
            {
                "min_plateau_seconds": args.min_plateau_seconds,
                "step_min_db": args.step_min_db,
                "speech_threshold_below_body_db": args.speech_threshold_below_body_db,
            }
        )
    except ValueError as exc:
        raise RvError(str(exc), repair) from exc

    sidecar_dir = json_out.parent / f"{json_out.stem}_curves"
    curves: dict[int, list[dict[str, Any]]] = {}
    lane_profiles: list[dict[str, Any]] = []
    curve_sidecars: dict[str, str] = {}
    for stream in actual_audio_streams:
        audio_index = int(stream["audio_stream_index"])
        channels = int(stream.get("channels") or 2)
        csv_path = sidecar_dir / f"lane_{audio_index:02d}_momentary.csv"
        curve = ebur128_curve(media, audio_index, channels, csv_path, repair)
        curves[audio_index] = curve["rows"]
        curve_sidecars[str(audio_index)] = curve["csv_path"]
        lane_profiles.append(profile_lane(audio_index, curve["rows"], curve["csv_path"]) | {"canonical_decode": curve["canonical_format"]})

    corr = correlation_report(curves)
    existing_mix_indexes = sorted(
        int(row["audio_stream_index"]) for row in corr.get("existing_mix_candidates", []) if row.get("existing_mix_signature") is True
    )
    direct_lane_profiles = [row for row in lane_profiles if int(row["audio_stream_index"]) not in existing_mix_indexes]
    if not direct_lane_profiles:
        raise RvError("all audio lanes profile as existing mixes; no direct mic/bed lanes remain for analyze", repair)
    inferred_roles, inference_conflicts = _infer_roles(direct_lane_profiles, existing_mix_indexes)
    inferred_mic_index = int(inferred_roles["mic_streams"][0])
    inferred_bed_indexes = [int(index) for index in inferred_roles["bed_streams"]]
    confirmed_roles = _confirmed_roles_from_args(args, actual_audio_streams, repair)
    mic_indexes = confirmed_roles["mic_streams"] if confirmed_roles else [inferred_mic_index]
    bed_indexes = confirmed_roles["bed_streams"] if confirmed_roles else inferred_bed_indexes
    mic_curve = _summed_curve([curves[idx] for idx in mic_indexes])
    bed_curve = _summed_curve([curves[idx] for idx in bed_indexes]) if bed_indexes else None
    speech = detect_speech_and_regimes(mic_curve, bed_curve, params)
    _attach_regime_ids(speech)
    bed_levels = detect_level_regimes(bed_curve, params) if bed_curve else {"bed_regimes": [], "bed_step_candidates": [], "bed_body_bins": [], "method": "no direct bed lane selected"}
    bed_presence = _regime_bed_presence_rows(speech["regimes"], has_bed=bool(bed_indexes))
    bed_presence_windows = _window_bed_presence_rows(speech["regimes"], speech["speech_windows"], has_bed=bool(bed_indexes))
    _annotate_bed_regime_policies(bed_levels["bed_regimes"], bed_presence_windows, bed_curve or [])
    analysis_mode = "single-program-repair" if len(actual_audio_streams) == 1 and not bed_indexes else "separate-mic-bed-remix"
    if confirmed_roles:
        selected = set(mic_indexes + bed_indexes)
        active_roles = {
            **confirmed_roles,
            "excluded_existing_mix_streams": sorted(idx for idx in existing_mix_indexes if idx not in selected),
            "unknown_streams": sorted(set(curves) - selected - set(existing_mix_indexes)),
            "mode": analysis_mode,
            "role_basis": "caller/agent-confirmed stream roles validated against the fresh ffprobe inventory; analysis speech and bed measurements use exactly these lanes",
        }
        role_conflicts: list[dict[str, Any]] = []
    else:
        role_conflicts = [*_role_conflicts(existing_mix_indexes, inferred_mic_index, inferred_bed_indexes), *inference_conflicts]
        active_roles = inferred_roles if not role_conflicts else {
            "mic_streams": [],
            "bed_streams": [],
            "excluded_existing_mix_streams": existing_mix_indexes,
            "unknown_streams": sorted(set(inferred_roles.get("mic_streams", [])) | set(inferred_roles.get("bed_streams", [])) | set(inferred_roles.get("unknown_streams", []))),
            "mode": "unresolved-role-inventory",
            "role_basis": "role evidence is ambiguous; rerun analyze with confirmed mic and bed stream selectors before planning",
        }
    analysis: dict[str, Any] = {
        "schema_version": 1,
        "generated_at": utc_now(),
        "media_path": str(media),
        "source_sha256": source_hash,
        "source_lineage": {
            "probe_json": str(probe_path),
            "probe_sha256": sha256_json(probe),
            "source_sha256": source_hash,
            "hash_verified": True,
            "probe_inventory_verified_against_fresh_ffprobe": True,
        },
        "container_kind": "video" if actual_video_streams else "audio-only",
        "analysis_mode": analysis_mode,
        "duration_seconds": _duration(actual_probe),
        "parameters": parameter_report,
        "inferred_roles": inferred_roles,
        "analysis_roles": active_roles,
        "role_confirmation": "caller/agent-confirmed" if confirmed_roles else "analyzer-inferred",
        "role_conflicts": role_conflicts,
        "lane_profiles": sorted(lane_profiles, key=lambda row: row["audio_stream_index"]),
        "cross_lane_correlation": corr,
        "regimes": speech["regimes"],
        "step_candidates": speech["step_candidates"],
        "bed_regimes": bed_levels["bed_regimes"],
        "bed_step_candidates": bed_levels["bed_step_candidates"],
        "bed_body_bins": bed_levels["bed_body_bins"],
        "speech_windows": speech["speech_windows"],
        "bed_presence": bed_presence,
        "bed_presence_windows": bed_presence_windows,
        "curve_sidecars": curve_sidecars,
        "body_bins": speech["body_bins"],
        "method": {
            "lane_curve": "ffmpeg ebur128 metadata at 10 Hz after canonical 48 kHz stereo f32 processing",
            "duration_tolerance_note": "ebur128 metadata can truncate the tail by roughly one cadence row (~0.1-0.2 s); duration comparisons should tolerate that measurement tail.",
            "speech_detection": speech["method"],
            "bed_level_regimes": bed_levels["method"],
            "correlation": "Pearson correlation over aligned momentary power curves; existing-mix flag fits non-negative per-lane weights and marks only the best dominant fitted mix candidate",
            "dense_regime_note": "Sub-plateau dips shorter than the minimum plateau are verify-side density-hole concerns; analyze records windows and raw active extents but does not split those dips into regimes.",
            "clean_gain_headroom_method": "Reference gain uses the loudest final per-regime raw_speech_body_lufs; noise floor uses q20 of rows outside detected speech active extents.",
        },
    }
    if confirmed_roles:
        analysis["confirmed_roles"] = active_roles
    write_json(json_out, analysis)
    return 0


def _summed_curve(curves: list[list[dict[str, Any]]]) -> list[dict[str, Any]]:
    if not curves:
        return []
    n = min(len(curve) for curve in curves)
    out: list[dict[str, Any]] = []
    for pos in range(n):
        power = sum(db_to_power(float(curve[pos]["momentary_lufs"])) for curve in curves)
        row = curves[0][pos].copy()
        row["power"] = power
        row["momentary_lufs"] = rounded(10.0 * __import__("math").log10(power) if power > 0 else -120.0, 3)
        out.append(row)
    return out


def _attach_regime_ids(speech: dict[str, Any]) -> None:
    regimes = speech["regimes"]
    for win in speech["speech_windows"]:
        start = float(win["start_seconds"])
        for regime in regimes:
            if float(regime["start_seconds"]) <= start < float(regime["end_seconds"]) + 1e-6:
                win["regime_id"] = regime["id"]
                break


def _refuse_inventory_mismatch(probe_audio_streams: Any, actual_audio_streams: list[dict[str, Any]], repair: list[str]) -> None:
    if not isinstance(probe_audio_streams, list):
        raise RvError("probe inventory mismatch: probe audio_streams is not a list", repair)
    probe_inventory = [_inventory_row(row) for row in probe_audio_streams]
    actual_inventory = [_inventory_row(row) for row in actual_audio_streams]
    if probe_inventory != actual_inventory:
        raise RvError(
            f"probe inventory mismatch: probe audio inventory {probe_inventory} != fresh ffprobe inventory {actual_inventory}",
            repair,
        )


def _inventory_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "audio_stream_index": row.get("audio_stream_index"),
        "index": row.get("index"),
        "channels": row.get("channels"),
    }


def _confirmed_roles_from_args(
    args: argparse.Namespace,
    actual_audio_streams: list[dict[str, Any]],
    repair: list[str],
) -> dict[str, list[int]] | None:
    mic_arg = getattr(args, "mic_streams", None)
    bed_arg = getattr(args, "bed_streams", None)
    if mic_arg is None and bed_arg is None:
        return None
    if mic_arg is None or bed_arg is None:
        raise RvError("confirmed roles require both --mic-streams and --bed-streams", repair)
    mic_streams = _parse_stream_list(mic_arg, "--mic-streams", repair)
    bed_streams = _parse_stream_list(bed_arg, "--bed-streams", repair)
    if not mic_streams:
        raise RvError("confirmed roles require at least one mic stream", repair)
    available = {int(row["audio_stream_index"]) for row in actual_audio_streams}
    unknown = sorted((set(mic_streams) | set(bed_streams)) - available)
    if unknown:
        raise RvError(f"confirmed role stream indexes are absent from fresh ffprobe inventory: {unknown}; available: {sorted(available)}", repair)
    overlap = sorted(set(mic_streams) & set(bed_streams))
    if overlap:
        raise RvError(f"confirmed mic and bed roles overlap: {overlap}", repair)
    if not bed_streams and not (len(available) == 1 and set(mic_streams) == available):
        raise RvError("confirmed roles may use an empty --bed-streams only when the one available lane is selected as the single program/mic stream", repair)
    return {"mic_streams": mic_streams, "bed_streams": bed_streams}


def _parse_stream_list(raw: str, label: str, repair: list[str]) -> list[int]:
    if not str(raw).strip():
        return []
    indexes: list[int] = []
    for part in str(raw).split(","):
        token = part.strip()
        if token.startswith("0:a:"):
            token = token[4:]
        try:
            index = int(token)
        except ValueError as exc:
            raise RvError(f"{label} contains invalid audio stream selector {part!r}", repair) from exc
        if index < 0:
            raise RvError(f"{label} contains negative audio stream index {index}", repair)
        if index in indexes:
            raise RvError(f"{label} contains duplicate audio stream index {index}", repair)
        indexes.append(index)
    return indexes


def _infer_roles(
    direct_lane_profiles: list[dict[str, Any]],
    existing_mix_indexes: list[int],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    ordered = sorted(
        direct_lane_profiles,
        key=lambda row: (float(row.get("speech_shape_ratio") or 0.0), -int(row["audio_stream_index"])),
        reverse=True,
    )
    mic = int(ordered[0]["audio_stream_index"])
    if len(ordered) == 1:
        return (
            {
                "mic_streams": [mic],
                "bed_streams": [],
                "excluded_existing_mix_streams": existing_mix_indexes,
                "unknown_streams": [],
                "mode": "single-program-repair",
                "role_basis": "the only direct audio lane is treated as the repair program/mic component; no bed component is inferred",
            },
            [],
        )

    top_shape = float(ordered[0].get("speech_shape_ratio") or 0.0)
    second_shape = float(ordered[1].get("speech_shape_ratio") or 0.0)
    if len(ordered) > 2 or top_shape - second_shape < 0.05:
        unknown = sorted(int(row["audio_stream_index"]) for row in ordered)
        conflict = {
            "type": "ambiguous_direct_lane_roles",
            "audio_stream_indexes": unknown,
            "requires_resolution": True,
            "impact": "the direct-lane inventory is ambiguous; three or more direct lanes are never auto-summed, and two lanes require distinct speech-shape evidence",
            "speech_shape_margin": rounded(top_shape - second_shape, 4),
            "next_action": "rerun analyze with both --mic-streams and --bed-streams after isolated lane review",
        }
        return (
            {
                "mic_streams": [mic],
                "bed_streams": [],
                "excluded_existing_mix_streams": existing_mix_indexes,
                "unknown_streams": unknown,
                "mode": "unresolved-role-inventory",
                "role_basis": "highest speech-shape lane is only a measurement hypothesis; direct lanes remain unknown until confirmed",
            },
            [conflict],
        )

    beds = sorted(int(row["audio_stream_index"]) for row in ordered[1:])
    return (
        {
            "mic_streams": [mic],
            "bed_streams": beds,
            "excluded_existing_mix_streams": existing_mix_indexes,
            "unknown_streams": [],
            "mode": "separate-mic-bed-remix",
            "role_basis": "highest speech-shape direct lane selected as mic; existing-mix candidates excluded; only clearly separated remaining direct lanes summed as bed",
        },
        [],
    )


def _role_conflicts(existing_mix_indexes: list[int], mic_index: int, bed_indexes: list[int]) -> list[dict[str, Any]]:
    conflicts: list[dict[str, Any]] = []
    for idx in existing_mix_indexes:
        conflicts.append(
            {
                "type": "existing_mix_lane_requires_role_resolution",
                "audio_stream_index": idx,
                "requires_resolution": True,
                "impact": "excluded from direct bed summation because it appears to contain a fitted mix of other lanes",
                "current_direct_roles": {"mic_streams": [mic_index], "bed_streams": bed_indexes},
            }
        )
    return conflicts


def _regime_bed_presence_rows(regimes: list[dict[str, Any]], *, has_bed: bool) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for regime in regimes:
        bed = regime.get("bed_body")
        if has_bed and isinstance(bed, dict):
            rows.append({"regime_id": regime["id"]} | bed)
        else:
            rows.append(
                {
                    "regime_id": regime["id"],
                    "raw_bed_body_lufs": None,
                    "noise_floor_lufs": None,
                    "basis": "no direct bed lanes available after existing-mix exclusion" if not has_bed else "bed analysis unavailable",
                    "presence_rule": {
                        "threshold_lufs": None,
                        "minimum_lufs": -60.0,
                        "present_speech_windows": 0,
                        "total_speech_windows": 0,
                        "bed_present": False,
                        "meaningful_threshold_lufs": None,
                        "meaningful_speech_windows": 0,
                        "marginal_speech_windows": 0,
                    },
                }
            )
    return rows


def _annotate_bed_regime_policies(
    bed_regimes: list[dict[str, Any]],
    presence_windows: list[dict[str, Any]],
    bed_curve: list[dict[str, Any]],
) -> None:
    """Preserve very quiet bed plateaus when available evidence cannot justify gain."""
    for regime in bed_regimes:
        start = float(regime.get("start_seconds") or 0.0)
        end = float(regime.get("end_seconds") or start)
        contained: list[dict[str, Any]] = []
        boundary_censored = 0
        for window in presence_windows:
            win_start = float(window.get("start_seconds") or 0.0)
            win_end = float(window.get("end_seconds") or win_start)
            if win_end <= start or win_start >= end:
                continue
            if win_start >= start - 0.001 and win_end <= end + 0.001:
                contained.append(window)
            else:
                boundary_censored += 1
        counts = {tier: sum(1 for row in contained if row.get("bed_presence_tier") == tier) for tier in ("meaningful", "marginal", "absent")}
        curve_evidence = _bed_curve_policy_evidence(bed_curve, start, end)
        raw_body = regime.get("raw_bed_body_lufs")
        low_body = raw_body is None or (math.isfinite(float(raw_body)) and float(raw_body) < BED_MEANINGFUL_FLOOR_LUFS)
        no_window_activity = counts["meaningful"] == 0 and counts["marginal"] == 0
        complete_curve = bool(curve_evidence["coverage_complete"])
        no_curve_activity = float(curve_evidence["meaningful_active_seconds"]) <= 0.001
        preserve = low_body and no_window_activity and no_curve_activity and complete_curve
        indeterminate = low_body and no_window_activity and not preserve
        regime["stitching_policy"] = (
            "preserve-unity-low-confidence"
            if preserve
            else ("hold-unity-indeterminate" if indeterminate else "stitchable")
        )
        regime["stitching_policy_evidence"] = {
            "full_regime_raw_bed_body_lufs": raw_body,
            "meaningful_floor_lufs": BED_MEANINGFUL_FLOOR_LUFS,
            "contained_speech_windows": len(contained),
            "meaningful_speech_windows": counts["meaningful"],
            "marginal_speech_windows": counts["marginal"],
            "absent_speech_windows": counts["absent"],
            "boundary_censored_speech_windows": boundary_censored,
            "curve": curve_evidence,
            "basis": "full independent bed-regime body, clipped 10 Hz bed-curve activity, and speech windows wholly contained inside that bed regime",
        }


def _bed_curve_policy_evidence(bed_curve: list[dict[str, Any]], start: float, end: float) -> dict[str, Any]:
    duration = max(0.0, end - start)
    intervals: list[tuple[float, float]] = []
    meaningful_seconds = 0.0
    longest_meaningful_run = 0.0
    current_run = 0.0
    previous_end: float | None = None
    values: list[float] = []
    for row in bed_curve:
        row_start = float(row.get("time_seconds") or 0.0)
        row_end = float(row.get("end_seconds") or (row_start + 0.1))
        overlap = max(0.0, min(end, row_end) - max(start, row_start))
        if overlap <= 0.0:
            continue
        value = float(row.get("momentary_lufs", -120.0))
        if not math.isfinite(value):
            current_run = 0.0
            continue
        clipped_start = max(start, row_start)
        clipped_end = min(end, row_end)
        intervals.append((clipped_start, clipped_end))
        values.append(value)
        if value >= BED_MEANINGFUL_FLOOR_LUFS:
            if previous_end is None or clipped_start - previous_end > 0.15:
                current_run = 0.0
            meaningful_seconds += overlap
            current_run += overlap
            longest_meaningful_run = max(longest_meaningful_run, current_run)
        else:
            current_run = 0.0
        previous_end = clipped_end
    merged: list[list[float]] = []
    overlap_seconds = 0.0
    for interval_start, interval_end in sorted(intervals):
        if not merged or interval_start > merged[-1][1] + 0.001:
            merged.append([interval_start, interval_end])
        else:
            overlap_seconds += max(0.0, min(merged[-1][1], interval_end) - interval_start)
            merged[-1][1] = max(merged[-1][1], interval_end)
    covered = sum(interval_end - interval_start for interval_start, interval_end in merged)
    internal_gaps = [right[0] - left[1] for left, right in zip(merged, merged[1:])]
    leading_gap = merged[0][0] - start if merged else duration
    trailing_gap = end - merged[-1][1] if merged else duration
    maximum_internal_gap = max(internal_gaps, default=0.0)
    coverage_ratio = covered / duration if duration > 0.0 else 0.0
    coverage_complete = coverage_ratio >= 0.98 and leading_gap <= 0.15 and trailing_gap <= 0.2 and maximum_internal_gap <= 0.15 and overlap_seconds <= 0.001
    return {
        "coverage_seconds": rounded(covered, 3),
        "coverage_ratio": rounded(coverage_ratio, 6),
        "coverage_complete": coverage_complete,
        "leading_gap_seconds": rounded(leading_gap, 3),
        "trailing_gap_seconds": rounded(trailing_gap, 3),
        "maximum_internal_gap_seconds": rounded(maximum_internal_gap, 3),
        "overlap_seconds": rounded(overlap_seconds, 3),
        "upper_tail_lufs": rounded(quantile(values, 0.99), 3),
        "maximum_lufs": rounded(max(values), 3) if values else None,
        "meaningful_active_seconds": rounded(meaningful_seconds, 3),
        "longest_meaningful_run_seconds": rounded(longest_meaningful_run, 3),
        "meaningful_floor_lufs": BED_MEANINGFUL_FLOOR_LUFS,
    }


def _window_bed_presence_rows(
    regimes: list[dict[str, Any]],
    speech_windows: list[dict[str, Any]],
    *,
    has_bed: bool,
) -> list[dict[str, Any]]:
    if has_bed:
        rows: list[dict[str, Any]] = []
        for regime in regimes:
            rows.extend(regime.get("bed_presence_windows", []))
        return rows
    return [
        {
            "window_id": win.get("id"),
            "regime_id": win.get("regime_id"),
            "start_seconds": win["start_seconds"],
            "end_seconds": win["end_seconds"],
            "bed_present": False,
            "bed_presence_tier": "absent",
            "meaningful": False,
            "bed_lufs": None,
            "basis": "no direct bed lanes available after existing-mix exclusion",
            "presence_rule": {"threshold_lufs": None, "minimum_lufs": -60.0, "meaningful_threshold_lufs": None},
        }
        for win in speech_windows
    ]
