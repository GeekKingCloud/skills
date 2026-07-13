from __future__ import annotations

from rv.speech import _earliest_supported_change_group, build_parameters, detect_speech_and_regimes


def _row(t: float, lufs: float) -> dict:
    return {
        "time_seconds": round(t, 3),
        "end_seconds": round(t + 0.1, 3),
        "momentary_lufs": lufs,
        "shortterm_lufs": lufs,
        "integrated_lufs": lufs,
        "power": 10 ** (lufs / 10.0),
    }


def test_regime_relative_speech_detection_keeps_quiet_twenty_db_regime() -> None:
    rows = []
    for idx in range(2400):
        t = idx / 10.0
        phrase = (t % 4.0) < 2.0
        if t < 60.0:
            lufs = -25.0 if phrase else -62.0
        elif t < 180.0:
            lufs = -45.0 if phrase else -82.0
        else:
            lufs = -25.5 if phrase else -62.0
        rows.append(_row(t, lufs))
    params, _ = build_parameters({"min_plateau_seconds": 60.0})
    result = detect_speech_and_regimes(rows, None, params)
    quiet = [reg for reg in result["regimes"] if reg["start_seconds"] <= 65.0 and reg["end_seconds"] >= 175.0]
    assert quiet, result["regimes"]
    quiet_windows = [win for win in result["speech_windows"] if 65.0 <= win["start_seconds"] < 175.0]
    assert quiet_windows
    assert sum(win["duration_seconds"] for win in quiet_windows) > 40.0


def test_dense_speech_regime_noise_floor_uses_non_speech_rows() -> None:
    rows = []
    for idx in range(1200):
        t = idx / 10.0
        phrase = (t % 10.0) < 8.8
        lufs = -25.0 if phrase else -82.0
        rows.append(_row(t, lufs))
    params, _ = build_parameters({})
    result = detect_speech_and_regimes(rows, None, params)
    assert result["regimes"]
    regime = result["regimes"][0]
    assert regime["raw_speech_body_lufs"] > -30.0
    assert regime["noise_floor_lufs"] < -75.0
    assert regime["clean_gain_headroom"]["noise_floor_basis"] == "q20 of momentary rows outside detected speech windows"


def test_step_boundary_refines_off_bin_capture_drop_to_near_real_time() -> None:
    rows = []
    for idx in range(1500):
        t = idx / 10.0
        phrase = (t % 2.0) < 1.2
        if t < 74.0:
            lufs = -25.0 if phrase else -80.0
        else:
            lufs = -55.0 if phrase else -110.0
        rows.append(_row(t, lufs))
    params, _ = build_parameters({"min_plateau_seconds": 60.0})
    result = detect_speech_and_regimes(rows, None, params)
    drop = next(step for step in result["step_candidates"] if step["direction"] == "drop")
    assert abs(drop["boundary_seconds"] - 74.0) <= 2.0
    assert drop["evidence"]["boundary_refined"] is True
    assert any(abs(regime["end_seconds"] - drop["boundary_seconds"]) <= 0.001 for regime in result["regimes"])


def test_file_start_censored_plateau_still_detects_early_capture_drop() -> None:
    rows = []
    for idx in range(1800):
        t = idx / 10.0
        phrase = (t % 2.0) < 1.2
        lufs = (-25.0 if t < 44.0 else -45.0) if phrase else (-80.0 if t < 44.0 else -100.0)
        rows.append(_row(t, lufs))
    params, _ = build_parameters({"min_plateau_seconds": 60.0})
    result = detect_speech_and_regimes(rows, None, params)
    drop = next(step for step in result["step_candidates"] if step["direction"] == "drop")
    assert abs(drop["boundary_seconds"] - 44.0) <= 2.0


def test_transition_refinement_uses_earliest_sustained_near_peak_group() -> None:
    candidates = [
        *[(18.0, 43.9 + idx / 10.0, -18.0) for idx in range(6)],
        *[(20.0, 44.8 + idx / 10.0, -20.0) for idx in range(27)],
    ]
    selected = _earliest_supported_change_group(candidates, -20.0)
    assert selected[0][1] == 43.9
    assert selected[-1][1] == 44.4


def test_silent_gap_does_not_create_bogus_regime_or_step_candidate() -> None:
    rows = []
    for idx in range(1200):
        t = idx / 10.0
        phrase = (t % 2.0) < 1.2
        if 30.0 <= t < 60.0:
            lufs = -105.0
        else:
            lufs = -25.0 if phrase else -80.0
        rows.append(_row(t, lufs))
    params, _ = build_parameters({})
    result = detect_speech_and_regimes(rows, None, params)
    assert len(result["regimes"]) == 1
    assert not any(abs(float(step["step_db"])) >= 50.0 for step in result["step_candidates"])


def test_thirty_second_expressive_passage_is_not_a_macro_capture_regime() -> None:
    rows = []
    for idx in range(3900):
        t = idx / 10.0
        phrase = (t % 2.0) < 1.2
        expressive = 180.0 <= t < 210.0
        lufs = (-5.0 if expressive else -20.0) if phrase else -80.0
        rows.append(_row(t, lufs))

    params, _ = build_parameters({})
    result = detect_speech_and_regimes(rows, None, params)

    assert result["step_candidates"] == []
    assert len(result["regimes"]) == 1
    assert result["regimes"][0]["start_seconds"] == 0.0
    assert result["regimes"][0]["end_seconds"] == 390.0


def test_sixty_second_expressive_passage_is_not_a_macro_capture_regime_by_default() -> None:
    rows = []
    for idx in range(4200):
        t = idx / 10.0
        phrase = (t % 2.0) < 1.2
        expressive = 180.0 <= t < 240.0
        lufs = (-5.0 if expressive else -20.0) if phrase else -80.0
        rows.append(_row(t, lufs))
    params, _ = build_parameters({})
    result = detect_speech_and_regimes(rows, None, params)
    assert result["step_candidates"] == []
    assert len(result["regimes"]) == 1
