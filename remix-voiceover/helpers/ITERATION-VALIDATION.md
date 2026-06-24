# Iteration And Validation

Use this helper after each candidate render.

## Candidate Proof

Every retained candidate needs a manifest and evidence packet:

- candidate id and path;
- source path and source hash/fingerprint;
- stream map and role map;
- selected and excluded streams;
- render source mode and every audio substrate used to render the candidate;
- render command or render script path/hash;
- candidate hash, codec, duration, and headroom;
- immutable render script or command content hash captured before review;
- processed metrics file paths and hashes;
- proof input data and proof outputs;
- blind-spot audit path;
- exception summary;
- reviewer status and independence;
- beside-source mux path/hash only when promoted;
- cleanup status and retained artifacts.

Every proof table should reference the candidate id or hash.

If checks are split across broad balance, mic alignment, envelope, transition, overducking, reviewer, and proof-lineage files, create or update an aggregate promotion proof for the candidate after all current gates run. The aggregate proof must list each gate as `pass`, `fail`, `not_run`, or `not_applicable`, include each gate evidence path/hash, and derive the candidate's current confidence label from the worst unresolved gate.

When a control-surface audit is required, aggregate promotion proof must include its path/hash and dependency map showing that balance, overducking, bed-envelope, listener-risk review, and report claims consumed the same audit. If any dependent gate uses a different basis, omits the audit, or contradicts it, aggregate promotion fails with `control-surface-verifier-gap`.

When a staged-repair summary is required, aggregate promotion proof must include its path/hash and strategy status. Automation-heavy candidates cannot be promoted unless the summary proves a passing parent chunk baseline, a compact exception queue, and bounded automation scope.

Do not let a single broad verifier or candidate manifest set the final candidate confidence to `producer-checked-candidate`, `independently-verified-ready-for-listener-test`, or any mux-eligible state while another required gate is failed, not run, stale, or missing. A broad-balance manifest with zero findings means only "broad balance passed"; it is not promotion proof by itself.

Do not let a required gate pass by proxy. `transition_checks`, `speech_envelope_stability_checks`, `overducking_checks`, and `mic_alignment_checks` must contain gate-specific rows and measurements. If a gate file only contains an aggregate row, says another check passed, or uses placeholder/proxy wording, the aggregate promotion proof must mark that gate `fail` with `failure_class=verifier-insufficient`. A proxy pass cannot support `independently-verified-ready-for-listener-test`.

If a manifest, report, or reviewer packet contains a narrower confidence label than the aggregate proof supports, repair the proof/report before asking for promotion review or before stopping. Conflicting confidence labels are a proof-lineage gap and become producer-side work.

If any proof object was edited after render, regenerate the candidate manifest and rerun the affected verifiers. If the edited object changes render behavior, rerender the candidate. Do not ask reviewers to clear a candidate whose proof packet is not immutable.

## Failure Taxonomy

Use these failure classes in reviewer findings and repair ledgers:

- `wrong-source-or-route`;
- `weak-commentary-buried`;
- `detector-exclusion`;
- `phrase-boundary-loss`;
- `transition-recovery-failure`;
- `speaking-level-misalignment`;
- `section-overgain`;
- `speech-envelope-waviness`;
- `background-masking`;
- `background-collapse`;
- `bed-envelope-waviness`;
- `high-bed-baseline`;
- `aggressive-ducking-primary`;
- `dense-automation-primary`;
- `strategy-order-violation`;
- `automation-scope-creep`;
- `control-surface-verifier-gap`;
- `hot-or-harsh-speech`;
- `constant-ratio-flattening`;
- `source-limited-unproven`;
- `raw-phrase-extraction-missing`;
- `boundary-taxonomy-error`;
- `mixed-baseline-proof-gap`;
- `verifier-insufficient`;
- `proof-lineage-gap`;
- `reviewer-blocked`;
- `iteration-stagnation`.

## Disproof Checks

Reject, downgrade, or repair a candidate when any are true:

