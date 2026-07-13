from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import shutil
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


class RvError(RuntimeError):
    def __init__(self, message: str, repair_commands: Iterable[str], code: int = 1) -> None:
        commands = "\n".join(f"  {command}" for command in repair_commands)
        super().__init__(f"{message}\nRepair commands:\n{commands}")
        self.code = code


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def read_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise RvError(f"{path} must contain a JSON object", [f'python remix-voiceover/scripts/rv.py probe "<media>" --json-out "{path}"'])
    return data


def write_json(path: str | Path, data: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        while temporary is None:
            candidate = target.with_name(f".{target.name}.{uuid.uuid4().hex}.tmp")
            try:
                handle = candidate.open("x", encoding="utf-8", newline="\n")
            except FileExistsError:
                continue
            temporary = candidate
        with handle:
            json.dump(data, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def refuse_output_alias(output: str | Path, protected: Iterable[str | Path], repair_commands: Iterable[str], *, label: str = "JSON output") -> None:
    target = Path(output)
    for value in protected:
        path = Path(value)
        same = target.resolve(strict=False) == path.resolve(strict=False)
        if not same and target.exists() and path.exists():
            try:
                same = os.path.samefile(target, path)
            except OSError:
                same = False
        if same:
            raise RvError(f"refused: {label} would overwrite or alias protected input {path}", repair_commands)


def write_csv(path: str | Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        # Exclusive creation matters even with UUID names: a pre-existing temp
        # path could itself be a link to a protected file. Never follow it.
        while temporary is None:
            candidate = target.with_name(f".{target.name}.{uuid.uuid4().hex}.tmp")
            try:
                handle = candidate.open("x", encoding="utf-8", newline="")
            except FileExistsError:
                continue
            temporary = candidate
        with handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow({field: row.get(field, "") for field in fieldnames})
            handle.flush()
            os.fsync(handle.fileno())
        # Replacing the directory entry severs an existing destination symlink
        # or hardlink instead of opening it and truncating its referent.
        os.replace(temporary, target)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def sha256_file(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_json(data: dict[str, Any]) -> str:
    payload = json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def require_tool(name: str, repair_commands: Iterable[str]) -> str:
    found = shutil.which(name)
    if not found:
        raise RvError(f"required tool not found on PATH: {name}", repair_commands)
    return found


def run_command(argv: list[str], repair_commands: Iterable[str], timeout: int = 900) -> subprocess.CompletedProcess[str]:
    try:
        proc = subprocess.run(
            argv,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            errors="replace",
            timeout=timeout,
        )
    except OSError as exc:
        raise RvError(f"failed to start command: {argv[0]}: {exc}", repair_commands) from exc
    except subprocess.TimeoutExpired as exc:
        raise RvError(f"command timed out after {timeout}s: {argv[0]}", repair_commands) from exc
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout)[-2000:].strip()
        raise RvError(f"command failed ({proc.returncode}): {' '.join(argv)}\n{detail}", repair_commands)
    return proc


def quantile(values: Iterable[float], q: float) -> float | None:
    vals = sorted(v for v in values if math.isfinite(v))
    if not vals:
        return None
    if len(vals) == 1:
        return vals[0]
    pos = (len(vals) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return vals[lo]
    return vals[lo] + (vals[hi] - vals[lo]) * (pos - lo)


def db_to_power(db_value: float) -> float:
    if not math.isfinite(db_value):
        return 0.0
    if db_value <= -120.0:
        return 0.0
    return 10 ** (db_value / 10.0)


def power_to_db(power: float) -> float:
    if power <= 0.0 or not math.isfinite(power):
        return -120.0
    return 10.0 * math.log10(power)


def power_mean_lufs(lufs_values: Iterable[float]) -> float | None:
    powers = [db_to_power(v) for v in lufs_values if math.isfinite(v) and v > -119.0]
    if not powers:
        return None
    return power_to_db(sum(powers) / len(powers))


def weighted_median(values_and_weights: Iterable[tuple[float, float]]) -> float | None:
    rows = sorted((float(value), max(0.0, float(weight))) for value, weight in values_and_weights if math.isfinite(float(value)) and math.isfinite(float(weight)) and float(weight) > 0.0)
    if not rows:
        return None
    total = sum(weight for _, weight in rows)
    midpoint = total / 2.0
    elapsed = 0.0
    for value, weight in rows:
        elapsed += weight
        if elapsed >= midpoint:
            return value
    return rows[-1][0]


def correlation(a_values: list[float], b_values: list[float]) -> float | None:
    aligned = [(x, y) for x, y in zip(a_values, b_values) if math.isfinite(x) and math.isfinite(y)]
    if len(aligned) < 2:
        return None
    a = [row[0] for row in aligned]
    b = [row[1] for row in aligned]
    n = len(aligned)
    ma = sum(a) / n
    mb = sum(b) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((y - mb) ** 2 for y in b)
    if va <= 0.0 or vb <= 0.0:
        return None
    return cov / math.sqrt(va * vb)


def rounded(value: float | None, places: int = 3) -> float | None:
    if value is None or not math.isfinite(value):
        return None
    return round(value, places)
