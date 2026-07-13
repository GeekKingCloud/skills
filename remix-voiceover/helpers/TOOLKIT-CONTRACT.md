# Toolkit Contract

Read this helper only when diagnosing `rv` render, peak-control, lineage, or verifier behavior. Normal runs should follow `SKILL.md` and machine `next_action` rows without loading these internals.

## Authority And Lineage

- `rv` commands are the only accepted source of promotion proof.
- Every stage binds its source, analysis, plan, candidate, and delivery inputs by canonical hashes.
- A diagnostic composite, custom render, manually rehashed artifact, or prior candidate may inform investigation but cannot replace a toolkit-owned component or promotion manifest.
- The workflow writes `plan_validation.json` beside the plan for auditability. Render does not trust that sidecar; it independently recomputes plan validation and records that result in its manifest.

## Plan Ownership

`plan-init` derives the highest safe shared mic target from the preferred house target and the weakest regime's measured clean-gain ceiling. Schema-3 plans then construct continuous mic and bed baselines, required transition ramps, bounded macro-balance sections, a uniform post-macro bed safety recovery, and recommended peak control. A low-confidence or evidence-indeterminate bed regime remains an exact unity baseline and does not participate in bed stitching, macro balance, or recovery; any material boundary step ramps wholly inside the adjacent stitchable segment.

Plan validation rejects arbitrary targets, plan-level role or boundary overrides, coverage gaps, micro-chunked baselines, unsafe gains, and unsupported automation. A coding agent may change schema-supported plan fields when applying a bounded caller calibration or following a machine `next_action`; the resulting plan must pass validation before rendering.

## Render Contract

- Mic and bed are rendered separately from confirmed direct source lanes.
- The listener mix is the exact `amix normalize=0` sum of the listener-heard mic component and bed component.
- Bed and mix are never limited.
- Optional peak control runs only on the mic after baseline and overlay gain automation. Its fixed mechanism is FFmpeg `alimiter` with a 5 ms attack, 50 ms release, auto-level disabled, and 4x processing rate returned to canonical 48 kHz.
- When peak control is enabled, render retains the pre-control mic and writes the post-control listener-heard mic separately.

## Verification Contract

Verification independently re-renders the pre-control mic and bed from the source and plan in verifier-owned system temp, reapplies the declared fixed limiter, and compares component and automation hashes. It measures the post-control listener-heard mic against the shared target and checks stitching, sustained masking, confirmed transition recovery, gain-shape artifacts, peak-control body change and duty, and true peak.

For every schema-2-or-newer bed plan, verification also computes a duration-weighted common-window gap distribution and counterfactual uniform bed-lift curve. It excludes held sections and bounds the actionable lift by both sustained masking and an actual lifted-bed/remixed-candidate true-peak check. Counterfactual peak search has fixed attempt, scratch-byte, free-space, and six-pass aggregate decoded-media budgets; it retains only one attempt at a time and must prove scratch cleanup. Only verifier-owned evidence can clear `bed_yield_necessity`; plan-authored judgments and recommendation fields are non-authoritative.

Peak control must remain sparse and transparent: silence-inclusive per-regime BODY energy delta no greater than 0.5 dB, global duty no greater than 3%, per-regime duty no greater than 5%, no controlled run over 1 second, and no 100 ms bin attenuated by more than 6 dB. It cannot raise loudness, flatten sustained delivery, control the bed, or limit the mix.

## Delivery Lineage

`deliver` accepts only a passing promotion manifest with intact lineage, and `validate-stop` cross-checks the finished report against promotion and delivery evidence. Filename, mux, overwrite, and reporting rules are owned by `helpers/DELIVERY.md`.
