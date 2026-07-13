from __future__ import annotations

import math
import shutil
import subprocess
import struct
import sys
import uuid
import wave
from array import array
from pathlib import Path
from typing import Any, Iterable

from .ffio import canonical_filter
from .util import RvError, require_tool, run_command, sha256_file


def ffmpeg_render_filter(
    source: str | Path,
    audio_stream_indexes: list[int],
    channel_counts: dict[int, int],
    segments: list[dict[str, Any]],
    gain_field: str,
    output: str | Path,
    duration: float,
    repair_commands: list[str],
) -> dict[str, Any]:
    """Render gain automation without building one expression for the whole plan.

    A canonical, unprocessed component is decoded once. Bounded batches then trim
    segment-local slices, apply the local ramp expression, and append headerless
    f32le output. Concatenating raw float samples is sample exact and keeps both
    the ffmpeg graph and the Windows command line independent of plan size.
    """
    require_tool("ffmpeg", repair_commands)
    if not audio_stream_indexes:
        ffmpeg_silence(output, duration, repair_commands)
        return {"audio_stream_indexes": [], "sample_count": _target_sample_count(duration)}
    target_samples = _target_sample_count(duration)
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ordered = sorted(segments, key=lambda row: float(row.get("start_seconds") or 0.0))
    temp_dir = output_path.parent / f".rv-segment-render-{uuid.uuid4().hex}"
    temp_dir.mkdir(parents=False)
    try:
        raw_component = temp_dir / "raw_component.wav"
        combined_f32 = temp_dir / "automated_component.f32le"
        _ffmpeg_render_raw_component(
            source,
            audio_stream_indexes,
            channel_counts,
            raw_component,
            target_samples,
            repair_commands,
        )
        stderr_tail = _render_segment_batches(
            raw_component,
            ordered,
            gain_field,
            combined_f32,
            target_samples,
            temp_dir,
            repair_commands,
        )
        run_command(
            [
                "ffmpeg",
                "-hide_banner",
                "-nostdin",
                "-v",
                "error",
                "-y",
                "-f",
                "f32le",
                "-ar",
                "48000",
                "-ac",
                "2",
                "-i",
                str(combined_f32),
                "-c:a",
                "pcm_f32le",
                str(output_path),
            ],
            repair_commands,
            timeout=1800,
        )
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
    return {
        "audio_stream_indexes": audio_stream_indexes,
        "sample_count": sample_count(output_path),
        "renderer": "bounded-segment-slices-f32le-concat",
        "segment_count": len(ordered),
        "segment_batch_size": _SEGMENT_BATCH_SIZE,
        "ffmpeg_stderr_tail": stderr_tail,
    }


def _ffmpeg_render_filter_legacy(
    source: str | Path,
    audio_stream_indexes: list[int],
    channel_counts: dict[int, int],
    segments: list[dict[str, Any]],
    gain_field: str,
    output: str | Path,
    duration: float,
    repair_commands: list[str],
) -> dict[str, Any]:
    """Compatibility reference used by the renderer equivalence regression."""
    require_tool("ffmpeg", repair_commands)
    if not audio_stream_indexes:
        ffmpeg_silence(output, duration, repair_commands)
        return {"audio_stream_indexes": [], "sample_count": _target_sample_count(duration)}
    filters: list[str] = []
    labels: list[str] = []
    gain_expr = gain_expression(segments, gain_field)
    for idx in audio_stream_indexes:
        label = f"lane{idx}"
        filters.append(f"{canonical_filter(idx, channel_counts.get(idx, 2))},asetnsamples=n=480,volume='{gain_expr}':eval=frame[{label}]")
        labels.append(f"[{label}]")
    if len(labels) == 1:
        filters.append(f"{labels[0]}apad,atrim=end_sample={_target_sample_count(duration)},asetpts=PTS-STARTPTS[out]")
    else:
        filters.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0,apad,atrim=end_sample={_target_sample_count(duration)},asetpts=PTS-STARTPTS[out]")
    proc = run_command(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostdin",
            "-y",
            "-i",
            str(source),
            "-filter_complex",
            ";".join(filters),
            "-map",
            "[out]",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-c:a",
            "pcm_f32le",
            str(output),
        ],
        repair_commands,
        timeout=1800,
    )
    return {"audio_stream_indexes": audio_stream_indexes, "sample_count": sample_count(output), "ffmpeg_stderr_tail": (proc.stderr or "")[-1000:]}


