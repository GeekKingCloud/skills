from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any

from .deliver import _validate_promotion_chain, _verify_mux_inventory
from .util import RvError, read_json, refuse_output_alias, sha256_file, sha256_json, utc_now, write_json


def validate_stop_command(args: argparse.Namespace) -> int:
    report = Path(args.report)
    promotion_path = Path(args.manifest)
    protected = [report, promotion_path, *([Path(args.delivery)] if args.delivery else [])]
    refuse_output_alias(args.json_out, protected, ["choose a stop-state output distinct from report, promotion, and delivery"], label="stop-state JSON output")
    promotion = read_json(promotion_path)
    delivery = read_json(args.delivery) if args.delivery else None
    extra_protected: list[str | Path] = []
    candidate = promotion.get("candidate") if isinstance(promotion.get("candidate"), dict) else {}
    if candidate.get("path"):
        extra_protected.append(candidate["path"])
    if isinstance(delivery, dict):
        for key in ("source_path", "output_path"):
            if delivery.get(key):
                extra_protected.append(delivery[key])
    refuse_output_alias(args.json_out, extra_protected, ["choose a stop-state output distinct from media artifacts"], label="stop-state JSON output")
    text = report.read_text(encoding="utf-8") if report.exists() else ""
    findings = validate_stop(text, promotion, promotion_path, delivery)
    try:
        _validate_promotion_chain(promotion, require_promotable=False)
    except RvError as exc:
        findings.append(_finding("promotion_chain_invalid", str(exc).split("\nRepair commands:", 1)[0]))
    payload = {
        "schema_version": 1,
        "generated_by": "rv-validate-stop",
        "generated_at": utc_now(),
        "status": "pass" if not findings else "fail",
        "report_path": str(report),
        "report_sha256": sha256_file(report) if report.is_file() else None,
        "promotion_manifest_path": str(promotion_path),
        "promotion_manifest_sha256": sha256_json(promotion),
        "delivery_manifest_sha256": sha256_json(delivery) if isinstance(delivery, dict) else None,
        "findings": findings,
    }
    write_json(args.json_out, payload)
    return 0 if not findings else 1


