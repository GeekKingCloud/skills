# Iteration Loop

Use this helper when validation or review blocks a candidate.

This phase owns the next action. A failed gate is work, not a caveat.

## Goal Ladder

Keep these fields visible:

```text
run_goal | accepted_reference_section | provisional_reference_anchor | current_blocker_goal | next_candidate_goal | clearing_evidence
```

- `run_goal`: the caller-facing outcome, such as caller-test-ready mux or retained scratch candidate.
- `accepted_reference_section`: explicit target section, or `NONE`.
- `provisional_reference_anchor`: required when no accepted section exists after measurable candidates.
- `current_blocker_goal`: the exact listener-risk, proof, source-limit, verifier, or lineage blocker preventing promotion.
- `next_candidate_goal`: one material change that should clear that blocker without regressing already-cleared areas.
- `clearing_evidence`: the exact checks, reviewer packet, or windows that must pass after the next render.

Do not render another candidate until a reviewer can tell whether `next_candidate_goal` worked.

When the loop gets long, the next goal should become narrower and simpler, not broader. Prefer "repair chunk X or boundary Y without regressing these protected chunks" over another whole-file strategy.

When blockers are counted by row, first collapse them into a small set of controlling failure groups. Hundreds of row-level failures from the same cause are not hundreds of separate work items.

## Work Queue

For each blocking group, record:

```text
failure_class | evidence_source | candidates_affected | accepted_reference_section | provisional_reference_anchor | current_cause_hypothesis | current_blocker_goal | target_delta_from_reference | next_candidate_goal | strategy_pivot_attempted | regression_windows | clearing_evidence | result | disposition
```

Evidence, proof, verifier, and lineage failures are work items too. A source-limited proof pass, active-speech-second verifier revision, reviewer-requested evidence packet, blind-spot measurement correction, render-script hash repair, metrics-hash repair, non-empty required evidence table, or manifest rerender counts as unattempted work until completed, proven irrelevant, impossible now, source-limited, or caller-budget-blocked.

Raw phrase extraction is verifier work, not an optional future strategy. If a failed gate says exact raw evidence requires phrase-local extraction, implement or run that extraction before rendering more candidates, classifying source limits, or reporting a source-limit-suspect queue. A proxy or fixed-frame measurement does not satisfy this work item and cannot be used to justify another candidate render before direct phrase extraction or a source-limit split.

A required verifier that is `not_run` because it is not implemented is the next work item before another promotion claim. Do not render more audio to escape a missing verifier unless the next render is explicitly needed to produce that verifier's inputs.

Chunk-map validity failures are audio-repair work, not paperwork. If a retained candidate used coarse fixed-width chunks that crossed transitions or mixed incompatible regimes, the next candidate goal is to split the invalid chunk and rerender from that corrected map before trying another broad gain, compressor, sidechain, or bed-floor tweak.

If a retained candidate used per-second or detector-flicker micro-chunks, the next candidate goal is to merge those rows into sustained phrase/regime chunks, move dense control into an automation table if needed, and rerender from the simplified map.

If a retained candidate uses dense automation as the main repair surface, the next candidate goal is not another bounded variant of that same surface. Rebuild the staged chunk baseline, collapse failures into a compact exception queue, and reapply automation only to those exceptions.

Lineage repair is not audio repair. If a candidate only rerenders or rebinds a stale best strategy and produces the same audio hash or failure pattern, count it as `proof-lineage-repaired`, not as an attempt at the next audio mechanism.

Render-path failure is not audio source limitation. If a scratch renderer stalls, runs away, writes no output, or leaves only a candidate directory, mark that attempt `partial-invalid`, inspect and stop orphaned render processes, patch the render path, run a slice smoke test, and then rerender. Do not count the stalled candidate as a strategy attempt against the audio problem.

For broad failure counts, add a controlling-group summary before rendering again:

```text
group_id | failure_classes | row_count | representative_windows | common_cause | source_or_candidate_basis | next_mechanism | slice_test_before_full_render | clearing_evidence
```

If the next mechanism is local reconstruction, overlay, bed-floor repair, or transition first-phrase support, test it on representative slices before another full-length render unless the implementation can only be evaluated full-file. Full-length renders are expensive and should follow a passing slice proof for the controlling groups.

When the next mechanism is local reconstruction, overlay, intelligibility-first fallback, phrase-local support, or detector-basis replacement, the work queue must reference `LOCAL-RECONSTRUCTION.md` and include its local reconstruction plan table. A report that only says this mechanism is needed is invalid; attempt the minimum slice contract or name the external blocker.

## Applicable Strategy Classes

Normal hard-source runs should not stop after a small number of similar candidates, but this is not a mandate to try every mechanism. Use source evidence and failed gates to identify the applicable classes:

- `commentary-regime-repair`;
- `speaking-level-alignment`;
- `section-level-realignment`;
- `phrase-window-or-transition-automation`;
- `background-placement-or-event-restraint`;
- `speech-envelope-stability-repair`;
- `intelligibility-first-fallback`.

For each applicable class, list one of:

