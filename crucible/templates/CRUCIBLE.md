# Crucible Report

## Work Completed

- Target and scope: `<authoritative artifact and changed surface>`.
- Intended ready state: `<release, merge, publish, deliver, submit for owner or qualified approval, execute, adopt, or hand off>`.
- Evidence mode: `<source, rendered/live behavior, artifact comparison, references, or combination>`.
- Action boundary: `<authorized edits, saves, commits, exports, delivery, publication, approval, or other mutations>`.
- Success criteria: `<observable completion result and quality bar>`.
- Work route: `work-led-no-roast/work-led-scope-roast/work-led-whole-target-roast/roast-led-whole-target`.
- Work source: `<supplied plan, brief, request, specification, issue, feedback, redline instruction, acceptance criteria, handoff, findings, or whole-target Roast queue>`.
- State what work source was completed.
- Mention any intentional scope limits.

## Completed Slices

- List each logical slice and its outcome.
- Include commit identifiers when local commits were authorized and created.
- Summarize sub-agent usage, or state why delegation was unavailable or disallowed.

## Verification

- List target-appropriate tests, builds, checks, comparisons, renders, walkthroughs, review passes, and risk or security checks run.
- State any checks that could not run and why.
- Evidence Gate ledger summary: list the material slice, remediation, and final readiness claims checked and the evidence source for each.
- Evidence Gate final sweep status: `run/capped/blocked`.
- Unresolved claim gaps: list every unresolved `Critical`, `High`, or `Medium` evidence gap, plus Low or nitpick gaps that affect confidence.
- Final-claim narrowing: state whether final report, target, supporting material, release, publication, delivery, compatibility, or behavior claims were narrowed to match available proof.

## Review And Cleanup

- Summarize slice-level peer review, Gate Remediation Loop outcomes, final risk and security pass, cleanup pass, and readability/supporting-material sweep results.
- Roast scope: `none/work-scope/whole-target`.
- Roast status: `run/skipped/fallback/capped/blocked`.
- Roast grade: `<letter or equivalent status>`.
- Roast cap reason: `<reason or None>`.
- Note whether the actual `roast` skill was used, omitted with a valid `work-led-no-roast` reason, replaced by an equivalent fallback review, or capped by documented non-actionable conditions.
- Gate Remediation Loops: for every run gate, include the dependency used or fallback performed, final grade or equivalent status, rerun evidence when available, whether any actionable finding remains above Low or nitpick level, and whether the result is capped by external, owner-blocked, or unverifiable conditions.
- Gate order: list selected adjunct assessment gates in the order run, confirm Roast ran after assessment fixes when Roast was used, confirm Roast was rerun after any material later remediation, and confirm the final Evidence Gate sweep ran after assessment, Roast, risk/security, cleanup, and readability/supporting-material passes stabilized.
- Adjunct assessment gates: for every selected gate, state `<Gate name>: run/skipped/unavailable/capped`, trigger or skip reason, fallback note when relevant, final grade or equivalent status, cap reason, and unresolved findings.
- If no adjunct assessment gate was selected, state the reason when it matters to the intended ready state.

## Remaining Risk

- List unresolved findings, if any, with severity.
- State whether remaining actionable issues are Low or nitpick-level only, and call out any explicitly accepted, external, owner-blocked, or unverifiable Critical, High, or Medium readiness risk.

## Ready State

- State `Ready`, `Blocked`, or `Needs follow-up`, and name what it is ready for.
- Give the exact next step if blocked.
