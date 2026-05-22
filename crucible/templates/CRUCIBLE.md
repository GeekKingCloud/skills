# Crucible Report

## Plan Implemented

- Work route: `plan-led/review-led/current-state/combined`.
- Work source: `plan/review/current-state inspection/other`.
- State the plan, review, or release-hardening target completed.
- Mention any intentional scope limits.

## Completed Slices

- List each logical slice and its outcome.
- Include commit identifiers when local commits were authorized and created.
- Summarize sub-agent usage, or state why delegation was unavailable or disallowed.

## Verification

- List tests, builds, checks, review passes, and security checks run.
- State any checks that could not run and why.

## Review And Cleanup

- Summarize slice-level peer review, roast loops and issue remediation, final security pass, docs/comment sweep, and orphan cleanup results.
- Roast role: `input/post-change gate/current-state gate/skipped/fallback`.
- Note whether the actual `roast` skill was used, skipped with a reason, or replaced by an equivalent fallback review.
- Optional gates: state `Assess Accessibility gate: run/skipped/unavailable`, `Assess Agent Readiness gate: run/skipped/unavailable`, and `Assess SEO gate: run/skipped/unavailable`, with skip reasons or fallback notes, grades when produced, and any unresolved Critical/High blockers.

## Remaining Risk

- List unresolved findings, if any, with severity.
- State whether remaining issues are low priority or lower.

## Release State

- State `Releasable`, `Blocked`, or `Needs follow-up`.
- Give the exact next step if blocked.
