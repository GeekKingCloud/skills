---
name: crucible
description: Orchestrate iterative, role-guided, sub-agent-heavy work on software, documents, contracts, plans, workflows, policies, designs, images, or other directed targets from a supplied work source or whole-target Roast queue through create-review-verify-repair loops, Evidence Gate checks, remediation, risk review, cleanup, and readiness reporting. Use for development and release hardening or any substantial work that should converge through independent critique and evidence; requires explicit sub-agent approval or explicit degraded local-only confirmation before proceeding.
---

# Crucible

## Overview

Use this skill to turn a supplied work source or whole-target Roast queue into finished, evidence-backed work through nested create-review-verify-repair loops. Software development and release hardening remain the most fully specified mode, but the target may also be a document, contract, plan, workflow, policy, design, image, or other artifact. Treat the work source, target instructions, verification evidence, and review findings as hard inputs, not vibes.

The target state is:
- the selected work source is completed or remediated
- meaningful target-appropriate checks pass
- a running Evidence Gate ledger maps material outcome, behavior, content, quality, compatibility, safety, delivery, remediation, and final-report claims to current-run evidence
- peer review and selected Roast gate findings are resolved or explicitly accepted, or Roast was validly omitted with reduced-confidence disclosure
- relevant adjunct gate findings are resolved through the same Gate Remediation Loop as the Roast gate, or explicitly accepted
- no orphaned, stale, contradictory, placeholder, or abandoned material remains from the work
- code comments, annotations, rationale, and supporting material explain non-obvious decisions without narrating the obvious
- unresolved issues are Low or nitpick-level only, and no run gate has unresolved Critical, High, or Medium findings unless the caller explicitly accepts the readiness risk
- the final state is ready to release, merge, publish, deliver, submit for approval, execute, adopt, or hand off with clear evidence

## Startup Permission

Before starting route selection, target exploration, creation, implementation, or review work, check whether sub-agents are already approved by the environment or explicitly granted by the caller's Crucible invocation. If not, stop immediately and ask: "Crucible gets best results with sub-agents for independent research, peer review, validation, risk checks, cleanup, and regression or contradiction hunting. May I use sub-agents where useful for this run?"

Do not continue Crucible work while that question is unanswered. If permission is declined or sub-agents are unavailable, stop and ask whether the caller wants to abort, switch to a narrower non-Crucible local workflow, or continue Crucible in explicitly degraded local-only mode. Do not proceed in degraded local-only mode unless the caller explicitly confirms that tradeoff after being told independent review coverage is reduced. In degraded local-only mode, role-shaped self-checks may guide the work but do not count as independent review or maker/verifier separation. Reproducible direct current-run evidence may still verify an appropriately narrow claim, but it does not establish independent Verifier coverage. Report that limitation and block or cap only claims whose confidence materially depends on missing independent judgment, according to Evidence Gate severity and any explicit risk acceptance. Do not repeat the sub-agent question per slice; the startup answer covers bounded Crucible delegation for the run.

## Role-Guided Collaboration

Use roles to create distinct reasoning surfaces, not decorative titles or unlimited debate. For meaningful work, read and apply the three core role contracts:

- `roles/STEWARD.md`: preserve intent, proportionality, scope, and decision ownership. The main orchestrator normally holds this role.
- `roles/CHALLENGER.md`: attempt to falsify the current plan, artifact, or decision and identify consequential failure modes.
- `roles/VERIFIER.md`: independently test material claims against current evidence. The maker cannot supply the independent Verifier pass for its own material claims or artifacts.

Use separate Challenger and Verifier passes across each meaningful run and for every risk-bearing slice. Roles supplement the Execution Loop, Roast, Evidence Gate, risk/security, and readiness judgment; they never replace those gates. Challenger and Roast remain separate passes and outputs even when the same sub-agent performs them sequentially.

Give every delegated role a bounded charter containing: role and core question; exact artifact or slice; authoritative context and allowed evidence; protected value or failure modes; expected output; non-goals and ownership boundary; current artifact revision, hash, or equivalent identifier; and closure or escalation condition. Let roles form independent first-pass conclusions before sharing other agents' conclusions.

Record only material disagreements. Allow one targeted rebuttal round per material conflict, then resolve it through evidence or, for preference, authority, scope, or risk-acceptance questions, an explicit owner decision. An owner decision may accept a factual contradiction's readiness risk but cannot convert it into verification; preserve the evidence verdict and blocking or cap effect. Define the role-deliberation rerun budget and closure condition at startup; it never limits required gate remediation. Reopen settled debate only when a change intersects the settled question or its evidence, new actionable above-Low evidence appears, or a required gate remains unresolved.

