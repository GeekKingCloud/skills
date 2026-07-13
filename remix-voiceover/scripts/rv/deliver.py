from __future__ import annotations

import argparse
import os
import uuid
from pathlib import Path
from typing import Any

from .audio import decoded_pcm_sha256
from .ffio import ffprobe_json
from .probe import _streams
from .util import RvError, read_json, refuse_output_alias, run_command, sha256_file, sha256_json, utc_now, write_json


def deliver_command(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest)
    promotion = read_json(manifest_path)
    source = Path(args.source)
    output = Path(args.output)
    delivery_path = manifest_path.with_name("delivery.json")
    rows = promotion.get("rows", [])
    blockers = [row for row in rows if row.get("status") == "fail"]
    if blockers:
        raise RvError(
            "deliver refused: promotion manifest has failing verifier rows",
            [f'python remix-voiceover/scripts/rv.py verify --manifest "<render_manifest.json>" --plan "<render_plan.json>" --analysis "<analysis.json>" --json-out "{manifest_path}"'],
        )
    candidate = promotion.get("candidate", {})
    if not candidate.get("path") or not Path(candidate["path"]).is_file():
        raise RvError(
            "deliver refused: promotion manifest candidate path is missing or not a file",
            [f'python remix-voiceover/scripts/rv.py verify --manifest "<render_manifest.json>" --plan "<render_plan.json>" --analysis "<analysis.json>" --json-out "{manifest_path}"'],
        )
    mix_path = Path(candidate["path"])
    if sha256_file(mix_path) != candidate.get("sha256"):
        raise RvError(
            "deliver refused: candidate mix hash does not match promotion manifest",
            [f'python remix-voiceover/scripts/rv.py verify --manifest "<render_manifest.json>" --plan "<render_plan.json>" --analysis "<analysis.json>" --json-out "{manifest_path}"'],
        )
    refuse_output_alias(
        delivery_path,
        [manifest_path, source, mix_path, output],
        _repair(manifest_path, source, output),
        label="delivery JSON output",
    )
    expected = source.with_name(f"{source.stem}-REMIX-VOICEOVER{source.suffix}")
    for protected_label, protected in (("source", source), ("verified candidate", mix_path)):
        try:
            same = output.exists() and protected.exists() and os.path.samefile(output, protected)
        except OSError:
            same = False
        if same or output.resolve() == protected.resolve():
            raise RvError(
                f"deliver refused: output path equals the {protected_label} path; the {protected_label} must never be overwritten",
                [f'python remix-voiceover/scripts/rv.py deliver --manifest "{manifest_path}" --source "{source}" --output "{expected}"'],
            )
    exact_quote = args.exact_output_request
    if output.resolve() != expected.resolve() and not exact_quote:
        raise RvError(
            f"deliver refused: output path must be the contract name {expected} unless --exact-output-request quotes the caller verbatim",
            [f'python remix-voiceover/scripts/rv.py deliver --manifest "{manifest_path}" --source "{source}" --output "{expected}"'],
        )
    if output.suffix.lower() not in {".mkv", ".mka", ".mp4", ".m4a", ".mov", ".flac", ".wav", ".wave"}:
        raise RvError(
            f"deliver refused: unsupported output container {output.suffix or '<none>'}; no verified same-container remix profile exists",
            ["add and test a delivery profile for this container; do not silently change the caller's extension"],
        )
    source_actual_sha = sha256_file(source)
    if source_actual_sha != promotion.get("source_sha256"):
        raise RvError(
            "deliver refused: source hash does not match promotion manifest",
            [
                f'python remix-voiceover/scripts/rv.py probe "{source}" --json-out "<probe.json>"',
                f'python remix-voiceover/scripts/rv.py analyze "{source}" --probe "<probe.json>" --json-out "<analysis.json>"',
                'python remix-voiceover/scripts/rv.py plan-init --analysis "<analysis.json>" --out "<render_plan.json>"',
                'python remix-voiceover/scripts/rv.py plan-validate --plan "<render_plan.json>" --analysis "<analysis.json>" --json-out "<plan_validation.json>"',
                f'python remix-voiceover/scripts/rv.py render --source "{source}" --plan "<render_plan.json>" --outdir "<candidate-dir>" --manifest-out "<render_manifest.json>"',
                f'python remix-voiceover/scripts/rv.py verify --manifest "<render_manifest.json>" --plan "<render_plan.json>" --analysis "<analysis.json>" --json-out "{manifest_path}"',
            ],
        )
    _validate_promotion_chain(promotion)
    if output.exists() and not args.allow_overwrite:
        payload = _base_delivery(promotion, manifest_path, source, output, expected, exact_quote)
        payload.update(
            {
                "status": "awaiting-overwrite",
                "artifact_mode": "scratch-candidate",
                "run_status": "caller-test-ready (awaiting overwrite approval)",
                "caller_test_mux_allowed_after_overwrite": True,
                "next_action": "approve overwrite",
                "output_written": False,
            }
        )
        write_json(delivery_path, payload)
        return 0
    mux = _mux_candidate(source, mix_path, output, _repair(manifest_path, source, output))
    payload = _base_delivery(promotion, manifest_path, source, output, expected, exact_quote)
    payload.update(
        {
            "status": "delivered",
            "artifact_mode": "caller-test-mux",
            "run_status": "caller-test-ready",
            "output_written": True,
            "output_sha256": sha256_file(output),
            "mux": mux,
            "next_action": "none",
        }
    )
    write_json(delivery_path, payload)
    return 0