_SEGMENT_BATCH_SIZE = 24
_BYTES_PER_STEREO_F32_SAMPLE = 2 * 4


def _ffmpeg_render_raw_component(
    source: str | Path,
    audio_stream_indexes: list[int],
    channel_counts: dict[int, int],
    output: Path,
    target_samples: int,
    repair_commands: list[str],
) -> None:
    filters: list[str] = []
    labels: list[str] = []
    for idx in audio_stream_indexes:
        label = f"lane{idx}"
        filters.append(f"{canonical_filter(idx, channel_counts.get(idx, 2))}[{label}]")
        labels.append(f"[{label}]")
    if len(labels) == 1:
        filters.append(f"{labels[0]}apad,atrim=end_sample={target_samples},asetpts=PTS-STARTPTS[out]")
    else:
        filters.append(
            f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0,"
            f"apad,atrim=end_sample={target_samples},asetpts=PTS-STARTPTS[out]"
        )
    run_command(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostdin",
            "-v",
            "error",
            "-y",
            "-i",
            str(source),
            "-filter_complex",
            ";".join(filters),
            "-map",
            "[out]",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-c:a",
            "pcm_f32le",
            str(output),
        ],
        repair_commands,
        timeout=1800,
    )


def _render_segment_batches(
    raw_component: Path,
    ordered: list[dict[str, Any]],
    gain_field: str,
    output: Path,
    target_samples: int,
    temp_dir: Path,
    repair_commands: list[str],
) -> str:
    units = _automation_units(ordered, target_samples)
    stderr_tail = ""
    processed_segments = 0
    with output.open("wb") as combined:
        pending: list[dict[str, Any]] = []

        def flush() -> None:
            nonlocal stderr_tail, processed_segments
            if not pending:
                return
            for offset in range(0, len(pending), _SEGMENT_BATCH_SIZE):
                batch = pending[offset : offset + _SEGMENT_BATCH_SIZE]
                processed_segments += len(batch)
                print(
                    f"rv render: {gain_field} segments {processed_segments - len(batch) + 1}-{processed_segments}/{len(ordered)}",
                    file=sys.stderr,
                    flush=True,
                )
                stderr_tail = _render_segment_batch(
                    raw_component,
                    ordered,
                    batch,
                    gain_field,
                    combined,
                    temp_dir,
                    repair_commands,
                    processed_segments,
                )
            pending.clear()

        for unit in units:
            if unit["kind"] == "segment":
                pending.append(unit)
                continue
            flush()
            combined.write(b"\x00" * (int(unit["sample_count"]) * _BYTES_PER_STEREO_F32_SAMPLE))
        flush()
    expected_bytes = target_samples * _BYTES_PER_STEREO_F32_SAMPLE
    actual_bytes = output.stat().st_size
    if actual_bytes != expected_bytes:
        raise RvError(
            f"segment renderer produced {actual_bytes} f32le bytes; expected {expected_bytes}",
            repair_commands,
        )
    return stderr_tail


def _automation_units(ordered: list[dict[str, Any]], target_samples: int) -> list[dict[str, Any]]:
    units: list[dict[str, Any]] = []
    cursor = 0
    for pos, segment in enumerate(ordered):
        original_start = max(0, min(target_samples, int(round(float(segment["start_seconds"]) * 48000))))
        end = max(0, min(target_samples, int(round(float(segment["end_seconds"]) * 48000))))
        if original_start > cursor:
            units.append({"kind": "silence", "sample_count": original_start - cursor})
            cursor = original_start
        start = max(cursor, original_start)
        if end <= start:
            continue
        units.append(
            {
                "kind": "segment",
                "pos": pos,
                "start_sample": start,
                "end_sample": end,
                "expression_offset_seconds": (start - original_start) / 48000.0,
            }
        )
        cursor = end
        if cursor >= target_samples:
            break
    if cursor < target_samples:
        units.append({"kind": "silence", "sample_count": target_samples - cursor})
    return units


