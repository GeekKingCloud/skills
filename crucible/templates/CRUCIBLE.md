# Crucible Report

## Work Completed

- Target and scope: `<authoritative artifact and changed surface>`.
- Current milestone: `<what becomes true after this run, and nothing more>`.
- Assurance posture: `exploratory/development/production-candidate/live-critical` with rationale.
- Present exposure and recoverability: `<current blast radius and recovery path>`.
- Current required invariants: `<acceptance criteria and credible failures that must be prevented now>`.
- Deferred lifecycle gates: `<named later requirements or None>`.
- Complexity boundary: `<acceptable new mechanisms and maintenance burden>`.
- Blocker policy and reframe trigger: `<current defaults, overrides, and stop/reconsider conditions>`.
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
- Role assignments: list Steward, Challenger, Verifier, and any justified optional role with its distinct question, bounded scope, and artifact revision.
- Independence: state who made each material artifact or claim and who verified it.
- Material disagreements: summarize each recorded conflict, targeted rebuttal, evidence or owner decision, and closure status.
- Summarize other sub-agent usage, or state why delegation was unavailable or disallowed.

## Verification

- List target-appropriate tests, builds, checks, comparisons, renders, walkthroughs, review passes, and risk or security checks run.
- State any checks that could not run and why.
- Evidence Gate ledger summary: list the material slice, remediation, and final readiness claims checked, the evidence source for each, and every material gap's classification and disposition.
- Evidence Gate final sweep status: `run/capped/blocked`.
- Unresolved claim gaps: list every current-milestone blocker plus deferred, accepted, external, owner-blocked, or unverifiable gaps that affect confidence.
- Final-claim narrowing: state whether final report, target, supporting material, release, publication, delivery, compatibility, or behavior claims were narrowed to match available proof.

## Review And Cleanup

- Summarize slice-level peer review, Gate Remediation Loop outcomes, final risk and security pass, cleanup pass, and readability/supporting-material sweep results. For cleanup, name the task-owned changed files and directly affected flow inspected, material simplifications or justified retentions, and affected verification reruns; use a concise `no material in-scope excess found` result when nothing needed changing rather than inventorying every construct.
- Roast scope: `none/work-scope/whole-target`.
- Roast status: `run/skipped/fallback/capped/blocked`.
- Roast grade: `<letter or equivalent status>`.
- Roast cap or blocker reason: `<reason or None>`.
- Note whether the actual `roast` skill was used, omitted with a valid `work-led-no-roast` reason, replaced by an equivalent fallback review, or capped by documented non-actionable conditions.
- Gate Remediation Loops: for every run gate, include the dependency used or fallback performed, final grade or equivalent status, rerun evidence when available, finding classifications and dispositions, Control-Cost or Steward reframe decisions, whether any current-milestone blocker remains, and whether the result is capped.
- Gate order: list selected adjunct assessment gates in the order run, confirm Roast ran after assessment fixes when Roast was used, confirm Roast was rerun after any material later remediation, and confirm the final Evidence Gate sweep ran after assessment, Roast, risk/security, cleanup, and readability/supporting-material passes stabilized.
- Adjunct assessment gates: for every selected gate, state `<Gate name>: run/skipped/unavailable/capped/blocked`, trigger or skip reason, fallback note when relevant, final grade or equivalent status, cap or blocker reason, and unresolved findings.
- If no adjunct assessment gate was selected, state the reason when it matters to the intended ready state.

## Remaining Risk

- List unresolved findings, if any, with severity, classification, disposition, and named later gate or owner when applicable.
- State whether any current-milestone blocker remains, and call out deferred, explicitly accepted, external, owner-blocked, or unverifiable material risk.

## Ready State

- State `Fit for milestone`, `Blocked`, or `Needs follow-up`, and name the exact milestone or ready state.
- Give the exact next step if blocked.