def validate_stop(text: str, promotion: dict[str, Any], promotion_path: Path, delivery: dict[str, Any] | None) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    status = _report_value(text, "Run status")
    artifact = _report_value(text, "Artifact mode")
    rows = promotion.get("rows", [])
    failing = [row for row in rows if row.get("status") == "fail"]
    runnable = [row for row in failing if row.get("action_scope", "current-plan") == "current-plan" and row.get("next_action") and row.get("next_action") != "none"]
    outcome = promotion.get("outcome") if isinstance(promotion.get("outcome"), dict) else {}
    outcome_class = outcome.get("class")
    allowed_statuses = {"caller-test-ready", "iteration-incomplete", "blocked-terminal", "delivered-final"}
    ready_statuses = {"caller-test-ready", "delivered-final"}
    artifact_modes = {"scratch-candidate", "caller-test-mux", "final-deliverable"}
    if status not in allowed_statuses:
        findings.append(_finding("missing_or_unknown_run_status", f"Run status must be one of {sorted(allowed_statuses)}; got {status!r}"))
    if artifact not in artifact_modes:
        findings.append(_finding("missing_or_unknown_artifact_mode", f"Artifact mode must be one of {sorted(artifact_modes)}; got {artifact!r}"))
    expected_artifacts = {
        "iteration-incomplete": {"scratch-candidate"},
        "blocked-terminal": {"scratch-candidate"},
        "caller-test-ready": {"scratch-candidate", "caller-test-mux"},
        "delivered-final": {"final-deliverable"},
    }
    if status in expected_artifacts and artifact not in expected_artifacts[status]:
        findings.append(_finding("artifact_status_mismatch", f"artifact mode {artifact!r} is not valid for run status {status!r}"))
    if status == "caller-test-ready" and isinstance(delivery, dict):
        expected_artifact = "caller-test-mux" if delivery.get("status") == "delivered" else "scratch-candidate"
        if artifact != expected_artifact:
            findings.append(_finding("artifact_delivery_mismatch", f"delivery state {delivery.get('status')!r} requires artifact mode {expected_artifact}"))
    if status in ready_statuses:
        if failing:
            findings.append(_finding("false_pass_with_failing_rows", f"ready status {status} has {len(failing)} failing verifier rows"))
        if promotion.get("status") != "pass":
            findings.append(_finding("false_pass_manifest_not_pass", f"promotion status is {promotion.get('status')}"))
        if not _delivery_ok(delivery, promotion, promotion_path):
            findings.append(_finding("delivery_chain_not_intact", "ready status requires delivered hash chain or recorded awaiting-overwrite state"))
        if outcome_class not in {"pass", "target-limited"}:
            findings.append(_finding("ready_status_outcome_mismatch", f"ready status {status} requires a promotable outcome class; got {outcome_class!r}"))
    if status == "delivered-final":
        finalization = _report_value(text, "Finalization evidence")
        if not finalization or _noneish(finalization) or not _quoted(finalization) or not delivery or delivery.get("output_written") is not True:
            findings.append(_finding("final_without_caller_finalization", "delivered-final requires quoted caller finalization evidence and delivery.json with output_written true"))
    if status == "iteration-incomplete":
        external = _report_value(text, "External blocker") or _report_value(text, "External stop reason")
        if runnable:
            findings.append(_finding("false_stop_runnable_work", f"iteration-incomplete has runnable next_action rows: {runnable[0].get('next_action')}"))
        if outcome_class not in {"toolkit-limited", "external-blocked"}:
            findings.append(_finding("iteration_incomplete_outcome_mismatch", "iteration-incomplete requires machine-owned toolkit-limited or external-blocked outcome"))
        if outcome_class in {None, "external-blocked"} and (not external or _noneish(external)):
            findings.append(_finding("iteration_incomplete_missing_external_blocker", "iteration-incomplete requires a concrete external blocker"))
    if status == "blocked-terminal":
        if runnable:
            findings.append(_finding("blocked_terminal_with_runnable_work", "blocked-terminal is invalid while runnable next_action rows remain"))
        if outcome_class != "source-terminal":
            findings.append(_finding("blocked_terminal_outcome_mismatch", "blocked-terminal requires a machine-owned source-terminal outcome"))
        terminal_rows = [row for row in rows if row.get("failure_class") == "source_terminal" and isinstance(row.get("terminal_evidence"), dict)]
        if not terminal_rows:
            findings.append(_finding("blocked_terminal_evidence_missing", "blocked-terminal requires a source_terminal verifier row with terminal_evidence"))
        else:
            evidence = terminal_rows[0]["terminal_evidence"]
            if evidence.get("source_sha256") != promotion.get("source_sha256") or evidence.get("analysis_sha256") != promotion.get("analysis_sha256") or not evidence.get("reason_class"):
                findings.append(_finding("blocked_terminal_evidence_mismatch", "terminal evidence must bind reason, source hash, and analysis hash"))
    findings.extend(_required_report_lines(text, promotion, promotion_path, delivery))
    return findings


