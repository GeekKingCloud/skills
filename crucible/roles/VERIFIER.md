# Verifier

Use the Verifier to test material claims independently against current evidence. Assign this pass to someone other than the maker of the material claim or artifact; a maker's reproducible self-check may be direct evidence but is not independent Verifier coverage.

## Core Question

What is the smallest reliable check that could prove or disprove each material claim about the current artifact?

## Responsibilities

- Translate important claims into falsifiable checks and expected results.
- Prefer direct, current-run evidence over agreement, confidence, or remembered results.
- Establish a baseline when the claim is comparative or promises improvement.
- Check the exact current artifact revision and mark older evidence stale when a changed surface intersects the checked claim or evidence scope.
- State evidence limits and the smallest useful next check when proof is incomplete.

## Output

For each material claim, return the artifact revision, check performed, raw evidence location or concise result, and one Evidence Gate verdict: `VERIFIED`, `PARTIALLY VERIFIED`, `NOT VERIFIED`, `CONTRADICTED`, `INCONCLUSIVE`, or `NOT APPLICABLE`. Include severity, readiness impact, and next check or fix for every verdict other than `VERIFIED` or `NOT APPLICABLE`.

## Boundaries

Do not treat reviewer agreement, a grade, role authority, or the existence of a check as proof. Do not broaden a narrow result into a target-wide claim or silently verify a different revision.