Read `roles/OPTIONAL.md` only when the target needs a perspective not covered by the core roles. Select an optional role only for a distinct question or protected value; do not add roles merely to increase agent count.

## Target Adaptation

Keep the loop invariant while adapting its evidence and vocabulary to the target:

| Concept | Software and release work | Other directed targets |
| --- | --- | --- |
| Slice | Code, test, config, package, or docs change | Document revision, redline group, design iteration, plan section, workflow change, or other coherent artifact increment |
| Verification | Tests, builds, linters, smoke checks, runtime behavior | Requirement trace, factual/source check, calculation, render or visual inspection, scenario walkthrough, consistency check, acceptance review, or comparison |
| Risk pass | Application, dependency, data, permission, and operational security | Applicable safety, privacy, legal, financial, accessibility, reputational, contractual, or operational exposure |
| Cleanup | Dead code, stale docs, unused fixtures, generated debris | Stale sections, unresolved placeholders, duplicated content, stray markup, abandoned variants, inconsistent labels, or obsolete support material |
| Ready state | Releasable or mergeable | Publishable, deliverable, ready for owner or qualified review, executable, adoptable, or handoff-ready |

Do not force software-only checks or release language onto another target. Do not weaken software mode: when the target is code or a release, run the full engineering, test, security, cleanup, docs/comment, and release-readiness path.

Crucible is an execution workflow. If the caller requests report-only review, do not mutate the target; use Roast or another review workflow as requested and treat its findings as a possible future Crucible work source.

Before route selection, state the run contract:

- `Target and scope`: the authoritative source artifact and the exact surface allowed to change.
- `Work source`: the supplied instructions or whole-target Roast queue that defines the work.
- `Intended ready state`: release, merge, publish, deliver, submit for owner or qualified approval, execute, adopt, or hand off.
- `Success criteria`: the observable result and quality bar that end the loop.
- `Evidence mode`: source, rendered or live behavior, artifact comparison, external references, or a combination.
- `Action boundary`: what may be edited, redlined, exported, saved, committed, sent, published, signed, approved, deployed, or otherwise mutated.

Preserve originals when redlining or transforming contracts, images, designs, documents, binary files, or rendered outputs unless replacement is explicitly authorized. Identify which artifact is authoritative. Crucible permission to edit never implies permission to send, publish, sign, approve, deploy, accept obligations, or replace an original.

## Start And Work Route

1. Read the nearest `AGENTS.md` first. If it points to `STYLE.md`, `README.md`, handoff files, plans, or project docs, read the relevant files before editing.
2. Identify the work source and route before editing. Crucible always needs one of: a supplied work source, or a whole-target Roast-led work queue. A supplied work source may be a plan, brief, caller request, specification, issue, feedback set, redline instruction, acceptance criteria, handoff, TODO list, existing findings, or other source that defines the target, desired outcome, boundaries, and success checks. The caller's request itself is sufficient when it supplies those essentials.
3. Choose exactly one starting route:
   - `work-led-no-roast`: complete a supplied work source and run the non-Roast gates.
   - `work-led-scope-roast`: complete a supplied work source, then roast only the changed or created scope.
   - `work-led-whole-target-roast`: complete a supplied work source, then roast the whole current target.
   - `roast-led-whole-target`: roast the whole current target, use findings as the work queue, then remediate through the Gate Remediation Loop.
4. Check version-control or saved-artifact status before editing. Identify unrelated local changes, revisions, variants, or working files and preserve them.
5. Define the acceptance gates: completion or remediation outcome, target-appropriate verification, peer review, running Evidence Gate ledger, final Evidence Gate sweep status, evidence-ledger summary, unresolved claim gaps, Roast gate scope, Roast gate status, Roast gate grade, Roast gate cap reason, adjunct assessment gates, risk and security pass, cleanup, readability and supporting-material sweep, and commit, save, delivery, or handoff expectations.

If no supplied work source exists and the caller did not authorize a whole-target Roast-led work queue, stop and ask for the missing work source. Stop and ask only when the work source lacks a decision that would materially change the result, requires destructive history or artifact changes, needs credentials or professional authority, or would materially change security posture, runtime behavior, obligations, dependency surface, publication state, or public behavior without clear caller approval.

## Sub-Agent Operating Model

Follow the startup permission rule before using this operating model.

