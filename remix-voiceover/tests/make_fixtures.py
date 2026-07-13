from __future__ import annotations

import math
import random
import subprocess
import wave
from pathlib import Path

SAMPLE_RATE = 48000


def make_all(outdir: Path) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    mic = outdir / "speech_drop_mic.wav"
    bed = outdir / "speech_drop_bed.wav"
    _write_mic(mic, duration=120.0, channels=2, drop=True)
    _write_bed(bed, duration=120.0, channels=2)
    video = outdir / "speech_drop_video.mkv"
    _mux(video, [mic, bed], video=True)

    mono_mic = outdir / "mono_mic.wav"
    stereo_bed = outdir / "stereo_bed.wav"
    _write_mic(mono_mic, duration=30.0, channels=1, drop=False)
    _write_bed(stereo_bed, duration=30.0, channels=2)
    mono_stereo = outdir / "mono_mic_stereo_bed.mka"
    _mux(mono_stereo, [mono_mic, stereo_bed], video=False)

    audio_only = outdir / "audio_only.mka"
    _mux(audio_only, [mic, bed], video=False)

    mix_mic = outdir / "mix_mic.wav"
    mix_bed = outdir / "mix_bed.wav"
    mix_lane = outdir / "mix_lane.wav"
    _write_mic(mix_mic, duration=45.0, channels=2, drop=False)
    _write_bed(mix_bed, duration=45.0, channels=2)
    _write_mix(mix_lane, mix_mic, mix_bed)
    mix_fixture = outdir / "existing_mix_signature.mka"
    _mux(mix_fixture, [mix_mic, mix_bed, mix_lane], video=False)

    single_lane = outdir / "single_lane.mka"
    _mux(single_lane, [mono_mic], video=False)

    dip_mic = outdir / "automation_dip_mic.wav"
    dip_bed = outdir / "automation_dip_bed.wav"
    _write_mic(dip_mic, duration=20.0, channels=2, drop=False)
    _write_bed(dip_bed, duration=20.0, channels=2)
    automation_dip = outdir / "automation_dip_source.mka"
    _mux(automation_dip, [dip_mic, dip_bed], video=False)
    return {
        "speech_drop_video": video,
        "mono_mic_stereo_bed": mono_stereo,
        "audio_only": audio_only,
        "existing_mix_signature": mix_fixture,
        "single_lane": single_lane,
        "automation_dip_source": automation_dip,
    }


def _write_mic(path: Path, *, duration: float, channels: int, drop: bool) -> None:
    rng = random.Random(991)
    total = int(duration * SAMPLE_RATE)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        frames = bytearray()
        for n in range(total):
            t = n / SAMPLE_RATE
            phrase = 1.0 if (t % 4.0) < 2.25 else 0.0
            attack = min(1.0, (t % 4.0) / 0.08) if phrase else 0.0
            release = min(1.0, (2.25 - (t % 4.0)) / 0.12) if phrase else 0.0
            env = phrase * max(0.0, min(attack, release, 1.0))
            level = 0.13
            if drop and 30.0 <= t < 90.0:
                level *= 10 ** (-18.0 / 20.0)
            carrier = 0.45 * math.sin(2.0 * math.pi * 180.0 * t) + 0.25 * math.sin(2.0 * math.pi * 997.0 * t)
            noise = rng.uniform(-1.0, 1.0) * 0.25
            sample = _clip16((carrier + noise) * env * level + rng.uniform(-1.0, 1.0) * 0.0008)
            for _ in range(channels):
                frames.extend(int(sample).to_bytes(2, "little", signed=True))
        wav.writeframes(frames)


def _write_bed(path: Path, *, duration: float, channels: int) -> None:
    rng = random.Random(337)
    total = int(duration * SAMPLE_RATE)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        frames = bytearray()
        for n in range(total):
            t = n / SAMPLE_RATE
            tone = 0.04 * math.sin(2.0 * math.pi * 91.0 * t) + 0.025 * math.sin(2.0 * math.pi * 311.0 * t)
            left = _clip16(tone + rng.uniform(-1.0, 1.0) * 0.012)
            right = _clip16(tone * 0.9 + rng.uniform(-1.0, 1.0) * 0.012)
            if channels == 1:
                frames.extend(int((left + right) / 2).to_bytes(2, "little", signed=True))
            else:
                frames.extend(int(left).to_bytes(2, "little", signed=True))
                frames.extend(int(right).to_bytes(2, "little", signed=True))
        wav.writeframes(frames)


def _write_mix(path: Path, mic_path: Path, bed_path: Path) -> None:
    with wave.open(str(mic_path), "rb") as mic, wave.open(str(bed_path), "rb") as bed, wave.open(str(path), "wb") as out:
        out.setnchannels(2)
        out.setsampwidth(2)
        out.setframerate(SAMPLE_RATE)
        mic_bytes = mic.readframes(mic.getnframes())
        bed_bytes = bed.readframes(bed.getnframes())
        frames = bytearray()
        for pos in range(0, min(len(mic_bytes), len(bed_bytes)), 2):
            a = int.from_bytes(mic_bytes[pos : pos + 2], "little", signed=True)
            b = int.from_bytes(bed_bytes[pos : pos + 2], "little", signed=True)
            frames.extend(int(max(-32768, min(32767, a + b))).to_bytes(2, "little", signed=True))
        out.writeframes(frames)


def _mux(output: Path, inputs: list[Path], *, video: bool) -> None:
    cmd = ["ffmpeg", "-hide_banner", "-nostdin", "-y"]
    if video:
        cmd += ["-f", "lavfi", "-i", "color=c=black:s=160x90:r=10:d=120"]
    for path in inputs:
        cmd += ["-i", str(path)]
    if video:
        cmd += ["-map", "0:v:0"]
        offset = 1
    else:
        offset = 0
    for idx in range(len(inputs)):
        cmd += ["-map", f"{idx + offset}:a:0"]
    cmd += ["-c:v", "ffv1", "-c:a", "flac", str(output)]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def _clip16(value: float) -> int:
    return int(max(-32768, min(32767, value * 32767.0)))
