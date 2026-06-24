---
name: remix-voiceover
description: Repair commentary-over-background audio or video with separate mic/commentary and background/system tracks into a listener-first REMIX-VOICEOVER output, using fresh source evidence, track-role discovery, regime mapping, iterative mix repair, adversarial review, copied video, preserved original audio, and honest delivery gates.
---

# Remix Voiceover

Skill version: `2026-06-23.04`

When updating this skill, increment the skill version. When using this skill, record the exact skill version, skill source path, and instruction bundle hash when practical in the scratch run metadata and final report so the caller can verify which installed instructions were used.

Use this when a recording has separate commentary/mic and background/system audio and needs a repaired voiceover-style mix.

The goal is a file a viewer can watch without losing the commentary, losing the background, hearing obvious pumping, or wondering whether the audio broke. The goal is not to satisfy a verifier.

## Operating Mode

This is a guidance-first skill with hard evidence and delivery contracts.

- Let the coding agent choose tools, filters, libraries, and scratch scripts.
- Prefer the simplest edit that matches the source evidence. For multi-regime commentary, that usually means chunk-level mic lift/trim, transparent stitching, stable bed placement, and narrow local event restraint.
- Use deterministic scripts for measurement, manifests, comparisons, and repeatable evidence when helpful.
- When a named repair needs phrase grouping, hysteresis, local envelopes, or overlay automation that is awkward in a single media filter graph, write scratch code to build that control data and render from it. "Beyond the current filter pivot" is not a stop condition.
- Dense automation is an exception tool, not the main repair model. A promotion-grade run must first render and evaluate a staged editorial chunk baseline before using phrase, window, sidechain, local-restraint, or overlay automation as a candidate's primary control surface.
- New scratch render code must pass the render-safety rules in `helpers/EVIDENCE-SCRIPT-CONTRACTS.md` before any full-length render.
- Do not use a packaged deterministic mix recipe as the default solution.
- Do not hardcode source-specific timestamps, settings, or known failures into the reusable skill.
- Treat caller-provided timestamps as examples of failure classes that must be detected across the whole source.
- Treat caller-supplied media paths as literal paths. Resolve and quote paths safely, avoid shell-string concatenation for commands, never overwrite the source file, and write beside-source outputs only through the delivery contract.

If a run is growing into many similar candidates, stop adding verifier complexity and return to the simple production question: which commentary chunk is still below, above, unstable, masked, or over-gained relative to the shared ordinary-speaking target? If the run has thousands of control regions, whole-duration automation, or repeated "bounded control" regressions, stop tuning that surface and rebuild the staged chunk plan.

Before rendering, read the helper files needed for the current phase:

- `helpers/RUN-SETUP.md` for startup, output modes, sub-agent use, and source/final contracts.
- `helpers/TRACK-DISCOVERY.md` for finding commentary, background, and existing-mix streams.
- `helpers/REGIME-MAPPING.md` for mapping mic capture regimes, transitions, blind spots, and source limits.
- `helpers/REFERENCE-TARGET.md` for accepted reference and provisional comfortable target selection.
- `helpers/CHUNK-ASSEMBLY.md` for the chunk-first production recipe: split, repair each regime, stitch, and verify.
- `helpers/SECTION-REALIGNMENT.md` for aligning normal speaking levels across weak, healthy, recovered, hot, and late regimes.
- `helpers/TRANSITION-RECOVERY.md` for fast phrase-aware recovery at capture-level changes.
- `helpers/BACKGROUND-BALANCE.md` for bed placement, event restraint, overducking checks, and mic/bed gap behavior.
- `helpers/ENVELOPE-STABILITY.md` for mic continuity, phrase-region repair, and bed-envelope stability.
- `helpers/LOCAL-RECONSTRUCTION.md` when failed gates name local overlay, intelligibility-first fallback, phrase-local support, or another materially different reconstruction mechanism.
- `helpers/ITERATION-LOOP.md` for failed-gate work queues, strategy-class accounting, finish-line mode, and dead-end escape rules.
- `helpers/ITERATION-VALIDATION.md` for candidate proof, reviewers, aggregate promotion proof, and confidence labels.
- `helpers/EVIDENCE-SCRIPT-CONTRACTS.md` for optional source-agnostic helper script inputs/outputs.
- `helpers/DELIVERY-CONTRACT.md` for beside-source mux permissions, preview handling, manifests, cleanup, and report evidence.
- `templates/REMIX-VOICEOVER.md` when writing the final report.

## Artifact Modes

Separate output shape from artifact mode.

Output shapes:

