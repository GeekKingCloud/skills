# Evidence Script Contracts

Use this helper when writing scratch scripts for measurement, manifests, or verification.

The skill does not require a packaged deterministic mixer. It does benefit from deterministic, source-agnostic evidence scripts. Scripts may be written per run, but their outputs should follow these contracts so reviewers can compare candidates consistently.

## Recommended Script Types

- `map_streams`: wrap stream metadata and source fingerprints.
- `analyze_lanes`: produce rolling RMS/peak/silence/activity summaries per stream.
- `select_blindspots`: select weak-mic/loud-bed, inactive-but-phrase-shaped, transition, phrase-start/tail, background-only, and random inactive/background-active windows.
- `make_chunk_map`: emit source-regime chunks, boundary basis, target body level, planned per-chunk gain/trim, boundary windows, stitch method, and bed baseline plan.
- `make_staged_repair_summary`: record the staged repair order, parent chunk-baseline candidate, exception queue, protected chunks, automation scope, and whether the candidate is strategy-valid.
- `extract_raw_phrases`: for transition, weak, buried, and detector-uncertain rows, measure raw mic phrase regions before source-limit or recovery classification.
- `make_local_reconstruction_plan`: for repairable exception groups, record the raw phrase evidence, baseline candidate, intended local support, protected chunks, slice test, and clearing evidence before full rendering.
- `make_manifest`: create candidate manifests with paths, hashes, commands, proof files, and cleanup status.
- `verify_candidate`: compare source evidence to candidate output and emit gap, headroom, duration, mic speaking-level alignment, section over-gain, speech-envelope stability, active-speech blind-spot, transition, bed-presence, overducking, and blind-spot checks.
- `audit_control_surface`: read the actual automation table, render script, filter graph, or command and summarize mic gain, bed baseline, local restraint depth, local restraint duty cycle, and smoothing/hold behavior.
- `verify_lineage`: verify candidate audio, render script/command, metrics scripts, processed metrics, manifests, and proof tables all identify the same retained candidate.
- `verify_mux`: check stream order/defaults, copied video, preserved original audio, duration, and candidate-to-final remix audio identity.
- `cleanup_report`: inspect retained/removed artifacts and report actual disk state.

## General Rules

- Scripts must be source-agnostic. Do not bake in file-specific timestamps or expected answers.
- Scripts must be path-safe. Treat paths as data, not shell fragments; use literal-path APIs or argument lists where the toolchain allows them.
- Use tools to measure and assemble the edit, not to replace the edit. A clean chunk map with per-chunk gain/trim and stitch proof is more useful than another broad full-track metric pass.
- Store scripts or command text in the scratch packet.
- Hash scripts or command files in the candidate manifest.
- Prefer structured JSON/CSV outputs over prose.
- Keep thresholds visible in output.
- Make missing evidence explicit instead of silently skipping a check.
- A script can flag listener risk; it cannot alone listener-accept a candidate.

Every verifier output should include:

```text
candidate_id | candidate_hash | source_hash_or_fingerprint | script_hash | tool_versions | status | thresholds | inputs | missing_evidence | blocking_findings | generated_at
```

Use `status=pass|fail|not_run|not_applicable`. Required checks that are `not_run` block promotion unless the report names the exact unavailable tool or permission and downgrades the artifact mode. `not_applicable` must include the source evidence or output-mode reason that makes the gate irrelevant.

Required gate outputs must not be placeholder/proxy passes. A gate output is invalid promotion evidence when it only reports that another verifier passed, contains only an aggregate row with no gate-specific measurements, or uses wording such as `metric proxy`, `blocking=NONE`, `see other check`, or equivalent instead of measuring the gate itself. Mark the gate `fail` with `failure_class=verifier-insufficient`, then repair the verifier or downgrade the artifact mode.

## Scratch Render Safety

Any new scratch render path must prove it is cheap enough before it processes the full recording.