def _render_segment_batch(
    raw_component: Path,
    ordered: list[dict[str, Any]],
    batch: list[dict[str, Any]],
    gain_field: str,
    output_handle: Any,
    temp_dir: Path,
    repair_commands: list[str],
    batch_serial: int,
) -> str:
    batch_start = int(batch[0]["start_sample"])
    batch_end = int(batch[-1]["end_sample"])
    filters: list[str] = []
    input_labels: list[str]
    if len(batch) == 1:
        input_labels = ["[0:a:0]"]
    else:
        input_labels = [f"[in{idx}]" for idx in range(len(batch))]
        filters.append(f"[0:a:0]asplit={len(batch)}{''.join(input_labels)}")
    output_labels: list[str] = []
    for idx, (input_label, unit) in enumerate(zip(input_labels, batch)):
        start = int(unit["start_sample"])
        end = int(unit["end_sample"])
        count = end - start
        relative_start = start - batch_start
        relative_end = end - batch_start
        expression = segment_gain_expression(
            ordered,
            int(unit["pos"]),
            gain_field,
            time_offset_seconds=float(unit["expression_offset_seconds"]),
        )
        label = f"[seg{idx}]"
        filters.append(
            f"{input_label}atrim=start_sample={relative_start}:end_sample={relative_end},"
            f"asetpts=PTS-STARTPTS,asetnsamples=n=480:pad=1,"
            f"volume='{expression}':eval=frame,atrim=end_sample={count}{label}"
        )
        output_labels.append(label)
    if len(output_labels) == 1:
        filters.append(f"{output_labels[0]}anull[out]")
    else:
        filters.append(f"{''.join(output_labels)}concat=n={len(output_labels)}:v=0:a=1[out]")
    script_path = temp_dir / f"batch-{batch_serial:05d}.ffgraph"
    script_path.write_text(";".join(filters), encoding="utf-8")
    command = [
        "ffmpeg",
        "-hide_banner",
        "-nostdin",
        "-v",
        "error",
        "-ss",
        f"{batch_start / 48000.0:.12f}",
        "-t",
        f"{(batch_end - batch_start) / 48000.0:.12f}",
        "-i",
        str(raw_component),
        "-filter_complex_script",
        str(script_path),
        "-map",
        "[out]",
        "-ar",
        "48000",
        "-ac",
        "2",
        "-c:a",
        "pcm_f32le",
        "-f",
        "f32le",
        "-",
    ]
    try:
        proc = subprocess.run(command, stdout=output_handle, stderr=subprocess.PIPE, timeout=1800)
    except subprocess.TimeoutExpired as exc:
        raise RvError("ffmpeg segment batch timed out after 1800 seconds", repair_commands) from exc
    stderr = proc.stderr.decode("utf-8", errors="replace") if isinstance(proc.stderr, bytes) else (proc.stderr or "")
    if proc.returncode != 0:
        raise RvError(
            f"ffmpeg segment batch failed with exit code {proc.returncode}: {stderr[-2000:]}",
            repair_commands,
        )
    return stderr[-1000:]


def segment_gain_expression(
    ordered: list[dict[str, Any]],
    pos: int,
    field: str,
    *,
    time_offset_seconds: float = 0.0,
) -> str:
    segment = ordered[pos]
    duration = max(0.0, float(segment["end_seconds"]) - float(segment["start_seconds"]))
    gain = _gain_value(segment, field, 0.0)
    previous = ordered[pos - 1] if pos > 0 else None
    following = ordered[pos + 1] if pos + 1 < len(ordered) else None
    previous_gain = _gain_value(previous, field, gain) if previous is not None else gain
    previous_owns_boundary = previous is not None and float(previous.get("ramp_out_seconds") or 0.0) <= 0.0
    if previous is not None and not previous_owns_boundary:
        previous_gain = gain
    next_gain = _gain_value(following, field, gain) if following is not None else gain
    ramp_in = max(0.0, min(float(segment.get("ramp_in_seconds") or 0.0), duration))
    ramp_out = max(0.0, min(float(segment.get("ramp_out_seconds") or 0.0), max(0.0, duration - ramp_in)))
    time_term = "t" if time_offset_seconds == 0.0 else f"(t+{time_offset_seconds:.12f})"
    clauses: list[tuple[float, float, str]] = []
    if ramp_in > 0.0:
        clauses.append(
            (
                0.0,
                ramp_in,
                f"pow(10\\,(({previous_gain:.6f})+(({gain:.6f})-({previous_gain:.6f}))*({time_term})/({ramp_in:.6f}))/20)",
            )
        )
    steady_start = ramp_in
    steady_end = duration - ramp_out
    if steady_end > steady_start:
        clauses.append((steady_start, steady_end, f"{10 ** (gain / 20.0):.12f}"))
    if ramp_out > 0.0:
        clauses.append(
            (
                duration - ramp_out,
                duration,
                f"pow(10\\,(({gain:.6f})+(({next_gain:.6f})-({gain:.6f}))*(({time_term})-({duration - ramp_out:.6f}))/({ramp_out:.6f}))/20)",
            )
        )
    expression = "".join(
        f"if(between({time_term}\\,{lo:.6f}\\,{hi:.6f})\\,{value}\\," for lo, hi, value in clauses
    ) + "0" + (")" * len(clauses))
    if previous_owns_boundary and time_offset_seconds == 0.0:
        boundary_value = 10 ** (previous_gain / 20.0)
        expression = f"if(eq(t\\,0)\\,{boundary_value:.12f}\\,{expression})"
    return expression


