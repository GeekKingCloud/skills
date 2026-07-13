# Repair Playbook

Use this after `rv plan-validate` or `rv verify` emits rows. Group by exact `failure_class`; when a matching heading exists, use it to understand the controlling cause. The row's machine-emitted `next_action` is authoritative for every class, including classes not expanded here. If the same class survives two candidates, switch mechanism instead of retuning the same surface.

## Plan And Lineage

### `stale_analysis_hash`

Plan or render no longer matches `analysis.json`; first rerun from `plan-init`, second rebuild the scratch chain from `probe` and `analyze`; clears when plan and verify hashes match.

### `stale_plan_hash`

Render came from a different plan; first rerun `render` from the current plan and sibling `plan_validation.json`, second render into a fresh candidate directory; clears when verify accepts the plan hash.

### `stale_source_hash`

The source changed across artifacts; first rerun the full probe-to-verify chain on the literal source path, second stop only if the source is externally unavailable; clears when all source hashes match.

### `hash_mismatch`

A component file no longer matches `render_manifest.json`; first rerun `render` and `verify`, second abandon the partial candidate and render fresh; clears when mic, bed, and mix hashes pass.

### `component_not_derived_from_plan`

A candidate mic or bed component, fixed-limiter result, or limiter metadata differs from verifier-owned derivation from the source and current plan. Discard substituted or additionally processed components and rerun `render` then `verify`; do not repair by rehashing the render manifest. Clears only when the verifier-derived hashes and fixed limiter metadata match.

### `missing_segments`

The plan has no coverage; first rerun `plan-init --analysis <analysis.json> --out <render_plan.json>`, second add full-duration segments only if generation is blocked; clears when coverage validates.

### `coverage_gap`

Segments leave unrendered time; first extend or split neighbors for continuous coverage, second regenerate if manual edits created multiple gaps; clears when no gap rows remain.

### `coverage_overlap`

Segments overlap; first align the later start to the prior end, second rebuild boundaries from `analysis.json` if overlap hides a real step; clears when coverage is continuous.

### `invalid_segment_duration`

A segment end is not after its start; first fix bounds from the regime map, second remove the segment and let neighbors cover the interval if it is not real; clears when every segment has positive duration.

### `micro_chunked_plan`

The plan has recreated dense per-window automation or lost baseline/overlay ownership. Repair continuous `mic_segments` and `bed_segments` first. Use `event_overlays` only for sparse residual events: at most six and 8% duration per owning baseline and 5% duration plan-wide. Give each overlay a distinct reason and a same-lineage structured citation within +/-5 s; never slice baselines per verifier window.

### `missing_step_boundary`

An analysis step lacks a split; split at the step and apply the new gain by the first coherent phrase. If the detector result is wrong, rerun `analyze` with bounded parameters and regenerate the plan. Plan-level boundary overrides are unsupported. Verify still checks recovery.

### `segment_spans_detected_step`

A segment crosses an analysis step; split the segment and set side-specific gains. If the step is false, rerun bounded analysis and regenerate the plan. Clears when no segment spans a detected step.

### `bed_segment_spans_detected_step`

The independent bed map has a sustained level step without a matching bed baseline boundary. Split `bed_segments` at that step and set each bed gain from its own raw bed BODY relative to the repaired mic target.

### `boundary_override_unsupported`

The plan attempts to erase a detected transition. Remove the override and retain the boundary, or rerun bounded analysis and regenerate the plan. Clears when `boundary_overrides` is empty.

### `non_finite_plan_value`

A segment or rails number is NaN, infinite, or outside sane bounds; first replace it with a real finite value from the regime map, second rerun `plan-init` if the plan was hand-corrupted; clears when validation passes.

### `todo_gain`

`mic_segments[].gain_db` or `bed_segments[].gain_db` is null; first set mic from shared target minus raw mic BODY and bed from repaired mic minus target gap, second rerun `plan-init` if stale; clears when all lane gains are numeric.

### `missing_judgment`

`mic_segments[].judgment` or `bed_segments[].judgment` is empty; first record `lift`, `trim`, `hold`, or `local-support`, second revisit role/regime decisions; clears when every baseline has judgment.

### `invalid_judgment`

One lane baseline uses an undocumented judgment; replace it with `lift`, `trim`, `hold`, or `local-support`, then revisit the baseline's role and evidence if none fit. Clears when every baseline has a valid judgment.

### `mic_gain_ceiling_exceeded`

Sustained mic gain exceeds the evidence-backed headroom ceiling for that regime; lower the affected `mic_segments[].gain_db` to `max_clean_gain_before_noise_floor_target_db` minus the rails safety margin, trim hot references, make the bed yield, or choose a bounded lower shared target. A digital capture-level drop with signal and floor lowered together can take a large clean lift; a noisy or analog-limited capture cannot.

### `mic_gain_ceiling_needs_evidence`