def _delivery_ok(delivery: dict[str, Any] | None, promotion: dict[str, Any], promotion_path: Path) -> bool:
    if not delivery:
        return False
    if delivery.get("generated_by") != "rv-deliver":
        return False
    if delivery.get("promotion_manifest_sha256") != sha256_json(promotion):
        return False
    candidate_hash = promotion.get("candidate", {}).get("sha256")
    delivery_candidate = delivery.get("candidate", {}) if isinstance(delivery.get("candidate"), dict) else {}
    delivery_candidate_hash = delivery_candidate.get("sha256") or delivery.get("candidate_mix_sha256")
    if candidate_hash and delivery_candidate_hash != candidate_hash:
        return False
    if delivery.get("source_sha256") != promotion.get("source_sha256"):
        return False
    if delivery.get("status") == "awaiting-overwrite" and delivery.get("caller_test_mux_allowed_after_overwrite"):
        return (
            delivery.get("artifact_mode") == "scratch-candidate"
            and bool(delivery.get("output_path"))
            and delivery.get("output_written") is False
            and delivery.get("next_action") == "approve overwrite"
        )
    mux = delivery.get("mux", {})
    if not delivery.get("output_path") or not delivery.get("output_sha256"):
        return False
    output_path = Path(delivery["output_path"])
    if not output_path.is_file() or sha256_file(output_path) != delivery.get("output_sha256"):
        return False
    if not (
        delivery.get("status") == "delivered"
        and delivery.get("artifact_mode") == "caller-test-mux"
        and delivery.get("output_written") is True
        and mux.get("extracted_audio_hash_match") is True
        and (delivery.get("contract_name_match") or delivery.get("exact_output_request"))
    ):
        return False
    source_value = delivery.get("source_path")
    candidate_value = promotion.get("candidate", {}).get("path")
    if not source_value or not candidate_value:
        return False
    source_path = Path(source_value)
    candidate_path = Path(candidate_value)
    if not source_path.is_file() or not candidate_path.is_file():
        return False
    if sha256_file(source_path) != delivery.get("source_sha256") or sha256_file(candidate_path) != candidate_hash:
        return False
    repair = ["rerun rv deliver from the current promotion manifest and source"]
    remix_codec = str(mux.get("remix_audio_codec") or "copy")
    sample_format = "s16le" if remix_codec == "alac" else "s24le" if remix_codec == "flac" else "f32le"
    try:
        preserve_original_streams = bool(mux.get("original_audio_streams_preserved_after_remix"))
        verified_inventory = _verify_mux_inventory(source_path, candidate_path, output_path, repair, sample_format, preserve_original_streams)
    except (RvError, OSError, ValueError):
        return False
    return mux.get("verified_audio_inventory") == verified_inventory