- weak commentary was marked inactive and skipped;
- recoverable commentary regimes are not aligned to a consistent normal speaking body level before bed ducking;
- weak regimes were repaired but already-loud or recovered regimes were not trimmed into alignment;
- caller or reviewer explicitly identified a target reference section, but the run leaves `accepted_reference_section=NONE` or chooses a louder raw capture regime as the target;
- any section becomes too loud, harsh, clipped, limited, saturated, or muffled from overpowering gain;
- the mic cuts in and out, pumps, or wobbles from overreactive normalization, gating, expansion, detector flicker, or sidechain behavior;
- selected windows look good while whole regimes still sound wrong;
- local hard-window snippets pass while a sustained weak/problem, healthy, recovered, hot, or late regime remains unmeasured or misaligned;
- background is audible only when nobody talks;
- background competes with speech then vanishes under speech;
- background is kept near full volume and then repeatedly carved down around speech;
- a candidate relies on frequent or deep bed cuts as the primary separation mechanism instead of stable bed placement under repaired speech;
- a candidate uses dense automation, generated per-window filters, sidechain curves, phrase controls, or local restraint as the primary repair surface before a staged chunk baseline exists;
- an automated candidate controls most of the recording without a compact exception queue and protected chunk regression set;
- a follow-up "bounds" the same dense automation surface after reviewer rejection instead of returning to chunk baseline plus exception repair;
- background disappears under ordinary commentary;
- background level audibly wobbles with mic dips, detector flicker, breaths, or phrase gaps;
- background surges between phrases;
- overducking, balance, or bed-envelope proof claims no bed movement while the render automation, filter graph, or script contains per-window bed controls;
- control-surface audit is missing even though the candidate uses automation, sidechain curves, phrase controls, local bed restraint, or generated filters;
- mic gain, compression, or limiting is used to fight a hot bed baseline instead of trimming the bed into a stable under-speech position;
- mic starts or tails are swallowed;
- transition recovery is slow or waits for long normalization convergence instead of the next coherent phrase;
- transition recovery evidence is a broad average, aggregate row, or proxy from another verifier instead of direct first-phrase/early-post-transition measurements;
- transition evidence contains `NOT RECOVERED` rows that are marked `not_applicable` without scanning to the next coherent phrase or proving source limit;
- ordinary chunk seams are counted as transition-recovery failures without source evidence of a capture-level transition, recovery, hot shift, or caller-example transition;
- transition or source-limit evidence says raw phrase extraction is required but promotion proof treats the row as source-limit-suspect, source-limited, or a caller-facing residual risk;
- healthy/recovered speech becomes hot, harsh, clipped, or recessed to compensate for weak sections;
- the candidate uses an over-hot section as the speech reference instead of choosing a comfortable reference and trimming it;
- the mix reaches a target gap by flattening mic and bed into a near-constant ratio;
- proof contains unresolved values, previous-candidate data, or missing scalar evidence;
- the candidate is rendered from a previous mixed candidate, existing mix, or muxed output as an audio substrate while separate source lanes exist and no exact separated reconstruction proof exists;
- render script hash, metrics hash, candidate hash, or manifest identity does not match the retained candidate;
- broad-balance, envelope, transition, reviewer, or final report confidence labels disagree about the same retained candidate;
- no aggregate promotion proof exists after multiple required gate files were produced;
- required evidence tables are empty without `NOT RUN - reason`;
- mic-alignment or section-overgain gates lack sustained-regime coverage and rely only on selected hard-window rows;
- section-overgain rows require peak/crest/limiter extraction but leave those fields `NOT RUN` while aggregate proof treats the gate as passing;
- required gate files contain only placeholder/proxy pass rows while promotion proof treats them as passed;
- `raw_phrase_extraction` contains fixed-frame, broad-window, detector-context, or `proxy` rows instead of direct phrase spans;
- `not_applicable` or raw-shaped classifications are used to silence caller-reported loudness, slow recovery, mic waviness, bed collapse, or masking;
- verifier logic counts silence or inactive portions of a blind spot as failed speech instead of measuring active speech seconds inside that blind spot;
- source-limited claims remain unproven for controlling windows;
- raw phrase extraction is missing for controlling transition, weak, buried, detector-uncertain, or source-limit rows;
- unresolved `ambiguous listener-risk` windows are moved into caller-test notes instead of becoming work.

## Promotion Validation

Use `helpers/ITERATION-LOOP.md` for failed-gate work queues, strategy-class accounting, finish-line mode, and stop-state validity.

This helper owns promotion proof. Before any candidate is promoted beyond scratch:

- every required gate is represented in aggregate promotion proof;
- raw phrase extraction is present and passing when controlling rows require phrase-local evidence;
- `control_surface_audit` is present and passing when automation, sidechain curves, generated filters, local bed restraint, or overlay control are used;
- aggregate proof maps control-surface-dependent gates to the same audit hash when the audit is required;
- `staged_repair_summary` is present and passing when automation, sidechain curves, generated filters, local bed restraint, phrase controls, or overlay control are used;
- every gate is `pass`, `fail`, `not_run`, or `not_applicable` with evidence path/hash;
- `not_run` has an explicit unavailable-tool, permission, output-mode, or caller-stop reason;
- `not_applicable` has source evidence or output-mode evidence, not convenience wording;
- confidence labels agree across manifest, aggregate proof, reviewer packet, and report;
- proof and candidate identity refer to the same retained file hash.