- `audio-only`;
- `muxed-video`;
- `verification-only`;
- `skill-validation`.

Artifact modes:

- `scratch-candidate`: audio candidate retained in scratch only. Producer-only or blocked results stay here.
- `preview-mux`: beside-source mux with known risks, allowed only after explicit preview approval.
- `caller-test-mux`: audio-only or muxed-video artifact cleared by independent read-only evidence review for caller listening, but not human listener accepted.
- `final-deliverable`: listener-accepted output.

Do not call `scratch-candidate`, `preview-mux`, or `caller-test-mux` final.

Separate artifact mode from run status:

- `iteration-incomplete`: a temporary handoff state when the loop still has a named repair, verifier, proof, source-limit, or reviewer-evidence action and an external stop reason prevents continuing in the current run.
- `blocked-terminal`: no safe useful output is possible with current tools/evidence/budget, and no named next action remains.
- `caller-test-ready`: a caller-test mux is allowed.
- `delivered-final`: listener-accepted final output was written.

Run status must be exactly one of those four values. Do not invent hybrid statuses such as `scratch-candidate blocked by required gates`; use `iteration-incomplete` when named work remains, or `blocked-terminal` only when no named next action remains.

Do not summarize an `iteration-incomplete` run as "completed", "done", or terminal `blocked`. Say it stopped/paused with a scratch candidate, name the exact next action, and name the external stop reason. A named next action without an external stop reason means continue the loop. Candidate count, reviewer rejection, preserving a proof packet, avoiding an invalid mux, or discovering that a new mechanism is needed is not an external stop reason.

## Non-Negotiable Outcome

A candidate is not acceptable unless all are true:

- It uses separate mic/commentary and background lanes when they exist, not the existing combined mix.
- Promotion-grade candidates must have direct source-lane lineage: the rendered audio is built from the proven mic/commentary and background lanes, not from the existing mix or a previous mixed candidate as an audio substrate. Previous candidates may be used as diagnostic references, regression references, or control-curve inspiration, but not as the baseline audio for a caller-test candidate unless exact separated-lane reconstruction proof exists.
- Commentary remains the priority wherever recoverable speech exists.
- Repair is chunk-first by default: split sustained mic regimes into editable chunks, align each chunk's ordinary speaking body to the shared target, then stitch with short transparent ramps. A full-file filter graph is only the primary strategy when source evidence proves one stable mic regime.
- Chunk-first does not mean fixed-width windows. A chunk that contains a detected capture-level change, transition, or mixed hot/weak behavior must be split before its ordinary-speaking body is estimated.
- Chunk-first also does not mean per-second micro-chunks. Dense second-by-second gain or bed control belongs in a separate automation table; the chunk map must remain an editorial map of sustained regimes, phrase regions, and explicit boundaries.
- Dense automation cannot substitute for chunk repair. It may only address named exception windows from a failed staged chunk baseline, with protected chunks and regression windows preserved.
- Sustained mic capture regimes are found from the whole source, including quiet, weak, recovered, intermittent, and hot sections.
- Weak or buried commentary is not excluded just because a speech detector marks it inactive.
- Normal speaking volume is aligned across recoverable commentary regimes before background balancing or ducking is used to create separation.
- Alignment is bidirectional: weak regimes may need lift, but hot/recovered regimes must be trimmed down to the same comfortable normal-speaking reference.
- Promotion-grade alignment must prove sustained regime coverage, not only selected hard-window snippets. Sparse phrase rows are useful for blind spots and transitions, but they cannot prove that a long weak/problem section, healthy beginning, recovered ending, or hot section is aligned as a whole.
- If any section is explicitly accepted as having the desired mic/background relationship, use that section as the reference anchor for remaining section realignment instead of inventing a new target.
- Caller listening feedback calibrates the target and failure classes, but it does not automatically make a section the accepted reference. A section becomes the accepted reference only when the caller or reviewer explicitly says to use that section as the desired target relationship. If the caller describes a section as broken, repaired, closest-so-far, or problematic, do not anchor the whole mix to it.
- If no listener-accepted reference exists yet, derive a provisional reference anchor from current evidence for a comfortable normal-speaking target and use it until reviewer or listener evidence replaces it. Do not leave the reference as `NONE` after rendering measurable candidates.
- The core target is a comfortable normal-talking level across all recoverable commentary regimes, constrained by a comfortable mic ceiling. If lifting a weak regime to that target causes harshness, noise, clipping, limiting, muffling, or excessive gain, lower the overall speech target or prove the source limit instead of raising healthy sections to match the damaged regime.
- No section may become loud, harsh, clipped, limited, saturated, or muffled because gain was pushed too far.
- No sustained recoverable commentary section may remain quietly shifted below the shared normal-speaking target unless source-limit proof shows the raw speech is absent, clipped beyond repair, or indistinguishable from noise across that section.
- Commentary does not cut in and out, pump, or wobble because of overreactive normalization, gating, expansion, detector flicker, or sidechain behavior.
- Background remains present and natural under normal commentary, not crushed or switched on/off.
- Background presence is not a license to run a hot bed and carve space with aggressive ducking. Establish a modest stable bed baseline after mic alignment, then use local restraint only for masking events.
- Major commentary-level transitions recover at the next coherent phrase and do not leave sections sounding broken.
- Not every chunk boundary is a transition. Only source-evidenced capture-level drops, recoveries, hot shifts, or caller-example failure classes belong in transition recovery. Ordinary chunk seams belong in chunk/stitch regression proof.
- Transition recovery proof is gate-specific: a broad blind-spot pass, coarse section average, or placeholder/proxy row cannot clear a transition gate.
- A transition row that says `NOT RECOVERED` cannot be promoted by marking it `not_applicable`; expand the search to the next coherent phrase or keep it as a transition-recovery blocker/source-limit proof item.
- Background automation stays stable; it must not audibly wobble by following mic dips, detector flicker, breaths, or short phrase gaps.
- Track role proof, render lineage, candidate evidence, reviewer findings, and cleanup status all refer to the exact retained candidate.
- Candidate proof is immutable: render command/script content, processed metrics, manifests, and reviewer evidence are hash-bound to the retained candidate before review.
- Candidate strategy proof is staged: a dense-automation candidate cannot be the strongest retained promotion candidate unless its parent staged chunk baseline, exception queue, protected chunks, and automation scope are all recorded and passing.
- Unresolved weak/buried, transition, phrase-start/tail, or masking failures become a repair queue, not final-report caveats.
- Beside-source output is written only when the artifact-mode permission matrix allows it.