def _required_report_lines(text: str, promotion: dict[str, Any], promotion_path: Path, delivery: dict[str, Any] | None) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    required_labels = [
        "Run status",
        "Artifact mode",
        "Source",
        "Output",
        "Candidate sha256",
        "Promotion manifest",
        "Analysis",
        "Render plan",
        "Stop state",
        "Runnable manifest work remains",
        "External blocker",
        "Outcome class",
        "Limitation owner",
        "Limitation evidence",
        "Recommended fix",
        "Informational rows",
        "Bed balance reconciliation",
        "Preferred mic/bed gap dB",
        "Delivered meaningful-bed gap distribution",
        "Gap widening reason",
        "Remaining safe uniform bed lift dB",
        "Source file preserved",
    ]
    for label in required_labels:
        values = _report_values(text, label)
        value = values[0] if values else None
        if value is None:
            findings.append(_finding("missing_report_label", f"report must include {label}:"))
        elif len(values) > 1:
            findings.append(_finding("duplicate_report_label", f"report must include {label}: exactly once"))
        elif not value.strip():
            findings.append(_finding("missing_report_value", f"report label {label}: must carry a value, NONE, or NOT RUN - <reason>".replace("<reason>", "reason")))
    verbatim_quote_labels = ("exact output request", "finalization evidence")
    for line in text.splitlines():
        label_part = line.split(":", 1)[0].strip().lstrip("-* ").lower()
        if label_part in verbatim_quote_labels:
            continue
        if re.search(r"<[^>\n]+>|\bTODO\b|\bTBD\b", line, flags=re.IGNORECASE):
            findings.append(_finding("report_contains_placeholder", "report must not contain angle-bracket placeholders, TODO, or TBD outside verbatim caller quotes"))
            break
    candidate_hash = promotion.get("candidate", {}).get("sha256")
    report_candidate_hash = _report_value(text, "Candidate sha256")
    if candidate_hash and report_candidate_hash and report_candidate_hash != candidate_hash:
        findings.append(_finding("candidate_sha256_mismatch", "Candidate sha256 must equal promotion.candidate.sha256"))
    expected_lineage = _expected_report_lineage(promotion, promotion_path, delivery)
    for label, expected_value in expected_lineage.items():
        if _report_value(text, label) != expected_value:
            findings.append(_finding("report_lineage_mismatch", f"{label} must exactly match machine lineage: {expected_value}"))
    outcome = promotion.get("outcome") if isinstance(promotion.get("outcome"), dict) else {}
    expected_outcome = outcome.get("class")
    if expected_outcome and _report_value(text, "Outcome class") != str(expected_outcome):
        findings.append(_finding("outcome_class_report_mismatch", "Outcome class must match promotion.outcome.class"))
    expected_owner = outcome.get("limitation_owner")
    if expected_owner is not None and _report_value(text, "Limitation owner") != str(expected_owner):
        findings.append(_finding("limitation_owner_report_mismatch", "Limitation owner must match promotion.outcome.limitation_owner"))
    expected_evidence = json.dumps(outcome.get("evidence", []), sort_keys=True)
    if outcome and _report_value(text, "Limitation evidence") != expected_evidence:
        findings.append(_finding("limitation_evidence_report_mismatch", "Limitation evidence must exactly match JSON-serialized promotion.outcome.evidence"))
    expected_fix = outcome.get("recommended_fix")
    if expected_fix is not None and _report_value(text, "Recommended fix") != str(expected_fix):
        findings.append(_finding("recommended_fix_report_mismatch", "Recommended fix must match promotion.outcome.recommended_fix"))
    expected_informational = _informational_rows_summary(promotion)
    if _report_value(text, "Informational rows") != expected_informational:
        findings.append(
            _finding(
                "informational_rows_report_mismatch",
                f"Informational rows must exactly match passing promotion rows with a failure_class: {expected_informational}",
            )
        )
    expected_bed_reconciliation = _bed_balance_reconciliation_summary(promotion)
    if _report_value(text, "Bed balance reconciliation") != expected_bed_reconciliation:
        findings.append(_finding("bed_balance_reconciliation_report_mismatch", f"Bed balance reconciliation must exactly match verifier-owned proof: {expected_bed_reconciliation}"))
    for label, expected_value in _bed_balance_readable_fields(promotion).items():
        if _report_value(text, label) != expected_value:
            findings.append(_finding("bed_balance_readable_report_mismatch", f"{label} must exactly match verifier-owned bed balance evidence: {expected_value}"))
    failing = [
        row
        for row in promotion.get("rows", [])
        if row.get("status") == "fail"
        and row.get("action_scope", "current-plan") == "current-plan"
    ]
    runnable_value = _report_value(text, "Runnable manifest work remains")
    if runnable_value is not None:
        says_yes = _yesish(runnable_value)
        says_no = _noneish(runnable_value) or _noish(runnable_value)
        if bool(failing) and not says_yes:
            findings.append(_finding("runnable_work_report_mismatch", "Runnable manifest work remains must be yes when failing current-plan rows exist"))
        if not failing and not says_no:
            findings.append(_finding("runnable_work_report_mismatch", "Runnable manifest work remains must be NONE/no when no failing current-plan rows exist"))
    surfaces = promotion.get("overrides_and_adjustments", {})
    if surfaces.get("rails_adjustment") and "Rails adjustments:" not in text:
        findings.append(_finding("missing_rails_adjustment_report_line", "report must headline rails adjustments"))
    if surfaces.get("non_default_analyze_parameters") and "Non-default analyze parameters:" not in text:
        findings.append(_finding("missing_analyze_override_report_line", "report must headline non-default analyze parameters"))
    findings.extend(_peak_control_report_findings(text, promotion.get("peak_control")))
    if isinstance(delivery, dict) and delivery.get("status") == "delivered" and isinstance(delivery.get("mux"), dict):
        mux = delivery["mux"]
        expected_delivery = {
            "Delivery status": "delivered",
            "Output written": "true",
            "Remix audio first/default": "true" if mux.get("remix_audio_stream_index") == 0 and mux.get("verified_audio_inventory", {}).get("default_audio_stream_indexes") == [0] else "false",
            "Original audio preserved": "true" if mux.get("original_audio_streams_preserved_after_remix") is True else "false",
            "Source file preserved": "true" if mux.get("source_file_preserved") is True else "false",
            "Video copied": "true" if mux.get("video_copied") is True else "false",
            "Remixed audio hash match": "true" if mux.get("extracted_audio_hash_match") is True else "false",
        }
        for label, expected_value in expected_delivery.items():
            if _report_value(text, label) != expected_value:
                findings.append(_finding("delivery_report_mismatch", f"{label} must exactly match delivery.json mux evidence"))
    if delivery and delivery.get("exact_output_request"):
        quote = str(delivery["exact_output_request"])
        if "Exact output request:" not in text or quote not in text:
            findings.append(_finding("missing_exact_output_quote", "report must include the exact-output caller quote verbatim"))
    return findings


