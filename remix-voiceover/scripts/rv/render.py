from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any

from .audio import _target_sample_count, ffmpeg_mix_components, ffmpeg_peak_control, ffmpeg_render_filter, sample_count
from .ffio import ffprobe_json
from .plan import materialize_lane_segments, validate_plan
from .probe import _streams
from .util import RvError, read_json, sha256_file, sha256_json, utc_now, write_json


def render_command(args: argparse.Namespace) -> int:
    source = Path(args.source)
    plan_path = Path(args.plan)
    outdir = Path(args.outdir)
    manifest_out = Path(args.manifest_out)
    plan = read_json(plan_path)
    analysis_path = Path(plan.get("analysis", {}).get("path") or plan_path.with_name("analysis.json"))
    analysis = read_json(analysis_path)
    validation = _validate_plan_for_render(plan_path, plan, analysis_path, analysis)
    if validation.get("status") != "pass":
        raise RvError("render refused: plan validation did not pass", _repair(plan_path, plan))
    if validation.get("plan_sha256") != sha256_json(plan):
        raise RvError("render refused: plan validation is stale for this render_plan.json", _repair(plan_path, plan))
    if sha256_file(source) != plan.get("analysis", {}).get("source_sha256"):
        raise RvError("render refused: source hash does not match plan analysis lineage", _repair(plan_path, plan))
    peak_control = plan.get("render", {}).get("peak_control") or {}
    peak_control_enabled = peak_control.get("enabled") is True
    mic_raw_path = outdir / "mic_component_raw.wav"
    mic_path = outdir / "mic_component.wav"
    bed_path = outdir / "bed_component.wav"
    mix_path = outdir / "mix.wav"
    fixed_outputs = [mic_path, bed_path, mix_path]
    if peak_control_enabled:
        fixed_outputs.insert(0, mic_raw_path)
    _refuse_output_aliases(source, manifest_out, fixed_outputs, [plan_path, analysis_path], plan)
    outdir.mkdir(parents=True, exist_ok=True)
    actual_probe = ffprobe_json(source, _repair(plan_path, plan))
    audio_streams = [row for row in _streams(actual_probe) if row["codec_type"] == "audio"]
    channel_counts = {int(row["audio_stream_index"]): int(row.get("channels") or 2) for row in audio_streams}
    duration = float(plan.get("analysis", {}).get("duration_seconds") or actual_probe.get("format", {}).get("duration") or 0.0)
    mic_segments = materialize_lane_segments(plan, "mic", analysis)
    bed_segments = materialize_lane_segments(plan, "bed", analysis)
    roles = plan.get("roles", {})
    mic_render_path = mic_raw_path if peak_control_enabled else mic_path
    print(f"rv render: rendering post-gain mic component to {mic_render_path}", file=sys.stderr, flush=True)
    mic_meta = ffmpeg_render_filter(source, [int(x) for x in roles.get("mic_streams", [])], channel_counts, mic_segments, "mic_gain_db", mic_render_path, duration, _repair(plan_path, plan))
    peak_control_meta = None
    if peak_control_enabled:
        print(f"rv render: applying declared mic-only alimiter to {mic_path}", file=sys.stderr, flush=True)
        peak_control_meta = ffmpeg_peak_control(
            mic_raw_path,
            mic_path,
            duration,
            float(peak_control["true_peak_ceiling_dbtp"]),
            _repair(plan_path, plan),
        )
    print(f"rv render: rendering bed component to {bed_path}", file=sys.stderr, flush=True)
    bed_meta = ffmpeg_render_filter(source, [int(x) for x in roles.get("bed_streams", [])], channel_counts, bed_segments, "bed_gain_db", bed_path, duration, _repair(plan_path, plan))
    print(f"rv render: summing components with amix normalize=0 to {mix_path}", file=sys.stderr, flush=True)
    ffmpeg_mix_components(mic_path, bed_path, mix_path, duration, _repair(plan_path, plan))
    manifest: dict[str, Any] = {
        "schema_version": 1,
        "generated_by": "rv-render",
        "generated_at": utc_now(),
        "status": "rendered",
        "source_path": str(source),
        "source_sha256": sha256_file(source),
        "plan_path": str(plan_path),
        "plan_sha256": sha256_json(plan),
        "analysis_sha256": plan.get("analysis", {}).get("sha256"),
        "plan_validation_path": str(plan_path.with_name("plan_validation.json")),
        "plan_validation_sha256": sha256_json(validation),
        "plan_validation_source": "render-internal-recomputed",
        "duration_seconds": duration,
        "target_sample_count": _target_sample_count(duration),
        "canonical_audio": {"sample_rate_hz": 48000, "channels": 2, "sample_format": "pcm_f32le"},
        "components": {
            "mic": {"path": str(mic_path), "sha256": sha256_file(mic_path), "sample_count": sample_count(mic_path), "lanes": mic_meta},
            "bed": {"path": str(bed_path), "sha256": sha256_file(bed_path), "sample_count": sample_count(bed_path), "lanes": bed_meta},
            "mix": {"path": str(mix_path), "sha256": sha256_file(mix_path), "sample_count": sample_count(mix_path)},
        },
        "peak_control": peak_control_meta,
        "materialized_automation": {
            "mic": {"sha256": sha256_json(mic_segments), "segment_count": len(mic_segments)},
            "bed": {"sha256": sha256_json(bed_segments), "segment_count": len(bed_segments)},
        },
        "sum_exactness": "mix.wav was rendered from listener-heard mic_component.wav and bed_component.wav using ffmpeg amix=inputs=2:normalize=0; bed and mix are never limited.",
        "lane_sample_counts": {
            "mic_component": sample_count(mic_path),
            "bed_component": sample_count(bed_path),
            "mix": sample_count(mix_path),
        },
    }
    if peak_control_enabled:
        manifest["components"]["mic_raw"] = {
            "path": str(mic_raw_path),
            "sha256": sha256_file(mic_raw_path),
            "sample_count": sample_count(mic_raw_path),
            "stage": "post-segment-gain, pre-peak-control",
        }
        manifest["lane_sample_counts"]["mic_component_raw"] = sample_count(mic_raw_path)
    write_json(manifest_out, manifest)
    return 0


