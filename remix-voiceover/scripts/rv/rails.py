from __future__ import annotations

import copy
import re
from pathlib import Path
from typing import Any

from .util import RvError, read_json


def rails_path() -> Path:
    return Path(__file__).resolve().parents[2] / "assets" / "default-rails.json"


def load_default_rails() -> dict[str, Any]:
    return read_json(rails_path())


def adjusted_rails(defaults: dict[str, Any], adjustment: dict[str, Any] | None) -> dict[str, Any]:
    rails = copy.deepcopy(defaults)
    if not adjustment:
        return rails
    mic_shift = float(adjustment.get("mic_band_center_shift_db", 0.0) or 0.0)
    gap_shift = float(adjustment.get("gap_band_shift_db", 0.0) or 0.0)
    rails["processed_mic_active_speech_lufs"]["min"] = round(float(rails["processed_mic_active_speech_lufs"]["min"]) + mic_shift, 3)
    rails["processed_mic_active_speech_lufs"]["max"] = round(float(rails["processed_mic_active_speech_lufs"]["max"]) + mic_shift, 3)
    rails["processed_mic_active_speech_lufs"]["preferred"] = round(float(rails["processed_mic_active_speech_lufs"]["preferred"]) + mic_shift, 3)
    rails["mic_over_bed_gap_db"]["min"] = round(float(rails["mic_over_bed_gap_db"]["min"]) + gap_shift, 3)
    rails["mic_over_bed_gap_db"]["max"] = round(float(rails["mic_over_bed_gap_db"]["max"]) + gap_shift, 3)
    rails["mic_over_bed_gap_db"]["preferred"] = round(float(rails["mic_over_bed_gap_db"]["preferred"]) + gap_shift, 3)
    return rails