def _informational_rows_summary(promotion: dict[str, Any]) -> str:
    informational = [
        row
        for row in promotion.get("rows", [])
        if row.get("status") == "pass" and row.get("failure_class")
    ]
    classes = sorted(
        {
            str(row["failure_class"])
            for row in informational
        }
    )
    return json.dumps({"count": len(informational), "failure_classes": classes}, sort_keys=True)


def _bed_balance_reconciliation_summary(promotion: dict[str, Any]) -> str:
    rows = [row for row in promotion.get("rows", []) if row.get("type") == "bed_yield_necessity" and isinstance(row.get("proof"), dict)]
    if len(rows) != 1:
        return "NONE"
    return json.dumps(rows[0]["proof"], sort_keys=True)


def _bed_balance_readable_fields(promotion: dict[str, Any]) -> dict[str, str]:
    rows = [row for row in promotion.get("rows", []) if row.get("type") == "bed_yield_necessity" and isinstance(row.get("proof"), dict)]
    if len(rows) != 1:
        return {
            "Preferred mic/bed gap dB": "NONE",
            "Delivered meaningful-bed gap distribution": "NONE",
            "Gap widening reason": "NONE",
            "Remaining safe uniform bed lift dB": "NONE",
        }
    proof = rows[0]["proof"]
    preferred = proof.get("preferred_gap_db")
    distribution = proof.get("common_window_gap_distribution")
    controlling = proof.get("controlling_failure")
    remaining = proof.get("maximum_candidate_safe_uniform_lift_db")
    triggered = proof.get("triggered") is True
    return {
        "Preferred mic/bed gap dB": str(preferred) if preferred is not None else "NONE",
        "Delivered meaningful-bed gap distribution": json.dumps(distribution, sort_keys=True) if isinstance(distribution, list) else "NONE",
        "Gap widening reason": json.dumps(controlling, sort_keys=True) if isinstance(controlling, dict) else "NONE - deep bed yield not triggered" if not triggered else "NONE",
        "Remaining safe uniform bed lift dB": str(remaining) if remaining is not None else "NOT RUN - deep bed yield not triggered" if not triggered else "NONE",
    }


def _expected_report_lineage(promotion: dict[str, Any], promotion_path: Path, delivery: dict[str, Any] | None) -> dict[str, str]:
    render_path = Path(str(promotion.get("render_manifest_path") or ""))
    render: dict[str, Any] = {}
    if render_path.is_file():
        try:
            render = read_json(render_path)
        except (OSError, ValueError, RvError):
            render = {}
    source_path = (delivery or {}).get("source_path") or render.get("source_path")
    output_path = (delivery or {}).get("output_path")
    analysis_path = str(promotion.get("analysis_path") or "")
    plan_path = str(promotion.get("plan_path") or "")
    return {
        "Source": str(source_path) if source_path else "NOT RUN - promotion render lineage unavailable",
        "Output": str(output_path) if output_path else "NOT RUN - no delivery manifest",
        "Promotion manifest": f"{promotion_path} sha256={sha256_json(promotion)} status={promotion.get('status')}",
        "Analysis": f"{analysis_path} sha256={promotion.get('analysis_sha256')}" if analysis_path else "NOT RUN - promotion analysis lineage unavailable",
        "Render plan": f"{plan_path} sha256={promotion.get('plan_sha256')}" if plan_path else "NOT RUN - promotion plan lineage unavailable",
        "Stop state": "NOT RUN - generated after report validation",
    }