- `attempted`, with candidate id and evidence path;
- `irrelevant`, with source evidence proving why it cannot address any remaining blocker;
- `impossible-now`, with the exact missing tool, permission, or caller constraint;
- `source-limited`, with raw evidence for the controlling regions.

Small gain, threshold, ceiling, attack/release, final loudness, limiter, or timing tweaks do not count as a new strategy class unless the report proves they targeted a named blocker and changed that blocker.

Do not mark a class `impossible-now` because it needs custom code. Source-agnostic scratch helpers for phrase regions, hysteresis, local envelopes, overlays, or verifier-specific evidence are normal work.

For each attempted class, also record:

```text
strategy_class | candidate_id | control_surface | material_change_from_parent | slice_or_probe_evidence | full_render_status | cleared_groups | regressed_groups | next_disposition
```

`control_surface` must name the actual mechanism, such as `chunk-gain-trim`, `phrase-region-support`, `transition-first-phrase-support`, `local-bed-event-restraint`, `detector-basis-replacement`, or `source-limit-proof`. A candidate that only changes thresholds, ceilings, global loudness, or sidechain bounds on the same surface is a tweak, not a new strategy attempt.

For classes not implicated by source evidence, failed gates, reviewer findings, or caller feedback, record them as `not-applicable-to-current-blocker` in the report summary rather than spending candidates on them.

## Finish-Line Mode

Enter finish-line mode when five or fewer listener-risk blockers remain, or one failure class remains after multiple candidates.

In finish-line mode:

- freeze the current best candidate as the baseline;
- use the accepted or provisional target from `REFERENCE-TARGET.md`;
- list each remaining blocker with raw evidence, candidate evidence, failure class, and why the current strategy did not clear it;
- preserve all already-cleared windows as regression checks;
- target the blocker class directly instead of changing the whole mix;
- rerun only after naming the new mechanism that should clear the blocker.

Use this table:

```text
blocker_id | failure_class | accepted_reference_section | provisional_reference_anchor | raw_evidence | candidate_evidence | target_delta_from_reference | why_current_strategy_failed | next_mechanism | regression_windows | clearing_evidence
```

If a targeted finish-line candidate regresses, produce a regression postmortem before stopping:

```text
baseline_candidate | regressed_candidate | intended_windows | improved_windows | worsened_windows | new_failures | lost_passes | likely_regression_cause | next_mechanism
```

Then return to the frozen baseline and use a narrower overlay, a different detector basis, a different control surface, or source-limit proof for windows that are truly unrecoverable.

## Dead-End Escapes

If the same failure class survives two candidates, switch mechanism.

- full-file automation causes section drift, pumping, or slow recovery -> return to chunk assembly with per-regime gain/trim and protected stitch windows;
- whole-runtime dense automation passes metrics but fails review -> rebuild the stage1 chunk baseline and stage2 exception queue before any stage3 automation;
- chunk assembly uses fixed bins that hide a transition -> rebuild chunk boundaries from raw source regime evidence and rerender;
- chunk assembly creates per-second micro-chunks -> merge into phrase/regime chunks and move dense control into an automation table;
- second-level gain hold fails phrase starts/tails -> phrase-region speech-envelope repair;
- per-second detector flickers -> phrase grouping with hysteresis and short-gap bridging;
- global gain or loudness causes section mismatch -> section-level realignment;
- late recovered mic stays too forward -> late-recovery realignment;
- bed is crushed after speech improves -> phrase-bed-floor or event-level bed restraint;
- local background masks speech -> local event restraint or mic-follow before global bed reduction;
- weak speech remains buried from whole-window medians -> active-speech-second checks inside the window;
- source-limit proof has mixed classes -> target `repair-not-source-limited` rows separately;
- source-limit or transition rows say raw phrase extraction is still required -> run raw phrase extraction and reclassify before another render;
- many repairable rows remain after source-limit split -> detector-basis replacement plus baseline-local overlay, or another materially different reconstruction mechanism;
- best numeric candidate becomes stale -> rerender or rebind that material strategy before moving to weaker candidates;
- best numeric candidate is a diagnostic composite or mixed-baseline overlay -> treat it as a reference experiment, extract the successful control behavior, and rerender from direct source lanes before more tuning;
- proof-grade source-lane reimplementation of a diagnostic composite regresses -> compare the composite and source-lane version to identify the exact lost support, overgain, bed, or envelope behavior before broad redesign;
- caller-test fails after promotion -> reopen failed gates and make the next candidate regression-protected.

## Mechanism Reset

Use this when applicable strategy classes are accounted for but aggregate gates still fail.

Do not treat "all applicable classes attempted" as terminal by itself. First run a mechanism reset:

1. Group remaining blockers by dominant failure model, not only by row count.
2. Identify which control surface caused the failure, such as per-frame gain, per-phrase gain, bed floor, sidechain envelope, event restraint, detector basis, or local overlay.
3. Choose a materially different control surface for the next candidate.
4. Preserve the best current-lineage candidate as the baseline and regression target.
5. Render or attempt one reset candidate, then rerun only the gates that prove the reset and its regressions.

Common reset mappings:

