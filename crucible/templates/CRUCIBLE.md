# Crucible Report

## Plan Implemented

- Work route: `plan-led-no-roast/plan-led-plan-scope-roast/plan-led-project-scope-roast/roast-led-project-scope`.
- Work source: `supplied plan/full-project roast-led work queue`.
- State the supplied plan or full-project roast-led work queue completed.
- Mention any intentional scope limits.

## Completed Slices

- List each logical slice and its outcome.
- Include commit identifiers when local commits were authorized and created.
- Summarize sub-agent usage, or state why delegation was unavailable or disallowed.

## Verification

- List tests, builds, checks, review passes, and security checks run.
- State any checks that could not run and why.

## Review And Cleanup

- Summarize slice-level peer review, review gate loops and issue remediation, final security pass, cleanup pass, and docs/comment sweep results.
- Roast scope/status: `none/plan-scope/project-scope/fallback/capped`.
- Roast grade: `<letter or equivalent status>`.
- Roast cap reason: `<reason or None>`.
- Note whether the actual `roast` skill was used, omitted with a valid `plan-led-no-roast` reason, replaced by an equivalent fallback review, or capped by documented non-actionable conditions.
- Gate loops: for every run gate, include the final grade or equivalent status, rerun evidence when available, whether any actionable finding remains above Low or nitpick level, and whether the result is capped by external, owner-blocked, or unverifiable conditions.
- Gate order: list the assessment gates in the order run and confirm roast ran after assessment fixes when roast was used.
- Optional gates: state `Assess Accessibility gate: run/skipped/unavailable/capped`, `Assess Agent Readiness gate: run/skipped/unavailable/capped`, and `Assess SEO gate: run/skipped/unavailable/capped`, with skip reasons or fallback notes, final grades or equivalent statuses, and any unresolved findings.

## Remaining Risk

- List unresolved findings, if any, with severity.
- State whether remaining actionable issues are Low or nitpick-level only, and call out any explicitly accepted, external, owner-blocked, or unverifiable Critical, High, or Medium release risk.

## Release State

- State `Releasable`, `Blocked`, or `Needs follow-up`.
- Give the exact next step if blocked.
