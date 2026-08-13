# Roast Gate

Read this helper when choosing Roast scope, running Roast, using Roast as Crucible's work queue, falling back because the `roast` skill is unavailable, or explaining why a work-led route has no Roast. Use `PROPORTIONALITY.md` for every finding disposition and gate decision.

Relationship type: default core gate when the selected route includes roast.

Dependency: the sibling `roast` skill, or an equivalent serious fallback review when that skill is unavailable. Report the dependency status as execution evidence; do not present Crucible as advertising or requiring a public bundle of skills.

## Routes

Crucible has exactly four valid routes:

- `work-led-no-roast`: complete a supplied work source and run the non-Roast gates.
- `work-led-scope-roast`: complete a supplied work source, then roast only the changed or created scope.
- `work-led-whole-target-roast`: complete a supplied work source, then roast the whole current target.
- `roast-led-whole-target`: roast the whole current target, use findings as the work queue, then remediate through the Gate Remediation Loop.

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
- classify each finding as a target defect, evidence gap, review-process invalidation, or future hardening
- disposition findings against the current milestone, assurance posture, and blocker policy
- apply the Control-Cost Test before adding review-induced machinery
- fix one current blocker or proportionate root-cause group at a time through the Execution Loop
- rerun roast, a focused roast, or the closest equivalent verification after fixes
- finish when the target is fit for the stated milestone and every material finding has an evidence-backed disposition

Fix applicable current-milestone Critical and High findings by default. Fix Medium findings when they violate a current acceptance criterion or required invariant, create credible material harm in the present exposure, or the assurance posture makes them blockers. Fix other findings when proportionate; otherwise defer, accept, or exclude them with evidence. Do not batch unrelated Roast findings into one broad rewrite or refactor.

Roast grade and Crucible gate disposition are separate. Report Roast's grade honestly. Do not require an A unless maximum assurance is caller-requested or justified by the current exposure; a B may be fit for the stated milestone under Roast's own rubric.

If the grade is capped by documented external, owner-blocked, or unverifiable conditions, report roast status as `capped` with the final grade, evidence, unblocker, and next step. Do not keep rerunning roast solely because of a documented non-actionable cap.

If risk/security, cleanup, readability, or supporting-material remediation materially changes the Roast-reviewed target, rerun a focused or whole-target Roast against the changed surface before the final Evidence Gate sweep. Do not carry an earlier grade forward across material post-Roast changes.

When exact artifact identity matters, review a stable commit, saved revision, hash-addressed bundle, or equivalent frozen candidate. If it changes during review, mark the Roast verdict process-invalidated and rerun the affected scope; do not convert review-path drift into a product defect.

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

Always report the final Roast grade or equivalent status and the Roast cap or blocker reason. Use `None` when the Roast gate is neither capped nor blocked. For scope `none` and status `skipped`, include the reason and reduced-confidence disclosure. For `fallback`, include why the actual skill was unavailable, what equivalent review was performed, and whether it covered the work scope or whole target. If a fallback review is also capped, report final status `capped` and separately disclose that the fallback mechanism was used. For `capped` or `blocked`, include the evidence and exact unblocker.

Do not claim a fit-for-milestone ready state if material target-appropriate verification did not run, Roast or equivalent review was sampled without disclosure, Roast was omitted without a valid `work-led-no-roast` reason, or a current-milestone blocker remains unresolved.

An A-grade Roast is evidence of quality within its reviewed scope and lenses, not professional certification, stakeholder acceptance, or authority to publish, sign, send, deploy, or release the target.