- many speech-envelope and bed-envelope failures remain -> redesign the envelope control surface; do not keep tuning thresholds on the same envelope;
- bed collapse and bed waviness coexist -> separate bed floor preservation from speech-triggered bed restraint;
- transition failures survive phrase automation -> rebuild transition regions from raw mic phrase boundaries and render transition-local support;
- repairable source-limit rows remain -> target those rows with a local reconstruction or overlay from the frozen baseline;
- reviewer says a new mechanism is required -> convert the reviewer finding into a mechanism-reset work item, not a stop reason.
- reviewer says control-surface proof or listener-risk proof failed for an automated candidate -> run a strategy-shape reset, not only tighter bounds on the same automation.

If no materially different mechanism can be identified, state what source, tool, runtime, permission, or caller constraint prevents it. "No mux-eligible state", "proof packet preserved", "reviewer rejected", or "new mechanism required" are not constraints.

## Stop-State Validity

Only stop early when:

- raw source proves speech is absent or unrecoverable;
- required tools or permissions are unavailable;
- the caller set a time/budget stop rule;
- practical budget is exhausted and the report lists elapsed time, the actual budget or runtime limit, candidate ids, attempted pivots, unattempted required pivots, and why each unattempted pivot is infeasible now.

Do not spend the remaining run on more full renders when a verifier/source-limit work item is already known to be the controlling blocker. If direct raw phrase extraction or source-limit split is named as the exact unblocker and the source lanes, stems, and scripts are available, that proof must be attempted before another candidate render or before reporting `iteration-incomplete`.

If practical budget is exhausted because of a stalled or runaway renderer, the report must include process inspection, orphan cleanup status, the invalid partial-candidate path if one exists, and the slice-safe render fix or external reason that prevented rerendering. A candidate folder without completed audio, manifest, and lineage proof cannot be the strongest retained candidate.

If any applicable strategy class is unattempted and not proven irrelevant, impossible-now, source-limited, or caller-budget-blocked, the run is not terminal `blocked`. Continue the loop unless an external stop reason forces an `iteration-incomplete` handoff.

If the report names a next candidate strategy, exact unblocker, verifier revision, source-limit pass, local reconstruction pass, reviewer evidence pass, proof-lineage fix, manifest repair, or rerender, either do it or record the concrete external reason it cannot be done now. Naming the next strategy is not itself a valid stop reason.

Valid `iteration-incomplete` reports require both:

- at least one named next action; and
- an external stop reason such as caller stop rule, time/budget limit, missing tool, denied permission, missing source artifact, runtime failure after a real attempt, or context handoff.

`context handoff` is valid only when the report identifies the actual context, system, or runtime constraint that forced handoff before the next proof/action could run. "After N candidates", "after a proof packet was created", or "the next mechanism is beyond this packet" is not a context handoff.

The named next action must be immediately actionable from the retained packet. If it says "render candidate8", the report must also say why candidate8 was not rendered now using a valid external stop reason. If the only reason is that candidate8 is the next strategy, continue.

Candidate count is not an external stop reason. "Practical run boundary" is invalid unless it names the actual caller, system, tool, context, or runtime limit that forced the handoff. Independent reviewer rejection is also not an external stop reason; reviewer rejection is gate feedback that becomes the next work queue. Preserving a blocked proof packet, avoiding an invalid mux, or lacking caller-test eligibility is correct delivery behavior, not a stop reason.

Invalid `iteration-incomplete` reports include:

- "why next candidate was not rendered" says only that the next mechanism is needed;
- the external stop reason is only "after N candidates", "after several renders", "reviewer rejected promotion", "current run boundary", or similar;
- the external stop reason is only "preserve proof packet", "avoid invalid mux", "no mux-eligible state", "reviewer confirmed a new mechanism is needed", or similar;
- a regressed candidate proves a different strategy is needed, but that strategy is not attempted;
- source-limit split is named as the next pivot but not run;
- raw phrase extraction is named as the next pivot but not run;
- fallback, overlay, verifier repair, or rerender is named as next work but left to the caller without an external blocker.
- all applicable strategy classes are marked attempted but failed gates remain and no mechanism reset was attempted.
- a candidate with dense automation is treated as the best retained promotion candidate without a passing staged-repair summary.
- `blocked-terminal` is claimed while any retained-candidate row remains `repair-not-source-limited`, `source-limit-suspect` due only to detector exclusion, or missing candidate-specific independent review.
- a report lists hundreds of row-level blockers but does not collapse them into controlling failure groups with representative windows and one next mechanism per group.
- a required gate is `not_run` because the verifier is "not implemented" and the report does not make verifier implementation the immediate next action or name a valid external blocker.

When source-limit proof or raw phrase extraction is the named next action, run that proof in the same loop before stopping unless a valid external stop reason exists. If the proof finds any `repair-not-source-limited` rows, immediately convert those rows into the next repair queue and render or attempt the named local reconstruction/overlay mechanism unless a valid external stop reason exists.

When invalid, continue the loop before reporting.

`blocked-terminal` requires no named next action remains. Do not write "run completed as blocked" when `iteration-incomplete` is true.
