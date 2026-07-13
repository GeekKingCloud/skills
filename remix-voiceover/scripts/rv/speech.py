from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from .util import power_mean_lufs, quantile, rounded, weighted_median


BED_MEANINGFUL_FLOOR_LUFS = -45.0


@dataclass(frozen=True)
class AnalyzeParameters:
    min_plateau_seconds: float = 120.0
    step_min_db: float = 10.0
    speech_threshold_below_body_db: float = 12.0
    bin_seconds: float = 30.0
    min_window_seconds: float = 1.0
    merge_gap_seconds: float = 0.4
    noise_floor_percentile: float = 0.20
    speech_body_percentile: float = 0.75
    bed_presence_floor_margin_db: float = 6.0
    clean_noise_floor_target_lufs: float = -45.0


PARAMETER_BOUNDS = {
    "min_plateau_seconds": [20.0, 180.0],
    "step_min_db": [6.0, 24.0],
    "speech_threshold_below_body_db": [6.0, 20.0],
}


def build_parameters(overrides: dict[str, float | None]) -> tuple[AnalyzeParameters, dict[str, Any]]:
    defaults = AnalyzeParameters()
    values = defaults.__dict__.copy()
    recorded: dict[str, Any] = {}
    for name, bounds in PARAMETER_BOUNDS.items():
        raw = overrides.get(name)
        default_value = getattr(defaults, name)
        value = default_value if raw is None else float(raw)
        lo, hi = bounds
        if not math.isfinite(value) or value < lo or value > hi:
            raise ValueError(f"{name}={value} outside bounds {lo}..{hi}")
        values[name] = value
        recorded[name] = {"default": default_value, "value": value, "bounds": bounds, "overridden": raw is not None}
    for name in (
        "bin_seconds",
        "min_window_seconds",
        "merge_gap_seconds",
        "noise_floor_percentile",
        "speech_body_percentile",
        "bed_presence_floor_margin_db",
        "clean_noise_floor_target_lufs",
    ):
        recorded[name] = {"default": getattr(defaults, name), "value": getattr(defaults, name), "bounds": None, "overridden": False}
    return AnalyzeParameters(**values), recorded


def detect_speech_and_regimes(
    mic_rows: list[dict[str, Any]],
    bed_rows: list[dict[str, Any]] | None,
    params: AnalyzeParameters,
) -> dict[str, Any]:
    provisional = _provisional_active(mic_rows)
    bins = _body_bins(mic_rows, provisional, params)
    step_candidates = _step_candidates(mic_rows, bins, params)
    regimes = _regimes_from_steps(mic_rows, bins, step_candidates, params)
    speech_windows: list[dict[str, Any]] = []
    window_counter = 1
    for regime in regimes:
        windows = _speech_windows_for_regime(mic_rows, regime["start_seconds"], regime["end_seconds"], params)
        for win in windows:
            win["regime_id"] = regime["id"]
            win["id"] = f"w{window_counter:04d}"
            win["raw_mic_window_lufs"] = rounded(
                power_mean_lufs(_values_between(mic_rows, float(win["start_seconds"]), float(win["end_seconds"]))),
                3,
            )
            win["raw_mic_window_lufs_basis"] = "power mean of raw direct-mic momentary rows over the detected speech window"
            window_counter += 1
        speech_windows.extend(windows)
        body = weighted_median(
            (float(win["raw_mic_window_lufs"]), float(win.get("duration_seconds") or 0.0))
            for win in windows
            if win.get("raw_mic_window_lufs") is not None
        )
        active_seconds = sum(win["end_seconds"] - win["start_seconds"] for win in windows)
        floor = _noise_floor_outside_windows(mic_rows, regime["start_seconds"], regime["end_seconds"], windows, params)
        regime["_noise_floor_for_headroom_lufs"] = floor
        max_clean_gain = max(0.0, params.clean_noise_floor_target_lufs - (floor or -120.0))
        regime.update(
            {
                "raw_speech_body_lufs": rounded(body, 3),
                "active_speech_seconds": rounded(active_seconds, 3),
                "active_speech_density": rounded(active_seconds / max(regime["end_seconds"] - regime["start_seconds"], 0.1), 4),
                "noise_floor_lufs": rounded(floor, 3),
                "_max_clean_gain_before_noise_floor_target_db": max_clean_gain,
            }
        )
        if bed_rows is not None:
            regime["bed_body"], regime["bed_presence_windows"] = _bed_body_for_regime(bed_rows, windows, regime, params)
    _attach_clean_gain_headroom(regimes, params)
    for regime in regimes:
        regime.pop("_noise_floor_for_headroom_lufs", None)
        regime.pop("_max_clean_gain_before_noise_floor_target_db", None)
    return {
        "speech_windows": speech_windows,
        "regimes": regimes,
        "step_candidates": step_candidates,
        "body_bins": bins,
        "method": "two-pass global provisional activity, sustained body bins, then per-regime thresholds relative to each regime speech body",
    }


