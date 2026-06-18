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
- Evidence Gate ledger summary: list the material slice, remediation, and final release claims checked and the evidence source for each.
- Evidence Gate final sweep status: `run/capped/blocked`.
- Unresolved claim gaps: list every unresolved `Critical`, `High`, or `Medium` evidence gap, plus Low or nitpick gaps that affect confidence.
- Final-claim narrowing: state whether final report, docs, release, package, compatibility, or behavior claims were narrowed to match available proof.

## Review And Cleanup

- Summarize slice-level peer review, Gate Remediation Loop outcomes, final security pass, cleanup pass, and docs/comment sweep results.
- Roast scope/status: `none/plan-scope/project-scope/fallback/capped`.
- Roast grade: `<letter or equivalent status>`.
- Roast cap reason: `<reason or None>`.
- Note whether the actual `roast` skill was used, omitted with a valid `plan-led-no-roast` reason, replaced by an equivalent fallback review, or capped by documented non-actionable conditions.
- Gate Remediation Loops: for every run gate, include the dependency used or fallback performed, final grade or equivalent status, rerun evidence when available, whether any actionable finding remains above Low or nitpick level, and whether the result is capped by external, owner-blocked, or unverifiable conditions.
- Gate order: list selected adjunct assessment gates in the order run, confirm roast ran after assessment fixes when roast was used, and confirm the final Evidence Gate sweep ran after assessment, roast, security, cleanup, and docs/comment passes stabilized.
- Adjunct assessment gates: for every selected gate, state `<Gate name>: run/skipped/unavailable/capped`, trigger or skip reason, fallback note when relevant, final grade or equivalent status, cap reason, and unresolved findings.
- If no adjunct assessment gate was selected, state the reason when it matters to release readiness.

## Remaining Risk

- List unresolved findings, if any, with severity.
- State whether remaining actionable issues are Low or nitpick-level only, and call out any explicitly accepted, external, owner-blocked, or unverifiable Critical, High, or Medium release risk.

## Release State

- State `Releasable`, `Blocked`, or `Needs follow-up`.
- Give the exact next step if blocked.
