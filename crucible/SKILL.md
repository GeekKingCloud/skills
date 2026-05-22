---
name: crucible
description: Orchestrate release-hardening work from a plan, existing review findings, or current codebase state through sub-agent-heavy implementation, remediation, verification, review gates, security pass, docs/comment sweep, cleanup, and release-readiness reporting.
---

# Crucible

## Overview

Use this skill to turn a plan, review, or current codebase state into finished, releasable work. Treat the work source, repository instructions, verification evidence, and review findings as hard inputs, not vibes.

The target state is:
- the selected work source is implemented or remediated
- meaningful tests and checks pass
- peer review and default review-gate findings are resolved or explicitly accepted
- relevant optional gate findings are resolved, documented, or explicitly accepted
- no orphaned code, stale comments, stale docs, unused fixtures, or abandoned config remain from the work
- comments explain tricky or unusual code without narrating obvious code
- unresolved issues are low priority or lower
- the final state is ready to release, merge, or hand off with clear evidence

## Start And Work Route

1. Read the nearest `AGENTS.md` first. If it points to `STYLE.md`, `README.md`, handoff files, plans, or project docs, read the relevant files before editing.
2. Identify the work source and route before editing. Look for explicit user text, `PLAN.md`, `ROAST_PLAN.md`, `HANDOFF.md`, issue text, existing review findings, TODO lists, or repo-specific planning files.
3. Choose exactly one starting route:
   - `Plan-led`: implement a supplied plan, then harden the result.
   - `Review-led`: remediate existing roast, review, or audit findings as the work queue.
   - `Current-state hardening`: inspect the current codebase, derive a bounded hardening plan, and use roast when appropriate.
   - `Combined`: implement a supplied plan, then run roast on the changed result and remediate findings.
4. Check version-control status before editing. Identify unrelated local changes and work around them without reverting them.
5. Define the acceptance gates: implementation or remediation outcome, tests, peer review, roast review role, security pass, optional adjunct gates, docs/comment sweep, cleanup, and commit or handoff expectations.

If no work source exists and the caller asked for hardening, derive a bounded current-state hardening plan from repository evidence before editing. Stop and ask only when the work source is missing critical product decisions, would require destructive Git history changes, needs credentials, or would materially change security posture, runtime behavior, dependency surface, or public behavior without clear caller approval.

## Sub-Agent Operating Model

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

Use the sibling `roast` skill as Crucible's default broad code-quality review gate and as a possible work source. Roast is central to Crucible's release-hardening identity, but it is not required for every route.

Roast can play these roles:
- `Input`: existing roast or review findings define the work queue.
- `Post-change gate`: after plan-led or combined implementation, run roast on the changed result when release-hardening is in scope.
- `Current-state gate`: during current-state hardening, run roast to derive a bounded remediation queue when appropriate.
- `Fallback`: if the actual `roast` skill is unavailable, perform an equivalent serious, evidence-backed review and disclose the fallback.
- `Skipped`: skip only when the caller opts out, the task is narrow/non-release, an existing accepted review already covers the scope, or repo instructions make roast inappropriate.

Run roast as a serious, evidence-backed release audit unless the caller explicitly asks for a snarkier presentation. Treat roast output as a default core quality gate when it runs:
- Treat each post-change roast run as the outer loop: collect findings, fix them, rerun roast or the focused equivalent review, and repeat until the project earns an A grade or the remaining issues are low priority and explicitly documented as acceptable.
- Treat each finding as the inner loop: handle one issue at a time using the Execution Loop rules, including surgical scope, sub-agent delegation, focused tests, narrow verification, and cleanup.
- Do not batch unrelated roast findings into one broad refactor. Group findings only when they share the same root cause and can be fixed surgically.
- Fix Critical, High, and Medium findings. Fix Low findings when they are cheap, clarify real confusion, or affect release confidence.
- After each finding or root-cause group, rerun the relevant focused verification before moving to the next finding.

If roast is skipped or unavailable, report the role as `skipped` or `fallback` in the final output with the reason. Do not claim an A-grade release state if tests did not run, the review was sampled, roast or equivalent review was skipped without justification, or major findings remain unresolved. State the limitation plainly.

## Optional Gates