def ffmpeg_silence(output: str | Path, duration: float, repair_commands: list[str]) -> None:
    target_samples = _target_sample_count(duration)
    run_command(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostdin",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "anullsrc=r=48000:cl=stereo",
            "-filter_complex",
            f"[0:a:0]atrim=end_sample={target_samples},asetpts=PTS-STARTPTS[out]",
            "-map",
            "[out]",
            "-c:a",
            "pcm_f32le",
            str(output),
        ],
        repair_commands,
        timeout=300,
    )


def ffmpeg_mix_components(mic: str | Path, bed: str | Path, mix: str | Path, duration: float, repair_commands: list[str]) -> None:
    target_samples = _target_sample_count(duration)
    run_command(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostdin",
            "-y",
            "-i",
            str(mic),
            "-i",
            str(bed),
            "-filter_complex",
            f"[0:a:0][1:a:0]amix=inputs=2:normalize=0,apad,atrim=end_sample={target_samples},asetpts=PTS-STARTPTS[out]",
            "-map",
            "[out]",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-c:a",
            "pcm_f32le",
            str(mix),
        ],
        repair_commands,
        timeout=900,
    )


def ffmpeg_peak_control(
    source: str | Path,
    output: str | Path,
    duration: float,
    true_peak_ceiling_dbtp: float,
    repair_commands: list[str],
) -> dict[str, Any]:
    """Apply the declared mic-only lookahead limiter with fixed timing."""
    target_samples = _target_sample_count(duration)
    linear_limit = 10 ** (float(true_peak_ceiling_dbtp) / 20.0)
    attack_ms = 5.0
    release_ms = 50.0
    oversample_rate_hz = 192000
    run_command(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostdin",
            "-y",
            "-i",
            str(source),
            "-filter_complex",
            (
                f"[0:a:0]aresample={oversample_rate_hz},"
                f"alimiter=limit={linear_limit:.12f}:attack={attack_ms:g}:"
                f"release={release_ms:g}:level=false:latency=true,aresample=48000,apad,"
                f"atrim=end_sample={target_samples},asetpts=PTS-STARTPTS[out]"
            ),
            "-map",
            "[out]",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-c:a",
            "pcm_f32le",
            str(output),
        ],
        repair_commands,
        timeout=900,
    )
    return {
        "mechanism": "alimiter",
        "true_peak_ceiling_dbtp": float(true_peak_ceiling_dbtp),
        "limit_linear": linear_limit,
        "attack_ms": attack_ms,
        "release_ms": release_ms,
        "auto_level": False,
        "latency_compensated": True,
        "oversample_rate_hz": oversample_rate_hz,
        "output_sample_rate_hz": 48000,
    }


def power_curve_100ms(path: str | Path, repair_commands: list[str]) -> list[dict[str, float]]:
    """Return non-overlapping 100 ms mean-square power rows from canonical audio."""
    samples_per_window = 4800 * 2
    pending = array("f")
    rows: list[dict[str, float]] = []
    window_index = 0
    for chunk in decoded_float_chunks(path, repair_commands):
        pending.extend(chunk)
        offset = 0
        while len(pending) - offset >= samples_per_window:
            values = pending[offset : offset + samples_per_window]
            power = sum(float(value) * float(value) for value in values) / samples_per_window
            start = window_index / 10.0
            rows.append({"time_seconds": start, "end_seconds": start + 0.1, "power": power})
            window_index += 1
            offset += samples_per_window
        if offset:
            del pending[:offset]
    if pending:
        power = sum(float(value) * float(value) for value in pending) / len(pending)
        start = window_index / 10.0
        rows.append({"time_seconds": start, "end_seconds": start + len(pending) / (48000.0 * 2.0), "power": power})
    return rows