def _mux_candidate(source: Path, mix_path: Path, output: Path, repair: list[str]) -> dict[str, Any]:
    """Mux a verified mix first while preserving source streams; return measured mux facts."""
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary_output = output.with_name(f".{output.stem}.rv-{uuid.uuid4().hex}{output.suffix}")
    probe = ffprobe_json(source, repair)
    streams = _streams(probe)
    has_video = any(row["codec_type"] == "video" for row in streams)
    preserve_original_streams = _container_supports_multiple_audio(output)
    if has_video and not preserve_original_streams:
        raise RvError(f"deliver failed: {output.suffix} cannot retain the source video and repaired audio under the same container contract", repair)
    remix_codec = _remix_codec_for_container(output)
    cmd = ["ffmpeg", "-hide_banner", "-nostdin", "-y", "-i", str(mix_path)]
    if preserve_original_streams:
        cmd += ["-i", str(source)]
        if has_video:
            cmd += ["-map", "1:v?"]
        cmd += ["-map", "0:a:0", "-map", "1:a?", "-map", "1:s?"]
        if _container_supports_attachments(output):
            cmd += ["-map", "1:t?"]
        if has_video:
            cmd += ["-c:v", "copy"]
    else:
        cmd += ["-map", "0:a:0"]
    cmd += ["-c", "copy", "-c:a:0", remix_codec]
    if remix_codec == "alac":
        cmd += ["-sample_fmt:a:0", "s16p"]
    elif remix_codec == "flac":
        cmd += ["-sample_fmt:a:0", "s32"]
    # Source dispositions are metadata and can contain a default flag. Clear every
    # audio disposition explicitly, then make only the verified remix the default.
    output_audio_count = len([row for row in streams if row["codec_type"] == "audio"]) + 1 if preserve_original_streams else 1
    for audio_index in range(output_audio_count):
        cmd += [f"-disposition:a:{audio_index}", "0"]
    cmd += ["-disposition:a:0", "default", str(temporary_output)]
    try:
        run_command(cmd, repair, timeout=1800)
        hash_sample_format = _remix_hash_sample_format(remix_codec)
        extracted_hash = decoded_pcm_sha256(temporary_output, repair, sample_format=hash_sample_format)
        candidate_pcm_hash = decoded_pcm_sha256(mix_path, repair, sample_format=hash_sample_format)
        if extracted_hash != candidate_pcm_hash:
            raise RvError("deliver failed: temporary mux remixed audio hash does not match candidate decoded PCM", repair)
        verified_inventory = _verify_mux_inventory(source, mix_path, temporary_output, repair, hash_sample_format, preserve_original_streams)
        os.replace(temporary_output, output)
    finally:
        temporary_output.unlink(missing_ok=True)
    return {
        "video_copied": bool(has_video and verified_inventory.get("video_streams_verified")),
        "remix_audio_stream_index": 0,
        "original_audio_streams_preserved_after_remix": preserve_original_streams,
        "source_file_preserved": True,
        "delivery_profile": "multiplex-preserved-originals" if preserve_original_streams else "native-single-program",
        "remix_audio_codec": remix_codec,
        "remix_hash_basis": f"decoded pcm {hash_sample_format} 48k stereo for container-transcoded remix streams",
        "candidate_audio_pcm_sha256": candidate_pcm_hash,
        "extracted_remix_audio_pcm_sha256": extracted_hash,
        "extracted_audio_hash_match": extracted_hash == candidate_pcm_hash,
        "verified_audio_inventory": verified_inventory,
    }