Mic gain exceeds the default clean ceiling without a citation to that segment's own `analysis.json` `clean_gain_headroom`; first cite the regime clean-headroom field or lower gain, second use bed yield or bounded target lowering if the headroom ceiling is too low. A file path or generic analysis citation is not enough; the citation must resolve to the affected regime's clean-gain evidence.

### `unramped_gain_step`

Adjacent mic gains jump too far; first add `ramp_in_seconds` or `ramp_out_seconds`, second split around the first coherent phrase and crossfade; clears when validation passes and no artifact row appears.

### `rails_adjustment_out_of_bounds`

A target shift exceeds `scripts/rv/audio-policy.json`; first bring the shift inside bounds, second remove the adjustment and solve with segment gains or bed yield; clears when adjusted rails validate.

### `rails_adjustment_missing_evidence`

A rail shift lacks `analysis_evidence_paths`; first cite concrete `analysis.json` fields, second remove the adjustment; clears when validation passes and the report headlines `Rails adjustments:`.

## Role Classes

### `plan_roles_mismatch_analysis`

The plan changed mic or bed lanes after analysis, so speech windows, bed body, and bed-presence rows are stale. Rerun `analyze` with both `--mic-streams` and `--bed-streams`, then rerun `plan-init`; do not use a plan-only override to reuse measurements from different lanes.

### `missing_mic_role`

No mic lane is selected; inspect isolated lanes, then rerun `analyze` with confirmed mic and bed selectors and rerun `plan-init`. Clears when analysis and plan agree on a direct commentary lane.

### `mic_role_has_mix_signature`

The selected mic behaves like an existing mix; inspect isolated lanes, choose the direct mic lane, rerun `analyze` with confirmed selectors, and rerun `plan-init`. Clears when the regenerated role map passes cross-exam.

### `unselected_lane_more_speech_shaped`

Another lane looks more like commentary; inspect isolated lanes, confirm the correct selectors in a fresh analysis, and regenerate the plan. Clears when `plan-validate` accepts the analysis-owned map.

## Render And Measurement

### `component_length_mismatch`

Components differ in length; first rerun `render` so mic, bed, and mix are explicitly padded and trimmed to the plan target sample count, second re-probe duration if decode start-time handling changed; clears when lengths match within tolerance.

### `null_test_failed`

Mix is not the exact component sum; first rerun `render`, second inspect stale replacement or partial writes; clears when null residual is within `scripts/rv/audio-policy.json`.

### `sample_peak_exceeded`

Sample peak exceeds the secondary headroom rail; first enable or tune declared mic-only peak control when the source has large clean lifts over expressive speech, then add a short structural `exception` trim over the named event with `event_reason`. Never limit the bed or mix. Clears when listener-heard component and mix sample peaks pass.

### `true_peak_unmeasured`

True peak was not reported; first rerun with an ffmpeg build that supports ebur128 peak output, second stop as `iteration-incomplete` only if the tool is unavailable; clears when true peak is measured.

### `true_peak_exceeded`

True peak exceeds the rail; first enable or tune declared mic-only peak control, then use structural event trims over any remaining named peaks. Do not trim a whole regime for one event and never limit the bed or mix. Clears when post-control mic, bed, and mix true peak satisfy `true_peak_dbtp.max` in `scripts/rv/audio-policy.json`.

### `peak_control_reshaped_body`

Declared peak control changed silence-inclusive matched-bin BODY energy by more than 0.5 dB or attenuated any 100 ms bin by more than 6 dB. First trim the offending regime's `mic_segments[].gain_db` slightly (0.3-0.5 dB, keeping BODY in band) so less material reaches the limiter; second raise the declared ceiling or replace broad limiting with cited structural event trims. Ceiling changes trade against mix true peak, so re-verify both. Do not widen the accounting rail.

### `peak_control_duty_exceeded`

Declared peak control attenuated 100 ms power by more than 0.5 dB for over 3% of all active speech or over 5% of one regime. Raise the ceiling or replace concentrated limiting with cited structural event trims.

### `peak_control_contiguous_run_exceeded`

Declared peak control remained active for more than 1.0 contiguous second of active speech. Raise the ceiling or replace sustained control with a cited structural event repair; clears when the longest run is <=1.0 s.

### `processed_mic_body_unmeasurable`

Raw speech exists but processed mic is not measurable; first check component routing and rerun render/verify, second revisit role choice; clears when processed mic windows measure.

### `insufficient_speech_coverage`

Processed speech is much thinner than raw speech density; first fix detector/render coverage and rerun analyze or verify, second repair phrase envelopes with hysteresis and short-gap bridging; clears when coverage meets the floor.

### `mic_below_rail`

