---
name: crucible
description: Orchestrate release-hardening work from a supplied plan or full-project roast-led work queue through sub-agent-heavy implementation, verification evidence checks, remediation, review gates, security pass, cleanup, docs/comment sweep, and release-readiness reporting.
---

# Crucible

## Overview

Use this skill to turn a supplied plan or a full-project roast-led work queue into finished, releasable work. Treat the work source, repository instructions, verification evidence, and review findings as hard inputs, not vibes.

The target state is:
- the selected work source is implemented or remediated
- meaningful tests and checks pass
- material behavior, release, compatibility, documentation, and final-report claims are mapped to current-run evidence
- peer review and default review-gate findings are resolved or explicitly accepted
- relevant adjunct gate findings are resolved through the same rerun-and-fix loop as default review gates, or explicitly accepted
- no orphaned code, stale comments, stale docs, unused fixtures, or abandoned config remain from the work
- comments explain tricky or unusual code without narrating obvious code
- unresolved issues are Low or nitpick-level only, and no run gate has unresolved Critical, High, or Medium findings unless the caller explicitly accepts the release risk
- the final state is ready to release, merge, or hand off with clear evidence

## Startup Permission

Before starting route selection, repository exploration, implementation, or review work, check whether sub-agents are already approved by the environment or explicitly granted by the caller's Crucible invocation. If not, ask once: "Crucible gets best results with sub-agents for peer review, validation, security, cleanup, and regression checks. May I use sub-agents where useful for this run?"

If permission is declined or sub-agents are unavailable, continue locally and state that independent review coverage is reduced. Do not repeat the question per slice; the startup answer covers bounded Crucible delegation for the run.

## Start And Work Route

1. Read the nearest `AGENTS.md` first. If it points to `STYLE.md`, `README.md`, handoff files, plans, or project docs, read the relevant files before editing.
2. Identify the work source and route before editing. Crucible always needs one of: a supplied plan, or a full-project roast-led work queue. Look for explicit user text, `PLAN.md`, `ROAST_PLAN.md`, `HANDOFF.md`, issue text, existing review findings, TODO lists, or repo-specific planning files.
3. Choose exactly one starting route:
   - `plan-led-no-roast`: implement a supplied plan and run the non-roast hardening gates.
   - `plan-led-plan-scope-roast`: implement a supplied plan, then roast only the changed plan scope.
   - `plan-led-project-scope-roast`: implement a supplied plan, then roast the full current project.
   - `roast-led-project-scope`: roast the full current project, use findings as the work queue, then remediate through the review gate loop.
4. Check version-control status before editing. Identify unrelated local changes and work around them without reverting them.
5. Define the acceptance gates: implementation or remediation outcome, tests, peer review, Evidence Gate status, claim evidence summary, unresolved claim gaps, roast scope/status, roast grade, roast cap reason, adjunct assessment gates, security pass, cleanup, docs/comment sweep, and commit or handoff expectations.

If no supplied plan exists and the caller did not authorize a full-project roast-led work queue, stop and ask for the missing work source. Stop and ask only when the work source is missing critical product decisions, would require destructive Git history changes, needs credentials, or would materially change security posture, runtime behavior, dependency surface, or public behavior without clear caller approval.

## Sub-Agent Operating Model

Follow the startup permission rule before using this operating model.

For meaningful Crucible work, treat sub-agents as the default way to improve coverage when the environment supports them and delegation is allowed. At each stage, actively look for independent work to delegate: codebase search, implementation of isolated slices, in-the-moment peer review, regression hunting, test review, security review, docs/comment sweeps, cleanup checks, and review-gate follow-up.

Keep delegated tasks bounded, parallel, and source-grounded. Give each sub-agent a clear scope, expected output, and ownership boundary. Keep blocking product decisions, final integration, and release-readiness judgment in the main thread, and verify sub-agent findings against the repository before acting.

## Execution Loop

Work in logically connected slices. For each slice:

1. State the slice goal and verification target.
2. Decide what can be delegated before editing. Use sub-agents by default for independent, bounded work such as codebase search, isolated implementation, risk review, test review, regression search, or patch review. If sub-agents are unavailable or delegation is not allowed, say so and do the pass locally.
3. Use at least one sub-agent as a peer reviewer or sounding board for each meaningful change when available. Give reviewers the slice goal, changed files or intended files, suspected risk areas, expected tests, and repo instructions.
4. Implement or remediate the slice with the smallest change that satisfies the work source and repo instructions.
5. Add or update focused tests when the slice changes behavior, fixes a bug, touches shared contracts, or guards a regression.
6. Run the narrowest meaningful verification. Broaden verification as risk or shared surface increases.
7. Ask reviewers to check the actual slice for correctness bugs, regressions, missing tests, security risks, stale comments/docs, orphaned code, and maintainability problems. Integrate findings critically; verify against source before changing code.
8. Review the slice for dead code, stale helpers, orphaned files, stale comments, stale docs, and unnecessary dependencies introduced by the change.
9. Commit the slice when local commits are authorized by the caller or repo workflow. Treat an explicit Crucible request as authorization for local logical commits unless the caller or repo instructions say otherwise. Do not push, force-push, rewrite history, tag releases, or publish artifacts without explicit approval.

If verification fails, fix the cause and rerun the relevant check. Do not change tests merely to pass; align tests and implementation with the intended behavior.

## Roast Review Gate

Use the sibling `roast` skill as Crucible's default broad code-quality review gate and as the only no-plan work source. Roast is central to Crucible's release-hardening identity, but plan-led work may explicitly choose no roast.

Read `helpers/ROAST-GATE.md` when choosing roast scope, running roast, using roast as the work queue, falling back because `roast` is unavailable, or explaining why a plan-led route has no roast. Keep the detailed route and scope rules in that helper.

## Evidence Gate

Use `helpers/EVIDENCE-GATE.md` as Crucible's default proof-boundary gate for every run. Run it after implementation and focused verification, before adjunct assessment gates and roast.

The Evidence Gate verifies that material behavior, release, compatibility, documentation, package, install, security, cleanup, and final-report claims are supported by current-run evidence. It is not a duplicate roast: narrow unsupported claims, add missing verification, or fix contradicted behavior through the Review Gate Loop before claiming release readiness.

## Review Gate Loop

Use the same outer loop for every gate that runs, whether it is the default Evidence Gate, default roast gate, an adjunct assessment gate, or an evidence-backed fallback pass:

1. Run the skill or equivalent fallback pass against the current changed state.
2. Capture the grade, severity list, evidence, and scope limitations.
3. Classify every finding as `actionable in scope`, `external or owner-blocked`, `unverifiable with current access`, or `explicitly accepted`.
4. Fix each actionable Critical, High, and Medium finding through the Execution Loop. Fix Low or nitpick findings when they are cheap, clarifying, or release-confidence-building.
5. For external, owner-blocked, or unverifiable findings, document the evidence, why Crucible cannot resolve or verify it from the current workspace, who or what would unblock it, and whether it caps the grade.
6. Rerun the same skill, a focused rerun, or the closest equivalent verification against the changed state.
7. Repeat until the gate produces an A grade or equivalent high result and no unresolved actionable finding remains above Low or nitpick level.

Do not keep rerunning a gate solely because its grade is capped by documented external, owner-blocked, or unverifiable conditions. After actionable fixes are exhausted, treat the gate as `capped` rather than failed when the remaining above-Low findings are outside Crucible's current ability to change or verify. Report the cap clearly with evidence, owner or unblocker, and next step.

If a skill does not produce a letter grade, treat the gate as passing only when its rerun has no unresolved actionable Critical, High, or Medium findings and the remaining Low, nitpick, external, owner-blocked, or unverifiable findings are documented. Do not claim release readiness while any run gate still has unresolved actionable Critical, High, or Medium findings unless the caller explicitly accepts that release risk in the final report.

Do not use `external`, `owner-blocked`, or `unverifiable` as an escape hatch for findings that can be fixed or tested in the current workspace. When in doubt, attempt the narrowest reasonable fix or verification once, then classify the remaining cap from evidence.

Run gate loops sequentially when later fixes can invalidate earlier evidence. For plan-led hardening, finish the implementation loop first, then run the Evidence Gate. Run selected adjunct assessment gates in the concrete order documented by `helpers/ASSESSMENT-GATES.md`. Run the roast loop after assessment fixes so roast reviews the final assessed state. Then run security, cleanup, and docs/comment passes. Parallelize independent investigation inside a loop when it will not create conflicting edits, but integrate patches through the main Execution Loop.