Independent review must inspect the control-surface audit when it exists. A reviewer cannot clear caller-test readiness by trusting balance rows alone if the render used local bed or mic controls.

Independent review must inspect the staged-repair summary when automation exists. A reviewer cannot clear caller-test readiness if the candidate skipped the chunk-baseline stage, has no exception queue, or treats whole-runtime control as the repair.

For audible failure classes such as aggressive ducking, pumping, hot bed, bed surge, mic waviness, or transition recovery, listener-risk clearance must review representative rendered worst-window audio evidence or explicitly classify the unreviewed audio as unresolved listener risk. This is not final human acceptance; it is the minimum evidence review needed before asking the caller to test a mux.

For a retained scratch candidate that is being used as a handoff baseline, `not_run` required gates still need hard treatment. A missing verifier may block promotion, but it cannot disappear into the notes: implement it, run it, or make verifier implementation the immediate next action with a valid external stop reason.

After caller listening fails a caller-test mux, reopen the matching gates before another render. Convert each caller complaint into a gate work item, identify which gate incorrectly passed or waived it, and require the next candidate to clear those reopened gates while preserving any section the caller said was acceptable.

## Reviewer Packets

Use read-only reviewer packets when sub-agents are available.

- **Source reviewer:** challenges track roles and neutral source coverage.
- **Blind-spot reviewer:** checks excluded and detector-uncertain regions before reading candidate pass claims.
- **Listener-risk reviewer:** checks worst windows for masking, pumping, missing starts/tails, crushed background, and transitions.
- **Control-surface reviewer:** when automation exists, checks bed baseline, local-restraint duty cycle, deepest cuts, highest mic gain, smoothing/hold behavior, and whether dependent proof files consumed the same audit.
- **Strategy-shape reviewer:** when automation exists, checks that the candidate followed staged chunk baseline -> exception queue -> bounded automation, and that the automation scope did not become the main mix strategy.
- **Proof reviewer:** checks hashes, stream lineage, exact candidate identity, mux structure, and cleanup.

Reviewer packets should include raw source evidence and blind spots before candidate success summaries. A reviewer who only validates hashes and mux structure cannot clear listener risk.

Listener-risk review has two modes:

- `promotion-clearance`: used only after local gates are clean enough for caller-test consideration.
- `blocker-review`: used on a blocked candidate to challenge the failed-gate queue, representative windows, and next mechanism.

If subagents/reviewers are available and the run is stopping with a retained scratch candidate, do not skip listener-risk review merely because local gates still fail. Run blocker-review unless a valid external stop reason prevents it.

`caller-test-mux` requires independent read-only evidence clearance for:

- source/track role map;
- blind-spot set;
- listener-risk worst-window evidence;
- control-stress windows and control-surface audit when automation is used;
- staged-repair summary and strategy-shape review when automation is used;
- proof/mux lineage when muxing.

Any pending or unavailable required reviewer keeps the artifact at `scratch-candidate` unless explicit preview approval is granted.

Proof review must explicitly classify source-lane lineage. A candidate with `render_source_mode=diagnostic-composite` can be useful scratch evidence, but it cannot be cleared for caller-test mux. Its next work item is to reimplement the successful mechanism from the proven source lanes, or to prove why exact separated reconstruction is impossible.

Candidate review is candidate-specific. A reviewer block or clearance for candidate4 cannot clear, terminally block, or substitute for review of candidate8 unless the report proves the relevant audio hash, render plan, and worst-window evidence are identical for the reviewed surfaces. Otherwise the retained candidate needs its own read-only evidence review or the run remains iteration work.

This evidence clearance is not the same as human listener acceptance. Human acceptance is required only for `listener-accepted` and `final-deliverable`. If all applicable strategy classes are accounted for, local metrics pass, independent evidence review finds no evidence blockers or unresolved listener-risk work items, and the only missing item is human listening, use `independently-verified-ready-for-listener-test`, not `blocked`.

Ask reviewers to return work items, not only verdicts:

```text
failure_class | evidence_source | raw_classification | likely_candidate_cause | minimum_next_strategy_pivot | clearing_evidence
```

## Confidence Labels

Use only:

- `listener-accepted`;
- `independently-verified-ready-for-listener-test`;
- `producer-checked-candidate`;
- `preview-with-known-risks`;
- `blocked/source-limited`;
- `blocked`.

Without human listening or independent read-only evidence verification, the best normal label is `producer-checked-candidate`, and that label does not allow beside-source mux by default.

`listener-accepted` requires listener identity or role, exact windows listened, sample/full-output path, acceptance wording and timestamp, and a statement that producer local checks did not substitute for human acceptance.
