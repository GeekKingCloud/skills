from __future__ import annotations

import math
from typing import Any

from .util import correlation, db_to_power, power_mean_lufs, quantile, rounded


def profile_lane(audio_stream_index: int, rows: list[dict[str, Any]], csv_path: str) -> dict[str, Any]:
    lufs = [float(row["momentary_lufs"]) for row in rows]
    finite = [v for v in lufs if v > -119.0 and math.isfinite(v)]
    floor = quantile(finite, 0.10) if finite else -120.0
    body = quantile(finite, 0.90) if finite else -120.0
    spread = max(0.0, (body or -120.0) - (floor or -120.0))
    active_threshold = (floor or -120.0) + max(6.0, spread * 0.35)
    active = [v >= active_threshold for v in lufs]
    active_density = sum(1 for v in active if v) / len(active) if active else 0.0
    inactive_runs = _inactive_runs(active, 0.1)
    sentence_gap_seconds = sum(duration for duration in inactive_runs if 0.5 <= duration <= 4.0)
    transitions = sum(1 for prev, cur in zip(active, active[1:]) if prev != cur)
    duration_minutes = max(len(active) * 0.1 / 60.0, 1.0 / 60.0)
    transition_rate = transitions / duration_minutes
    gap_fraction = sentence_gap_seconds / max(len(active) * 0.1, 0.1)
    speech_shape = (spread / 24.0) * active_density * (1.0 - active_density) * min(1.0, transition_rate / 24.0)
    speech_shape += min(0.4, gap_fraction)
    true_peaks = [float(row.get("true_peak_dbtp", -120.0)) for row in rows if math.isfinite(float(row.get("true_peak_dbtp", -120.0)))]
    return {
        "audio_stream_index": audio_stream_index,
        "curve_csv": csv_path,
        "integrated_lufs": rounded(float(rows[-1].get("integrated_lufs", -70.0)), 3) if rows else None,
        "maximum_true_peak_dbtp": rounded(max(true_peaks), 3) if true_peaks else None,
        "ungated_power_mean_lufs": rounded(power_mean_lufs(lufs), 3),
        "speech_shape_ratio": rounded(speech_shape, 4),
        "continuity": rounded(active_density, 4),
        "noise_floor_lufs": rounded(floor, 3),
        "speech_body_lufs": rounded(body, 3),
        "active_threshold_lufs": rounded(active_threshold, 3),
        "sentence_gap_fraction": rounded(gap_fraction, 4),
        "transition_rate_per_minute": rounded(transition_rate, 3),
    }


def correlation_report(curves: dict[int, list[dict[str, Any]]]) -> dict[str, Any]:
    powers = {idx: [_finite_power(row.get("momentary_lufs")) for row in rows] for idx, rows in curves.items()}
    indexes = sorted(powers)
    matrix: dict[str, dict[str, float | None]] = {}
    for left in indexes:
        matrix[str(left)] = {}
        for right in indexes:
            matrix[str(left)][str(right)] = rounded(correlation(powers[left], powers[right]), 4)
    mix_flags: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    for idx in indexes:
        other = [other for other in indexes if other != idx]
        if len(other) < 2:
            continue
        target, aligned_inputs = _finite_aligned_regression(powers[idx], [powers[o] for o in other])
        weights = _fit_nonnegative_weights(aligned_inputs, target)
        fitted = [sum(weights[pos] * aligned_inputs[pos][row] for pos in range(len(other))) for row in range(len(target))]
        corr = correlation(target, fitted)
        r2 = _fit_r2(target, fitted)
        dominance = _dominance_fraction(target, aligned_inputs)
        target_energy = sum(target)
        contribution_fractions = [
            (weights[pos] * sum(aligned_inputs[pos]) / target_energy) if target_energy > 0.0 else 0.0
            for pos in range(len(other))
        ]
        row = {
            "audio_stream_index": idx,
            "correlation_with_fitted_sum_of_other_lanes": rounded(corr, 4),
            "fit_r2": rounded(r2, 4),
            "dominance_fraction": rounded(dominance, 4),
            "fit_weights_by_audio_stream_index": {str(other[pos]): rounded(weights[pos], 4) for pos in range(len(other))},
            "fit_contribution_fraction_by_audio_stream_index": {str(other[pos]): rounded(contribution_fractions[pos], 4) for pos in range(len(other))},
            "existing_mix_signature": False,
        }
        meaningful_contributors = sum(1 for fraction in contribution_fractions if fraction >= 0.05)
        if corr is not None and corr >= 0.85 and r2 is not None and r2 >= 0.85 and dominance >= 0.65 and meaningful_contributors >= 2:
            candidates.append(row)
        mix_flags.append(row)
    if candidates:
        best = max(candidates, key=lambda row: ((row["fit_r2"] or -1.0), (row["correlation_with_fitted_sum_of_other_lanes"] or -1.0)))
        for row in mix_flags:
            if row["audio_stream_index"] == best["audio_stream_index"]:
                row["existing_mix_signature"] = True
    return {"matrix": matrix, "existing_mix_candidates": mix_flags}


