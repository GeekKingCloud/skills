# Adjunct Assessment Gates

Read this helper only when the caller asks Crucible to pair with an assessment skill, requirement, or scan, or when the plan or changed surface makes an assessment gate relevant to release confidence.

Adjunct assessment gates are optional. They are selected for the current target surface; they are not a fixed checklist that every Crucible run must execute.

## Selecting Gates

Choose assessment gates from concrete current-run evidence:

- caller-requested skills, scans, or requirements
- changed surfaces such as UI, docs, public sites, APIs, SDKs, CLIs, packages, installers, workflows, generated documents, auth boundaries, data handling, platform support, performance-sensitive paths, compliance-sensitive flows, or agent-facing content
- repository instructions, release criteria, issue text, handoff files, plans, CI requirements, or deployment constraints
- gaps exposed by the Evidence Gate

Each selected gate must have:

- a specific gate name
- the relationship type `optional adjunct gate`
- the trigger that made it relevant
- the skip condition that would make it irrelevant on a future run
- the evidence or tool used
- blocking behavior for unresolved findings
- final-report fields for status, grade or equivalent result, cap reason, and unresolved findings

Examples of possible assessment gates include accessibility, classic SEO, agent-readiness, performance, package/install smoke, platform compatibility, API contract checks, documentation freshness, compliance requirements, or project-specific release scans. Treat named examples as examples only; do not report them as mandatory fields unless they were selected for the run.

## Shared Gate Rules

Use the Crucible Review Gate Loop for every selected assessment gate.

Classify every assessment finding as:

- `actionable in scope`
- `external or owner-blocked`
- `unverifiable with current access`
- `explicitly accepted`

Loop on actionable Critical, High, and Medium findings. Fix Low or nitpick findings when they are cheap, clarifying, or release-confidence-building.

Do not keep rerunning a gate solely because its grade is capped by documented external, owner-blocked, or unverifiable conditions. After actionable fixes are exhausted, treat the gate as `capped` rather than failed when the remaining above-Low findings are outside Crucible's current ability to change or verify.

For capped gates, report:

- evidence for the cap
- why Crucible cannot resolve or verify it from the current workspace
- who or what would unblock it
- whether the cap affects release readiness
- the exact next step

Do not use `external`, `owner-blocked`, or `unverifiable` as an escape hatch for findings that can be fixed or tested in the current workspace. When in doubt, attempt the narrowest reasonable fix or verification once, then classify the remaining cap from evidence.

## Gate Order

When more than one assessment gate applies, choose an order that prevents later fixes from invalidating earlier evidence. Document the chosen order before running the gates.

Default ordering principles:

- Run gates that can change source, generated output, markup, packaging, or docs before gates that judge final publication or consumption.
- Run foundational discovery, packaging, install, compatibility, or contract gates before higher-level workflow and agent-facing gates that depend on those foundations.
- Run target-specific assessment gates before roast, so roast reviews the final assessed state.

If two gates are independent and will not create conflicting edits, their investigation can run in parallel, but patch integration still goes through the main Crucible Execution Loop.

## Fallbacks

If a selected assessment skill or tool is unavailable, perform the closest evidence-backed fallback pass that is proportional to the risk and available context.

Report fallback gates as `unavailable` when the named skill or tool could not run, then include:

- the unavailable skill, tool, scan, or requirement
- why it could not run
- what fallback was performed
- what the fallback could and could not prove
- whether unresolved gaps cap the gate or block release readiness

Do not claim the same confidence as the unavailable assessment unless the fallback produced equivalent evidence.

## Reporting

For every selected adjunct assessment gate, report:

- gate name
- status: `run`, `skipped`, `unavailable`, or `capped`
- trigger or skip reason
- final grade, score, verdict, or equivalent status
- rerun evidence when fixes were made
- unresolved findings by severity
- cap reason, owner or unblocker, and exact next step when capped

For gates not selected, report nothing unless the omission could be misread as a missing release check. When relevant, say `No adjunct assessment gates selected` with the reason.
