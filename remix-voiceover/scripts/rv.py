#!/usr/bin/env python3
"""Thin CLI entry for the rebuilt remix-voiceover measurement spine."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from rv.analyze import analyze_command
from rv.audition import audition_command
from rv.cleanup import cleanup_command
from rv.deliver import deliver_command
from rv.plan import plan_init_command, plan_validate_command
from rv.probe import probe_command
from rv.render import render_command
from rv.stop import validate_stop_command
from rv.util import RvError
from rv.verify import verify_command


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="remix-voiceover deterministic repair spine")
    sub = parser.add_subparsers(dest="command", required=True)

    probe = sub.add_parser("probe", help="write source inventory and lineage fingerprint")
    probe.add_argument("media", help="source media path")
    probe.add_argument("--json-out", required=True, help="probe JSON output path")
    probe.set_defaults(func=probe_command)

    analyze = sub.add_parser("analyze", help="profile lanes and detect speech regimes")
    analyze.add_argument("media", help="source media path")
    analyze.add_argument("--probe", required=True, help="probe JSON path")
    analyze.add_argument("--json-out", required=True, help="analysis JSON output path")
    analyze.add_argument("--min-plateau-seconds", type=float)
    analyze.add_argument("--step-min-db", type=float)
    analyze.add_argument("--speech-threshold-below-body-db", type=float)
    analyze.add_argument("--mic-streams", help="comma-separated confirmed mic audio indexes, for example 1 or 0:a:1")
    analyze.add_argument("--bed-streams", help="comma-separated confirmed bed audio indexes, for example 2 or 0:a:2")
    analyze.set_defaults(func=analyze_command)

    plan_init = sub.add_parser("plan-init", help="draft render_plan.json from analysis.json")
    plan_init.add_argument("--analysis", required=True, help="analysis JSON path")
    plan_init.add_argument("--out", required=True, help="render plan output path")
    plan_init.set_defaults(func=plan_init_command)

    plan_validate = sub.add_parser("plan-validate", help="validate render_plan.json against analysis.json")
    plan_validate.add_argument("--plan", required=True, help="render plan JSON path")
    plan_validate.add_argument("--analysis", required=True, help="analysis JSON path")
    plan_validate.add_argument("--json-out", required=True, help="plan validation JSON output path")
    plan_validate.set_defaults(func=plan_validate_command)

    render = sub.add_parser("render", help="render mic, bed, and float-summed mix components")
    render.add_argument("--source", required=True, help="source media path")
    render.add_argument("--plan", required=True, help="validated render plan JSON path")
    render.add_argument("--outdir", required=True, help="candidate output directory")
    render.add_argument("--manifest-out", required=True, help="render manifest JSON output path")
    render.set_defaults(func=render_command)

    verify = sub.add_parser("verify", help="verify a rendered candidate manifest")
    verify.add_argument("--manifest", required=True, help="render manifest JSON path")
    verify.add_argument("--plan", required=True, help="render plan JSON path")
    verify.add_argument("--analysis", required=True, help="analysis JSON path")
    verify.add_argument("--json-out", required=True, help="promotion manifest JSON output path")
    verify.set_defaults(func=verify_command)

    audition = sub.add_parser("audition", help="generate a raw/processed diagnostic A/B packet")
    audition.add_argument("--source", required=True)
    audition.add_argument("--candidate-mic", required=True)
    audition.add_argument("--manifest", required=True, help="current rv-render manifest")
    audition.add_argument("--plan", required=True)
    audition.add_argument("--analysis", required=True)
    audition.add_argument("--regime-id", required=True)
    audition.add_argument("--start", required=True, type=float)
    audition.add_argument("--duration", required=True, type=float)
    audition.add_argument("--outdir", required=True)
    audition.add_argument("--json-out", required=True)
    audition.add_argument("--reviewed", action="store_true")
    audition.add_argument("--reviewed-by")
    audition.add_argument("--commentary-quality", choices=sorted({"excellent", "good", "fair", "poor", "unusable"}))
    audition.add_argument("--background-quality", choices=sorted({"excellent", "good", "fair", "poor", "unusable"}))
    audition.add_argument("--overall-quality", choices=sorted({"excellent", "good", "fair", "poor", "unusable"}))
    audition.set_defaults(func=audition_command)

    deliver = sub.add_parser("deliver", help="deliver a verified candidate with filename and hash-chain checks")
    deliver.add_argument("--manifest", required=True, help="promotion manifest JSON path")
    deliver.add_argument("--source", required=True, help="source media path")
    deliver.add_argument("--output", required=True, help="delivery output path")
    deliver.add_argument("--exact-output-request", help="verbatim caller text for exact non-contract output path")
    deliver.add_argument("--allow-overwrite", action="store_true", help="allow replacing an existing contract output")
    deliver.set_defaults(func=deliver_command)

    stop = sub.add_parser("validate-stop", help="validate report status against promotion and delivery manifests")
    stop.add_argument("--report", required=True, help="REMIX-VOICEOVER report path")
    stop.add_argument("--manifest", required=True, help="promotion manifest JSON path")
    stop.add_argument("--delivery", help="delivery JSON path")
    stop.add_argument("--json-out", required=True, help="stop-state JSON output path")
    stop.set_defaults(func=validate_stop_command)

    cleanup = sub.add_parser("cleanup", help="delete a successfully delivered and validated scratch transaction")
    cleanup.add_argument("--scratch", required=True, help="scratch transaction root under system temp")
    cleanup.add_argument("--delivery", required=True, help="delivery JSON inside scratch")
    cleanup.add_argument("--stop-state", required=True, help="passing stop-state JSON inside scratch")
    cleanup.set_defaults(func=cleanup_command)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except RvError as exc:
        print(str(exc), file=sys.stderr)
        return exc.code


if __name__ == "__main__":
    raise SystemExit(main())