def _verify_mux_inventory(
    source: Path,
    mix_path: Path,
    output: Path,
    repair: list[str],
    hash_sample_format: str,
    preserve_original_streams: bool = True,
) -> dict[str, Any]:
    source_streams = _streams(ffprobe_json(source, repair))
    output_streams = _streams(ffprobe_json(output, repair))
    source_audio = [row for row in source_streams if row["codec_type"] == "audio"]
    output_audio = [row for row in output_streams if row["codec_type"] == "audio"]
    expected_count = len(source_audio) + 1 if preserve_original_streams else 1
    if len(output_audio) != expected_count:
        raise RvError(f"deliver failed: mux has {len(output_audio)} audio streams; expected {expected_count}", repair)
    defaults = [int(row["audio_stream_index"]) for row in output_audio if int((row.get("disposition") or {}).get("default") or 0) == 1]
    if not preserve_original_streams and len(output_audio) == 1 and not defaults:
        # Native single-program audio containers have one implicit program and
        # may not serialize a default disposition flag.
        defaults = [0]
    if defaults != [0]:
        raise RvError(f"deliver failed: mux default audio streams are {defaults}; expected only audio stream 0", repair)

    remix_hash = decoded_pcm_sha256(output, repair, sample_format=hash_sample_format, audio_stream_index=0)
    candidate_hash = decoded_pcm_sha256(mix_path, repair, sample_format=hash_sample_format)
    if remix_hash != candidate_hash:
        raise RvError("deliver failed: post-probed remix stream does not decode to the verified candidate", repair)

    preserved: list[dict[str, Any]] = []
    for source_index, source_row in enumerate(source_audio if preserve_original_streams else []):
        output_index = source_index + 1
        output_row = output_audio[output_index]
        identity_fields = ("codec_name", "channels", "channel_layout", "sample_rate")
        if any(source_row.get(field) != output_row.get(field) for field in identity_fields):
            raise RvError(f"deliver failed: preserved audio stream {source_index} inventory changed", repair)
        source_pcm = decoded_pcm_sha256(source, repair, audio_stream_index=source_index)
        output_pcm = decoded_pcm_sha256(output, repair, audio_stream_index=output_index)
        if source_pcm != output_pcm:
            raise RvError(f"deliver failed: preserved audio stream {source_index} decoded PCM changed", repair)
        preserved.append(
            {
                "source_audio_stream_index": source_index,
                "output_audio_stream_index": output_index,
                "codec_name": source_row.get("codec_name"),
                "channels": source_row.get("channels"),
                "channel_layout": source_row.get("channel_layout"),
                "sample_rate": source_row.get("sample_rate"),
                "default_disposition": int((output_row.get("disposition") or {}).get("default") or 0),
                "source_decoded_pcm_sha256": source_pcm,
                "output_decoded_pcm_sha256": output_pcm,
                "decoded_pcm_match": True,
            }
        )
    source_video = [row for row in source_streams if row["codec_type"] == "video"]
    output_video = [row for row in output_streams if row["codec_type"] == "video"]
    expected_video_count = len(source_video) if preserve_original_streams else 0
    if len(output_video) != expected_video_count:
        raise RvError(f"deliver failed: mux has {len(output_video)} video streams; expected {expected_video_count}", repair)
    verified_video: list[dict[str, Any]] = []
    for video_index, (source_row, output_row) in enumerate(zip(source_video if preserve_original_streams else [], output_video)):
        identity_fields = ("codec_name", "profile", "width", "height", "pix_fmt", "level")
        if any(source_row.get(field) != output_row.get(field) for field in identity_fields):
            raise RvError(f"deliver failed: copied video stream {video_index} inventory changed", repair)
        source_packet_hash = _copied_stream_hash(source, "v", video_index, repair)
        output_packet_hash = _copied_stream_hash(output, "v", video_index, repair)
        if source_packet_hash != output_packet_hash:
            raise RvError(f"deliver failed: copied video stream {video_index} packet hash changed", repair)
        verified_video.append(
            {
                "source_video_stream_index": video_index,
                "output_video_stream_index": video_index,
                "codec_name": source_row.get("codec_name"),
                "width": source_row.get("width"),
                "height": source_row.get("height"),
                "source_packet_sha256": source_packet_hash,
                "output_packet_sha256": output_packet_hash,
                "packet_hash_match": True,
            }
        )
    return {
        "audio_stream_count": len(output_audio),
        "expected_audio_stream_count": expected_count,
        "default_audio_stream_indexes": defaults,
        "remix_audio_stream_index": 0,
        "remix_candidate_decoded_pcm_match": True,
        "preserved_original_audio_streams": preserved,
        "original_streams_embedded": preserve_original_streams,
        "source_file_preserved_beside_output": True,
        "video_stream_count": len(output_video),
        "expected_video_stream_count": expected_video_count,
        "video_streams_verified": len(verified_video) == expected_video_count,
        "copied_video_streams": verified_video,
    }