Use optional adjunct gates when the implemented plan has a relevant surface. Optional gates are not hard dependencies for every Crucible run, and they must be skipped with a short reason when irrelevant.

### Universal Accessibility Gate

Run the sibling `universal` skill when the plan or changed surface touches UI, frontend components, forms, public websites, generated documents, PDFs, emails, design systems, human-facing output, or user-facing workflows. Also run it when the caller explicitly asks for accessibility hardening.

Skip Universal for backend-only, infrastructure-only, internal refactor-only, test-only, or non-user-facing work unless the caller explicitly asks for it.

If the `universal` skill is unavailable but the target has an accessibility surface, perform a smaller evidence-backed accessibility pass and disclose that the actual skill was unavailable.

Treat Universal output as an accessibility release gate when it runs:
- Fix unresolved `Critical` and `High` Universal findings before release readiness, unless the caller explicitly accepts them.
- Fix `Medium` findings when practical inside scope; otherwise document them as follow-up.
- Fix `Low` findings when cheap, clarifying, or confidence-building.
- Do not require a Universal Grade A unless the caller explicitly asks for accessibility hardening to that level.

Report the Universal gate status in the final output as `run`, `skipped`, or `unavailable`. Include the skip reason, fallback note, Universal grade when produced, and any unresolved `Critical` or `High` accessibility blockers.

## Security Pass

Run a dedicated security pass after review-gate remediation is complete and before final cleanup.
Prefer a separate sub-agent for this pass when available, especially when the change touches inputs, permissions, storage, shell commands, dependencies, network boundaries, or generated artifacts.

Inspect:
- untrusted input reaching shell commands, SQL, paths, templates, HTML, eval-like APIs, redirects, URLs, dynamic imports, regexes, or deserializers
- authentication, authorization, tenant boundaries, sessions, tokens, and permission checks
- secrets in source, examples, configs, logs, CI, fixtures, generated output, and docs
- dependency changes, install hooks, lockfiles, network calls, CORS, CSRF, webhook validation, SSRF, open redirects, and unsafe defaults
- file operations, destructive commands, cleanup behavior, temp paths, and permissions

Patch confirmed security issues through the Execution Loop rules. If a security concern cannot be resolved inside scope, report it with severity, evidence, impact, and the safest next action.

## Comments And Docs

Do a focused readability sweep after review-gate remediation and the final security pass are stable.
For broad or user-facing changes, delegate a docs/comment sweep to a sub-agent and reconcile its findings locally.

Keep good comments:
- explain tricky algorithms, unusual constraints, compatibility requirements, security decisions, and non-obvious failure handling
- document strange behavior that must remain strange because of an external contract or platform limitation
- clarify test fixtures when the fixture shape is not self-evident

Remove or rewrite bad comments:
- comments that merely restate the next line of code
- stale TODOs, outdated warnings, misleading rationale, commented-out code, and apology comments
- docs that describe old behavior, old commands, old flags, old config, or removed files

Update user-facing docs, internal docs, examples, and changelogs only when the plan or repo rules require them. Keep docs close to the source of truth.

## Cleanup Gate

Before final response or handoff:

1. Recheck version-control status.
2. Confirm there are no new orphaned files, unused helpers, stale fixtures, obsolete comments, outdated docs, dead imports, or accidental generated artifacts.
3. Confirm local commits were created for each logical slice when commits were authorized. If commits were not authorized, summarize commit-ready groups.
4. Confirm verification commands and results.
5. Confirm slice-level sub-agent reviews were integrated, or explain why review was performed locally.
6. Confirm unresolved risks are low priority or lower, or explain why release readiness is blocked.

## Final Output

Keep the final report concise and evidence-based:

- what plan was implemented
- work route and work source used
- logical slices completed and commits created, if any
- how sub-agents were used, or why they were unavailable or disallowed
- tests and verification run
- slice-level peer review, security pass, docs/comment sweep, cleanup, and roast role/status
- optional gate status, including Universal run/skipped/unavailable when relevant
- unresolved findings or release blockers
- whether the final state is releasable

Use `templates/CRUCIBLE.md` as the final report skeleton.

If the work cannot reach release-ready state, say what blocks it and what exact next step would unblock it.