def _finite_power(raw: Any) -> float:
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return math.nan
    return db_to_power(value) if math.isfinite(value) else math.nan


def _finite_aligned_regression(target: list[float], inputs: list[list[float]]) -> tuple[list[float], list[list[float]]]:
    n = min([len(target), *(len(values) for values in inputs)]) if inputs else len(target)
    kept: list[tuple[float, list[float]]] = []
    for pos in range(n):
        actual = target[pos]
        values = [series[pos] for series in inputs]
        if math.isfinite(actual) and all(math.isfinite(value) for value in values):
            kept.append((actual, values))
    return [row[0] for row in kept], [[row[1][idx] for row in kept] for idx in range(len(inputs))]


def _fit_nonnegative_weights(inputs: list[list[float]], target: list[float]) -> list[float]:
    if not inputs:
        return []
    if not target:
        return [0.0 for _ in inputs]
    weights = [1.0 for _ in inputs]
    for _ in range(30):
        for idx, values in enumerate(inputs):
            residual = []
            for pos, actual in enumerate(target):
                without_current = sum(weights[j] * inputs[j][pos] for j in range(len(inputs)) if j != idx)
                residual.append(actual - without_current)
            denom = sum(value * value for value in values)
            weights[idx] = max(0.0, sum(value * res for value, res in zip(values, residual)) / denom) if denom > 0.0 else 0.0
    return weights


def _fit_r2(target: list[float], fitted: list[float]) -> float | None:
    aligned = [(actual, predicted) for actual, predicted in zip(target, fitted) if math.isfinite(actual) and math.isfinite(predicted)]
    if len(aligned) < 2:
        return None
    actual = [row[0] for row in aligned]
    predicted = [row[1] for row in aligned]
    n = len(aligned)
    mean_actual = sum(actual) / n
    total = sum((value - mean_actual) ** 2 for value in actual)
    if total <= 0.0:
        return None
    residual = sum((value - pred) ** 2 for value, pred in zip(actual, predicted))
    return max(0.0, 1.0 - residual / total)


def _dominance_fraction(target: list[float], others: list[list[float]]) -> float:
    actual, aligned_others = _finite_aligned_regression(target, others)
    if not actual:
        return 0.0
    return sum(1 for pos in range(len(actual)) if actual[pos] >= max(values[pos] for values in aligned_others)) / len(actual)


def _inactive_runs(active: list[bool], step_seconds: float) -> list[float]:
    runs: list[float] = []
    current = 0
    for value in active:
        if value:
            if current:
                runs.append(current * step_seconds)
                current = 0
        else:
            current += 1
    if current:
        runs.append(current * step_seconds)
    return runs
