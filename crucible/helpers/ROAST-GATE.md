# Roast Gate

Read this helper when choosing Roast scope, running Roast, using Roast as Crucible's work queue, falling back because the `roast` skill is unavailable, or explaining why a work-led route has no Roast.

Relationship type: default core gate when the selected route includes roast.

Dependency: the sibling `roast` skill, or an equivalent serious fallback review when that skill is unavailable. Report the dependency status as execution evidence; do not present Crucible as advertising or requiring a public bundle of skills.

## Routes

Crucible has exactly four valid routes:

- `work-led-no-roast`: complete a supplied work source and run the non-Roast gates.
- `work-led-scope-roast`: complete a supplied work source, then roast only the changed or created scope.
- `work-led-whole-target-roast`: complete a supplied work source, then roast the whole current target.
- `roast-led-whole-target`: roast the whole current target, use findings as the work queue, then remediate through the Gate Remediation Loop.

Do not use legacy route names outside the four valid routes above. Do not treat `Roast skipped` as its own route. A no-Roast run is only valid as `work-led-no-roast`, and it still requires a concrete supplied work source.

When resuming older work, map legacy names to the current routes and report the current name:

- `plan-led-no-roast` -> `work-led-no-roast`
- `plan-led-plan-scope-roast` -> `work-led-scope-roast`
- `plan-led-project-scope-roast` -> `work-led-whole-target-roast`
- `roast-led-project-scope` -> `roast-led-whole-target`

## Choosing Roast Scope

Use `work-led-no-roast` only when the caller opts out of Roast, the work is narrow enough that broad review would be disproportionate, or target instructions make Roast inappropriate. Disclose reduced readiness confidence in the final report.

Use `work-led-scope-roast` as the default work-led Roast route. Scope Roast to the changed or created code, content, sections, regions, states, files, tests, configuration, documentation, contracts, or supporting material needed to judge the completed work source.

Use `work-led-whole-target-roast` when the caller asks for whole-target hardening, the work changes architecture, governing structure, or shared contracts, the blast radius is unclear, prior findings suggest systemic risk, or the changed surface is too broad for a scope review to be meaningful.

Use `roast-led-whole-target` when no separate work source is supplied and the caller asks Crucible to harden, improve, finish, or converge the current target. This route always roasts the whole current target first through relevant lenses; Roast findings become the work queue.

## Running Roast

Run Roast as a serious, evidence-backed review through caller-specified and target-appropriate lenses. Use the full engineering and release lens for software; do not force software categories onto other targets.

Keep the Challenger role and Roast distinct. Challenger attempts to falsify a bounded plan, artifact, or decision during the work; Roast is the selected broad-quality gate against the current changed state. If one sub-agent performs both sequentially, close the Challenger pass, issue a new Roast charter, and produce a separate Roast report bound to the current artifact revision. Never treat Challenger agreement or silence as a Roast result.

Use the Gate Remediation Loop:
- collect findings, grade, evidence, and scope limitations
- fix one finding or root-cause group at a time through the Execution Loop
- rerun roast, a focused roast, or the closest equivalent verification after fixes
- repeat until the gate earns an A grade or equivalent high result and no unresolved actionable finding remains above Low or nitpick level

Fix actionable Critical, High, and Medium findings. Fix Low findings when they are cheap, clarify real confusion, or affect readiness confidence. Do not batch unrelated Roast findings into one broad rewrite or refactor.

If the grade is capped by documented external, owner-blocked, or unverifiable conditions, report roast status as `capped` with the final grade, evidence, unblocker, and next step. Do not keep rerunning roast solely because of a documented non-actionable cap.

If risk/security, cleanup, readability, or supporting-material remediation materially changes the Roast-reviewed target, rerun a focused or whole-target Roast against the changed surface before the final Evidence Gate sweep. Do not carry an earlier grade forward across material post-Roast changes.

## Fallbacks And Reporting

If the actual `roast` skill is unavailable on a route that requires roast, perform an equivalent serious, evidence-backed review and report roast status as `fallback`.

Report Roast scope as one of:

- `none`
- `work-scope`
- `whole-target`

Report Roast status separately as one of:

- `run`
- `skipped`
- `fallback`
- `capped`
- `blocked`

Always report the final Roast grade or equivalent status and the Roast cap reason. Use `None` as the cap reason when the Roast gate is not capped. For scope `none` and status `skipped`, include the reason and reduced-confidence disclosure. For `fallback`, include why the actual skill was unavailable, what equivalent review was performed, and whether it covered the work scope or whole target. If a fallback review is also capped, report final status `capped` and separately disclose that the fallback mechanism was used. For `capped`, include non-actionable cap evidence and the exact unblocker.

Do not claim an A-grade ready state if material target-appropriate verification did not run, Roast or equivalent review was sampled, Roast was omitted without a valid `work-led-no-roast` reason, or actionable Critical, High, or Medium findings remain unresolved.

An A-grade Roast is evidence of quality within its reviewed scope and lenses, not professional certification, stakeholder acceptance, or authority to publish, sign, send, deploy, or release the target.
