---
name: remix-voiceover
description: Repair commentary-over-background audio or video, including single-program audio, into a listener-first REMIX-VOICEOVER output using deterministic measurement, macro-regime repair, verifier-derived component gates, source-container preservation, copied video, and untouched source media.
---

# Remix Voiceover

Skill version: `2026-07-12.03`

Use this when a recording has commentary/mic audio and needs a repaired voiceover-style result. With one audio lane, repair that program without inventing a background component. With separate commentary and background/system lanes, align each component's sustained capture-level sections, place the background beneath the repaired commentary, and deliver `<source-stem>-REMIX-VOICEOVER.<source-extension>` beside the source.

The goal is a file a listener can enjoy without losing the commentary, losing the background, or wondering whether the audio broke. The goal is never to satisfy a verifier.

## Responsibility Split

**The toolkit proposes, renders, and proves. You confirm, diagnose, and steer bounded exceptions.**

- The bundled `scripts/rv.py` CLI owns source profiling, default role inference, macro-regime detection, the initial highest safe shared target and baseline plan, transition ramps, rendering, verification, delivery, and stop-state validation.
- Confirm ambiguous roles and regime evidence. Diagnose failing machine rows. Modify a generated plan only through its supported schema when a bounded caller calibration or authoritative machine `next_action` requires it, then rerun validation.
- Do not invent an arbitrary target, erase detected boundaries in the plan, substitute an ad-hoc renderer, waive a verifier row, or promote from prose. Ad-hoc measurements and listening may inform a supported adjustment but can never clear a gate.
- You may suspect and investigate a source limitation. Only machine-produced terminal evidence may classify one.

The CLI is the only promotion-proof authority. Every command verifies its input hash chain and prints repair commands for stale or mismatched state; follow those commands instead of working around the refusal.

## Completion Contract

Normal success is a `caller-test-ready` file at the contract path. Deliver it when every promotion row passes; do not insert a mid-run human-listener gate. The caller judges the delivered file afterward.

A delivered success is not complete until `rv cleanup` deletes its scratch transaction. Keep scratch only while awaiting overwrite approval or when a failed or blocked outcome still needs evidence. Never leave full candidate components behind after successful delivery.

- `caller-test-ready`: all gates pass at the declared target; output is delivered or awaits overwrite approval at the contract name.
- `iteration-incomplete`: a machine-owned `toolkit-limited` or `external-blocked` outcome has no remaining `current-plan` action.
- `blocked-terminal`: machine-produced `source-terminal` evidence proves no supported repair remains.
- `delivered-final`: the caller explicitly finalizes an output after listening.

Artifact modes are `scratch-candidate`, `caller-test-mux`, and `final-deliverable`. A passing candidate awaiting overwrite approval remains successfully `caller-test-ready`; do not invent another filename. Any failing row with a `current-plan` action means continue the repair loop.

For multiple independent sources, give each source its own scratch transaction and outcome. A pre-manifest error or unsupported case blocks only that source; continue the others unless one shared failure makes every remaining source unsafe or the caller explicitly requested fail-fast behavior.

## Load Guidance When Needed

- Before classifying feedback or confirming roles, regimes, or a caller-driven adjustment: `helpers/JUDGMENT.md`.
- After a plan or promotion failure: read only the matching class in `helpers/REPAIR-PLAYBOOK.md`.
- When interpreting a machine outcome or stop permission: `helpers/OUTCOMES.md`.
- After promotion passes: `helpers/DELIVERY.md`.
- Only when debugging render, peak-control, lineage, or verifier mechanics: `helpers/TOOLKIT-CONTRACT.md`.
- Only when a target or quality-limit decision needs engineering rationale: `references/AUDIO-ENGINEERING.md`.

## Feedback Mode

Classify the run before `plan-init` or any rails adjustment:

- Use `listener-feedback-rerun` when the caller references an earlier attempt, asks to try again, or describes listening symptoms. Express caller calibration through one bounded, evidence-backed `rails_adjustment` and its corresponding validated plan fields across all recoverable regimes.
- Use `fresh-repair` when no earlier attempt or listening symptom is part of the request.
- Caller timestamps identify examples of a failure class, never the repair scope. Do not spot-fix them.
- "Make the commentary more present" must raise its measured target when safely possible; lowering only the bed does not satisfy that request.
- If a retry is implied but its concrete feedback is inaccessible, ask one clarifying question before rendering.

## Vocabulary

- `macro regime`: a sustained capture-level plateau where one component's ordinary body remains at one level. Mic and bed have independent regime maps. Pauses, breaths, yells, whispers, jump scares, and dialogue scenes remain inside a regime unless the capture level itself changes.
- `speech window`: a detected active-speech span used for measurement.
- `transition`: a boundary where sustained mic body steps because of a capture drop, recovery, or hot shift. Recovery after it must be fast.

## Workflow

Use one scratch directory under the system temp per run. `<rv>` means `python <skill-dir>/scripts/rv.py`.

### 1. Probe And Analyze

```text
<rv> probe <source> --json-out <scratch>/probe.json
<rv> analyze <source> --probe <scratch>/probe.json --json-out <scratch>/analysis.json [--mic-streams <indexes> --bed-streams <indexes>]
```

`analysis.json` profiles every audio lane, detects speech windows, maps independent sustained mic and bed regimes, and computes clean-gain headroom. A one-lane input enters `single-program-repair`. Ambiguous direct-lane inventories fail closed; the analyzer never auto-sums three or more unexplained lanes into the bed.

### 2. Confirm Roles And Regimes

Confirm the analyzer's evidence before planning. Speech-shaped bursts with sentence gaps indicate mic; continuous audio indifferent to sentences indicates bed; a lane mirroring mic and bed together is an existing mix to preserve but never remix from when direct lanes exist.

If roles conflict or remain doubtful, render short isolated lane samples, inspect them, and rerun `analyze` with confirmed mic and bed selectors. If a regime boundary is wrong, adjust bounded analyzer parameters and regenerate analysis. Role and boundary correction never happens through plan overrides.

### 3. Generate And Validate The Plan

```text
<rv> plan-init --analysis <scratch>/analysis.json --out <scratch>/render_plan.json
```

Treat the generated plan as the baseline repair, in this order. Edit its supported fields only for a bounded calibration or machine-directed repair:

1. Align every recoverable mic regime to the highest shared target the weakest regime can reach safely.
2. Preserve bed regimes unchanged at unity when complete 10 Hz curve evidence stays below the `-45 LUFS` meaningful floor with no contained meaningful/marginal speech-window evidence. Hold incomplete low-body evidence at unity as indeterminate rather than amplifying it speculatively. Align only stitchable bed regimes to their loudest safe baseline and disclose held regimes in proof.
3. Position sustained meaningful bed beneath the repaired mic with bounded macro-balance correction, then recover uniform post-correction bed headroom up to the most constrained section's masking-safe ceiling.
4. Add sparse, cited overlays only for residual events that baseline repair cannot resolve.

Preserve phrase dynamics, whispers, shouts, quiet game passages, and brief source-natural peaks. Do not normalize phrases, fragment the baseline into micro-chunks, or raise quiet bed merely to improve a gap statistic. Use bounded, evidence-backed `rails_adjustment` only for caller calibration or a proven quality limit.

```text
<rv> plan-validate --plan <scratch>/render_plan.json --analysis <scratch>/analysis.json --json-out <scratch>/plan_validation.json
```

Keep `plan_validation.json` beside the plan. Validation failures are repair instructions, not stop conditions.

### 4. Render

```text
<rv> render --source <source> --plan <scratch>/render_plan.json --outdir <scratch>/candidates/c1 --manifest-out <scratch>/candidates/c1/render_manifest.json
```