Recoverable mic BODY is too quiet; first raise that regime's `mic_segments[].gain_db` within the default or cited headroom ceiling, second rebuild the regime baseline if only phrase islands were lifted. If this is a digital capture-level drop and floor dropped equally, cite clean headroom and lift; if it is noisy or analog-limited, use bed yield, bounded target lowering, or report the still-failing limitation. Clears only when mic BODY and rolling coverage pass.

### `mic_above_rail`

Mic BODY is too hot; first trim that regime's `mic_segments[].gain_db`, second split a hot plateau from the parent regime; clears when BODY and rolling coverage pass.

### `invalid_shared_mic_target` / `mic_baseline_misses_shared_target`

The plan declared an arbitrary target or a baseline that does not reach the highest safe shared line. Rerun `plan-init`; use only bounded, evidence-backed `rails_adjustment` for caller calibration or limiter-feasibility retargeting. Never lower the target merely to make the verifier pass.

### `invalid_shared_bed_target` / `bed_stitch_target_missed`

The independent bed states do not meet the common loudest-safe mic-priority line. Rebuild bed baselines from the shared bed target minus each raw bed regime BODY. Deeper yield is legal only when the planner's sustained-masking evidence requires it.

### `bed_stitch_adjacent_jump` / `bed_stitch_body_spread`

Processed sustained bed states still contain an audible capture-level jump. Align their baseline BODY targets; do not flatten jump scares, fades, or quiet events inside a state.

### `preserve_unity_bed_modified` / `preserved_unity_bed_body_changed`

A low-confidence bed regime was amplified, attenuated, ramped, overlaid, split, or no longer matches its raw BODY despite its machine-owned preserve-unity policy. Rerun `plan-init`; keep that regime as one exact 0 dB hold segment, put any boundary ramp wholly inside the adjacent stitchable regime, then rerun render and verify. Do not relabel quiet ambience as absent or include the held regime in shared bed stitching.

### `expressive_window_variation_disclosure`

The shared mic BODY passes but many individual windows sit outside the reference band. This is informational: inspect for natural whispers, shouts, and delivery changes. Repair only when BODY, stitching, transition, or applied-gain shape rows also identify a capture or automation fault.

### `mic_bed_gap_out_of_rail`

Meaningful bed masks the commentary for too much time or in too long a contiguous run. Lower the owning sustained bed baseline after mic stitching. Preserve brief cited expressive events; the gate is duration-weighted, not a single worst-window veto. There is no upper-gap failure and the bed may yield to silence. Every schema-2-or-newer bed plan remains blocking until `bed_yield_necessity` proves no material candidate-safe uniform lift remains.

### `bed_yield_not_minimal` / `missing_bed_yield_reconciliation`

Deep deliberate bed attenuation has not proven that the final macro plan is the loudest uniformly safe result. Rerun `plan-init` to generate schema 3 and its post-macro global recovery. If verification still names recoverable lift, increase every measured stitchable bed segment by exactly that uniform candidate-safe amount, keep relative macro corrections unchanged, update `targets.bed_yield_reconciliation`, then rerun plan validation, render, and verify. Held or unmeasured sections remain unchanged. Do not clear this with schema downgrade, `judgment`, `bed_yield_reason`, recommendation prose, or an upper-gap waiver.

### `bed_gain_exceeds_safe_ceiling` / `bed_yield_recovery_mismatch`

The declared global recovery is unsafe or is not applied uniformly. Rerun `plan-init`; retain one recovery value across every stitchable bed segment and leave preserve-unity regimes untouched.

### `unmeasured_bed_recovery_evidence_required` / `unmeasured_bed_recovery`

A stitchable bed segment lacks the BODY evidence needed to prove one global recovery. Rerun analysis to obtain that evidence or classify the indeterminate region as held, then regenerate the plan. Do not edit gains: the planner intentionally keeps global recovery at 0 dB until every participating segment is measurable.

### `unexplained_bed_present_gap_hole`

A bed-present speech window lacks measurable processed mic or bed; first fix component routing or measurement holes, second rerender if a component is partial; clears when all bed-present windows measure.

### `transition_recovery_late`

Post-step speech reaches rail too slowly; first split at the source-evidenced boundary and apply new gain by the first coherent phrase, second change mechanism with shorter ramp, crossfade, or parent-regime repair; clears when recovery is inside the active-speech deadline.

### `applied_gain_dip_artifact`

Processed/raw gain has a short unplanned dip; first remove the dip or make the ramp explicit, second replace detector-flicker movement with phrase/regime chunks; clears when applied gain matches the plan.

## Informational Limits

### `sparse-speech`

The source is genuinely sparse; first disclose it, second do not inflate silence to create coverage; clears by caller-packet disclosure.

### `sparse-bed`

No bed-present windows exist for gap checks; first disclose the coverage limit, second rerun analyze only if raw bed should be present; clears by disclosure or corrected analysis.

### `no-speech-after-step`

A detected step has no later speech to measure recovery; first disclose it, second rerun analyze only if raw post-step speech exists; clears by disclosure or corrected analysis.