def validate_adjustment(defaults: dict[str, Any], adjustment: dict[str, Any] | None, analysis: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not adjustment:
        return rows
    bounds = defaults["rails_adjustment_bounds"]
    mic_lo, mic_hi = bounds["mic_band_center_shift_db"]
    gap_lo, gap_hi = bounds["gap_band_shift_db"]
    mic_shift = float(adjustment.get("mic_band_center_shift_db", 0.0) or 0.0)
    gap_shift = float(adjustment.get("gap_band_shift_db", 0.0) or 0.0)
    evidence = adjustment.get("analysis_evidence_paths")
    if mic_shift < mic_lo or mic_shift > mic_hi:
        rows.append(_fail("rails_adjustment_out_of_bounds", f"mic shift {mic_shift} outside {mic_lo}..{mic_hi}", "set mic_band_center_shift_db inside bounds or remove rails_adjustment"))
    if gap_shift < gap_lo or gap_shift > gap_hi:
        rows.append(_fail("rails_adjustment_out_of_bounds", f"gap shift {gap_shift} outside {gap_lo}..{gap_hi}", "set gap_band_shift_db inside bounds or remove rails_adjustment"))
    if not isinstance(evidence, list) or not evidence:
        rows.append(_fail("rails_adjustment_missing_evidence", "rails_adjustment lacks analysis_evidence_paths", "cite concrete analysis.json fields in rails_adjustment.analysis_evidence_paths"))
    elif analysis is not None:
        missing = [str(ref) for ref in evidence if not _analysis_ref_exists(analysis, str(ref))]
        if missing:
            rows.append(_fail("rails_adjustment_missing_evidence", f"rails_adjustment.analysis_evidence_paths do not resolve in current analysis.json: {', '.join(missing)}", "cite concrete current analysis.json fields such as regimes[0].raw_speech_body_lufs or /regimes/0/raw_speech_body_lufs"))
    return rows


def clean_gain_default_ceiling(rails: dict[str, Any]) -> float:
    return float(rails["clean_mic_gain_ceiling_db"]["default"])


def clean_gain_headroom_safety_margin(rails: dict[str, Any]) -> float:
    return float(rails["clean_mic_gain_ceiling_db"].get("headroom_safety_margin_db", 0.0))


def clean_gain_allowed_ceiling(regime: dict[str, Any], rails: dict[str, Any]) -> float:
    headroom = regime.get("clean_gain_headroom") if isinstance(regime.get("clean_gain_headroom"), dict) else {}
    raw_ceiling = float(headroom.get("max_clean_gain_before_noise_floor_target_db") or 0.0)
    return max(0.0, raw_ceiling - clean_gain_headroom_safety_margin(rails))


def has_regime_clean_gain_headroom_evidence(analysis: dict[str, Any], regime_id: Any, refs: list[Any]) -> bool:
    regimes = analysis.get("regimes", [])
    for raw_ref in refs:
        ref = str(raw_ref)
        regime = _regime_from_clean_headroom_ref(analysis, ref, regimes)
        if regime is not None and regime.get("id") == regime_id:
            return True
    return False


def _regime_from_clean_headroom_ref(analysis: dict[str, Any], ref: str, regimes: Any) -> dict[str, Any] | None:
    try:
        _resolve_analysis_ref(analysis, ref)
    except (KeyError, IndexError, TypeError, ValueError):
        return None
    idx: int | None = None
    pointer = re.match(r"^/regimes/(\d+)(?:/clean_gain_headroom(?:/.*)?)?$", ref)
    dotted = re.match(r"^regimes\[(\d+)\]\.clean_gain_headroom(?:\..*)?$", ref)
    if pointer:
        idx = int(pointer.group(1))
    elif dotted:
        idx = int(dotted.group(1))
    if idx is None or not isinstance(regimes, list) or idx >= len(regimes):
        return None
    regime = regimes[idx]
    return regime if isinstance(regime, dict) else None


def _analysis_ref_exists(analysis: dict[str, Any], ref: str) -> bool:
    try:
        _resolve_analysis_ref(analysis, ref)
    except (KeyError, IndexError, TypeError, ValueError):
        return False
    return True


def _resolve_analysis_ref(analysis: dict[str, Any], ref: str) -> Any:
    if not ref:
        raise ValueError("empty analysis reference")
    if ref.startswith("/"):
        return _resolve_json_pointer(analysis, ref)
    return _resolve_dotted_ref(analysis, ref)


def _resolve_json_pointer(data: Any, pointer: str) -> Any:
    current = data
    for raw_part in pointer.split("/")[1:]:
        part = raw_part.replace("~1", "/").replace("~0", "~")
        current = _descend(current, part)
    return current


def _resolve_dotted_ref(data: Any, ref: str) -> Any:
    current = data
    for token in ref.split("."):
        if not token:
            raise ValueError("empty path token")
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*)(.*)$", token)
        if not match:
            raise ValueError(f"invalid path token {token!r}")
        current = _descend(current, match.group(1))
        rest = match.group(2)
        while rest:
            bracket = re.match(r"^\[(\d+)\](.*)$", rest)
            if not bracket:
                raise ValueError(f"invalid bracket path {token!r}")
            current = _descend(current, bracket.group(1))
            rest = bracket.group(2)
    return current


def _descend(current: Any, part: str) -> Any:
    if isinstance(current, dict):
        if part not in current:
            raise KeyError(part)
        return current[part]
    if isinstance(current, list):
        if not part.isdigit():
            raise TypeError(part)
        return current[int(part)]
    raise TypeError(part)


def require_rails_file() -> None:
    if not rails_path().exists():
        raise RvError(
            "missing default rails file",
            ['python remix-voiceover/scripts/rv.py plan-init --analysis "<analysis.json>" --out "<render_plan.json>"'],
        )


def _fail(failure_class: str, measurement: str, next_action: str) -> dict[str, Any]:
    return {
        "type": "rails_adjustment",
        "measurement": measurement,
        "target": "pinned rails adjustment bounds with analysis evidence citation",
        "status": "fail",
        "failure_class": failure_class,
        "next_action": next_action,
    }