If any condition fails, keep iterating, prove a source limit, or stop with a non-deliverable scratch candidate and the work queue still open.

## Required Workflow

### 1. Start The Run

Follow `helpers/RUN-SETUP.md`.

- Confirm requested output mode: audio-only candidate, muxed video, preview, verification, or skill validation.
- Use a fresh scratch folder and record source path, start time, output mode, and scratch path.
- Request sub-agents/reviewers at startup when available and not already approved.
- Start from raw source unless the caller explicitly asks to verify or promote a named artifact.
- For video inputs, preserve the source video stream unchanged in beside-source muxes.

### 2. Build Neutral Source Evidence

Follow `helpers/TRACK-DISCOVERY.md` and `helpers/REGIME-MAPPING.md`.

Before choosing a mix strategy:

- identify every audio stream as `0:a:N` plus container stream number;
- classify likely `commentary/mic`, `background/system`, and `existing mix`;
- prove why the existing mix is excluded from remix source when separate lanes exist;
- measure full-file rolling behavior for mic and background lanes;
- map healthy, weak, buried, recovered, hot, intermittent, silence/noise, background-only, and source-limited regions;
- build a candidate-independent blind-spot set.
- emit a stream-role evidence table and mic-regime map in the artifact packet.

This evidence challenges the candidate later. Do not tune it after seeing whether a candidate passed.

### 3. Choose The Target And Plan The Repair

Follow `helpers/REFERENCE-TARGET.md` and `helpers/CHUNK-ASSEMBLY.md`, then read only the stage helpers required by the current source evidence: `helpers/SECTION-REALIGNMENT.md`, `helpers/TRANSITION-RECOVERY.md`, `helpers/BACKGROUND-BALANCE.md`, and `helpers/ENVELOPE-STABILITY.md`.

Write a compact plan before rendering:

- selected streams and excluded streams;
- commentary chunks/regimes and intended repair for each;
- chunk boundaries, boundary basis, stitch method, and protected boundary windows;
- ordinary-speaking reference and comfortable mic ceiling;
- accepted reference section, if one exists, with its mic body, bed body, gap, bed floor, and envelope behavior;
- provisional reference anchor when no accepted reference exists yet, including why it represents a comfortable normal-speaking target and how it will be challenged;
- how normal speaking body levels will be aligned across recoverable commentary regimes before bed ducking, including both weak-regime lift and hot/recovered-regime trim;
- transition-recovery plan for detected capture-level boundaries;
- background baseline and hearable floor;
- when shallow bed riding, local event restraint, mic-follow, phrase-region repair, or transition automation is allowed;
- what must be reviewed before any beside-source mux.