The toolkit renders direct-source mic and bed components separately and sums them without normalization. Declared peak control is mic-only; the bed and final mix are never limited. Do not replace this path with a custom renderer.

### 5. Verify And Iterate

```text
<rv> verify --manifest <render_manifest> --plan <plan> --analysis <analysis> --json-out <scratch>/candidates/c1/promotion_manifest.json
```

The promotion manifest is the only promotion truth. If it fails, read the matching class in `helpers/REPAIR-PLAYBOOK.md`, group rows by root cause, and run each machine `next_action`. If the same class survives two candidates, change mechanism instead of retuning the same one.

Every schema-2-or-newer bed plan must include exactly one passing verifier-owned `bed_yield_necessity` counterfactual. Planner judgments, recommendation fields, reason strings, and schema downgrade cannot prove necessity. Held or unmeasured bed sections do not participate in the lift. A wide gap alone remains nonblocking; unexplained candidate-safe uniform bed lift is a `current-plan` failure.

A lineage-bound A/B packet can guide a supported adjustment but never waive a row:

```text
<rv> audition --source <source> --candidate-mic <mic_component.wav> --manifest <render_manifest.json> --plan <plan> --analysis <analysis> --regime-id <id> --start <seconds> --duration <seconds> --outdir <dir> --json-out <audition.json>
```

Interpret machine-owned outcomes with `helpers/OUTCOMES.md`. Do not manufacture `external-blocked` or `source-terminal` in prose.

### 6. Deliver And Report

```text
<rv> deliver --manifest <promotion_manifest> --source <source> --output <contract-path> [--allow-overwrite]
<rv> validate-stop --report <scratch>/REMIX-VOICEOVER-report.md --manifest <promotion_manifest> --delivery <delivery.json> --json-out <scratch>/stop_state.json
```

Delivery enforces the filename, source container and extension, copied video, untouched source media, and decoded remix equality. Multiplex containers also retain original streams after the remix; native single-program audio containers deliver the repaired program while leaving the source beside it. Write the report from `templates/REMIX-VOICEOVER.md`, follow `helpers/DELIVERY.md`, and run `validate-stop` before responding. If it names runnable work, continue.

### 7. Clean Successful Scratch

After delivery succeeds and `validate-stop` passes:

```text
<rv> cleanup --scratch <scratch> --delivery <delivery.json> --stop-state <scratch>/stop_state.json
```

The guarded command verifies that the transaction is under system temp, the final output exists outside scratch and matches the delivery hash, the report/promotion/delivery/stop chain is intact, and the tree contains no links or junctions before deleting it. Verify `<scratch>` no longer exists. A success response is forbidden until cleanup reports `status=cleaned`. Do not run it for scratch-only, awaiting-overwrite, failed, or blocked outcomes.

## Stop Rules

Continue while any machine row names a `current-plan` action. Candidate count, context length, repeated failure, and "the current approach hit its ceiling" are not stop reasons.

Stop only for caller interruption or budget, a machine-owned toolkit limitation, missing required source or tool, denied permission, a resource/process failure requiring caller intervention, or machine-produced terminal source evidence. Any stop response must name the blocker, owner, evidence, recommended fix, and resume action.

If `probe`, `analyze`, `plan-init`, `plan-validate`, `render`, or `verify` cannot produce a promotion manifest, report the exact workflow error directly and preserve its repair command. Do not invent a run status or call `validate-stop` without a promotion manifest. Once a promotion manifest exists, outcome and stop reporting must use its machine-owned state.

## Non-Negotiables

- Never overwrite or modify the source recording.
- Never remix from an existing-mix lane when separate mic and bed lanes exist.
- Quote caller-supplied paths literally.
- Never bypass a reachable `rv` render, verify, deliver, or stop-validation stage. Pre-manifest workflow errors follow the explicit exception above.
- Never finish a successfully delivered run while its scratch transaction still exists; run guarded `rv cleanup` after stop validation.
- When updating this skill, bump the version and keep the full `rv` test suite green.