- Run a 30-60 second representative slice through the new path first, including any chunk stitch, transition, overlay, smoothing, sidechain, or bed-control logic that the full render will use.
- Do not build full-duration sample-rate automation arrays and then smooth them with unbounded convolution. Any operation shaped like `duration_samples * kernel_samples` is a render-path bug unless the report proves bounded streaming or chunking.
- Keep dense automation at a low control rate. Expand it cheaply during render with interpolation, media filters, block streaming, or bounded-window processing.
- For smoothing gain or envelopes, prefer interpolation, bounded IIR/FIR filters, media-filter smoothing, or block-wise processing over `np.repeat(..., sample_rate)` plus full-array convolution.
- A renderer must show progress, emit a growing output file, or write a current progress marker within a short expected interval. If it does not, stop the render and inspect the process state instead of waiting indefinitely.
- After an interrupted or killed render, check for orphaned render processes such as media encoders or script interpreters before starting the next candidate.
- Treat a candidate directory with no completed audio, manifest, and lineage proof as `partial-invalid`, not as a retained candidate or baseline.
- Manifests and lineage files must be built from plain JSON-serializable data. Do not serialize parser objects, functions, file handles, or other runtime objects as command proof.

## Minimum Evidence Objects

For repair runs, produce these objects or report `NOT RUN - reason`:

```text
stream_roles.csv/json
mic_regimes.csv/json
background_regimes.csv/json
blindspots.csv/json
chunk_map.csv/json
chunk_map_validity.csv/json
raw_phrase_extraction.csv/json when transition, weak, buried, detector-uncertain, or source-limit rows need phrase-local evidence
staged_repair_summary.csv/json
local_reconstruction_plan.csv/json when local reconstruction, overlay, phrase-local support, detector-basis replacement, or intelligibility-first fallback is named
automation_control.csv/json when dense gain, phrase, bed, or overlay control is needed
render_safety_check.csv/json for any new scratch render path
source_lane_lineage_check.csv/json
control_surface_audit.csv/json when automation_control, generated filters, sidechain, phrase controls, local restraint, or overlay control is used
candidate_manifest.json
lineage_verification.json
balance_checks.csv/json
mic_alignment_checks.csv/json
section_overgain_checks.csv/json
active_speech_blindspot_checks.csv/json
transition_checks.csv/json
speech_envelope_stability_checks.csv/json
overducking_checks.csv/json
worst_window_packet.csv/json
repair_ledger.csv/json
mux_verification.json
cleanup_summary.json
```

`lineage_verification` must be produced before listener-risk or proof promotion review. It should include candidate hash, render script or command hash, metrics script hashes, processed metric hashes, manifest hash, and a stale/edited-proof check. If a render script changed after the candidate was rendered, rerender or mark the candidate lineage-broken. If required evidence CSV/JSON files are empty, they must contain `NOT RUN - reason`; otherwise promotion and terminal `blocked` are both invalid while rerun/reverification is possible.

`candidate_manifest` and `source_lane_lineage_check` must identify every audio input used to render the candidate. Use `render_source_mode=direct-source-lanes` only when the candidate is rendered from the proven mic/commentary and background source lanes. Use `render_source_mode=diagnostic-composite` when an existing mix, prior candidate, muxed output, or other already-mixed audio is used as an audio substrate. A diagnostic composite may be retained as scratch evidence or a regression reference, but it cannot support caller-test promotion. If the candidate claims `exact-separated-reconstruction`, prove the reconstructed separated mic and bed lineage with hashes and per-lane evidence before review.

Recommended source-lane lineage schema:

```text
candidate_id | candidate_hash | render_source_mode | direct_mic_source | direct_bed_source | composite_audio_inputs | reference_only_inputs | audio_substrate_inputs | separated_reconstruction_proof | status | failure_class | action
```

`staged_repair_summary` must prove the run followed the staged order before any automation-heavy candidate is promotion-eligible. A candidate that uses dense automation, generated per-window filters, sidechain curves, local restraint, phrase controls, or overlays must identify a parent `stage1-chunk-baseline`, the failed-gate exception queue it targets, the protected chunks/regression windows, and the automation scope. If automation covers most of the recording or has hundreds/thousands of control rows without proving those rows are only exception support, fail with `dense-automation-primary` or `strategy-order-violation`.

