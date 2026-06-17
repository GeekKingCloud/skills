# Evidence Gate

Read this helper for every Crucible run after implementation and focused verification, before adjunct assessment gates and roast.

Relationship type: default core gate.

The Evidence Gate verifies proof boundaries. It does not judge code style, architecture, or broad quality; that remains the roast gate's job. Its job is to compare claims against evidence and identify which release, behavior, compatibility, documentation, package, install, security, or workflow claims are actually proven.

## Evidence Inputs

Build the evidence map from current-run sources whenever possible:

- tests, builds, linters, format checks, type checks, package smoke tests, install smoke tests, CI results, manual commands, screenshots, logs, generated artifacts, docs checks, and review outputs
- changed source, configs, scripts, package metadata, docs, examples, templates, and release notes
- caller-provided acceptance criteria, issue text, handoff files, plans, and final-report claims

Do not treat old handoff notes, remembered results, previous CI runs, stale logs, or intended behavior as verified evidence unless the current run revalidates them or clearly labels them as reused and potentially stale.

## Claim Extraction

Extract claims that matter to release readiness, including:

- user-visible behavior and workflow claims
- public install, launch, packaging, platform, or compatibility claims
- API, CLI, MCP, automation, or integration claims
- security, permission, privacy, destructive-operation, credential, or data-handling claims
- documentation, example, changelog, migration, or release-note claims
- test, verification, CI, review, assessment, or cleanup claims made in the final report

Group duplicate claims by root behavior. Keep each claim concrete enough that a reader can tell what evidence would prove it.

## Verdicts

Assign one verdict to each material claim:

- `VERIFIED`: current-run evidence directly proves the claim.
- `PARTIALLY VERIFIED`: current-run evidence proves a narrower version of the claim, or only part of the supported environment.
- `NOT VERIFIED`: no current-run evidence proves the claim.
- `CONTRADICTED`: current-run evidence conflicts with the claim.
- `INCONCLUSIVE`: evidence was attempted but blocked, ambiguous, flaky, incomplete, or too indirect.
- `NOT APPLICABLE`: the claim does not apply to the selected work route or target surface.

For every verdict other than `VERIFIED` or `NOT APPLICABLE`, record the reason, release impact, and the smallest useful next check or fix.

## Severity And Blocking Rules

Classify unresolved evidence gaps by release risk:

- `Critical`: a claim could cause data loss, security exposure, credential leakage, destructive action, broken release artifact, or severe production outage if false.
- `High`: a public install, launch, packaging, compatibility, API, migration, deployment, or core workflow claim is unproven or contradicted.
- `Medium`: a meaningful user-facing behavior, docs, example, verification, or cleanup claim is unproven or only partially proven.
- `Low`: a narrow edge case, non-core environment, minor documentation claim, or convenience claim lacks direct proof.
- `Nitpick`: wording can be tightened without changing the release decision.

Unresolved `Critical`, `High`, and `Medium` Evidence Gate findings block release readiness unless the caller explicitly accepts the risk. Public release, package install, launcher, update, migration, platform, security, destructive-operation, and credential-handling claims block at any unresolved severity when they are advertised as supported.

Low and nitpick findings do not block release readiness when they are documented and do not make the final report overclaim.

## Remediation Loop

Use the Crucible Review Gate Loop for actionable evidence findings:

1. Replace unsupported claims with narrower, evidence-true language, or run the missing verification.
2. Fix implementation, docs, packaging, tests, or examples when the evidence shows the claim is false.
3. Rerun the narrowest check that can prove the updated claim.
4. Update the evidence map and final report after every fix.

Do not add broad claims just because a related narrow check passed. Do not mark a claim verified because a reviewer agreed with the design; reviewers are evidence for review coverage, not proof that behavior works.

## Reporting

Report the Evidence Gate as `run`, `capped`, or `blocked`.

Include:

- the evidence sources inspected
- a concise claim evidence summary
- every unresolved `Critical`, `High`, and `Medium` claim gap
- any Low or nitpick gaps that materially affect confidence
- capped conditions with evidence, unblocker, and exact next step
- whether final report language was narrowed to match the evidence

Use `capped` only when actionable checks have been exhausted and the remaining gap is external, owner-blocked, unavailable in the current environment, or intentionally accepted. Use `blocked` when an actionable above-Low evidence gap remains unresolved.