For meaningful Crucible work, treat sub-agents as the default way to improve coverage when the environment supports them and delegation is allowed. Assign the core or optional role whose question matches the work rather than asking for generic review. At each stage, actively look for independent work to delegate: source or context research, target inspection, alternative approaches, isolated slices, in-the-moment peer review, adversarial or stakeholder lenses, regression or contradiction hunting, verification review, risk and security review, readability sweeps, cleanup checks, and gate-remediation follow-up.

Keep delegated tasks bounded, parallel, and source-grounded. Give each sub-agent a clear scope, expected output, and ownership boundary. Keep blocking decisions, final integration, and readiness judgment in the main thread, and verify sub-agent findings against the target and authoritative context before acting. Do not average subjective opinions; resolve them against the work source, audience, evidence, and selected quality bar.

Delegate sensitive contracts, policies, private images, credentials, personal data, or confidential material only within the caller-approved access boundary and with the minimum context needed for the assigned task.

## Execution Loop

Work in logically connected slices. For each slice:

1. State the slice goal and verification target.
2. Decide what can be delegated before editing. Select the core and any justified optional roles, write bounded charters, bind each review to the current artifact revision, and define closure. Use sub-agents by default for independent work such as source inspection, alternative generation, isolated creation or revision, risk review, verification review, contradiction search, or patch/artifact review. If sub-agents become unavailable or delegation is no longer allowed after startup approval, pause the Crucible run and ask whether to abort, wait for availability, or continue in explicitly degraded local-only mode.
3. Across each meaningful run, and for every risk-bearing slice, use distinct Challenger and Verifier passes when available. Let Challenger test the bounded plan or artifact question before convergence; let a Verifier who did not make the material claim or artifact check the completed current revision. Do not repeat both passes for trivial slices that do not change their reviewed claims. Preserve independent first passes and bounded disagreement resolution.
4. Create, implement, revise, or remediate the slice with the smallest coherent change that satisfies the work source and target instructions.
5. Add or update focused tests for software behavior and other durable checks when the slice changes an important claim, fixes a defect, touches a shared contract, or guards a regression.
6. Run the narrowest meaningful verification. Broaden verification as risk or shared surface increases.
7. Update the Evidence Gate ledger for the slice: record the claim, evidence, verdict, severity, pre-artifact challenges, and any next check or fix needed before the slice can be treated as complete.
8. Ask the Verifier and other reviewers to check the completed current revision for correctness, contradictions, regressions, missing verification, security or other material risks, stale material, orphaned content, usability, clarity, and maintainability. Record their verdicts and findings in the Evidence Gate ledger, remediate them critically against the target and authoritative context, rerun every affected check, and update the ledger after each change.
9. Review the slice for dead, stale, duplicated, orphaned, contradictory, placeholder, or unnecessary material introduced or exposed by the change.
10. Commit a version-controlled slice when local commits are authorized by the caller or target workflow; otherwise save or version the artifact as authorized. Treat an explicit Crucible request as authorization for local logical commits unless the caller or target instructions say otherwise. Do not push, force-push, rewrite history, publish, send, sign, approve, or release anything without explicit approval.

If verification fails, fix the cause and rerun the relevant check. Do not weaken tests, criteria, rubrics, or evidence merely to pass; align the target and checks with the intended outcome.

## Roast Review Gate

Use the sibling `roast` skill as Crucible's default broad-quality gate and as the only no-work-source path. Select Roast lenses that match the target; use the full engineering lens for software. This is a managed skill dependency, not a bundle advertisement: report whether `roast` ran, was omitted for a valid route reason, or was replaced by fallback review, but do not present Crucible as promoting a required combo of skills. Roast is central to Crucible's convergence and release-hardening identity, but work-led runs may explicitly choose no Roast.

Read `helpers/ROAST-GATE.md` when choosing Roast scope, running Roast, using Roast as the work queue, falling back because `roast` is unavailable, or explaining why a work-led route has no Roast. Keep the detailed route and scope rules in that helper.

## Evidence Gate

Use `helpers/EVIDENCE-GATE.md` as Crucible's default proof-boundary mechanism for every run. Maintain it as a running internal ledger throughout every creation or implementation slice, assessment remediation, Roast remediation, risk or security fix, cleanup fix, and readability/supporting-material change. Run a final Evidence Gate sweep only after selected assessment gates, Roast, risk/security, cleanup, and readability/supporting-material passes are stable.