### 4. Render And Prove A Candidate

Render a chunk-assembled full-duration candidate first. A generic full-file normalizer, fixed gain, or sidechain graph is valid only when source evidence shows one stable mic regime.

The normal repair shape is:

- cut or logically segment the commentary lane into sustained regimes, splitting at detected capture-level changes instead of averaging across them;
- apply stable per-chunk commentary lift/trim toward the shared ordinary-speaking target;
- handle boundaries with short ramps, phrase-aware support, or crossfades;
- place the background under the repaired commentary per chunk;
- assemble one full-duration candidate for proof.

For each retained candidate, save:

- `candidate_manifest.json`;
- render command or script path/hash;
- candidate path/hash;
- render source mode, such as `direct-source-lanes`, `diagnostic-composite`, or `exact-separated-reconstruction`;
- any previous candidate, existing mix, stem, or composite used as an audio input, with proof of whether it is a reference only or an audio substrate;
- stream map and excluded streams;
- processed mic/background evidence when practical;
- headroom, duration, regime parity, transition recovery, background-under-commentary, background-only, and blind-spot checks.
- chunk-map validity checks proving chunks are source-regime segments, not coarse fixed bins that hide transitions;
- chunk-map density checks proving the retained chunk map is not per-second automation mislabeled as editorial chunks;
- over-hot, harshness, clipping/limiting, and muffled-overgain checks for already-loud or recovered regimes;
- balance/gap checks for ordinary, weak, buried, transition, and phrase-tail windows;
- control-surface audit proving the actual render automation, filter graph, or script agrees with bed-naturalness and overducking claims;
- staged-repair summary proving the candidate followed the order `source evidence -> chunk baseline -> exception queue -> bounded automation`, when automation is used;
- worst-window packets for reviewer or caller inspection.

Required verifier implementation is part of the run, not optional polish. If a required verifier is missing or not implemented for the retained candidate, implement or repair that verifier before treating the candidate packet as a valid stop point, unless a concrete tool, permission, source, caller-budget, or runtime constraint prevents it.

Scratch scripts are encouraged for measurement and evidence extraction. Keep them with the artifact packet and reference their hash. Scripts that only exist to make one file pass are not reusable skill logic.

Required gate files must contain real gate evidence. Do not promote a candidate from a `transition_checks`, `speech_envelope_stability_checks`, `overducking_checks`, or `mic_alignment_checks` file that only says another check passed, contains only an aggregate row, or uses placeholder/proxy language. Treat that as `verifier-insufficient` and rerun or rewrite the verifier before review.

If the render uses automation, phrase controls, sidechain curves, local bed restraints, compressor/limiter compensation, or a generated filter graph, `overducking_checks`, `balance_checks`, and reviewer packets must consume the actual control surface. A gate that claims `global bed trim only`, `no bed movement`, or similar while the retained render contains per-window bed or mic controls is invalid proof and blocks caller-test promotion.

If the retained render uses dense automation before proving a staged chunk baseline, or if automation controls most of the recording without a compact exception queue, classify it as `dense-automation-primary` or `strategy-order-violation`. Do not respond by bounding the same dense surface; rebuild the chunk baseline and exception queue first.

If source-limit or transition evidence says raw evidence "requires phrase-local extraction" or equivalent, the gate is not source-limit proof yet. Perform raw phrase extraction, reclassify the boundary, or mark the verifier `verifier-insufficient`; do not park those rows as `source-limit-suspect` or a caller-facing caveat. A coarse frame, fixed-window, broad RMS, or `proxy` measurement is not raw phrase extraction even if it is stored in a file named `raw_phrase_extraction`.

Do not allow `not_applicable` to become a waiver for listener-reported failures. If caller feedback reports loud sections, slow recovery, mic waviness, bed collapse, or masking, the matching gate is reopened and must either fail with a named work item or prove from raw source why the issue is unrecoverable.

Freeze candidate proof before review. If a render script, metrics script, processed metrics file, manifest, or proof table changes after a candidate is rendered, either rerender/reverify the candidate with a new manifest or mark the old candidate as lineage-broken scratch evidence only. A lineage-broken candidate cannot be the strongest retained candidate for promotion.

If a diagnostic composite candidate beats the proof-grade direct-lane candidates, do not promote it and do not keep iterating on that composite as the baseline. Extract the mechanism it proved, such as the local support curve, event restraint, or phrase envelope, then re-render that mechanism from the proven source lanes. If the source-lane version regresses, compare it against the diagnostic composite to identify the exact lost behavior before trying another broad strategy.