def detect_level_regimes(rows: list[dict[str, Any]], params: AnalyzeParameters) -> dict[str, Any]:
    """Detect sustained bed capture-level changes independently from mic speech regimes."""
    bins = _level_bins(rows, params)
    steps = _level_step_candidates(rows, bins, params)
    duration = float(rows[-1]["end_seconds"]) if rows else 0.0
    boundaries = [0.0, *[float(step["boundary_seconds"]) for step in steps], duration]
    regimes: list[dict[str, Any]] = []
    for idx, (start, end) in enumerate(zip(boundaries, boundaries[1:]), start=1):
        if end - start <= 0.2:
            continue
        values = _values_between(rows, start, end)
        regimes.append(
            {
                "id": f"b{idx:03d}",
                "start_seconds": round(start, 3),
                "end_seconds": round(end, 3),
                "duration_seconds": round(end - start, 3),
                "raw_bed_body_lufs": rounded(weighted_median((value, 0.1) for value in values), 3),
                "source": "detected_sustained_bed_level_step" if len(boundaries) > 2 else "whole_file",
            }
        )
    return {
        "bed_regimes": regimes,
        "bed_step_candidates": steps,
        "bed_body_bins": bins,
        "method": "independent 30 s duration-weighted-median bed-level bins with sustained-step refinement; mic speech regimes are unchanged",
    }


def _level_bins(rows: list[dict[str, Any]], params: AnalyzeParameters) -> list[dict[str, Any]]:
    duration = float(rows[-1]["end_seconds"]) if rows else 0.0
    bins: list[dict[str, Any]] = []
    start = 0.0
    while start < duration - 1e-6:
        end = min(start + params.bin_seconds, duration)
        values = _values_between(rows, start, end)
        bins.append(
            {
                "start_seconds": round(start, 3),
                "end_seconds": round(end, 3),
                "level_lufs": rounded(weighted_median((value, 0.1) for value in values), 3),
                "measured_seconds": rounded(len(values) * 0.1, 3),
            }
        )
        start = end
    return bins