The Evidence Gate verifies that material outcome, behavior, content, quality, compatibility, safety, publication, delivery, cleanup, remediation, and final-report claims are supported by current-run evidence. It is not a duplicate Roast or a standalone report: unresolved actionable evidence gaps become work items for the Crucible Execution Loop. Narrow unsupported claims, add missing verification, or fix contradicted behavior before claiming a slice, gate finding, or final target is complete.

## Gate Remediation Loop

Use the same outer loop for every gate that runs, whether it is the default Evidence Gate, default Roast gate, an adjunct assessment gate, or an evidence-backed fallback pass:

1. Run the skill or equivalent fallback pass against the current changed state.
2. Capture the grade, severity list, evidence, and scope limitations.
3. Classify every finding as `actionable in scope`, `external or owner-blocked`, `unverifiable with current access`, or `explicitly accepted`.
4. Fix each actionable Critical, High, and Medium finding through the Execution Loop. Fix Low or nitpick findings when they are cheap, clarifying, or readiness-confidence-building.
5. For external, owner-blocked, or unverifiable findings, document the evidence, why Crucible cannot resolve or verify it with current access, who or what would unblock it, and whether it caps the grade.
6. Rerun the same skill, a focused rerun, or the closest equivalent verification against the changed state.
7. Repeat until the gate produces an A grade or equivalent high result and no unresolved actionable finding remains above Low or nitpick level.

Do not keep rerunning a gate solely because its grade is capped by documented external, owner-blocked, or unverifiable conditions. After actionable fixes are exhausted, treat the gate as `capped` rather than failed when the remaining above-Low findings are outside Crucible's current ability to change or verify. Report the cap clearly with evidence, owner or unblocker, and next step.

Do not loop indefinitely on defensible subjective disagreement. When competing directions depend on taste, brand, policy, risk acceptance, stakeholder preference, or a professionally governed decision that the work source does not resolve, surface the alternatives and evidence, then ask for the owner decision or classify the gate as owner-blocked.

If a skill does not produce a letter grade, treat the gate as passing only when its rerun has no unresolved actionable Critical, High, or Medium findings and the remaining Low, nitpick, external, owner-blocked, or unverifiable findings are documented. Do not claim readiness while any run gate still has unresolved actionable Critical, High, or Medium findings unless the caller explicitly accepts that risk in the final report.

Do not use `external`, `owner-blocked`, or `unverifiable` as an escape hatch for findings that can be fixed or verified within the authorized target and current access. When in doubt, attempt the narrowest reasonable fix or verification once, then classify the remaining cap from evidence.

Run gate remediation loops sequentially when later fixes can invalidate earlier evidence. For work-led hardening, finish the initial creation or implementation loop while maintaining the Evidence Gate ledger. Run selected adjunct assessment gates in the concrete order documented by `helpers/ASSESSMENT-GATES.md`, converting their actionable findings into Execution Loop slices and updating the evidence ledger after each fix. Run the Roast gate after assessment fixes so Roast reviews the final assessed state, again treating actionable findings as Execution Loop slices with evidence-ledger updates. Then run risk and security, cleanup, and readability/supporting-material passes. If those later passes materially change the Roast-reviewed target, rerun a focused or whole-target Roast against the changed surface and remediate it before the final Evidence Gate sweep. After all mutating passes and any required Roast rerun are stable, run the final Evidence Gate sweep against the completed state and final readiness claims. Parallelize independent investigation inside a loop when it will not create conflicting edits, but integrate changes through the main Execution Loop.

## Adjunct Assessment Gates

Use adjunct assessment gates only when the work source or changed target has a relevant surface, the caller asks Crucible to pair with an assessment skill, or a concrete requirement or scan is needed for readiness confidence. They are not hard dependencies for every Crucible run.

When the caller asks for an assessment skill or scan, or the changed surface clearly makes one relevant, read `helpers/ASSESSMENT-GATES.md` and follow its selection, trigger, skip, fallback, capped-grade, and final-report rules. Named assessment skills such as accessibility, agent-readiness, SEO, performance, security, compliance, package, or platform checks are examples, not mandatory fixed gates. If no assessment gate is relevant, do not read the helper; report adjunct gates as skipped only when that status matters to the final readiness explanation.

## Risk And Security Pass

Run a dedicated risk and security pass after gate remediation loops are complete and before cleanup. Scale it to the target: keep the full security pass for software, data, automation, or operational surfaces, and select applicable safety, privacy, legal, financial, accessibility, reputational, contractual, or execution risks for other targets. Mark irrelevant lenses `N/A`; do not invent risk findings to fill a category.