`local_reconstruction_plan` is required when a failed-gate queue names local reconstruction, overlay, intelligibility-first fallback, phrase-local support, detector-basis replacement, or baseline-local overlay. It must identify the controlling groups, raw phrase evidence, parent baseline, intended support, slice proof, protected regression windows, and full-render disposition. The parent baseline is a regression/reference plan, not an audio substrate; promotion-grade output still needs direct source-lane lineage unless exact separated reconstruction is proven. A row whose action is only `try different mechanism` or `needs local reconstruction` fails as `verifier-insufficient` until the mechanism is attempted or an external blocker is recorded.

Recommended local reconstruction schema:

```text
candidate_id | parent_baseline | group_id | failure_classes | representative_windows | raw_phrase_evidence_path | source_limit_class | intended_support | control_surface | protected_chunks | regression_windows | slice_test_path | slice_status | material_change_from_parent | full_render_status | clearing_evidence | status | failure_class | action
```

Recommended staged-repair schema:

```text
candidate_id | candidate_hash | stage | parent_chunk_baseline_candidate | parent_chunk_baseline_hash | chunk_count | median_chunk_duration | exception_group_count | exception_window_count | exception_coverage_seconds | automation_required_reason | automation_scope | automation_coverage_seconds | automation_region_count | protected_chunks | protected_regression_windows | strategy_status | failure_class | action
```

Use `stage=stage1-chunk-baseline|stage2-exception-queue|stage3-bounded-automation`. `stage3-bounded-automation` cannot pass with `parent_chunk_baseline_candidate=NONE`, with an empty exception queue, or with `automation_scope=whole-recording-primary`.

`control_surface_audit` must be generated from the actual retained render inputs when automation is present. It is not enough to infer from output loudness. The audit must fail if proof says there is no bed movement while `automation_control`, the filter graph, sidechain configuration, render script, or command contains per-window bed controls.

Recommended control-surface schema:

```text
candidate_id | candidate_hash | automation_path | filter_or_script_path | staged_repair_summary_path | parent_chunk_baseline_candidate | control_region_count | controlled_seconds | automation_scope | raw_bed_body_db | repaired_mic_body_db | target_bed_relationship | bed_baseline_decision | mic_gain_min_db | mic_gain_max_db | mic_gain_avg_db | mic_gain_ceiling_hit_count | bed_base_min_db | bed_base_max_db | bed_base_avg_db | bed_extra_min_db | bed_extra_max_db | bed_extra_avg_db | bed_cut_ge_6db_seconds | bed_cut_ge_10db_seconds | bed_cut_duty_cycle | shallow_restraint_ratio | abrupt_enable_count | smoothing_or_hold_basis | compressor_limiter_summary | status | failure_class | action
```

Promotion fails when `control_surface_audit` shows `high-bed-baseline`, `aggressive-ducking-primary`, `dense-automation-primary`, `strategy-order-violation`, `bed-envelope-waviness`, `hot-or-harsh-speech`, or `control-surface-verifier-gap`. These are not style notes; they mean the candidate reached acceptable-looking numbers through the wrong mechanism.

`balance_checks` must use the control-surface audit when it exists. A gap below target indicates masking risk. A very large gap indicates bed collapse or absent raw bed unless raw source proves otherwise. A hot bed baseline plus frequent local cuts is an overducking failure even when per-window gap values pass.

When a control-surface audit exists, aggregate promotion proof must record its path/hash and list which gate outputs consumed that exact hash. Balance, overducking, bed-envelope, listener-risk review, and the report cannot clear promotion from a different or missing control-surface basis. When a staged-repair summary exists, aggregate promotion proof must also record its path/hash and fail promotion if the strategy status is not passing.

`mic_alignment_checks` must compare ordinary speaking-body level across recoverable commentary regimes after repair. It should exclude silence, breaths, yells, whispers, and source-limited noise-floor spans. Both quiet and hot regimes are repair targets. A regime that remains shifted down or over-forward from the same speaker's normal talking level blocks promotion unless the report proves it is source-limited.

