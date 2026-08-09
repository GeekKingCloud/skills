# Proportionality Contract

Read this helper before route selection and use it for every gate finding, remediation decision, scope-drift checkpoint, and final readiness judgment.

The purpose is to preserve strict review without turning every valid criticism into an immediate implementation requirement. A finding remains true when it is deferred or accepted; disposition decides what the current milestone requires.

## Startup Contract

Record:

- `Current milestone`: what becomes true after this run, and nothing more.
- `Assurance posture`: `exploratory`, `development`, `production-candidate`, or `live-critical`, selected from the current lifecycle state rather than eventual ambition.
- `Present exposure`: current users, data, systems, obligations, and blast radius.
- `Recoverability`: how safely and cheaply the current state can be undone, recreated, or corrected.
- `Current required invariants`: acceptance criteria and credible failures that this milestone must prevent.
- `Deferred lifecycle gates`: production, migration, scale, observability, certification, or other requirements owned by later milestones.
- `Complexity boundary`: acceptable new mechanisms, dependencies, operational duties, and maintenance burden.
- `Blocker policy`: the defaults below plus any stricter caller or target requirement.
- `Reframe trigger`: the default triggers below plus any caller-defined limit.

Use the posture labels as shorthand, not as substitutes for evidence:

- `Exploratory`: disposable or local work; block safety, authority, scope, and experiment-invalidating failures.
- `Development`: recoverable internal work not serving users; block applicable Critical and High findings, and Medium findings that violate a current acceptance criterion or required invariant.
- `Production-candidate`: realistic release, migration, or deployment candidate; resolve applicable Critical and High findings, and normally resolve or explicitly disposition relevant Medium findings.
- `Live-critical`: live or irreversible work involving material security, money, safety, regulated data, destructive operations, or equivalent exposure; use maximum assurance and treat unresolved relevant Medium findings as blockers unless the caller explicitly accepts the risk.

## Finding Classification

Classify each finding before remediation:

- `Target defect`: the current artifact fails a requirement or credible current use.
- `Evidence gap`: a claim is broader than the current proof.
- `Review-process invalidation`: the review did not inspect a stable or authoritative subject, or its evidence became stale.
- `Future hardening`: a credible later-lifecycle concern that does not apply to the current milestone.

Assign one current disposition:

- `block current milestone`
- `fix now if proportionate`
- `simplify or remove the parent control`
- `defer to named milestone`
- `explicitly accepted`
- `external or owner-blocked`
- `unverifiable with current access`
- `out of scope`

Record the finding, severity, classification, disposition, rationale, named later gate or owner when applicable, and whether it affects the current ready state. Do not lower severity merely to avoid remediation, and do not call an applicable defect future hardening without evidence.

Only the current caller or qualified decision owner may assign `explicitly accepted` when material risk remains. The orchestrator or reviewer may recommend acceptance but must preserve the owner decision boundary.

## Blocking Rules

- Applicable current-milestone Critical findings block.
- Applicable current-milestone High findings block by default.
- Medium findings block when they violate a current acceptance criterion or required invariant, create credible material harm in the present exposure, or the selected posture makes them blockers.
- Low and nitpick findings do not block unless they contradict an explicit exact requirement; fix them when cheap and useful.
- A review-process invalidation blocks use of that review verdict, not the artifact itself. Rerun the affected review against a stable subject.
- An evidence gap blocks the unsupported claim. Narrow or defer the claim when the milestone does not require it; change the artifact only when current required behavior is false.
- Accepted or deferred findings remain visible in the ledger and final report. Acceptance does not convert them into verification.

Security, authorization, privacy, destructive operations, data integrity, money, safety, regulated obligations, irreversible migrations, and live production behavior stay strict according to their actual current exposure. Recoverability can reduce disposition pressure, but it does not excuse silent corruption, unauthorized action, or dishonest readiness claims.

## Control-Cost Test

Before adding or materially expanding a control because of a gate finding, record:

1. the current required invariant it protects
2. one credible present-milestone failure it prevents
3. the simplest available correction, including removal, claim narrowing, manual recovery, or deferral
4. new states, failure modes, dependencies, and proof obligations introduced
5. operational ownership and maintenance cost
6. why net risk decreases after those costs

Do not add machinery merely to make a gate harder to falsify. Prefer removing an unnecessary parent control over adding another control to protect it. A remediation that exceeds the complexity boundary requires a Steward reframe before implementation.

## Steward Reframe

Run a Steward checkpoint when:

- two whole-gate revisions fail without materially reducing current-milestone risk
- remediation adds a subsystem, dependency, service, certification layer, automatic recovery mechanism, locking scheme, provenance system, monitoring system, or comparable operational obligation
- size, object count, configuration, or maintenance surface materially expands because of review remediation
- the same risk class reappears in a control added to address it
- work begins satisfying a deferred lifecycle gate instead of the current milestone
- the complexity boundary or caller's scope is about to be crossed

At the checkpoint, decide whether to continue, simplify, remove the parent control, narrow a claim, defer the finding, change the architecture, or ask for an owner decision. Ask the caller only when the decision changes scope, acceptance criteria, complexity budget, current-risk acceptance, or another authority boundary. Do not interrupt for every ordinary remediation loop.

## Stable Review Subjects

When exact artifact identity matters, review a commit, immutable saved revision, hash-addressed bundle, or equivalent frozen candidate. If the subject changes during review, mark the verdict `process invalidated`, preserve any still-useful findings as stale evidence, and rerun the narrowest affected review against the new stable candidate. Do not create a product change merely to repair review-path drift.

## Terminal Rule

The default terminal state is `fit for the stated milestone`: no unresolved current-milestone blocker, required claims supported or honestly narrowed, deferred hardening assigned to a named later gate, and accepted risk disclosed.

An A-grade or maximum-assurance convergence target applies only when the caller requests it or the assurance posture and current exposure justify it. Report the final Roast grade honestly even when a lower grade is sufficient for the stated milestone.
