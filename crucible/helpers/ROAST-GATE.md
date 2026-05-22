# Roast Gate

Read this helper when choosing roast scope, running roast, using roast as Crucible's work queue, falling back because the `roast` skill is unavailable, or explaining why a plan-led route has no roast.

## Routes

Crucible has exactly four valid routes:

- `plan-led-no-roast`: implement a supplied plan and run the non-roast hardening gates.
- `plan-led-plan-scope-roast`: implement a supplied plan, then roast only the changed plan scope.
- `plan-led-project-scope-roast`: implement a supplied plan, then roast the full current project.
- `roast-led-project-scope`: roast the full current project, use findings as the work queue, then remediate through the Review Gate Loop.

Do not use legacy route names outside the four valid routes above. Do not treat `roast skipped` as its own route. A no-roast run is only valid as `plan-led-no-roast`, and it still requires a concrete supplied plan.

## Choosing Roast Scope

Use `plan-led-no-roast` only when the caller opts out of roast, the plan is narrow enough that broad roast would be disproportionate, or repo instructions make roast inappropriate. Disclose reduced release confidence in the final report.

Use `plan-led-plan-scope-roast` as the default plan-led roast route. Scope roast to the changed files, touched modules, tests, configuration, documentation, and contracts needed to judge the implemented plan.

Use `plan-led-project-scope-roast` when the caller asks for full-project hardening, the plan touches architecture or shared contracts, the blast radius is unclear, prior findings suggest systemic risk, or the changed surface is too broad for a plan-scope review to be meaningful.

Use `roast-led-project-scope` when no separate implementation plan is supplied and the caller asks Crucible to harden, release-ready, or converge the current project. This route always roasts the full current project first; roast findings become the work queue.

## Running Roast

Run roast as a serious, evidence-backed release audit unless the caller explicitly asks for a snarkier presentation.

Use the Review Gate Loop:
- collect findings, grade, evidence, and scope limitations
- fix one finding or root-cause group at a time through the Execution Loop
- rerun roast, a focused roast, or the closest equivalent verification after fixes
- repeat until the gate earns an A grade or equivalent high result and no unresolved actionable finding remains above Low or nitpick level

Fix actionable Critical, High, and Medium findings. Fix Low findings when they are cheap, clarify real confusion, or affect release confidence. Do not batch unrelated roast findings into one broad refactor.

If the grade is capped by documented external, owner-blocked, or unverifiable conditions, report roast status as `capped` with the final grade, evidence, unblocker, and next step. Do not keep rerunning roast solely because of a documented non-actionable cap.

## Fallbacks And Reporting

If the actual `roast` skill is unavailable on a route that requires roast, perform an equivalent serious, evidence-backed review and report roast status as `fallback`.

Report roast scope/status as one of:
- `none`
- `plan-scope`
- `project-scope`
- `fallback`
- `capped`

Always report the final roast grade or equivalent status and the roast cap reason. Use `None` as the cap reason when the roast gate is not capped. For `none`, include the reason and reduced-confidence disclosure. For `fallback`, include why the actual skill was unavailable and what equivalent review was performed. For `capped`, include non-actionable cap evidence and the exact unblocker.

Do not claim an A-grade release state if tests did not run, roast or equivalent review was sampled, roast was omitted without a valid `plan-led-no-roast` reason, or actionable Critical, High, or Medium findings remain unresolved.