def _target_sample_count(duration: float) -> int:
    return int(round(float(duration) * 48000))


def gain_expression(segments: list[dict[str, Any]], field: str) -> str:
    ordered = sorted(segments, key=lambda row: float(row.get("start_seconds") or 0.0))
    pieces: list[str] = []
    for pos, seg in enumerate(ordered):
        start = float(seg["start_seconds"])
        end = float(seg["end_seconds"])
        gain = _gain_value(seg, field, 0.0)
        prev = ordered[pos - 1] if pos > 0 else None
        prev_gain = _gain_value(prev, field, gain) if prev is not None else gain
        if prev is not None and float(prev.get("ramp_out_seconds") or 0.0) > 0.0:
            prev_gain = gain
        next_gain = _gain_value(ordered[pos + 1], field, gain) if pos + 1 < len(ordered) else gain
        ramp_in = max(0.0, min(float(seg.get("ramp_in_seconds") or 0.0), max(0.0, end - start)))
        ramp_out = max(0.0, min(float(seg.get("ramp_out_seconds") or 0.0), max(0.0, end - start - ramp_in)))
        clauses: list[tuple[float, float, str]] = []
        if ramp_in > 0.0:
            clauses.append((start, start + ramp_in, f"pow(10\\,(({prev_gain:.6f})+(({gain:.6f})-({prev_gain:.6f}))*(t-({start:.6f}))/({ramp_in:.6f}))/20)"))
        steady_start = start + ramp_in
        steady_end = end - ramp_out
        if steady_end > steady_start:
            clauses.append((steady_start, steady_end, f"{10 ** (gain / 20.0):.12f}"))
        if ramp_out > 0.0:
            clauses.append((end - ramp_out, end, f"pow(10\\,(({gain:.6f})+(({next_gain:.6f})-({gain:.6f}))*(t-({end - ramp_out:.6f}))/({ramp_out:.6f}))/20)"))
        for lo, hi, expr in clauses:
            pieces.append(f"if(between(t\\,{lo:.6f}\\,{hi:.6f})\\,{expr}\\,")
    return "".join(pieces) + "0" + (")" * len(pieces))


def _gain_value(segment: dict[str, Any], field: str, fallback: float) -> float:
    value = segment.get(field)
    return fallback if value is None else float(value)


def sample_count(path: str | Path) -> int:
    try:
        with wave.open(str(path), "rb") as wav:
            return int(wav.getnframes())
    except wave.Error:
        proc = run_command(
            [
                "ffprobe",
                "-hide_banner",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=nw=1:nk=1",
                str(path),
            ],
            [f'python remix-voiceover/scripts/rv.py render --source "<source>" --plan "<render_plan.json>" --outdir "<candidate-dir>" --manifest-out "<render_manifest.json>"'],
            timeout=60,
        )
        return int(round(float(proc.stdout.strip()) * 48000))


def decoded_float_samples(path: str | Path, repair_commands: list[str]) -> list[float]:
    values: list[float] = []
    for chunk in decoded_float_chunks(path, repair_commands):
        values.extend(chunk)
    return values


