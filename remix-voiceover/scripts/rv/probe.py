from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from .ffio import ffmpeg_version, ffprobe_json, ffprobe_version, repair_probe
from .util import refuse_output_alias, sha256_file, utc_now, write_json


def probe_command(args: argparse.Namespace) -> int:
    media = Path(args.media)
    json_out = Path(args.json_out)
    repair = repair_probe(media, json_out)
    refuse_output_alias(json_out, [media], repair, label="probe JSON output")
    probe = ffprobe_json(media, repair)
    streams = _streams(probe)
    audio_streams = [row for row in streams if row["codec_type"] == "audio"]
    video_streams = [row for row in streams if row["codec_type"] == "video"]
    supported = len(audio_streams) >= 1
    mode = "single-program-repair" if len(audio_streams) == 1 else "separate-mic-bed-remix"
    payload: dict[str, Any] = {
        "schema_version": 1,
        "generated_at": utc_now(),
        "media_path": str(media),
        "source_sha256": sha256_file(media),
        "container_kind": "video" if video_streams else "audio-only",
        "duration_seconds": _duration(probe),
        "format": probe.get("format", {}),
        "streams": streams,
        "audio_streams": audio_streams,
        "video_streams": video_streams,
        "supported_shape": {
            "supported": supported,
            "reason": "requires at least one audio lane" if not supported else f"{mode} candidate available for analyze",
            "mode": mode if supported else None,
            "mic_streams_policy": "analyze infers a single mic lane from profiles; callers may later declare multiple mic streams in the plan slice, summed pre-automation",
            "bed_streams_policy": "single-program repair has no bed lane; multi-lane analysis uses only unambiguous or caller-confirmed direct bed lanes",
            "audio_only_supported": not video_streams,
            "per_speaker_repair": "out of scope",
        },
        "tool_versions": {
            "ffmpeg": ffmpeg_version(repair),
            "ffprobe": ffprobe_version(repair),
        },
    }
    write_json(json_out, payload)
    return 0


def _streams(probe: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    audio_pos = 0
    video_pos = 0
    for stream in probe.get("streams", []):
        codec_type = stream.get("codec_type")
        row = {
            "index": stream.get("index"),
            "codec_type": codec_type,
            "codec_name": stream.get("codec_name"),
            "channels": stream.get("channels"),
            "channel_layout": stream.get("channel_layout"),
            "sample_rate": stream.get("sample_rate"),
            "duration_seconds": _stream_duration(stream),
            "tags": stream.get("tags", {}),
            "disposition": stream.get("disposition", {}),
        }
        if codec_type == "audio":
            row["audio_stream_index"] = audio_pos
            audio_pos += 1
        elif codec_type == "video":
            row["video_stream_index"] = video_pos
            video_pos += 1
        rows.append(row)
    return rows


def _duration(probe: dict[str, Any]) -> float | None:
    try:
        return round(float(probe.get("format", {}).get("duration")), 3)
    except (TypeError, ValueError):
        return None


def _stream_duration(stream: dict[str, Any]) -> float | None:
    try:
        return round(float(stream.get("duration")), 3)
    except (TypeError, ValueError):
        return None