def _level_step_candidates(
    rows: list[dict[str, Any]],
    bins: list[dict[str, Any]],
    params: AnalyzeParameters,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for idx in range(1, len(bins)):
        before = bins[idx - 1].get("level_lufs")
        after = bins[idx].get("level_lufs")
        if before is None or after is None:
            continue
        delta = float(after) - float(before)
        if abs(delta) < params.step_min_db:
            continue
        before_len = _level_plateau_length(bins, idx - 1, -1, float(before), params.step_min_db / 2.0)
        after_len = _level_plateau_length(bins, idx, 1, float(after), params.step_min_db / 2.0)
        coarse = float(bins[idx]["start_seconds"])
        duration = float(bins[-1]["end_seconds"])
        if not _sustained_on_both_sides_or_edge_censored(before_len, after_len, coarse, duration, params, bins, idx, "level_lufs", float(before), float(after), delta):
            continue
        boundary, refined_delta = _refine_level_step_boundary(rows, coarse, "rise" if delta > 0.0 else "drop", params)
        candidates.append(
            {
                "boundary_seconds": boundary,
                "direction": "rise" if delta > 0.0 else "drop",
                "step_db": rounded(refined_delta if refined_delta is not None else delta, 3),
                "before_plateau_seconds": rounded(before_len, 3),
                "after_plateau_seconds": rounded(after_len, 3),
                "min_plateau_seconds": params.min_plateau_seconds,
                "evidence": {
                    "before_bin": bins[idx - 1],
                    "after_bin": bins[idx],
                    "level_curve": "30 s binned direct-bed power-mean curve",
                    "coarse_boundary_seconds": coarse,
                    "boundary_refined": refined_delta is not None,
                },
            }
        )
    return candidates


def _level_plateau_length(bins: list[dict[str, Any]], start_idx: int, direction: int, reference: float, tolerance: float) -> float:
    total = 0.0
    idx = start_idx
    while 0 <= idx < len(bins):
        level = bins[idx].get("level_lufs")
        if level is None or abs(float(level) - reference) > tolerance:
            break
        total += float(bins[idx]["end_seconds"]) - float(bins[idx]["start_seconds"])
        idx += direction
    return total


def _refine_level_step_boundary(
    rows: list[dict[str, Any]],
    coarse_boundary: float,
    direction: str,
    params: AnalyzeParameters,
) -> tuple[float, float | None]:
    start = max(0.0, coarse_boundary - params.bin_seconds)
    end = coarse_boundary + params.bin_seconds
    scoped = [row for row in rows if start <= float(row["time_seconds"]) < end and math.isfinite(float(row["momentary_lufs"])) and float(row["momentary_lufs"]) > -119.0]
    best: tuple[float, float, float] | None = None
    for row in scoped:
        split = float(row["time_seconds"])
        before = power_mean_lufs(float(item["momentary_lufs"]) for item in scoped if float(item["time_seconds"]) < split)
        after = power_mean_lufs(float(item["momentary_lufs"]) for item in scoped if float(item["time_seconds"]) >= split)
        before_count = sum(1 for item in scoped if float(item["time_seconds"]) < split)
        after_count = len(scoped) - before_count
        if before is None or after is None or before_count < 5 or after_count < 5:
            continue
        delta = after - before
        if (direction == "drop" and delta >= 0.0) or (direction == "rise" and delta <= 0.0):
            continue
        score = abs(delta)
        if score < params.step_min_db:
            continue
        distance = abs(split - coarse_boundary)
        if best is None or score > best[0] + 0.05 or (abs(score - best[0]) <= 0.05 and distance < abs(best[1] - coarse_boundary)):
            best = (score, split, delta)
    if best is None:
        return round(coarse_boundary, 3), None
    return round(best[1], 3), best[2]


def _provisional_active(rows: list[dict[str, Any]]) -> list[bool]:
    vals = [float(row["momentary_lufs"]) for row in rows if float(row["momentary_lufs"]) > -119.0]
    floor = quantile(vals, 0.20) or -100.0
    body = quantile(vals, 0.90) or floor
    threshold = floor + max(6.0, (body - floor) * 0.35)
    return [float(row["momentary_lufs"]) >= threshold for row in rows]


def _body_bins(rows: list[dict[str, Any]], provisional: list[bool], params: AnalyzeParameters) -> list[dict[str, Any]]:
    duration = rows[-1]["end_seconds"] if rows else 0.0
    out: list[dict[str, Any]] = []
    start = 0.0
    while start < duration - 1e-6:
        end = min(start + params.bin_seconds, duration)
        vals = [
            float(row["momentary_lufs"])
            for pos, row in enumerate(rows)
            if start <= float(row["time_seconds"]) < end and pos < len(provisional) and provisional[pos] and float(row["momentary_lufs"]) > -119.0
        ]
        fallback = [float(row["momentary_lufs"]) for row in rows if start <= float(row["time_seconds"]) < end and float(row["momentary_lufs"]) > -119.0]
        floor = quantile(fallback, params.noise_floor_percentile)
        body = quantile(vals, params.speech_body_percentile) if len(vals) >= 3 else quantile(fallback, 0.85)
        active_seconds = len(vals) * 0.1
        speech_detected = body is not None and floor is not None and active_seconds >= 0.3 and (body - floor) >= 6.0
        out.append(
            {
                "start_seconds": round(start, 3),
                "end_seconds": round(end, 3),
                "speech_body_lufs": rounded(body, 3) if speech_detected else None,
                "speech_detected": speech_detected,
                "active_seconds": rounded(active_seconds, 3),
                "noise_floor_lufs": rounded(floor, 3),
            }
        )
        start = end
    return out


def _step_candidates(rows: list[dict[str, Any]], bins: list[dict[str, Any]], params: AnalyzeParameters) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for idx in range(1, len(bins)):
        before = bins[idx - 1].get("speech_body_lufs")
        after = bins[idx].get("speech_body_lufs")
        if not bins[idx - 1].get("speech_detected") or not bins[idx].get("speech_detected"):
            continue
        if before is None or after is None:
            continue
        delta = float(after) - float(before)
        if abs(delta) < params.step_min_db:
            continue
        before_len = _plateau_length(bins, idx - 1, -1, before, params.step_min_db / 2.0)
        after_len = _plateau_length(bins, idx, 1, after, params.step_min_db / 2.0)
        coarse_boundary = float(bins[idx]["start_seconds"])
        duration = float(bins[-1]["end_seconds"])
        sustained = _sustained_on_both_sides_or_edge_censored(before_len, after_len, coarse_boundary, duration, params, bins, idx, "speech_body_lufs", float(before), float(after), delta)
        if sustained:
            refined_boundary, refined_delta = _refine_step_boundary(rows, coarse_boundary, "rise" if delta > 0 else "drop", params, delta)
            candidates.append(
                {
                    "boundary_seconds": refined_boundary,
                    "direction": "rise" if delta > 0 else "drop",
                    "step_db": rounded(refined_delta if refined_delta is not None else delta, 3),
                    "before_plateau_seconds": rounded(before_len, 3),
                    "after_plateau_seconds": rounded(after_len, 3),
                    "min_plateau_seconds": params.min_plateau_seconds,
                    "evidence": {
                        "before_bin": bins[idx - 1],
                        "after_bin": bins[idx],
                        "body_curve": "30 s binned speech-body curve",
                        "coarse_boundary_seconds": coarse_boundary,
                        "boundary_refined": refined_delta is not None,
                        "boundary_refinement_method": "10 Hz sliding split within +/-1 body bin using the earliest sustained near-maximum local 5 s q75 contrast group",
                        "refined_window_seconds": [round(max(0.0, coarse_boundary - params.bin_seconds), 3), round(coarse_boundary + params.bin_seconds, 3)],
                    },
                }
            )
    return candidates


def _sustained_on_both_sides_or_edge_censored(
    before_len: float,
    after_len: float,
    boundary: float,
    duration: float,
    params: AnalyzeParameters,
    bins: list[dict[str, Any]],
    split_index: int,
    field: str,
    before_reference: float,
    after_reference: float,
    delta: float,
) -> bool:
    """Require two sustained sides, except a real plateau clipped by file start/end."""
    before_full = before_len >= params.min_plateau_seconds
    after_full = after_len >= params.min_plateau_seconds
    if before_full and after_full:
        return True
    edge_floor = min(params.min_plateau_seconds, params.bin_seconds)
    sign = 1.0 if delta > 0.0 else -1.0
    after_directional = _directional_sustained_seconds(bins, split_index, 1, field, before_reference, sign, params)
    before_directional = _directional_sustained_seconds(bins, split_index - 1, -1, field, after_reference, -sign, params)
    if before_directional >= params.min_plateau_seconds and after_directional >= params.min_plateau_seconds:
        return True
    before_reaches_start = (
        before_len >= edge_floor and before_len >= boundary - 0.001
    ) or (
        before_directional >= edge_floor and before_directional >= boundary - 0.001
    )
    after_reaches_end = (
        after_len >= edge_floor and after_len >= (duration - boundary) - 0.001
    ) or (
        after_directional >= edge_floor and after_directional >= (duration - boundary) - 0.001
    )
    return (
        before_reaches_start and after_directional >= params.min_plateau_seconds
    ) or (
        after_reaches_end and before_directional >= params.min_plateau_seconds
    )


def _directional_sustained_seconds(
    bins: list[dict[str, Any]],
    start_index: int,
    direction: int,
    field: str,
    reference: float,
    sign: float,
    params: AnalyzeParameters,
) -> float:
    total = 0.0
    index = start_index
    while 0 <= index < len(bins):
        value = bins[index].get(field)
        if value is None or sign * (float(value) - reference) < params.step_min_db:
            break
        total += float(bins[index]["end_seconds"]) - float(bins[index]["start_seconds"])
        index += direction
    return total


def _refine_step_boundary(
    rows: list[dict[str, Any]],
    coarse_boundary: float,
    direction: str,
    params: AnalyzeParameters,
    expected_delta: float | None = None,
) -> tuple[float, float | None]:
    start = max(0.0, coarse_boundary - params.bin_seconds)
    end = coarse_boundary + params.bin_seconds
    scoped = [row for row in rows if start <= float(row["time_seconds"]) < end and float(row["momentary_lufs"]) > -119.0]
    candidates: list[tuple[float, float, float]] = []
    local_span = 5.0
    for row in scoped:
        split = float(row["time_seconds"])
        before_vals = [float(item["momentary_lufs"]) for item in scoped if split - local_span <= float(item["time_seconds"]) < split]
        after_vals = [float(item["momentary_lufs"]) for item in scoped if split <= float(item["time_seconds"]) < split + local_span]
        if len(before_vals) < 50 or len(after_vals) < 50:
            continue
        before = quantile(before_vals, 0.75)
        after = quantile(after_vals, 0.75)
        if before is None or after is None:
            continue
        delta = after - before
        if (direction == "drop" and delta >= 0.0) or (direction == "rise" and delta <= 0.0):
            continue
        score = abs(delta)
        if score < params.step_min_db:
            continue
        candidates.append((score, split, delta))
    if not candidates:
        return round(coarse_boundary, 3), None
    chosen_group = _earliest_supported_change_group(candidates, expected_delta)
    split = (chosen_group[0][1] + chosen_group[-1][1]) / 2.0
    chosen = min(chosen_group, key=lambda item: abs(item[1] - split))
    return round(split, 3), chosen[2]


def _earliest_supported_change_group(
    candidates: list[tuple[float, float, float]],
    expected_delta: float | None,
) -> list[tuple[float, float, float]]:
    """Choose onset evidence without chasing one cadence-dependent contrast peak."""
    bounded = candidates
    if expected_delta is not None:
        expected = abs(float(expected_delta))
        upper = expected + max(3.0, expected * 0.5)
        plausible = [item for item in candidates if item[0] <= upper]
        if plausible:
            bounded = plausible
    max_score = max(item[0] for item in bounded)
    tolerance = min(3.0, max(1.0, max_score * 0.15))
    near_peak = sorted((item for item in bounded if max_score - item[0] <= tolerance), key=lambda item: item[1])
    groups: list[list[tuple[float, float, float]]] = []
    for item in near_peak:
        if not groups or item[1] > groups[-1][-1][1] + 0.11:
            groups.append([item])
        else:
            groups[-1].append(item)
    sustained = [group for group in groups if group[-1][1] - group[0][1] >= 0.4]
    return (sustained or groups)[0]


def _plateau_length(bins: list[dict[str, Any]], start_idx: int, direction: int, reference: float, tolerance: float) -> float:
    total = 0.0
    idx = start_idx
    while 0 <= idx < len(bins):
        body = bins[idx].get("speech_body_lufs")
        if body is None or abs(float(body) - float(reference)) > tolerance:
            break
        total += float(bins[idx]["end_seconds"]) - float(bins[idx]["start_seconds"])
        idx += direction
    return total


def _regimes_from_steps(
    rows: list[dict[str, Any]],
    bins: list[dict[str, Any]],
    steps: list[dict[str, Any]],
    params: AnalyzeParameters,
) -> list[dict[str, Any]]:
    duration = rows[-1]["end_seconds"] if rows else 0.0
    boundaries = [0.0] + [float(step["boundary_seconds"]) for step in steps] + [duration]
    regimes: list[dict[str, Any]] = []
    for idx, (start, end) in enumerate(zip(boundaries, boundaries[1:]), start=1):
        if end - start <= 0.2:
            continue
        regimes.append(
            {
                "id": f"r{idx:03d}",
                "start_seconds": round(start, 3),
                "end_seconds": round(end, 3),
                "duration_seconds": round(end - start, 3),
                "source": "detected_sustained_step" if len(boundaries) > 2 else "whole_file",
            }
        )
    return regimes


def _speech_windows_for_regime(
    rows: list[dict[str, Any]],
    start: float,
    end: float,
    params: AnalyzeParameters,
) -> list[dict[str, Any]]:
    vals = _values_between(rows, start, end)
    if not vals:
        return []
    floor = quantile(vals, min(params.noise_floor_percentile, 0.10)) or -120.0
    body_seed = quantile(vals, 0.90) or floor
    threshold = max(floor + 5.0, body_seed - params.speech_threshold_below_body_db)
    active_rows = [row for row in rows if start <= float(row["time_seconds"]) < end and float(row["momentary_lufs"]) >= threshold]
    if active_rows:
        body = quantile([float(row["momentary_lufs"]) for row in active_rows], params.speech_body_percentile) or body_seed
        threshold = max(floor + 5.0, body - params.speech_threshold_below_body_db)
    windows = _merge_active_rows(
        [row for row in rows if start <= float(row["time_seconds"]) < end and float(row["momentary_lufs"]) >= threshold],
        params.merge_gap_seconds,
        params.min_window_seconds,
        start,
        end,
    )
    out: list[dict[str, Any]] = []
    for win_start, win_end, active_start, active_end in windows:
        out.append(
            {
                "regime_id": "",
                "start_seconds": win_start,
                "end_seconds": win_end,
                "duration_seconds": rounded(win_end - win_start, 3),
                "active_start_seconds": active_start,
                "active_end_seconds": active_end,
                "active_duration_seconds": rounded(active_end - active_start, 3),
                "padded_to_minimum_seconds": (win_start < active_start - 1e-6) or (win_end > active_end + 1e-6),
                "threshold_lufs": rounded(threshold, 3),
                "threshold_basis": "regime_relative_speech_body_minus_margin",
            }
        )
    return out


def _merge_active_rows(
    active_rows: list[dict[str, Any]],
    merge_gap: float,
    min_window: float,
    regime_start: float,
    regime_end: float,
) -> list[tuple[float, float, float, float]]:
    if not active_rows:
        return []
    windows: list[list[float]] = [[float(active_rows[0]["time_seconds"]), float(active_rows[0]["end_seconds"])]]
    for row in active_rows[1:]:
        start = float(row["time_seconds"])
        end = float(row["end_seconds"])
        if start <= windows[-1][1] + merge_gap:
            windows[-1][1] = max(windows[-1][1], end)
        else:
            windows.append([start, end])
    out: list[tuple[float, float, float, float]] = []
    for start, end in windows:
        active_start = start
        active_end = end
        if end - start < min_window:
            pad = (min_window - (end - start)) / 2.0
            start = max(regime_start, start - pad)
            end = min(regime_end, end + pad)
        if end - start >= min_window - 1e-6:
            out.append((round(start, 3), round(end, 3), round(active_start, 3), round(active_end, 3)))
    return out


def _values_between(rows: list[dict[str, Any]], start: float, end: float) -> list[float]:
    return [
        float(row["momentary_lufs"])
        for row in rows
        if start <= float(row["time_seconds"]) < end and float(row["momentary_lufs"]) > -119.0 and math.isfinite(float(row["momentary_lufs"]))
    ]


def _values_in_windows(rows: list[dict[str, Any]], windows: list[dict[str, Any]]) -> list[float]:
    vals: list[float] = []
    for win in windows:
        vals.extend(_values_between(rows, float(win["start_seconds"]), float(win["end_seconds"])))
    return vals


def _reference_gain(body: float | None, bins: list[dict[str, Any]]) -> float:
    bodies = [float(row["speech_body_lufs"]) for row in bins if row.get("speech_body_lufs") is not None]
    ref = max(bodies) if bodies else body
    if body is None or ref is None:
        return 0.0
    return max(0.0, ref - body)


def _attach_clean_gain_headroom(regimes: list[dict[str, Any]], params: AnalyzeParameters) -> None:
    bodies = [float(regime["raw_speech_body_lufs"]) for regime in regimes if regime.get("raw_speech_body_lufs") is not None]
    reference_body = max(bodies) if bodies else None
    for regime in regimes:
        body = regime.get("raw_speech_body_lufs")
        required_gain = max(0.0, float(reference_body) - float(body)) if body is not None and reference_body is not None else 0.0
        max_clean_gain = float(regime.get("_max_clean_gain_before_noise_floor_target_db") or 0.0)
        regime["clean_gain_headroom"] = {
            "reference_body_lufs": rounded(reference_body, 3),
            "reference_gain_to_loudest_regime_db": rounded(required_gain, 3),
            "reference_basis": "max per-regime raw_speech_body_lufs",
            "max_clean_gain_before_noise_floor_target_db": rounded(max_clean_gain, 3),
            "noise_floor_target_lufs": params.clean_noise_floor_target_lufs,
            "noise_floor_basis": "q20 of momentary rows outside detected speech windows",
            "margin_db": rounded(max_clean_gain - required_gain, 3),
            "preferred_target_limited_if_margin_negative": (max_clean_gain - required_gain) < 0.0,
        }


def _noise_floor_outside_windows(
    rows: list[dict[str, Any]],
    start: float,
    end: float,
    windows: list[dict[str, Any]],
    params: AnalyzeParameters,
) -> float | None:
    def outside_windows(row: dict[str, Any]) -> bool:
        row_start = float(row["time_seconds"])
        if not (start <= row_start < end):
            return False
        for win in windows:
            active_start = float(win.get("active_start_seconds", win["start_seconds"]))
            active_end = float(win.get("active_end_seconds", win["end_seconds"]))
            if active_start <= row_start < active_end:
                return False
        return True

    floor = quantile(
        [
            float(row["momentary_lufs"])
            for row in rows
            if outside_windows(row) and float(row["momentary_lufs"]) > -119.0 and math.isfinite(float(row["momentary_lufs"]))
        ],
        params.noise_floor_percentile,
    )
    if floor is not None:
        return floor
    return quantile(_values_between(rows, start, end), params.noise_floor_percentile)


def _bed_body_for_regime(
    bed_rows: list[dict[str, Any]],
    windows: list[dict[str, Any]],
    regime: dict[str, Any],
    params: AnalyzeParameters,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    all_vals = _values_between(bed_rows, float(regime["start_seconds"]), float(regime["end_seconds"]))
    floor = quantile(all_vals, params.noise_floor_percentile)
    body = weighted_median((value, 0.1) for value in all_vals)
    present_threshold = (floor or -120.0) + params.bed_presence_floor_margin_db
    meaningful_threshold = max((body if body is not None else -120.0) - 10.0, BED_MEANINGFUL_FLOOR_LUFS)
    present_windows = 0
    meaningful_windows = 0
    marginal_windows = 0
    window_rows: list[dict[str, Any]] = []
    for win in windows:
        vals = _values_between(bed_rows, float(win["start_seconds"]), float(win["end_seconds"]))
        win_body = power_mean_lufs(vals)
        bed_present = win_body is not None and win_body >= present_threshold and win_body > -60.0
        meaningful = win_body is not None and win_body >= meaningful_threshold
        tier = "meaningful" if meaningful else ("marginal" if bed_present else "absent")
        if bed_present:
            present_windows += 1
        if meaningful:
            meaningful_windows += 1
        elif bed_present:
            marginal_windows += 1
        window_rows.append(
            {
                "window_id": win.get("id"),
                "regime_id": win.get("regime_id"),
                "start_seconds": win["start_seconds"],
                "end_seconds": win["end_seconds"],
                "bed_present": bed_present,
                "bed_presence_tier": tier,
                "meaningful": meaningful,
                "bed_lufs": rounded(win_body, 3),
                "basis": "power mean of summed direct-bed lane momentary rows over speech window",
                "presence_rule": {
                    "threshold_lufs": rounded(present_threshold, 3),
                    "minimum_lufs": -60.0,
                    "meaningful_threshold_lufs": rounded(meaningful_threshold, 3),
                },
            }
        )
    return (
        {
            "raw_bed_body_lufs": rounded(body, 3),
            "noise_floor_lufs": rounded(floor, 3),
            "basis": "summed direct-bed lane momentary rows across regime",
            "presence_rule": {
                "threshold_lufs": rounded(present_threshold, 3),
                "minimum_lufs": -60.0,
                "present_speech_windows": present_windows,
                "meaningful_threshold_lufs": rounded(meaningful_threshold, 3),
                "meaningful_speech_windows": meaningful_windows,
                "marginal_speech_windows": marginal_windows,
                "total_speech_windows": len(windows),
                "bed_present": present_windows > 0,
            },
        },
        window_rows,
    )
