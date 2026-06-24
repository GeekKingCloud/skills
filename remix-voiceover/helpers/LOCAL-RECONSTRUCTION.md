# Local Reconstruction

Use this helper only after a staged chunk baseline exists and failed gates still show repairable weak, buried, transition, phrase-start/tail, masking, or envelope rows. This is the fallback for cases where another global gain, ducking, limiter, detector-threshold, or whole-file automation pass would repeat the same failure.

This helper is guidance, not a packaged recipe. The coding agent may choose tools and implementation, but the attempt must be concrete enough that a reviewer can tell whether the mechanism was actually tried.

The parent baseline is a regression reference and control-plan reference, not permission to use a previous mixed candidate as the audio substrate. Promotion-grade local reconstruction still renders from the proven mic/commentary and background source lanes unless exact separated-lane reconstruction proof exists.

## Trigger

Read and apply this helper when the next work item names any of:

- `local reconstruction`;
- `overlay`;
- `intelligibility-first-fallback`;
- `phrase-local support`;
- `detector-basis replacement`;
- `baseline-local overlay`;
- local support for transition first phrases, phrase starts, phrase tails, or weak buried commentary.

Do not use this as the first strategy. First prove the chunk baseline and exception queue from `CHUNK-ASSEMBLY.md`.

## Minimum Attempt Contract

Before another full render, build a local reconstruction plan:

```text
group_id | failure_classes | representative_windows | raw_phrase_evidence | baseline_candidate | intended_support | protected_chunks | regression_windows | slice_test_path | clearing_evidence
```

For each controlling group:

1. Re-read the raw mic and bed evidence for the representative windows.
2. Locate raw phrase spans directly when the failure involves weak, buried, detector-uncertain, transition, phrase-start, or phrase-tail speech.
3. Decide whether the source contains recoverable speech. If not, run source-limit proof instead of rendering.
4. Add stable local speech support over the whole phrase or boundary region, not per-frame gain following detector flicker.
5. Keep the bed baseline from the chunk plan unless masking evidence proves a local event restraint is needed.
6. Protect already-cleared chunks and windows from broad level shifts.
7. Run a 30-60 second slice proof covering at least one representative failure and one protected regression window.
8. Full-render only after the slice proof shows the mechanism improves the target class without obvious overgain, waviness, bed collapse, or masking regression.

A slice that only changes final loudness, sidechain settings, threshold values, or global bed level is not a local reconstruction attempt.

## Acceptable Mechanisms

Choose the simplest mechanism that fits the evidence:

- phrase-region mic support: stable gain/trim for whole phrase regions, with short ramps;
- transition-local first-phrase support: align the next coherent recoverable phrase after a capture-level change;
- baseline-local overlay: reproduce the baseline chunk plan from source lanes, then add source-lane mic support only over failed phrases;
- detector-basis replacement: rebuild phrase regions from raw mic energy and source evidence when the prior detector skipped recoverable speech;
- local event restraint: restrain a bed event only where it masks otherwise repaired speech;
- source-limit split: prove raw speech is absent, clipped beyond repair, or indistinguishable from noise before giving up on a local row.

Do not make the background vanish to pass an intelligibility row. Do not push the mic above the comfortable ceiling to fight a hot bed. If local speech support would exceed the ceiling, trim the local bed event first; if that still fails, classify the source limit with raw evidence.

## Strategy Accounting

Record this table for every candidate that claims this mechanism:

```text
candidate_id | parent_baseline | strategy_class | control_surface | targeted_groups | material_change_from_parent | slice_pass | full_render_status | protected_regression_status | evidence_path | result
```

`material_change_from_parent` must identify what changed in the control surface, not just that candidate numbers changed. Examples:

- `phrase-region stable support replaced detector-flicker gain`;
- `first coherent post-transition phrase aligned locally`;
- `local bed event restraint replaced high-bed-baseline ducking`;
- `raw phrase extraction proved source-limited row`.

If `slice_pass=not_run`, the row must name an external tool, permission, runtime, source, caller-budget, or context constraint. "Needs a different mechanism" is not a valid reason.

## Evidence

Retained packets using this helper must include:

- the local reconstruction plan;
- raw phrase extraction or source-limit proof for targeted rows;
- slice render path, manifest, and measurements;
- full candidate manifest when promoted beyond slice proof;
- control-surface audit if any automation, overlay, generated filter, or local restraint is used;
- before/after checks for targeted windows;
- protected regression checks for already-cleared chunks;
- reviewer packet explaining why this was a different mechanism from the failed baseline.

If the local reconstruction candidate regresses, keep the prior baseline as the retained baseline and write a regression postmortem before choosing the next mechanism.
