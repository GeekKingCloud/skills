---
name: crucible
description: Implement plans to release-ready state with tests, peer review, cleanup, security and docs/comment sweeps, and roast-gated remediation. Use when the caller asks to run a plan, harden for release, or loop fixes until Grade A or low-only findings.
---

# Crucible

## Overview

Use this skill to turn a plan into finished, releasable work. Treat the plan, repository instructions, verification evidence, and review findings as hard inputs, not vibes.

The target state is:
- the requested plan is implemented
- meaningful tests and checks pass
- peer review and roast findings are resolved or explicitly accepted
- no orphaned code, stale comments, stale docs, unused fixtures, or abandoned config remain from the work
- comments explain tricky or unusual code without narrating obvious code
- unresolved issues are low priority or lower
- the final state is ready to release, merge, or hand off with clear evidence

## Start

1. Read the nearest `AGENTS.md` first. If it points to `STYLE.md`, `README.md`, handoff files, plans, or project docs, read the relevant files before editing.
2. Find the plan. Look for explicit user text, `PLAN.md`, `ROAST_PLAN.md`, `HANDOFF.md`, issue text, TODO lists, or repo-specific planning files.
3. If no plan exists, derive a short implementation plan from the request and repository evidence before editing. Keep the plan scoped to the caller's requested outcome.
4. Check version-control status before editing. Identify unrelated local changes and work around them without reverting them.
5. Define the acceptance gates: implementation outcome, tests, review passes, security pass, docs/comment sweep, cleanup, and commit or handoff expectations.

Stop and ask only when the plan is missing critical product decisions, would require destructive Git history changes, needs credentials, or would materially change security posture, runtime behavior, dependency surface, or public behavior without clear caller approval.

## Execution Loop

Work in logically connected slices. For each slice:

1. State the slice goal and verification target.
2. Use sub-agents when the environment permits them and the current request authorizes agent delegation. Prefer independent, bounded tasks such as codebase search, risk review, test review, regression search, or patch review. Keep blocking implementation decisions in the main thread.
3. Implement the slice with the smallest change that satisfies the plan and repo instructions.
4. Add or update focused tests when the slice changes behavior, fixes a bug, touches shared contracts, or guards a regression.
5. Run the narrowest meaningful verification. Broaden verification as risk or shared surface increases.
6. Review the slice for dead code, stale helpers, orphaned files, stale comments, stale docs, and unnecessary dependencies introduced by the change.
7. Commit the slice when local commits are authorized by the caller or repo workflow. Treat an explicit Crucible request as authorization for local logical commits unless the caller or repo instructions say otherwise. Do not push, force-push, rewrite history, tag releases, or publish artifacts without explicit approval.

If verification fails, fix the cause and rerun the relevant check. Do not change tests merely to pass; align tests and implementation with the intended behavior.

## Peer Review

After meaningful implementation work, run an independent review pass before considering the work complete.

Use sub-agents for review when available and allowed. Give reviewers concrete scope:
- changed files and plan goals
- suspected risk areas
- tests that should prove the behavior
- repo instructions they must respect

Ask reviewers to look for correctness bugs, regressions, missing tests, security risks, stale comments/docs, orphaned code, and maintainability problems. Integrate findings critically; verify against source before changing code.

If sub-agents are not available, perform the same review manually and disclose that peer review was simulated locally.

## Security Pass

Run a dedicated security pass after implementation and before final cleanup.

Inspect:
- untrusted input reaching shell commands, SQL, paths, templates, HTML, eval-like APIs, redirects, URLs, dynamic imports, regexes, or deserializers
- authentication, authorization, tenant boundaries, sessions, tokens, and permission checks
- secrets in source, examples, configs, logs, CI, fixtures, generated output, and docs
- dependency changes, install hooks, lockfiles, network calls, CORS, CSRF, webhook validation, SSRF, open redirects, and unsafe defaults
- file operations, destructive commands, cleanup behavior, temp paths, and permissions

Patch confirmed security issues. If a security concern cannot be resolved inside scope, report it with severity, evidence, impact, and the safest next action.

## Comments And Docs

Do a focused readability sweep after code behavior is stable.

Keep good comments:
- explain tricky algorithms, unusual constraints, compatibility requirements, security decisions, and non-obvious failure handling
- document strange behavior that must remain strange because of an external contract or platform limitation
- clarify test fixtures when the fixture shape is not self-evident

Remove or rewrite bad comments:
- comments that merely restate the next line of code
- stale TODOs, outdated warnings, misleading rationale, commented-out code, and apology comments
- docs that describe old behavior, old commands, old flags, old config, or removed files

Update user-facing docs, internal docs, examples, and changelogs only when the plan or repo rules require them. Keep docs close to the source of truth.

## Roast Gate

Use the sibling `roast` skill near the end of the run, after implementation, normal verification, peer review, security review, and cleanup are complete enough to judge. If the `roast` skill is unavailable, perform an equivalent serious, evidence-backed roast-style review and disclose that the actual skill was unavailable.

Run the roast as a serious, evidence-backed release audit unless the caller explicitly asks for a snarkier presentation. Treat roast output as a hard quality gate:
- Fix Critical, High, and Medium findings.
- Fix Low findings when they are cheap, clarify real confusion, or affect release confidence.
- Rerun the relevant review or roast pass after fixes.
- Continue looping until the project earns an A grade or the remaining issues are low priority and explicitly documented as acceptable.

Do not claim an A-grade release state if tests did not run, the review was sampled, or major findings remain unresolved. State the limitation plainly.

## Cleanup Gate

Before final response or handoff:

1. Recheck version-control status.
2. Confirm there are no new orphaned files, unused helpers, stale fixtures, obsolete comments, outdated docs, dead imports, or accidental generated artifacts.
3. Confirm local commits were created for each logical slice when commits were authorized. If commits were not authorized, summarize commit-ready groups.
4. Confirm verification commands and results.
5. Confirm unresolved risks are low priority or lower, or explain why release readiness is blocked.

## Final Output

Keep the final report concise and evidence-based:

- what plan was implemented
- logical slices completed and commits created, if any
- tests and verification run
- peer review, security pass, docs/comment sweep, cleanup, and roast status
- unresolved findings or release blockers
- whether the final state is releasable

Use `templates/CRUCIBLE.md` as the final report skeleton.

If the work cannot reach release-ready state, say what blocks it and what exact next step would unblock it.