## Adjunct Assessment Gates

Use adjunct assessment gates only when the implemented plan has a relevant surface, the caller asks Crucible to pair with an assessment skill, or a concrete requirement or scan is needed for release confidence. They are not hard dependencies for every Crucible run.

When the caller asks for an assessment skill or scan, or the changed surface clearly makes one relevant, read `helpers/ASSESSMENT-GATES.md` and follow its selection, trigger, skip, fallback, capped-grade, and final-report rules. Named assessment skills such as accessibility, agent-readiness, SEO, performance, security, compliance, package, or platform checks are examples, not mandatory fixed gates. If no assessment gate is relevant, do not read the helper; report adjunct gates as skipped only when that status matters to the final release-readiness explanation.

## Security Pass

Run a dedicated security pass after review-gate loops are complete and before cleanup.
Prefer a separate sub-agent for this pass when available, especially when the change touches inputs, permissions, storage, shell commands, dependencies, network boundaries, or generated artifacts. Parallelize independent security investigation and focused patch review when it will not create conflicting edits.

Inspect:
- untrusted input reaching shell commands, SQL, paths, templates, HTML, eval-like APIs, redirects, URLs, dynamic imports, regexes, or deserializers
- authentication, authorization, tenant boundaries, sessions, tokens, and permission checks
- secrets in source, examples, configs, logs, CI, fixtures, generated output, and docs
- dependency changes, install hooks, lockfiles, network calls, CORS, CSRF, webhook validation, SSRF, open redirects, and unsafe defaults
- file operations, destructive commands, cleanup behavior, temp paths, and permissions

Patch confirmed security issues through the Execution Loop rules. Rerun focused security checks after patches. If a security concern cannot be resolved inside scope, report it with severity, evidence, impact, and the safest next action.

## Cleanup Gate

Run cleanup after security patches are stable and before the docs/comment sweep. Parallelize independent cleanup checks and small cleanup patches when they do not conflict.

Before final response or handoff:

1. Recheck version-control status.
2. Confirm there are no new orphaned files, unused helpers, stale fixtures, obsolete comments, outdated docs, dead imports, or accidental generated artifacts.
3. Confirm local commits were created for each logical slice when commits were authorized. If commits were not authorized, summarize commit-ready groups.
4. Confirm verification commands and results.
5. Confirm slice-level sub-agent reviews were integrated, or explain why review was performed locally.
6. Confirm unresolved risks are Low or nitpick-level only, or explain why release readiness is blocked.

## Comments And Docs

Do a focused readability sweep after review-gate loops, the final security pass, and cleanup are stable. Parallelize independent docs/comment review and updates when they do not conflict, then reconcile the final wording locally.

Keep good comments:
- explain tricky algorithms, unusual constraints, compatibility requirements, security decisions, and non-obvious failure handling
- document strange behavior that must remain strange because of an external contract or platform limitation
- clarify test fixtures when the fixture shape is not self-evident

Remove or rewrite bad comments:
- comments that merely restate the next line of code
- stale TODOs, outdated warnings, misleading rationale, commented-out code, and apology comments
- docs that describe old behavior, old commands, old flags, old config, or removed files

Update user-facing docs, internal docs, examples, and changelogs only when the plan or repo rules require them. Keep docs close to the source of truth.

## Final Output

Keep the final report concise and evidence-based:

- what plan was implemented
- work route and work source used
- logical slices completed and commits created, if any
- how sub-agents were used, or why they were unavailable or disallowed
- tests and verification run
- Evidence Gate status, claim evidence summary, unresolved claim gaps, and whether final claims were narrowed to match proof
- slice-level peer review, review gate loops, security pass, cleanup, docs/comment sweep, and roast scope/status, grade, and cap reason
- adjunct assessment gate loop status for every selected gate, including gate name, run/skipped/unavailable/capped status, final grade or equivalent, cap reason, and unresolved findings
- unresolved findings or release blockers
- whether the final state is releasable

Use `templates/CRUCIBLE.md` as the final report skeleton.

If the work cannot reach release-ready state, say what blocks it and what exact next step would unblock it.
