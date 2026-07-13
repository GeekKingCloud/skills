# Judgment Guide

Use this helper for evidence the coding agent must confirm and the bounded adjustments the `rv` toolkit permits. The toolkit owns the default target and baseline plan; do not rewrite generated values merely to express judgment. Record supported adjustments in `render_plan.json`; later commands consume them through `plan-validate`, `verify`, `deliver`, and `validate-stop`.

## Feedback Mode

Classify the request before `plan-init` or any rails adjustment.

- Use `listener-feedback-rerun` when the caller mentions a prior attempt, says to try again, or describes listening symptoms such as mic too quiet or background too close.
- Use `fresh-repair` only when no retry or listening symptom is present.
- If a retry is implied but the concrete feedback is not accessible, ask one clarifying question before rendering.
- Express caller calibration through one bounded, evidence-backed `rails_adjustment` and corresponding validated plan fields across all recoverable regimes, never a timestamp-only spot fix.
- Prove direction-of-change with `verify`; a louder-feeling result made only by lowering the bed does not satisfy "more present" commentary.

Pipeline record:

- Record the classification in the report's `Feedback mode decision`.
- When feedback changes targets, record `rails.rails_adjustment` in `render_plan.json` with `analysis_evidence_paths`.
- `verify` carries rail adjustments into `promotion_manifest.json` under `overrides_and_adjustments`.
- `validate-stop` requires a `Rails adjustments:` headline when an adjustment exists.

## Role Proof

Confirm roles after `probe` and `analyze`, before plan edits.

- Treat full-file behavior as evidence, not stream labels.
- Mic lanes have speech-shaped bursts, sentence gaps, breaths, delivery changes, and capture-level steps.
- Bed lanes are more continuous and less tied to sentence gaps.
- Existing-mix lanes mirror commentary plus bed; preserve them as original streams but never remix from them when separate mic and bed lanes exist.
- A ducked bed can look like an existing mix during mic-active windows; check background-only spans before excluding it.
- Same-recorder conventions are only priors. Overturn them only with multi-window isolated-role evidence.
- If the chosen mic lane omits recoverable speech present in another lane, the role map is wrong.
- After resolving a conflict, rerun `analyze` with both `--mic-streams` and `--bed-streams`, then rerun `plan-init`. This makes speech, bed body, and bed-presence measurements use exactly the confirmed lanes instead of carrying stale inferred-role measurements into a new plan.

Pipeline record:

- `analyze` writes lane profiles and inferred roles; when role flags are supplied it also writes `confirmed_roles` plus `role_confirmation: caller/agent-confirmed` in `analysis.json`.
- Keep normal choices in `roles.mic_streams`, `roles.bed_streams`, and `roles.excluded_existing_mix_streams`.
- If `role_conflicts` appear, inspect isolated lanes and rerun `analyze` with confirmed mic and bed selectors. Plan-level role overrides are unsupported because the measurements must be regenerated for the chosen lanes.
- `plan-validate` consumes the role fields and emits `missing_mic_role`, `mic_role_has_mix_signature`, or `unselected_lane_more_speech_shaped`.
- `plan-validate` rejects non-null `roles.role_override`; role correction happens by regenerating `analysis.json` and the plan.

## Regime Confirmation

Confirm the macro-regime map before setting gains.

- A macro regime is a sustained capture-level plateau for one component. Confirm mic and bed maps independently; a bed level step does not split the mic and a mic step does not split the bed.
- The default detector requires 120 seconds of directional evidence on both sides, with a bounded file-edge exception for an opening or closing plateau. This deliberately keeps 30-60 second expressive passages inside a regime. Lower `--min-plateau-seconds` only when source evidence identifies a shorter real capture transition; the override is recorded in analysis and the report.
- Pauses, breaths, menu silence, background-only gaps, yells, and whispers stay inside a regime unless raw evidence shows a capture state change.
- Merge speech-active groups across no-speech gaps when body level and capture behavior match.
- Split only on local evidence: speech-body step, capture-level drop or recovery, or hot shift.
- Do not split from clock cadence, chunk convenience, detector flicker, or ordinary pauses.
- Challenge a long weak first regime when later regimes are healthy; run an early-vs-rest step check and split only if bodies differ.
- Treat weak-regime boundaries and ordinary stitch regressions as section realignment work, not transition recovery.

Pipeline record:

- `analyze` writes mic `regimes`/`step_candidates` and independent `bed_regimes`/`bed_step_candidates` in `analysis.json`.
- `plan-init` places continuous `mic_segments` and `bed_segments` at their own detected steps.
- Keep confirmed mic boundaries in `mic_segments`; keep independent bed boundaries in `bed_segments`.
- Put sparse residual repairs in `event_overlays`, not in baseline arrays. Overlays compile deterministically into renderer slices and cannot consume the baseline budget.
- Use at most six residual overlays and 8% overlay duration per owning baseline, with a 5% whole-plan duration limit. Give every overlay a distinct `event_reason` and structured `event_citation`: `{source: analysis, ref: /step_candidates/0}` or `{source: promotion_manifest, path: prior/promotion_manifest.json, ref: /rows/0}`. A prior promotion citation may point to a passing or failing row, but its source and analysis hashes must match the current run. The cited object must carry event time, and the overlay must stay inside one baseline and its +/-5 s evidence neighborhood.
- Detected sustained mic and bed boundaries remain structural plan boundaries. If a detector result is wrong, rerun `analyze` with bounded detector parameters and regenerate the plan; plan-level boundary overrides are unsupported.
- `plan-validate` rejects non-empty `boundary_overrides` so a hand-authored evidence path cannot erase a real capture transition.