`mic_alignment_checks` must contain sustained-regime rows as well as hard-window rows. A long weak/problem section cannot pass from one or two phrase snippets. Each sustained-regime row should state the section start/end, active phrase count, active speech seconds, coverage basis, repaired body level, target, delta, status, and failure class. If active-speech coverage is too sparse to represent the section, the gate fails as `verifier-insufficient`, `raw-phrase-extraction-missing`, or `source-limited-unproven`; it does not pass by omission.

`chunk_map_validity` must prove the retained candidate's chunks are source-regime chunks, not coarse fixed-width bins or per-second control rows. It should flag any chunk that crosses a detected transition, mixes incompatible hot and weak behavior, lacks a boundary basis, uses fixed windows as a substitute for source evidence, or is so dense that it acts like detector flicker/automation rather than an editorial chunk map. A failed chunk-map-validity row blocks promotion and requires rebuilding the chunk map before another gain or bed tweak.

At minimum, `chunk_map_validity` should include:

```text
candidate_id | candidate_hash | chunk_count | duration_seconds | median_chunk_duration | short_chunk_ratio | fixed_bin_basis_ratio | micro_chunk_basis_ratio | dense_automation_separate | status | failure_class | action
```

Short chunks are allowed for true boundaries, first phrases, and phrase starts/tails. They are not allowed to dominate the whole map. If dense second-level control is needed, write `automation_control.csv/json` and keep `chunk_map` at phrase/regime level.

`mic_alignment_checks` must use the accepted reference section when caller or reviewer listening explicitly identifies one as the target relationship. Do not choose a raw healthy or loud capture regime as the target when caller feedback says it is too loud, and do not choose a repaired weak/problem section as the target when the caller describes it as the broken section. `accepted_reference_section=NONE` is valid when the caller has not explicitly named a target section, but the verifier must still derive and report a provisional comfortable speech target.

`mic_alignment_checks` must be fine enough to catch transition-adjacent drift. Coarse fixed windows are useful context only. When a mic regime boundary, caller-example transition, or detected level step exists inside a broad window, emit separate pre-transition, first-recoverable-phrase, early-post-transition, and sustained-post-transition rows. A candidate cannot pass mic alignment from a broad average that hides slow recovery or section mismatch.

`section_overgain_checks` must compare first, middle, late, recovered, and hot commentary regimes after repair. It should flag sections whose normal speech body, peaks, crest behavior, or listener notes indicate excessive gain, clipping, limiting, saturation, harshness, or muffling. A candidate cannot pass by making weak sections correct while leaving other regimes uncomfortably loud.

Section over-gain proof must compare each section against the accepted or provisional reference, not only against a generous ceiling. A section several dB hotter than the reference, a positive `dBFS` peak in a field labeled as dBFS, or any ambiguous peak unit that appears above full scale blocks promotion as `section-overgain` or `verifier-insufficient` until resolved.

Section over-gain proof cannot pass when `peak_after_dbfs`, crest behavior, limiter stress, or artifact checks are `NOT RUN - per-window peak extraction required` for caller-test-relevant sections. Either run the peak/crest check, keep the candidate scratch-only, or classify the proof as `verifier-insufficient`.

`active_speech_blindspot_checks` must evaluate active speech seconds inside each weak, transition, phrase-start, phrase-tail, and detector-uncertain blind spot. Keep whole-window statistics as context only. Do not call a window buried or cleared solely from whole-window medians when much of the window is silence, breath, pause, or inactive background. Each row should include active-speech duration, active-speech body level, bed level during active speech, detector basis, and whether the candidate preserves starts/tails.

Hard-window active-speech rows with tiny active-speech duration are local probes, not whole-section clearance. If a hard-window row is the only proof for a sustained weak/problem section, aggregate promotion fails with `verifier-insufficient` or `speaking-level-misalignment` until sustained-regime coverage is produced.

