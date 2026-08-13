# Adjunct Assessment Gates

Read this helper only when the caller asks Crucible to pair with an assessment skill, requirement, or scan, or when the work source or changed target makes an assessment gate relevant to readiness confidence.

Adjunct assessment gates are optional. They are selected for the current target surface; they are not a fixed checklist that every Crucible run must execute.

## Selecting Gates

Choose assessment gates from concrete current-run evidence:

- caller-requested skills, scans, or requirements
- changed surfaces such as UI, designs, images, documents, contracts, policies, plans, public sites, APIs, SDKs, CLIs, packages, installers, workflows, auth boundaries, data handling, platform support, performance-sensitive paths, compliance-sensitive material, or agent-facing content
- repository instructions, release criteria, issue text, handoff files, plans, CI requirements, or deployment constraints
- gaps exposed by the running Evidence Gate ledger

Each selected gate must have:

- a specific gate name
- the relationship type `optional adjunct gate`
- the trigger that made it relevant
- the skip condition that would make it irrelevant on a future run
- the evidence or tool used
- blocking behavior for unresolved findings
- final-report fields for status, grade or equivalent result, cap or blocker reason, and unresolved findings

Examples of possible assessment gates include accessibility, classic SEO, agent-readiness, performance, package/install smoke, platform compatibility, API or document contract checks, factual/source review, visual quality, usability, documentation freshness, compliance requirements, or target-specific readiness scans. Treat named examples as examples only; do not report them as mandatory fields unless they were selected for the run.

## Shared Gate Rules

Use the Crucible Gate Remediation Loop and `PROPORTIONALITY.md` for every selected assessment gate.

Treat selected assessment skills or tools as optional adjunct dependencies, not as a promoted skill bundle. Report which gate ran, what evidence or fallback was used, and why it was relevant to this target surface. Do not list unselected assessment skills as missing features or imply they are mandatory Crucible companions.

Classify and disposition every assessment finding through the shared Proportionality Contract. Loop on current-milestone blockers and proportionate fixes, not every above-Low finding automatically. Keep valid deferred, accepted, external, owner-blocked, unverifiable, and out-of-scope findings visible with their readiness effect.

Do not keep rerunning a gate solely because of documented deferred, external, owner-blocked, or unverifiable conditions. After current blockers and selected proportionate fixes are exhausted, keep the gate's ordinary `run` status when remaining findings are fully dispositioned and do not limit the intended ready state. Use `capped` only when a remaining condition limits the grade, evidence, or readiness claim that the current milestone requires.

For capped gates, report:

- evidence for the cap
- why Crucible cannot resolve or verify it with current access
- who or what would unblock it
- whether the cap affects the intended ready state
- the exact next step

Do not use deferral, acceptance, `external`, `owner-blocked`, or `unverifiable` as an escape hatch for a current-milestone blocker that can be fixed or verified within the authorized target and current access. When in doubt, attempt the narrowest reasonable verification or Steward review before deciding.

## Gate Order

When more than one assessment gate applies, choose an order that prevents later fixes from invalidating earlier evidence. Document the chosen order before running the gates.

Default ordering principles:

- Run gates that can change source, content, design, generated output, markup, packaging, or supporting material before gates that judge final publication, delivery, approval, or consumption.
- Run foundational discovery, packaging, install, compatibility, or contract gates before higher-level workflow and agent-facing gates that depend on those foundations.
- Run target-specific assessment gates before Roast, so Roast reviews the final assessed state.

If two gates are independent and will not create conflicting edits, their investigation can run in parallel, but patch integration still goes through the main Crucible Execution Loop and updates the Evidence Gate ledger after each remediation slice.

## Fallbacks

If a selected assessment skill or tool is unavailable, perform the closest evidence-backed fallback pass that is proportional to the risk and available context.

Report fallback gates as `unavailable` when the named skill or tool could not run, then include:

- the unavailable skill, tool, scan, or requirement
- why it could not run
- what fallback was performed
- what the fallback could and could not prove
- whether unresolved gaps cap the gate or block the intended ready state

Do not claim the same confidence as the unavailable assessment unless the fallback produced equivalent evidence.

## Reporting

For every selected adjunct assessment gate, report:

- gate name
- status: `run`, `skipped`, `unavailable`, `capped`, or `blocked`
- trigger or skip reason
- final grade, score, verdict, or equivalent status
- rerun evidence when fixes were made
- unresolved findings by severity
- cap reason, owner or unblocker, and exact next step when capped
- current-milestone blocker and exact unblocker when blocked

For gates not selected, report nothing unless the omission could be misread as a missing readiness check. When relevant, say `No adjunct assessment gates selected` with the reason.
