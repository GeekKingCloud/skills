from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from .util import RvError, read_json, sha256_file, sha256_json


def cleanup_command(args: argparse.Namespace) -> int:
    scratch = Path(args.scratch)
    cleanup_successful_transaction(scratch, Path(args.delivery), Path(args.stop_state))
    print(json.dumps({"status": "cleaned", "scratch_root": str(scratch)}, sort_keys=True))
    return 0


def cleanup_successful_transaction(scratch: Path, delivery_path: Path, stop_path: Path) -> dict[str, Any]:
    raw_scratch = scratch.absolute()
    raw_is_junction = getattr(raw_scratch, "is_junction", lambda: False)
    if raw_scratch.is_symlink() or raw_is_junction():
        raise RvError("cleanup refused: scratch root cannot be a link or junction", [])
    scratch = scratch.resolve()
    delivery_path = delivery_path.resolve()
    stop_path = stop_path.resolve()
    temp_root = Path(tempfile.gettempdir()).resolve()
    if scratch == temp_root or temp_root not in scratch.parents:
        raise RvError("cleanup refused: scratch root must be a descendant of the system temp directory", [])
    if not scratch.name.lower().startswith("remix-voiceover"):
        raise RvError("cleanup refused: scratch root basename must start with remix-voiceover", [])
    if not scratch.is_dir():
        raise RvError("cleanup refused: scratch root is missing or is not a directory", [])
    _require_regular_tree(scratch)
    for label, path in (("delivery", delivery_path), ("stop state", stop_path)):
        if scratch != path and scratch not in path.parents:
            raise RvError(f"cleanup refused: {label} must be inside the scratch transaction", [])
        if not path.is_file():
            raise RvError(f"cleanup refused: {label} file is missing", [])

    delivery = read_json(delivery_path)
    stop = read_json(stop_path)
    if stop.get("generated_by") != "rv-validate-stop" or stop.get("status") != "pass" or stop.get("findings"):
        raise RvError("cleanup refused: stop state is not a clean rv-validate-stop pass", [])
    if stop.get("delivery_manifest_sha256") != sha256_json(delivery):
        raise RvError("cleanup refused: stop state does not bind the current delivery manifest", [])
    if delivery.get("generated_by") != "rv-deliver" or delivery.get("status") != "delivered" or delivery.get("output_written") is not True:
        raise RvError("cleanup refused: delivery is not complete", [])
    output = Path(str(delivery.get("output_path") or "")).resolve()
    source = Path(str(delivery.get("source_path") or "")).resolve()
    for label, path in (("output", output), ("source", source)):
        if path == scratch or scratch in path.parents:
            raise RvError(f"cleanup refused: {label} must be outside scratch", [])
        if not path.is_file():
            raise RvError(f"cleanup refused: {label} is missing", [])
    if sha256_file(output) != str(delivery.get("output_sha256") or "").lower():
        raise RvError("cleanup refused: final output hash does not match delivery", [])
    report_path = Path(str(stop.get("report_path") or "")).resolve()
    promotion_path = Path(str(stop.get("promotion_manifest_path") or "")).resolve()
    for label, path in (("report", report_path), ("promotion manifest", promotion_path)):
        if scratch != path and scratch not in path.parents:
            raise RvError(f"cleanup refused: {label} must be inside scratch", [])
        if not path.is_file():
            raise RvError(f"cleanup refused: {label} is missing", [])
    if sha256_file(report_path) != stop.get("report_sha256"):
        raise RvError("cleanup refused: report hash does not match stop state", [])
    if sha256_json(read_json(promotion_path)) != stop.get("promotion_manifest_sha256"):
        raise RvError("cleanup refused: promotion manifest hash does not match stop state", [])

    summary = {"output_path": str(output), "output_sha256": delivery["output_sha256"]}
    shutil.rmtree(scratch, ignore_errors=False)
    if scratch.exists():
        raise RvError(f"cleanup failed: scratch root still exists: {scratch}", [])
    return summary


def _require_regular_tree(root: Path) -> None:
    for current, directories, files in os.walk(root):
        for name in [*directories, *files]:
            path = Path(current, name)
            is_junction = getattr(path, "is_junction", lambda: False)
            if path.is_symlink() or is_junction():
                raise RvError(f"cleanup refused: scratch contains a link or junction: {path}", [])
