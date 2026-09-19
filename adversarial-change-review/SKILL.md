---
name: adversarial-change-review
description: "Use for exact-commit and stateful safety reviews."
metadata:
  version: 1.2.0
---

# Adversarial Change Review

Ask **what could break for actual users under the declared operating and threat model?** Find consequential defects, support them with evidence, and disposition them without turning review into an expanding product or repeated approval loop.

## Set the boundary

Read the applicable repository guidance and owner request. Establish the change, deliberately unchanged behavior, real users, relevant risks, and required checks. A review supplies evidence, not permission to implement, publish, deploy, contact people, incur new costs, or widen scope. Preserve privacy, content restrictions, explicit approvals, and stop/pause instructions.

Use the candidate identity the task requires. For an exact-commit review, verify the supplied base/target objects and inspect those immutable bytes; never silently substitute a likely commit for a missing or malformed identifier. For an uncommitted candidate, capture the relevant staged, unstaged, and untracked content. A plain diff hash does not identify all three. Reproduce a supplied digest's literal serialization before judging a mismatch.

Do not alter a review-only candidate or reset, clean, stash, or overwrite others' work. When concurrent edits or mutating tests could affect attribution, use an isolated snapshot or disposable checkout. Keep test state, credentials, and outputs away from live application homes; inspect install-capable runners before invoking them. Access to a live host is not authorization for a live test.

## Review the consequential behavior

1. Read the changed behavior and enough callers, persistence, defaults, migrations, tests, and guidance to understand its effects. Follow a routed reference only when it owns a relevant risk or authority boundary.
2. Form concrete failure hypotheses. For stateful changes, consider identity collisions, stale or unknown state, retry after ambiguous side effects, ownership across asynchronous work, partial failure, bounded resources, and preservation of accepted work. Select the cases that can matter here, not every case in a catalog.
3. Run the checks required by the task/repository and the smallest useful counterexample probes within the granted budget. Distinguish a candidate defect from an inherited defect, unsupported environment, test-double assumption, or wrong artifact. Verify that the tested/imported bytes are the intended ones when that attribution matters.
4. Compare claimed policy with real behavior. Unknown is not zero, inactive, absent, or safe. A negative live-state claim needs live evidence; repository absence proves only a provisioning or reproducibility gap. Do not upgrade that gap into a host failure without an authorized readback.

Prioritize security and authority violations, data loss, incorrect results, broken supported paths, and operational failures over speculative completeness. Preserve existing useful safeguards; do not demand hostile-local race defenses or new frameworks when the operating model excludes that risk. Findings must trace to the agreed contract, not an attractive requirement invented by the reviewer.

## Guidance and verification proportionality

Classify the delta: executable behavior, machine-parsed policy, registration metadata, or agent-facing prose. Guidance-only work normally needs a semantic read for coherence, authority, contradictions, and scope, plus format/rendering checks where applicable. It does not automatically need model tests, a semantic parser, a person-facing-line allowlist, a mutation matrix, or a runtime drill.

Add a focused regression when a consequential, realistic failure is mechanically testable or a named gate requires it. For an existing prose evaluator, a deletion or direct-contradiction control may expose its limits; a finite vocabulary test is a sentinel, not proof of natural-language consistency. Do not expand the supported grammar merely to satisfy hypothetical paraphrases. Prefer agent judgment and a narrow mechanical invariant over encoding a second policy engine.

## Findings, disposition, and stopping

Report each material finding with severity, candidate/path/line, concrete failure and user impact, evidence or reproduction, and an actionable correction. Label hypotheses and untested risks plainly. Separate content findings from CI, authorization, stale-base, packaging, or deployment status. Follow a requested PASS-or-findings-only format without process narration.

Disposition findings as current defects, superseded observations, out-of-scope suggestions, or brief-induced scope conflicts. Repair only when authorized. After a repair, check the affected behavior and required dependent gates; preserve unrelated evidence whose inputs did not change. Exact-candidate approval remains bound to its original bytes and must not be relabeled as approval of a successor.

Stop when findings are dispositioned and the requested evidence/report is complete, or when the budget or a real blocker is reached. Do not automatically commission another independent review or rerun every gate after every edit. A fresh approval round is needed only when the owner/repository contract requires it or a material unresolved risk justifies it within the authorized budget. Report remaining uncertainty rather than growing the workflow.

## Situational technical references

The reference collection preserves focused technical probes. It is a menu, not a cumulative checklist: **every reference is subordinate to the current task, threat model, authority, and verification budget.** Instructions to run suites, add mutations, inspect hosts, or repeat review apply only to the selected in-scope claim. Existing named owner/repository gates still govern.

Useful entry points:

- `references/exact-commit-stateful-guardrail-review.md` — exact-artifact and stateful reproduction patterns.
- `references/repository-vs-live-host-review-evidence.md` — repository versus deployment claims.
- `references/continuation-and-observability-claims.md` — unknown state and truthful continuation.
- `references/policy-bundle-and-routed-guidance-closure.md` — coupled machine/prose authority surfaces.
- `references/semantic-guidance-contract-mutations.md` and `references/semantic-policy-negation-mutation-probes.md` — bounded probes of an existing evaluator, not a requirement to build one.
- `references/test-suite-live-state-isolation.md` and `references/python-import-identity-for-exact-artifacts.md` — isolation and artifact attribution when running tests.
- Other references remain available by their specific risk names. Load only the one needed; localization, release, fleet, or production-transaction examples do not impose those workflows on unrelated reviews.