def _peak_control_report_findings(text: str, peak_control: Any) -> list[dict[str, Any]]:
    if not isinstance(peak_control, dict) or peak_control.get("enabled") is not True:
        return []
    findings: list[dict[str, Any]] = []
    expected = {
        "Peak control enabled": True,
        "Peak control mechanism": peak_control.get("mechanism"),
        "Peak control declared ceiling dBTP": peak_control.get("declared_true_peak_ceiling_dbtp"),
        "Peak control pre mic sha256": peak_control.get("pre_control_mic_sha256"),
        "Peak control post mic sha256": peak_control.get("post_control_mic_sha256"),
        "Peak control worst regime BODY delta dB": peak_control.get("worst_per_regime_body_delta_db"),
        "Peak control global duty": peak_control.get("global_duty_fraction"),
        "Peak control worst regime duty": peak_control.get("worst_regime_duty_fraction"),
        "Peak control max contiguous run seconds": peak_control.get("max_contiguous_controlled_run_seconds"),
    }
    numeric_labels = {
        "Peak control declared ceiling dBTP",
        "Peak control worst regime BODY delta dB",
        "Peak control global duty",
        "Peak control worst regime duty",
        "Peak control max contiguous run seconds",
    }
    for label, expected_value in expected.items():
        actual = _report_value(text, label)
        if actual is None or not actual.strip():
            findings.append(_finding("missing_peak_control_report_line", f"enabled peak control requires {label}:"))
            continue
        if expected_value is None:
            findings.append(_finding("peak_control_manifest_incomplete", f"promotion peak_control.{label} lacks a value"))
            continue
        if label == "Peak control enabled":
            matches = actual.strip().lower() == "true"
        elif label in numeric_labels:
            try:
                matches = math.isclose(float(actual), float(expected_value), rel_tol=0.0, abs_tol=1e-6)
            except ValueError:
                matches = False
        else:
            matches = actual == str(expected_value)
        if not matches:
            findings.append(_finding("peak_control_report_mismatch", f"{label} must match promotion_manifest.json peak_control"))
    return findings


def _report_value(text: str, label: str) -> str | None:
    values = _report_values(text, label)
    return values[0] if values else None


def _report_values(text: str, label: str) -> list[str]:
    pattern = re.compile(rf"^[ \t]*[-*]?[ \t]*{re.escape(label)}[ \t]*:[ \t]*([^\r\n]*?)[ \t]*$", re.IGNORECASE | re.MULTILINE)
    return [match.group(1).strip() for match in pattern.finditer(text)]


def _noneish(value: str) -> bool:
    normalized = value.strip().lower().strip(".")
    return normalized in {"none", "n/a", "na", "not applicable", "no", "no external blocker", "null", "-"}


def _noish(value: str) -> bool:
    normalized = value.strip().lower().strip(".")
    return normalized in {"false", "0", "none - no failing verifier rows"}


def _yesish(value: str) -> bool:
    normalized = value.strip().lower().strip(".")
    return normalized.startswith("yes") or normalized in {"true", "1"}


def _quoted(value: str) -> bool:
    stripped = value.strip()
    return len(stripped) >= 2 and ((stripped.startswith('"') and stripped.endswith('"')) or (stripped.startswith("'") and stripped.endswith("'")))


def _finding(code: str, message: str) -> dict[str, Any]:
    return {"code": code, "message": message}