### 5. Convert Failed Gates Into Work

Follow `helpers/ITERATION-LOOP.md` and `helpers/ITERATION-VALIDATION.md`.

If validation or review blocks a candidate:

- group failures by cause;
- write a failed-gate work queue;
- set a concrete `current_blocker_goal`, `next_candidate_goal`, and `clearing_evidence`;
- choose a materially different strategy pivot;
- render a new candidate;
- rerun the relevant checks and reviewers.

Do not stop after the first honest block. Convert failed gates into a work queue and continue through materially different applicable strategy classes until a delivery gate clears, a source limit is proven, or a real external stop reason exists.

When the failed-gate queue names local reconstruction, overlay, intelligibility-first fallback, phrase-local support, detector-basis replacement, or another "different mechanism", read `helpers/LOCAL-RECONSTRUCTION.md` and either attempt its minimum slice-to-full-candidate contract or record the concrete external blocker. Naming that mechanism is not enough.

Use `helpers/ITERATION-LOOP.md` as the source of truth for failed-gate work queues, strategy-class accounting, finish-line mode, stale-best recovery, dead-end escapes, local overlays, practical-budget stops, and stop-state validity.

Use `helpers/ITERATION-VALIDATION.md` as the source of truth for candidate proof, proof-lineage repair, reviewer packets, aggregate promotion proof, confidence labels, and mux eligibility review.

If the report names a next repair, verifier revision, proof action, rerender, source-limit pass, or reviewer evidence pass, either perform it or record the concrete source, tool, permission, caller-budget, context-handoff, or stop-rule reason it cannot be performed now. Do not turn named next work into a caller-facing caveat.

### 6. Decide Honestly

Use only these labels:

- `listener-accepted`: the caller or another explicitly identified human listener accepted representative worst windows. The producing coding agent cannot self-listen or substitute local checks for this label.
- `independently-verified-ready-for-listener-test`: a read-only verifier or reviewer that did not tune or render the candidate found no evidence blocker and no unresolved listener-risk work item, but no human listener accepted the file.
- `producer-checked-candidate`: local checks found no blocking issue, but no independent verifier or human listener accepted it. This is not deliverable by default.
- `preview-with-known-risks`: structurally safe and possibly useful, but known risks remain. This is not a final deliverable.
- `blocked/source-limited`: raw speech is absent, clipped beyond repair, or indistinguishable from noise in controlling areas.
- `blocked`: safe useful output is not possible with current evidence, tools, permissions, stream roles, or practical budget, and no unattempted named repair, verifier, reviewer, or source-limited-proof action remains.

Unresolved `ambiguous listener-risk`, pending evidence reviewer status, producer comfort, or exact-path write approval cannot clear mux delivery.

Missing human listener acceptance alone does not block `caller-test-mux`. It blocks only `final-deliverable`. A candidate that has complete applicable strategy accounting, clean local metric checks, clean independent read-only evidence review, and no unresolved listener-risk work items should be promoted to `independently-verified-ready-for-listener-test` so the caller can perform the human listening step.

Do not use `blocked-terminal` when the retained candidate has unresolved `repair-not-source-limited` rows, source-limit-suspect rows that only failed because the detector found zero raw active speech, or no candidate-specific independent review. Those are iteration work items unless a concrete external stop reason prevents the named next action.

### 7. Deliver Or Stop

Follow `helpers/DELIVERY-CONTRACT.md`.

Beside-source writes are allowed only in these cases:

- `final-deliverable`: `confidence_label=listener-accepted`; report as final.
- `caller-test-mux`: `confidence_label=independently-verified-ready-for-listener-test`; report as ready for caller listening, not final.
- `preview-mux`: `confidence_label=preview-with-known-risks`; requires explicit preview approval after the risk summary; report as risky preview only.

No other beside-source write is allowed.

For any beside-source video:

- stream-copy original video;
- place remixed audio first/default;
- preserve original audio streams afterward when possible;
- verify video properties, stream order, duration, default flags, and stream hashes where practical.
- use the caller-facing same-folder name `<source-stem>-REMIX-VOICEOVER.<ext>` unless the caller explicitly requests another exact path. Put labels such as caller-test, preview, or not-final in the report, not in an invented filename suffix.

## Final Report

Use `templates/REMIX-VOICEOVER.md`. Keep the report short and evidence-bound.

Do not describe a preview, scratch candidate, or producer-only result as done.
If the run status is `iteration-incomplete`, lead the final response with that status, the next action, and the external stop reason. Do not lead with `blocked` unless the run is `blocked-terminal`.
