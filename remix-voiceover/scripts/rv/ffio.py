from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

from .util import RvError, require_tool, run_command, write_csv

MONO_UPMIX_COEFFICIENT = 0.7071067811865476


def repair_probe(media: str | Path, probe_json: str | Path) -> list[str]:
    return [f'python remix-voiceover/scripts/rv.py probe "{media}" --json-out "{probe_json}"']


def repair_analyze(media: str | Path, probe_json: str | Path, analysis_json: str | Path) -> list[str]:
    return [
        f'python remix-voiceover/scripts/rv.py probe "{media}" --json-out "{probe_json}"',
        f'python remix-voiceover/scripts/rv.py analyze "{media}" --probe "{probe_json}" --json-out "{analysis_json}"',
    ]


def ffprobe_json(media: str | Path, repair_commands: list[str]) -> dict[str, Any]:
    require_tool("ffprobe", repair_commands)
    proc = run_command(
        [
            "ffprobe",
            "-hide_banner",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(media),
        ],
        repair_commands,
        timeout=120,
    )
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RvError("ffprobe returned invalid JSON", repair_commands) from exc
    if not isinstance(data, dict):
        raise RvError("ffprobe returned non-object JSON", repair_commands)
    return data


def ffmpeg_version(repair_commands: list[str]) -> str:
    require_tool("ffmpeg", repair_commands)
    proc = run_command(["ffmpeg", "-version"], repair_commands, timeout=30)
    return proc.stdout.splitlines()[0] if proc.stdout else "unknown"


def ffprobe_version(repair_commands: list[str]) -> str:
    proc = run_command(["ffprobe", "-version"], repair_commands, timeout=30)
    return proc.stdout.splitlines()[0] if proc.stdout else "unknown"


def canonical_filter(audio_stream_index: int, channels: int) -> str:
    src = f"[0:a:{audio_stream_index}]aresample=48000"
    if channels == 1:
        return (
            f"{src},pan=stereo|c0={MONO_UPMIX_COEFFICIENT:.16f}*c0|"
            f"c1={MONO_UPMIX_COEFFICIENT:.16f}*c0,aformat=sample_fmts=flt:channel_layouts=stereo"
        )
    return f"{src},aformat=sample_fmts=flt:channel_layouts=stereo"


def ebur128_curve(
    media: str | Path,
    audio_stream_index: int,
    channels: int,
    csv_path: str | Path,
    repair_commands: list[str],
) -> dict[str, Any]:
    require_tool("ffmpeg", repair_commands)
    filtergraph = f"{canonical_filter(audio_stream_index, channels)},ebur128=peak=true:metadata=1,ametadata=mode=print:file=-"
    proc = run_command(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostdin",
            "-v",
            "error",
            "-i",
            str(media),
            "-map",
            f"0:a:{audio_stream_index}",
            "-af",
            filtergraph,
            "-f",
            "null",
            "-",
        ],
        repair_commands,
        timeout=1800,
    )
    rows, missing_m_rows, frame_rows = _parse_metadata(proc.stdout)
    if not rows:
        raise RvError(f"no ebur128 metadata produced for 0:a:{audio_stream_index}", repair_commands)
    missing_fraction = missing_m_rows / frame_rows if frame_rows else 1.0
    if missing_fraction > 0.01:
        raise RvError(
            f"ebur128 metadata missing momentary M values for {missing_m_rows}/{frame_rows} frame rows",
            repair_commands,
        )
    write_csv(
        csv_path,
        rows,
        ["time_seconds", "end_seconds", "momentary_lufs", "shortterm_lufs", "integrated_lufs", "true_peak_dbtp", "power"],
    )
    return {
        "rows": rows,
        "csv_path": str(Path(csv_path)),
        "canonical_format": {
            "sample_rate_hz": 48000,
            "layout": "stereo",
            "sample_format": "pcm_f32le",
            "mono_upmix_coefficient_per_channel": MONO_UPMIX_COEFFICIENT if channels == 1 else None,
        },
    }


def _parse_metadata(text: str) -> tuple[list[dict[str, Any]], int, int]:
    rows: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    missing_m_rows = 0
    frame_rows = 0
    frame_re = re.compile(r"^frame:\d+\s+pts:\S+\s+pts_time:(\S+)")
    for line in text.splitlines():
        match = frame_re.match(line)
        if match:
            if current is not None:
                if not _finish_row(rows, current):
                    missing_m_rows += 1
            frame_rows += 1
            try:
                pts_time = float(match.group(1))
            except ValueError:
                current = None
                continue
            current = {"time_seconds": pts_time}
            continue
        if current is None or not line.startswith("lavfi.r128."):
            continue
        key, value = line.split("=", 1)
        try:
            val = float(value)
        except ValueError:
            continue
        if key.endswith(".M"):
            current["momentary_lufs"] = val
        elif key.endswith(".S"):
            current["shortterm_lufs"] = val
        elif key.endswith(".I"):
            current["integrated_lufs"] = val
        elif key.endswith(".TPK") or key.endswith(".FTPK") or key.endswith(".true_peak") or key.endswith(".TruePeak"):
            current["true_peak_dbtp"] = 20.0 * math.log10(val) if val > 0.0 else -120.0
    if current is not None:
        if not _finish_row(rows, current):
            missing_m_rows += 1
    return rows, missing_m_rows, frame_rows


def _finish_row(rows: list[dict[str, Any]], current: dict[str, Any]) -> bool:
    if "momentary_lufs" not in current:
        return False
    start = float(current.get("time_seconds", len(rows) * 0.1))
    momentary = float(current.get("momentary_lufs", -120.0))
    rows.append(
        {
            "time_seconds": round(start, 3),
            "end_seconds": round(start + 0.1, 3),
            "momentary_lufs": round(momentary, 3),
            "shortterm_lufs": round(float(current.get("shortterm_lufs", -120.0)), 3),
            "integrated_lufs": round(float(current.get("integrated_lufs", -70.0)), 3),
            "true_peak_dbtp": round(float(current.get("true_peak_dbtp", -120.0)), 3),
            "power": 0.0 if momentary <= -120.0 else 10 ** (momentary / 10.0),
        }
    )
    return True