def decoded_float_chunks(path: str | Path, repair_commands: list[str], *, audio_stream_index: int = 0, chunk_size: int = 1024 * 1024):
    require_tool("ffmpeg", repair_commands)
    proc = subprocess.Popen(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostdin",
            "-v",
            "error",
            "-i",
            str(path),
            "-map",
            f"0:a:{audio_stream_index}",
            "-f",
            "f32le",
            "-acodec",
            "pcm_f32le",
            "-ar",
            "48000",
            "-ac",
            "2",
            "pipe:1",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    assert proc.stdout is not None
    leftover = b""
    try:
        while True:
            block = proc.stdout.read(chunk_size)
            if not block:
                break
            data = leftover + block
            usable = len(data) - (len(data) % 4)
            leftover = data[usable:]
            if usable:
                floats = array("f")
                floats.frombytes(data[:usable])
                yield floats
        try:
            code = proc.wait(timeout=120)
        except subprocess.TimeoutExpired:
            raise RvError(f"failed to decode {path}: ffmpeg did not exit after end of stream", repair_commands)
    finally:
        if proc.poll() is None:
            proc.kill()
    if code != 0:
        raise RvError(f"failed to decode {path}: ffmpeg exited with code {code}", repair_commands)
    if leftover:
        raise RvError(f"failed to decode {path}: partial float sample at end of stream", repair_commands)


def decoded_pcm_sha256(
    path: str | Path,
    repair_commands: list[str],
    *,
    sample_format: str = "f32le",
    audio_stream_index: int = 0,
) -> str:
    import hashlib

    digest = hashlib.sha256()
    require_tool("ffmpeg", repair_commands)
    proc = subprocess.Popen(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostdin",
            "-v",
            "error",
            "-i",
            str(path),
            "-map",
            f"0:a:{audio_stream_index}",
            "-f",
            sample_format,
            "-acodec",
            f"pcm_{sample_format}",
            "-ar",
            "48000",
            "-ac",
            "2",
            "pipe:1",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    assert proc.stdout is not None
    try:
        for block in iter(lambda: proc.stdout.read(1024 * 1024), b""):
            digest.update(block)
        try:
            code = proc.wait(timeout=120)
        except subprocess.TimeoutExpired:
            raise RvError(f"failed to decode {path}: ffmpeg did not exit after end of stream", repair_commands)
    finally:
        if proc.poll() is None:
            proc.kill()
    if code != 0:
        raise RvError(f"failed to decode {path}: ffmpeg exited with code {code}", repair_commands)
    return digest.hexdigest()


def streamed_component_stats(mic: str | Path, bed: str | Path, mix: str | Path, repair_commands: list[str]) -> dict[str, Any]:
    peaks = {"mic": 0.0, "bed": 0.0, "mix": 0.0}
    peak_times = {"mic": 0.0, "bed": 0.0, "mix": 0.0}
    null_peak = 0.0
    sample_count_total = 0
    for mic_chunk, bed_chunk, mix_chunk in _zip_float_chunks(
        decoded_float_chunks(mic, repair_commands),
        decoded_float_chunks(bed, repair_commands),
        decoded_float_chunks(mix, repair_commands),
    ):
        n = min(len(mic_chunk), len(bed_chunk), len(mix_chunk))
        for i in range(n):
            mic_value = float(mic_chunk[i])
            bed_value = float(bed_chunk[i])
            mix_value = float(mix_chunk[i])
            for label, value in (("mic", mic_value), ("bed", bed_value), ("mix", mix_value)):
                magnitude = abs(value)
                if magnitude > peaks[label]:
                    peaks[label] = magnitude
                    peak_times[label] = ((sample_count_total + i) // 2) / 48000.0
            null_peak = max(null_peak, abs(mix_value - (mic_value + bed_value)))
        sample_count_total += n
    return {"peaks": peaks, "peak_times_seconds": peak_times, "null_peak": null_peak, "decoded_float_samples": sample_count_total}


def _zip_float_chunks(*iterables):
    iterators = [iter(item) for item in iterables]
    while True:
        chunks = []
        for iterator in iterators:
            try:
                chunks.append(next(iterator))
            except StopIteration:
                return
        yield tuple(chunks)


def component_stats(paths: Iterable[str | Path], repair_commands: list[str]) -> dict[str, dict[str, float]]:
    stats: dict[str, dict[str, float]] = {}
    for path in paths:
        proc = run_command(
            [
                "ffmpeg",
                "-hide_banner",
                "-nostdin",
                "-v",
                "error",
                "-i",
                str(path),
                "-af",
                "astats=metadata=1:reset=0",
                "-f",
                "null",
                "-",
            ],
            repair_commands,
            timeout=600,
        )
        peak = 0.0
        for line in proc.stderr.splitlines():
            if "Peak level dB" in line:
                try:
                    peak = max(peak, float(line.rsplit(":", 1)[1].strip()))
                except ValueError:
                    pass
        stats[str(path)] = {"sample_count": sample_count(path), "peak_dbfs": peak, "sha256": sha256_file(path)}
    return stats
