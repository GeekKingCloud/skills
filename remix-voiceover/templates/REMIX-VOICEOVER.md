# Remix Voiceover Report

## Status

- Run status: caller-test-ready
- Artifact mode: caller-test-mux
- Source: literal source path
- Output: literal output path or NOT RUN - reason
- Candidate sha256: promotion.candidate.sha256 value
- Filename contract: contract path or exact-output approved path
- Feedback mode decision: fresh-repair
- Rails adjustments: NONE
- Non-default analyze parameters: NONE
- Peak control enabled: false
- Peak control mechanism: NONE
- Peak control declared ceiling dBTP: NONE
- Peak control pre mic sha256: NONE
- Peak control post mic sha256: NONE
- Peak control worst regime BODY delta dB: NONE
- Peak control global duty: NONE
- Peak control worst regime duty: NONE
- Peak control max contiguous run seconds: NONE
- Exact output request: NONE
- Finalization evidence: NONE
- Outcome class: pass
- Limitation owner: NONE
- Limitation evidence: []
- Recommended fix: NONE

## Sidecars

- Probe: scratch/probe.json sha256=hash
- Analysis: scratch/analysis.json sha256=hash
- Render plan: scratch/render_plan.json sha256=hash
- Plan validation: scratch/plan_validation.json sha256=hash status=pass
- Render manifest: scratch/candidates/id/render_manifest.json sha256=hash
- Promotion manifest: scratch/candidates/id/promotion_manifest.json sha256=hash status=pass
- Delivery: scratch/candidates/id/delivery.json sha256=hash
- Stop state: NOT RUN - generated after report validation

## Proof

- Stream roles: mic streams, bed streams, excluded existing-mix streams, evidence path
- Macro regimes: regime ids and source-evidence summary
- Target rails: feasibility-derived shared mic BODY, shared bed BODY, sustained masking, transition recovery, true peak
- Candidate: mix path sha256=hash
- Commentary alignment: promotion_manifest rows summary
- Mic/bed gap: promotion_manifest rows summary
- Bed stitching: promotion_manifest bed_stitch rows summary
- Transition recovery: promotion_manifest rows summary
- Artifact and peak checks: promotion_manifest rows summary
- Peak-control disclosure: values above match promotion_manifest.json peak_control; NONE when disabled
- Diagnostic A/B evidence: NONE
- Informational rows: {"count": 0, "failure_classes": []}
- Bed balance reconciliation: NONE
- Preferred mic/bed gap dB: NONE
- Delivered meaningful-bed gap distribution: NONE
- Gap widening reason: NONE
- Remaining safe uniform bed lift dB: NONE

## Delivery

- Delivery status: delivered
- Output written: true
- Awaiting overwrite approval: false
- Next action: none
- Remix audio first/default: true
- Original audio preserved: true
- Source file preserved: true
- Video copied: true
- Remixed audio hash match: true

## Caller Summary

Short caller-facing summary of what was produced, where it is, and what remains for caller judgment or approval.

## Stop Or Blocker

- External blocker: NONE
- Runnable manifest work remains: NONE
- Terminal evidence: NONE
