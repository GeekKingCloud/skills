from __future__ import annotations

import argparse
import re
import wave
from pathlib import Path
from typing import Any

from .audio import ffmpeg_render_filter
from .ffio import ffprobe_json
from .plan import validate_plan
from .probe import _streams
from .util import RvError, read_json, refuse_output_alias, run_command, sha256_file, sha256_json, utc_now, write_json


_QUALITY_VALUES = {"excellent", "good", "fair", "poor", "unusable"}


def audition_command(args: argparse.Namespace) -> int:
    if not re.fullmatch(r"[A-Za-z0-9_-]+", str(args.regime_id)):
        raise RvError("audition refused: regime id may contain only letters, digits, underscore, and hyphen", ["use the exact regime id from analysis.json"])
    source = Path(args.source)
    candidate = Path(args.candidate_mic)
    manifest_path = Path(args.manifest)
    plan_path = Path(args.plan)
    analysis_path = Path(args.analysis)
    json_out = Path(args.json_out)
    plan = read_json(plan_path)
    analysis = read_json(analysis_path)
    manifest = read_json(manifest_path)
    repair = ["rerun plan-validate, render, and audition from the current source lineage"]
    if sha256_file(source) != analysis.get("source_sha256") or plan.get("analysis", {}).get("sha256") != sha256_json(analysis):
        raise RvError("audition refused: source, analysis, and plan lineage do not match", repair)
    if any(row.get("status") == "fail" for row in validate_plan(plan, analysis)):
        raise RvError("audition refused: render plan does not validate", repair)
    if not candidate.is_file():
        raise RvError("audition refused: candidate mic component is missing", repair)
    rendered_mic = manifest.get("components", {}).get("mic", {})
    rendered_path = Path(str(rendered_mic.get("path") or ""))
    try:
        same_candidate = rendered_path.is_file() and candidate.is_file() and rendered_path.samefile(candidate)
    except OSError:
        same_candidate = rendered_path.resolve(strict=False) == candidate.resolve(strict=False)
    if (
        manifest.get("generated_by") != "rv-render"
        or manifest.get("status") != "rendered"
        or manifest.get("source_sha256") != analysis.get("source_sha256")
        or manifest.get("plan_sha256") != sha256_json(plan)
        or manifest.get("analysis_sha256") != sha256_json(analysis)
        or not same_candidate
        or rendered_mic.get("sha256") != sha256_file(candidate)
    ):
        raise RvError("audition refused: candidate mic is not the current render-manifest mic component", repair)
    regime = next((row for row in analysis.get("regimes", []) if str(row.get("id")) == str(args.regime_id)), None)
    if regime is None:
        raise RvError(f"audition refused: unknown regime {args.regime_id!r}", repair)
    start = float(args.start)
    duration = float(args.duration)
    rstart = float(regime.get("start_seconds") or 0.0)
    rend = float(regime.get("end_seconds") or 0.0)
    if duration <= 0.0 or start < rstart or start + duration > rend + 0.001:
        raise RvError("audition refused: sample must have positive duration and stay inside the claimed regime", repair)
    review = _review_payload(args)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    raw_full = outdir / ".raw-mic-full.wav"
    raw_sample = outdir / f"{args.regime_id}-raw.wav"
    processed_sample = outdir / f"{args.regime_id}-processed.wav"
    _refuse_aliases(
        [raw_full, raw_sample, processed_sample, json_out],
        [source, candidate, manifest_path, plan_path, analysis_path],
        repair,
    )
    actual_probe = ffprobe_json(source, repair)
    audio_streams = [row for row in _streams(actual_probe) if row["codec_type"] == "audio"]
    channels = {int(row["audio_stream_index"]): int(row.get("channels") or 2) for row in audio_streams}
    roles = plan.get("roles", {})
    full_duration = float(analysis.get("duration_seconds") or 0.0)
    ffmpeg_render_filter(
        source,
        [int(value) for value in roles.get("mic_streams", [])],
        channels,
        [{"start_seconds": 0.0, "end_seconds": full_duration, "mic_gain_db": 0.0, "ramp_in_seconds": 0.0, "ramp_out_seconds": 0.0}],
        "mic_gain_db",
        raw_full,
        full_duration,
        repair,
    )
    try:
        _extract_sample(raw_full, raw_sample, start, duration, repair)
        _extract_sample(candidate, processed_sample, start, duration, repair)
    finally:
        raw_full.unlink(missing_ok=True)
    payload: dict[str, Any] = {
        "schema_version": 1,
        "generated_at": utc_now(),
        "generated_by": "rv-audition",
        "source_sha256": sha256_file(source),
        "analysis_sha256": sha256_json(analysis),
        "plan_sha256": sha256_json(plan),
        "render_manifest_path": str(manifest_path),
        "render_manifest_sha256": sha256_json(manifest),
        "candidate_mic_sha256": sha256_file(candidate),
        "audio_stream_indexes": [int(value) for value in roles.get("mic_streams", [])],
        "regime_id": str(args.regime_id),
        "start_seconds": start,
        "duration_seconds": duration,
        "raw_sample": _sample_record(raw_sample),
        "processed_sample": _sample_record(processed_sample),
        "review": review,
    }
    write_json(json_out, payload)
    return 0


def _review_payload(args: argparse.Namespace) -> dict[str, Any]:
    scores = {
        "commentary_quality": args.commentary_quality,
        "noise_background_quality": args.background_quality,
        "overall_quality": args.overall_quality,
    }
    if args.reviewed:
        if not args.reviewed_by or any(value not in _QUALITY_VALUES for value in scores.values()):
            raise RvError(
                "audition --reviewed requires --reviewed-by and all three quality ratings",
                ["use ratings: excellent, good, fair, poor, or unusable"],
            )
    return {"reviewed": bool(args.reviewed), "reviewed_by": args.reviewed_by, **scores}


def _extract_sample(source: Path, output: Path, start: float, duration: float, repair: list[str]) -> None:
    run_command(
        [
            "ffmpeg", "-hide_banner", "-nostdin", "-v", "error", "-y",
            "-ss", f"{start:.6f}", "-t", f"{duration:.6f}", "-i", str(source),
            "-vn", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s24le", str(output),
        ],
        repair,
        timeout=600,
    )


def _sample_record(path: Path) -> dict[str, Any]:
    with wave.open(str(path), "rb") as handle:
        return {
            "path": str(path),
            "sha256": sha256_file(path),
            "sample_rate_hz": handle.getframerate(),
            "channels": handle.getnchannels(),
            "frames": handle.getnframes(),
        }


def _refuse_aliases(outputs: list[Path], protected: list[Path], repair: list[str]) -> None:
    for index, output in enumerate(outputs):
        refuse_output_alias(output, [*protected, *outputs[:index], *outputs[index + 1 :]], repair, label="audition output")