`speech_envelope_stability_checks` must look for the mic cutting in/out, pumping, wobbling, or following detector flicker. It should include transition windows, weak-mic windows, phrase starts/tails, and random active-speech windows. A candidate that makes the commentary sound shaped by a gate, expander, overreactive normalizer, or sidechain detector blocks promotion even if the numeric voice/background gap looks acceptable.

`raw-shaped-envelope-movement` is not an automatic pass or `not_applicable`. Use it only when raw and candidate evidence show the repair did not amplify the movement and the movement does not create audible mic waviness. If the caller reports waviness, or if processed active-speech movement is large enough to be distracting, keep the row blocking until a phrase-stable repair or source-limit proof clears it.

`transition_checks` must directly measure recovery at every detected capture-level commentary transition and caller-reported transition failure class. Use the canonical `boundary_type` enum from `REGIME-MAPPING.md`; only `capture-level-transition`, `recovery-transition`, `hot-shift`, and `caller-example-transition` are transition rows. Do not convert every chunk boundary, weak-regime boundary, or background boundary into a transition check. Each row should include boundary type, transition basis, raw phrase evidence, raw pre/post mic body, repaired first-recoverable-phrase body, repaired early-post-transition body, target reference body, seconds to recovery, phrase-start/tail preservation, bed body during recovery, bed gap during recovery, and action. A pass means the next coherent recoverable phrase is already near the ordinary-speaking target without harshness, muffling, missing starts/tails, bed masking, or bed collapse. Do not derive transition pass from `active_speech_blindspot_checks`, broad balance, or section averages.

If the first detected active span is shorter than the active-speech threshold, the verifier must expand to the next coherent phrase within the transition region before using `not_applicable`. A row with `NOT RECOVERED`, a large early-post-transition miss from target, or a caller-reported slow recovery cannot be promotion-neutral.

If a transition or source-limit row says raw evidence `requires phrase-local extraction`, `unknown`, or equivalent, the verifier must run `extract_raw_phrases` or mark the gate `fail` with `failure_class=verifier-insufficient`. Such rows cannot be counted as source-limit-suspect, source-limited, or caller-facing remaining risk.

`extract_raw_phrases` must locate actual raw phrase spans inside the search window and measure those spans. Coarse 2-second frame summaries, fixed-window RMS/peak rows, detector-context rows, broad window medians, or any `extraction_status` containing `proxy` are not phrase extraction. If a run produces those rows, name the file `raw_phrase_proxy` or similar diagnostic evidence, keep `raw_phrase_extraction` as `NOT RUN - direct phrase extraction required`, and make direct extraction or source-limit split the immediate work item before another render.

Recommended transition schema:

```text
candidate_id | candidate_hash | transition_id | boundary_type | transition_basis | raw_phrase_evidence_path | raw_phrase_body_db | raw_pre_body_db | raw_post_body_db | repaired_first_phrase_body_db | repaired_early_post_body_db | target_reference_db | seconds_to_recovery | phrase_start_tail_class | bed_body_during_recovery_db | gap_during_recovery_db | loudness_artifact_class | status | failure_class | action
```

Recommended raw phrase extraction schema:

```text
candidate_id | source_hash_or_fingerprint | row_id | gate | boundary_type | search_window | raw_phrase_start | raw_phrase_end | raw_active_speech_seconds | raw_mic_body_db | raw_bed_body_db | detector_basis | extraction_status | source_limit_class | action
```

## Worst-Window Packet

For listener-risk review, collect:

```text
raw_window | candidate_window | source_lanes_used | reason_selected | active_speech_seconds | active_speech_basis | expected_failure_mode | reviewer_result
```

Include raw mic/background evidence beside candidate evidence. Do not review the rendered candidate alone when the question is whether recoverable mic was buried, skipped, or distorted.

Also include control-stress windows when automation is used:

- deepest local bed cut;
- longest sustained restraint;
- highest local-restraint duty-cycle region;
- ordinary-speech baseline regions before local restraint;
- bed surge or phrase-gap return regions;
- highest mic-gain or limiter/compressor-stress regions.

These windows are source-agnostic. They come from the control surface and source evidence, not from known timestamps in one recording.