def _copied_stream_hash(media: Path, stream_type: str, stream_index: int, repair: list[str]) -> str:
    proc = run_command(
        ["ffmpeg", "-hide_banner", "-nostdin", "-i", str(media), "-map", f"0:{stream_type}:{stream_index}", "-c", "copy", "-f", "hash", "-hash", "sha256", "-"],
        repair,
        timeout=1800,
    )
    line = next((line.strip() for line in proc.stdout.splitlines() if line.strip().upper().startswith("SHA256=")), "")
    digest = line.split("=", 1)[1].lower() if "=" in line else ""
    if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
        raise RvError(f"deliver failed: could not hash copied {stream_type}:{stream_index} stream", repair)
    return digest


def _validate_promotion_chain(promotion: dict[str, Any], *, require_promotable: bool = True) -> None:
    repair = ['rerun rv verify from the current render manifest, plan, and analysis before delivery']
    outcome = promotion.get("outcome") if isinstance(promotion.get("outcome"), dict) else {}
    if promotion.get("generated_by") != "rv-verify":
        raise RvError("promotion is not an rv-verify manifest", repair)
    if require_promotable and promotion.get("status") != "pass":
        raise RvError("promotion is not passing", repair)
    if require_promotable and outcome.get("class") not in {"pass", "target-limited"}:
        raise RvError("promotion outcome is not caller-test promotable", repair)
    required = {
        "render": (promotion.get("render_manifest_path"), promotion.get("render_manifest_sha256")),
        "plan": (promotion.get("plan_path"), promotion.get("plan_sha256")),
        "analysis": (promotion.get("analysis_path"), promotion.get("analysis_sha256")),
    }
    loaded: dict[str, dict[str, Any]] = {}
    for label, (path_value, expected_hash) in required.items():
        path = Path(str(path_value or ""))
        if not path.is_file():
            raise RvError(f"deliver refused: promotion {label} lineage file is missing", repair)
        payload = read_json(path)
        if not expected_hash or sha256_json(payload) != expected_hash:
            raise RvError(f"deliver refused: promotion {label} lineage hash does not match", repair)
        loaded[label] = payload
    render = loaded["render"]
    plan = loaded["plan"]
    analysis = loaded["analysis"]
    candidate = promotion.get("candidate") if isinstance(promotion.get("candidate"), dict) else {}
    rendered_mix = render.get("components", {}).get("mix", {})
    if render.get("generated_by") != "rv-render" or render.get("status") != "rendered":
        raise RvError("deliver refused: render lineage is not an rv-render manifest", repair)
    if candidate.get("path") != rendered_mix.get("path") or candidate.get("sha256") != rendered_mix.get("sha256"):
        raise RvError("deliver refused: promotion candidate differs from render lineage mix", repair)
    if render.get("plan_sha256") != sha256_json(plan) or render.get("analysis_sha256") != sha256_json(analysis):
        raise RvError("deliver refused: render, plan, and analysis lineage do not agree", repair)
    source_hash = promotion.get("source_sha256")
    if not source_hash or render.get("source_sha256") != source_hash or analysis.get("source_sha256") != source_hash:
        raise RvError("deliver refused: promotion source lineage is absent or inconsistent", repair)
    if plan.get("analysis", {}).get("sha256") != sha256_json(analysis) or plan.get("analysis", {}).get("source_sha256") != source_hash:
        raise RvError("deliver refused: plan analysis lineage is inconsistent", repair)
    row_type_counts: dict[str, int] = {}
    for row in promotion.get("rows", []):
        if isinstance(row, dict):
            row_type = str(row.get("type"))
            row_type_counts[row_type] = row_type_counts.get(row_type, 0) + 1
    row_types = set(row_type_counts)
    required_rows = {"hash", "lineage", "component_derivation", "length", "null_test", "sample_peak", "true_peak", "mic_lufs", "gain_dip_artifact"}
    if plan.get("roles", {}).get("bed_streams"):
        required_rows |= {"mic_bed_gap", "bed_stitch_target", "bed_stitch_spread", "bed_yield_necessity"}
    if int(plan.get("schema_version") or 1) >= 2:
        required_rows |= {"mic_stitch_target", "mic_stitch_spread"}
    if (plan.get("render", {}).get("peak_control") or {}).get("enabled") is True:
        required_rows |= {"peak_control_body_delta", "peak_control_duty", "peak_control_contiguous_run"}
    missing_rows = sorted(required_rows - row_types)
    if missing_rows:
        raise RvError(f"promotion verifier row inventory is incomplete: {', '.join(missing_rows)}", repair)
    if plan.get("roles", {}).get("bed_streams") and row_type_counts.get("bed_yield_necessity") != 1:
        raise RvError("promotion verifier row inventory must contain exactly one bed_yield_necessity row", repair)
    if plan.get("roles", {}).get("bed_streams"):
        bed_proof_row = next(row for row in promotion.get("rows", []) if isinstance(row, dict) and row.get("type") == "bed_yield_necessity")
        bed_proof = bed_proof_row.get("proof")
        required_proof_fields = {"policy", "triggered", "preferred_gap_db", "planned_bed_gains_db", "common_window_gap_distribution", "counterfactual_step_db", "maximum_allowed_unexplained_lift_db", "candidate_peak_evaluation"}
        if isinstance(bed_proof, dict):
            required_proof_fields |= {"maximum_masking_safe_uniform_lift_db", "controlling_failure"}
            if bed_proof.get("triggered") is True:
                required_proof_fields.add("maximum_candidate_safe_uniform_lift_db")
        if not isinstance(bed_proof, dict) or required_proof_fields - set(bed_proof):
            raise RvError("promotion bed_yield_necessity row has incomplete verifier-owned proof", repair)
    from .plan import materialized_overrides_and_adjustments
    from .verify import _classify_outcome, _peak_control_summary, _with_action_scopes, verify_candidate

    replayed_rows = _with_action_scopes(verify_candidate(render, plan, analysis, Path(str(promotion["render_manifest_path"]))))
    if sha256_json({"rows": replayed_rows}) != sha256_json({"rows": promotion.get("rows", [])}):
        raise RvError("promotion rows differ from a fresh verifier replay", repair)
    replayed_outcome = _classify_outcome(replayed_rows, plan)
    if replayed_outcome != outcome:
        raise RvError("promotion outcome differs from a fresh verifier replay", repair)
    replayed_blocking = [row for row in replayed_rows if row.get("status") == "fail"]
    expected_status = "fail" if replayed_blocking else "pass"
    if promotion.get("status") != expected_status:
        raise RvError("promotion status differs from a fresh verifier replay", repair)
    replayed_peak_control = _peak_control_summary(plan, render, replayed_rows)
    if promotion.get("peak_control") != replayed_peak_control:
        raise RvError("promotion peak_control differs from a fresh verifier replay", repair)
    replayed_surfaces = {
        **materialized_overrides_and_adjustments(plan),
        "non_default_analyze_parameters": [
            {"name": name, "value": row.get("value"), "default": row.get("default")}
            for name, row in analysis.get("parameters", {}).items()
            if isinstance(row, dict) and row.get("overridden")
        ],
    }
    if promotion.get("overrides_and_adjustments") != replayed_surfaces:
        raise RvError("promotion overrides_and_adjustments differs from a fresh verifier replay", repair)
    replayed_overall = {
        "status": "fail-with-work" if replayed_blocking else "pass",
        "pass": not replayed_blocking,
        "fail_with_work": bool(replayed_blocking),
        "fail_terminal_candidates": [],
    }
    if promotion.get("overall") != replayed_overall:
        raise RvError("promotion overall differs from a fresh verifier replay", repair)


