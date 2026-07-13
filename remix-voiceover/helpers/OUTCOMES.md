# Outcome And Limitation Guide

Use this helper after every verify pass and whenever work appears unable to continue. Failure ownership is part of the result; do not collapse every unsuccessful run into "the source is bad."

## Outcome classes

### `pass`

All promotion gates pass. The candidate is objectively ready for caller testing, not automatically listener-approved.

### `target-limited`

A coherent, quality-safe common commentary target exists below the preferred house range. The candidate may be caller-test-ready when all gates measured against the declared shared target pass.

Report:

- preferred and achieved shared targets;
- the regime that constrained the target;
- the quality evidence that prevented a higher target;
- background placement relative to the achieved target.

### `source-terminal`

No safe useful commentary result is possible. Examples include absent commentary with no alternate direct lane, unrecoverable clipping that destroys intelligibility, or speech indistinguishable from the source floor throughout the required program.

This outcome requires machine-recorded terminal evidence. Repeated candidate failure, fatigue, a low preferred target, or a toolkit limitation is never terminal source proof.

Reserved today: the current verifier does not synthesize terminal source evidence. Never hand-author this outcome into a report or manifest.

### `tuning-required`

The current plan has a concrete in-contract repair. Continue the candidate loop. Do not stop merely because the same numeric adjustment is inconvenient.

### `toolkit-limited`

A safe useful repair is supported by source evidence, but the current plan schema, renderer, verifier, or delivery contract cannot represent or prove it.

Required report fields:

- limitation owner: `toolkit`;
- exact incompatible capability or constraints;
- evidence paths and hashes;
- strongest retained safe candidate;
- recommended toolkit fix;
- exact command or workflow to resume after the fix.

A toolkit-limited stop is honest engineering evidence, not source failure. It must be machine-owned by a verifier row with `action_scope: toolkit-change`; prose alone cannot create it.

### `external-blocked`

A required source, tool, permission, storage resource, or caller decision is unavailable. Name the exact blocker and the smallest next action. Do not use this class for work that the current plan can still perform.

Reserved today: pre-verifier external failures are reported as workflow errors, not promoted manifests. Use this outcome only when a machine row explicitly supplies `external` or `caller-action` scope.

## Action scopes

Every failing promotion-manifest row identifies one action scope (plan-validation rows instead carry an exact `next_action`):

- `current-plan`: repair the current analysis, plan, candidate, or report; blocks stopping.
- `toolkit-change`: implementation or contract change outside the current media run.
- `caller-action`: overwrite approval, missing role decision, or other explicit caller choice.
- `external`: missing tool, source, permission, or resource.
- `none`: no runnable work remains.

## Final report rule

State both the run status and outcome class. The run status describes workflow state; the outcome class explains why.

Always include:

- `Outcome class:`
- `Limitation owner:`
- `Limitation evidence:`
- `Recommended fix:`

Use `NONE` for pass outcomes. Values must match machine state. A report cannot promote, terminalize, or reassign ownership by wording alone.
