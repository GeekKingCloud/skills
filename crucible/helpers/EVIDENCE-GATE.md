# Evidence Gate

Read this helper for every Crucible run. Maintain it as a running internal proof ledger throughout creation or implementation, gate remediation, risk and security review, cleanup, readability/supporting-material work, and final readiness review. Use `PROPORTIONALITY.md` to decide whether an evidence gap blocks the current milestone.

Relationship type: default core gate.

The Evidence Gate verifies proof boundaries. It does not judge broad quality; that remains the Roast gate's job through target-appropriate lenses. Its job is to compare claims against evidence, identify which outcome, behavior, content, quality, compatibility, safety, publication, delivery, remediation, and final-readiness claims are actually proven, and feed unresolved proof gaps back into the Crucible Execution Loop.

## Evidence Inputs

Build the evidence map from current-run sources whenever possible:

- tests, builds, linters, format checks, type checks, package or install smoke tests, CI results, manual commands, screenshots, renders, visual inspection, calculations, comparisons, scenario walkthroughs, requirement traces, source checks, logs, generated artifacts, consistency checks, and review outputs
- changed source, configs, scripts, package metadata, documents, contracts, plans, workflows, policies, designs, images, examples, templates, annotations, and supporting material
- caller-provided acceptance criteria, issue text, handoff files, plans, and final-report claims
- assessment, Roast, risk/security, cleanup, readability/supporting-material, and peer-review findings that become Crucible work items

Do not treat old handoff notes, remembered results, previous CI runs, stale logs, or intended behavior as verified evidence unless the current run revalidates them or clearly labels them as reused and potentially stale.

Bind delegated review and verification outputs to the exact artifact revision, hash, saved version, or equivalent identifier inspected. When a delayed or asynchronous output arrives, compare that bound subject and scope with the current target before treating its verdict as current. If an intersecting change makes the output stale, preserve it as historical evidence and reconcile each material finding against the current target as `still applicable`, `already remediated`, `misattributed or unsupported`, or `newly exposed`. Independently verify factual findings, and rerun the narrowest affected review or check when final gate status depends on it. Do not silently discard a stale output, transfer its grade to a newer target, or imply that it reviewed later changes. Reuse evidence across an unrelated change only when the non-intersection is recorded and demonstrable.

## Claim Extraction

Extract claims that matter to the intended ready state, including:

- purpose, audience, completion, quality, usability, and fitness-for-purpose claims
- user-visible behavior, content, presentation, and workflow claims
- public install, launch, packaging, platform, or compatibility claims
- API, CLI, MCP, automation, or integration claims
- security, permission, privacy, destructive-operation, credential, or data-handling claims
- factual, legal, financial, accessibility, compliance, contractual, operational, or other governed claims when relevant
- documentation, citation, definition, obligation, acceptance, example, changelog, migration, publication, delivery, or release-note claims
- remediation claims such as an assessment finding, Roast finding, risk or security issue, cleanup issue, or readability/supporting-material issue being fixed
- test, verification, CI, review, assessment, or cleanup claims made in the final report

Group duplicate claims by root behavior. Keep each claim concrete enough that a reader can tell what evidence would prove it.

## Working Evidence Ledger

Maintain an internal ledger while the Crucible run is in progress. The ledger is a work queue control surface, not just a final report.

For each material slice, gate finding, remediation, or final readiness claim, record:

- claim
- source of the claim, such as a work-source item, assessment finding, Roast finding, risk or security issue, cleanup item, target/supporting-material change, or final readiness statement
- evidence checked
- verdict
- severity
- classification and current disposition from `PROPORTIONALITY.md`
- disposition rationale, named later gate, owner, or unblocker when applicable
- next check or fix when unresolved
- rerun result after remediation
- final state: `closed`, `deferred`, `capped`, `accepted`, `process-invalidated`, `not-applicable`, or `blocked`

Do not stop at producing an evidence report. Treat current-milestone evidence blockers and selected proportionate checks as work items for the Crucible Execution Loop. A slice is not complete until its material claims are verified, narrowed to match evidence, dispositioned with evidence, or explicitly accepted by the caller.

## Verdicts

Assign one verdict to each material claim:

- `VERIFIED`: current-run evidence directly proves the claim.
- `PARTIALLY VERIFIED`: current-run evidence proves a narrower version of the claim, or only part of the supported environment.
- `NOT VERIFIED`: no current-run evidence proves the claim.
- `CONTRADICTED`: current-run evidence conflicts with the claim.
- `INCONCLUSIVE`: evidence was attempted but blocked, ambiguous, flaky, incomplete, or too indirect.
- `NOT APPLICABLE`: the claim does not apply to the selected work route or target surface.

For every verdict other than `VERIFIED` or `NOT APPLICABLE`, record the reason, readiness impact, and the smallest useful next check or fix.

## Severity And Blocking Rules

Classify unresolved evidence gaps by readiness risk:

- `Critical`: a claim could cause catastrophic harm, data loss, security exposure, credential leakage, destructive action, invalid binding commitment, broken release artifact, or severe operational failure if false.
- `High`: a core outcome, obligation, public behavior, install, launch, compatibility, API, migration, deployment, delivery, or workflow claim is unproven or contradicted.
- `Medium`: a meaningful user-facing behavior, content, design, documentation, example, verification, or cleanup claim is unproven or only partially proven.
- `Low`: a narrow edge case, non-core environment or audience, minor supporting claim, or convenience claim lacks direct proof.
- `Nitpick`: wording can be tightened without changing the readiness decision.

Applicable current-milestone Critical and High evidence gaps block readiness by default. Medium evidence gaps block when they leave a current acceptance criterion or required invariant unsupported, create credible material harm in the present exposure, or the assurance posture makes them blockers. An explicit support or completeness claim blocks only while the claimed current behavior remains materially unsupported; narrow or defer a non-required claim instead of adding product machinery merely to preserve it.

Low and nitpick findings do not block readiness when they are documented and do not make the final report overclaim. A review-process invalidation blocks reliance on the affected evidence, not the artifact; rerun the narrowest check against a stable current subject.

## Remediation Loop

Use the Crucible Gate Remediation Loop for current blockers and selected proportionate evidence findings:

1. Replace unsupported claims with narrower, evidence-true language, or run the missing verification.
2. Fix the target, supporting material, implementation, packaging, checks, or examples when the evidence shows the claim is false.
3. Rerun the narrowest check that can prove the updated claim.
4. Update the evidence ledger after every fix.

Do not add broad claims just because a related narrow check passed. Do not mark a claim verified because a role conclusion or reviewer agreement says it is correct; those are evidence for review coverage, not proof that behavior works. Reproducible current-run checks and inspectable artifacts may support a claim when their provenance, scope, and revision binding are sound, including in degraded local-only mode. Do not report the maker's self-check as independent Verifier coverage; assign the independent Verifier pass to someone who did not make the material claim or artifact.

## Final Sweep And Summary

After creation or implementation, selected adjunct assessment gates, Roast, risk and security, cleanup, and readability/supporting-material passes are stable, run a final Evidence Gate sweep against the completed state and final readiness claims.

Use the final sweep to:

- confirm the ledger has no unresolved current-milestone evidence blocker
- confirm public release, publication, delivery, obligation, package install, launcher, update, migration, platform, security, destructive-operation, and credential-handling claims are verified or explicitly accepted when relevant
- confirm final report wording is no broader than the evidence
- reopen the Execution Loop if a final claim is unsupported, contradicted, or too broad

Summarize the Evidence Gate as `run`, `capped`, or `blocked` only after the ledger has been used to drive remediation.

In the final Crucible report, include:

- the evidence sources inspected
- a concise evidence-ledger summary
- every unresolved `Critical`, `High`, and `Medium` claim gap
- any Low or nitpick gaps that materially affect confidence
- capped conditions with evidence, unblocker, and exact next step
- whether final report language was narrowed to match the evidence

Keep status `run` when every remaining gap is fully dispositioned and does not limit a current required claim. Use `capped` only when proportionate actionable checks have been exhausted and a deferred, external, owner-blocked, unavailable, or intentionally accepted gap still limits the grade, evidence, or readiness claim required by the current milestone. Use `blocked` when a current-milestone evidence blocker remains unresolved.