def _refuse_output_aliases(source: Path, manifest_out: Path, fixed_outputs: list[Path], protected_inputs: list[Path], plan: dict[str, Any]) -> None:
    protected = [("source", source), ("render plan", protected_inputs[0]), ("analysis", protected_inputs[1])]
    outputs = [("manifest_out", manifest_out), *[(path.name, path) for path in fixed_outputs]]
    for index, (left_label, left_path) in enumerate(outputs):
        for right_label, right_path in outputs[index + 1 :]:
            if _same_path(left_path, right_path):
                raise RvError(
                    f"render refused: {left_label} would overwrite or alias output {right_label}",
                    _alias_repair(left_path.parent, plan),
                )
    for out_label, out_path in outputs:
        for protected_label, protected_path in protected:
            if _same_path(out_path, protected_path):
                raise RvError(
                    f"render refused: {out_label} would overwrite or alias the {protected_label}",
                    _alias_repair(out_path.parent, plan),
                )


def _same_path(left: Path, right: Path) -> bool:
    left_resolved = left.resolve(strict=False)
    right_resolved = right.resolve(strict=False)
    if left_resolved == right_resolved:
        return True
    if left.exists() and right.exists():
        try:
            return os.path.samefile(left, right)
        except OSError:
            return False
    return False


def _alias_repair(outdir: Path, plan: dict[str, Any]) -> list[str]:
    analysis = plan.get("analysis", {}).get("path", "<analysis.json>")
    sibling = outdir.with_name(f"{outdir.name}-candidate")
    return [
        f'choose a different --outdir that does not contain the source, plan, or analysis files, such as "{sibling}"',
        f'python remix-voiceover/scripts/rv.py plan-validate --plan "<render_plan.json>" --analysis "{analysis}" --json-out "<plan_validation.json>"',
        f'python remix-voiceover/scripts/rv.py render --source "<source>" --plan "<render_plan.json>" --outdir "{sibling}" --manifest-out "{sibling / "render_manifest.json"}"',
    ]


def _validate_plan_for_render(plan_path: Path, plan: dict[str, Any], analysis_path: Path, analysis: dict[str, Any]) -> dict[str, Any]:
    rows = validate_plan(plan, analysis)
    return {
        "schema_version": 1,
        "generated_at": utc_now(),
        "status": "pass" if all(row["status"] == "pass" for row in rows) else "fail",
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


def _repair(plan_path: Path, plan: dict[str, Any]) -> list[str]:
    analysis = plan.get("analysis", {}).get("path", "<analysis.json>")
    return [
        f'python remix-voiceover/scripts/rv.py plan-validate --plan "{plan_path}" --analysis "{analysis}" --json-out "{plan_path.with_name("plan_validation.json")}"',
        f'python remix-voiceover/scripts/rv.py render --source "<source>" --plan "{plan_path}" --outdir "<candidate-dir>" --manifest-out "<render_manifest.json>"',
    ]