def _base_delivery(promotion: dict[str, Any], manifest_path: Path, source: Path, output: Path, expected: Path, exact_quote: str | None) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "generated_by": "rv-deliver",
        "generated_at": utc_now(),
        "promotion_manifest_path": str(manifest_path),
        "promotion_manifest_sha256": sha256_json(promotion),
        "candidate_mix_sha256": promotion.get("candidate", {}).get("sha256"),
        "source_path": str(source),
        "source_sha256": sha256_file(source),
        "output_path": str(output),
        "contract_output_path": str(expected),
        "contract_name_match": output.resolve() == expected.resolve(),
        "exact_output_request": exact_quote,
        "filename_contract": "<source-stem>-REMIX-VOICEOVER.<source-extension> unless exact caller output is quoted verbatim",
    }


def _remix_codec_for_container(output: Path) -> str:
    if output.suffix.lower() in {".mp4", ".m4a", ".mov"}:
        return "alac"
    if output.suffix.lower() in {".mkv", ".mka", ".flac"}:
        return "flac"
    if output.suffix.lower() in {".wav", ".wave"}:
        return "pcm_f32le"
    return "copy"


def _remix_hash_sample_format(remix_codec: str) -> str:
    if remix_codec == "alac":
        return "s16le"
    if remix_codec == "flac":
        # FFmpeg's FLAC encoder stores s32 input at 24-bit coded precision.
        # Compare on that native lossless basis rather than the discarded low byte.
        return "s24le"
    return "f32le"


def _container_supports_attachments(output: Path) -> bool:
    return output.suffix.lower() in {".mkv", ".mka", ".webm"}


def _container_supports_multiple_audio(output: Path) -> bool:
    return output.suffix.lower() in {".mkv", ".mka", ".mp4", ".m4a", ".mov"}


def _repair(manifest_path: Path, source: Path, output: Path) -> list[str]:
    return [
        f'python remix-voiceover/scripts/rv.py verify --manifest "<render_manifest.json>" --plan "<render_plan.json>" --analysis "<analysis.json>" --json-out "{manifest_path}"',
        f'python remix-voiceover/scripts/rv.py deliver --manifest "{manifest_path}" --source "{source}" --output "{output}" --allow-overwrite',
    ]