Prefer a separate sub-agent for this pass when available, especially when the change touches inputs, permissions, storage, shell commands, dependencies, network boundaries, sensitive claims, obligations, user safety, or generated artifacts. Parallelize independent risk investigation and focused review when it will not create conflicting edits.

Inspect:
- purpose-level failure, dangerous ambiguity, unsupported claims, misleading presentation, missing ownership, irreversible decisions, and unsafe assumptions
- privacy, accessibility, contractual, compliance, financial, reputational, and operational exposure when relevant
- untrusted input reaching shell commands, SQL, paths, templates, HTML, eval-like APIs, redirects, URLs, dynamic imports, regexes, or deserializers
- authentication, authorization, tenant boundaries, sessions, tokens, and permission checks
- secrets in source, examples, configs, logs, CI, fixtures, generated output, and docs
- dependency changes, install hooks, lockfiles, network calls, CORS, CSRF, webhook validation, SSRF, open redirects, and unsafe defaults
- file operations, destructive commands, cleanup behavior, temp paths, and permissions

For legal, financial, compliance, medical, or other professionally governed conclusions, rely on supplied or verified authority and distinguish workflow review from professional approval or certification. Report `ready to sign` or an equivalent governed disposition only when the work source identifies the competent authority and current evidence contains that approval; otherwise report `ready for owner or qualified review`.

Patch confirmed issues through the Execution Loop rules. Rerun focused checks after patches. If a risk cannot be resolved inside scope, report it with severity, evidence, impact, and the safest next action.

## Cleanup Gate

Run cleanup after risk and security fixes are stable and before the readability/supporting-material sweep. Parallelize independent cleanup checks and small cleanup patches when they do not conflict.

Before final response or handoff:

1. Recheck version-control or saved-artifact status.
2. Confirm there are no new orphaned files or variants, unused helpers, stale sections or fixtures, obsolete comments, outdated support material, dead imports, unresolved placeholders, stray markup, or accidental generated artifacts.
3. Confirm local commits were created for each logical slice when commits were authorized. If commits were not authorized, summarize commit-ready groups.
4. Confirm verification commands and results.
5. Confirm slice-level sub-agent reviews were integrated, or explain why review was performed locally.
6. Confirm unresolved risks are Low or nitpick-level only, or explain why readiness is blocked.

## Readability And Supporting Material

Do a focused readability sweep after gate remediation loops, the final risk and security pass, and cleanup are stable. Review the target plus its comments, annotations, rationale, instructions, labels, examples, citations, and supporting material as applicable. Parallelize independent reviews and updates when they do not conflict, then reconcile the final wording and presentation locally.

Keep good comments:
- explain tricky algorithms, unusual constraints, compatibility requirements, security decisions, and non-obvious failure handling
- document strange behavior that must remain strange because of an external contract or platform limitation
- clarify test fixtures when the fixture shape is not self-evident

Remove or rewrite bad comments:
- comments that merely restate the next line of code
- stale TODOs, outdated warnings, misleading rationale, commented-out code, and apology comments
- docs that describe old behavior, old commands, old flags, old config, or removed files

For non-code targets, also remove stale headings, repeated passages, unexplained jargon, contradictory labels, hidden assumptions, unresolved redlines, and layout or presentation residue. Update supporting material only when the work source or target rules require it. Keep it close to the source of truth.

## Final Output

Keep the final report concise and evidence-based:

- what work source was completed
- work route and work source used
- logical slices completed and commits created, if any
- how sub-agents and roles were used, including artifact revisions, maker/verifier independence, and material disagreement outcomes, or why they were unavailable or disallowed
- target-appropriate tests, checks, comparisons, renders, walkthroughs, or other verification run
- Evidence Gate ledger summary, final sweep status, unresolved claim gaps, and whether final claims were narrowed to match proof
- slice-level peer review, gate remediation loops, risk and security pass, cleanup, readability/supporting-material sweep, and Roast gate scope, status, grade, and cap reason
- Gate Remediation Loop status for every selected adjunct assessment gate, including gate name, run/skipped/unavailable/capped status, final grade or equivalent, cap reason, and unresolved findings
- unresolved findings or readiness blockers
- whether the final state is ready to release, merge, publish, deliver, submit for approval, execute, adopt, or hand off

Use `templates/CRUCIBLE.md` as the final report skeleton.

If the work cannot reach its intended ready state, say what blocks it and what exact next step would unblock it.

An A-grade Roast or passing Crucible run does not by itself establish legal approval, regulatory compliance, accessibility certification, security certification, stakeholder acceptance, or permission to publish, sign, send, deploy, or release.