## Target Confirmation And Adjustment

Start from the target and baselines generated from source evidence and the shipped rails. Change them only through a bounded caller calibration or a machine-directed repair, then rerun plan validation.

- `plan-init` selects the source-first highest safe target; do not require an already-good prior candidate.
- Use `assets/default-rails.json` as the house numeric authority: processed mic ordinary BODY preferred -20.5 LUFS, mic-over-bed preferred 10.5 dB, sustained masking minimum 8 dB, and true peak <= -1.0 dBTP. These are workflow calibrations, not universal standards; see `references/AUDIO-ENGINEERING.md`.
- Align every recoverable regime's ordinary-speaking body to one shared target: lift weak regimes, trim hot regimes, hold healthy regimes.
- If the weakest recoverable regime cannot reach the preferred target cleanly, lower the shared target to its measured safe ceiling and trim healthier regimes to that line. Do not leave an audible dip and do not overgain the weak regime.
- Never choose the loudest raw regime, a damaged weak section, a muted-bed pass, or a previous candidate as the target unless the caller explicitly names it.
- Apply caller calibration requests across all recoverable regimes.
- Set bed after mic repair, from the repaired shared mic target and preferred gap. Start with the loudest safe independent bed baseline, retain bounded macro-balance corrections across sustained mic/bed intersections, then apply the planner's uniform post-macro safety recovery. These steps let the bed follow durable repaired-mic sections without phrase ducking; short, sparse, and absent-bed sections stay unchanged. There is no upper-gap blocker, but deliberate deep attenuation must pass verifier-owned counterfactual proof that no material uniform lift remains.
- When analysis marks an independent bed regime `preserve-unity-low-confidence` or `hold-unity-indeterminate`, leave it at exact unity. The former has complete curve evidence with no meaningful activity; the latter lacks complete evidence and must not be amplified speculatively. Either may contain silence, floor, or intentional quiet ambience. Exclude held regimes from stitching, macro balance, overlays, and ramps inside the held interval.
- Twelve decibels is the default evidence-and-audition trigger, not a physical damage threshold. Above it, cite the affected regime's `clean_gain_headroom`; the legal ceiling is that regime's measured maximum minus the safety margin, subject to true peak and peak-control checks.
- Treat digital capture-level drops differently from noisy analog limits. If the signal and floor dropped together, restoring gain preserves the original SNR and may be clean up to the measured headroom. If the floor did not drop, or the measured headroom minus safety margin is below the needed lift, do not force gain through the noise limit.
- Enable declared mic-only peak control when large clean regime lifts over expressive speech create isolated yell or emphasis peaks while ordinary speech BODY is already aligned. Use `render.peak_control` with `mechanism: alimiter` and a ceiling such as -1.5 dBTP; do not use it to raise loudness, flatten sustained delivery, control the bed, or limit the mix. Verification must show silence-inclusive per-regime BODY energy delta <=0.5 dB, duty <=3% globally and <=5% per regime, no controlled run over 1.0 s, and no 100 ms bin attenuated by more than 6 dB.

Pipeline record:

- When a machine `next_action` or valid rails adjustment requires plan edits, keep each baseline's `judgment` synchronized as `lift`, `trim`, `hold`, or `local-support`.
- Under that same supported repair, derive `mic_segments[].gain_db` from mic regime BODY and the validated shared target, and derive `bed_segments[].gain_db` from independent bed regime BODY and the repaired mic target.
- Use `rails.rails_adjustment` only inside the bounds in `assets/default-rails.json`; cite exact `analysis.json` fields.
- `plan-validate` consumes gain fields, judgment, gain ceilings, ramps, and rail adjustments.
- `render` and `verify` consume the validated plan through the fixed component and lineage contract in `helpers/TOOLKIT-CONTRACT.md`; load that helper only when diagnosing those mechanics.
- `verify` measures duration-weighted median typical-dialogue BODY, mic stitching, processed bed BODY stitching, sustained masking, and true peak; mix loudness is informational only.
- `verify` also owns `bed_yield_necessity`: it ignores planner prose, excludes held sections, raises the measured stitchable bed counterfactually in fixed increments, and blocks promotion when a material masking- and peak-safe uniform lift remains. Report the exact proof JSON under `Bed balance reconciliation:`.

## Diagnostic Quality-Limit Evidence

Use reviewed samples to choose the safest next repair or shared target; they do not waive a failing machine gate.

- Detector silence, threshold math, fatigue, or repeated candidate failure is not proof that a source is unrecoverable.
- Use direct raw-source or artifact evidence plus `analysis.json` clean-gain headroom.
- Generate and review a lineage-bound A/B packet yourself when playback is available and subjective damage is in question. Do not ask the caller to review scratch samples mid-run. Separate commentary quality, noise/background quality, and overall quality; objective metrics alone do not certify subjective quality.
- A digital capture-level drop is not unrecoverable merely because the needed lift is large; cite the regime headroom and repair it when the floor dropped equally.
- When a noisy or analog-limited capture cannot take the needed lift after the safety margin, use bed yield or bounded target lowering instead of overgain. Stop with a limitation report only when the promotion manifest supplies an eligible machine-owned outcome with no `current-plan` action.

Pipeline record:

- Keep `gain_db` inside the measured clean ceiling after the safety margin; a low-effort undergain does not clear.
- `verify` never turns subjective sample review into a nonblocking row. A caller-test candidate must still pass every gate at its declared shared target.
