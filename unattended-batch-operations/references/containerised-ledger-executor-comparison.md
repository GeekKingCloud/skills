# Containerised Ledger/Executor Comparison Pattern

Use this reference when deciding whether to route a long checkpointed programme through a durable worker queue or through a lightweight ticket ledger plus a supervised shell-agent loop.

## Compare execution patterns, not databases

A ticket ledger does not execute or recover agents. The meaningful comparison is:

- **queue pattern:** ledger + dispatcher + worker claiming + retry/circuit-breaker policy;
- **supervised-ledger pattern:** lightweight ticket state + an explicit supervisor that inspects checkpoints, classifies exits, relaunches agents, and records attempts.

Do not credit a spreadsheet or another passive ledger with recovery performed by custom supervisor code. Conversely, do not call a worker queue worthless because one retry policy was undersized.

## Controlled recovery fixture

Build a synthetic workload with these properties:

1. deterministic units and a known final digest;
2. atomic checkpoint after every unit;
3. duplicate execution rejected or recorded;
4. process/run identity recorded with every checkpoint;
5. deterministic termination of the owning agent process after a chosen number of completed units;
6. enough units to require multiple fresh agent processes;
7. an acceptance file independent of either ledger.

Give each pattern the same model, provider, workload bytes, resource envelope, fault boundaries, and acceptance condition. Isolate credentials and mount only synthetic work plus the minimum runtime state.

For a detached queue worker, killing the process may leave its card running until dispatcher maintenance. In an isolated fixture, exercise the real maintenance path; distinguish missing maintenance from recovery latency.

## Metrics

Record at least:

- terminal status and completed units;
- number of agent processes/attempts;
- induced failures recovered;
- duplicate units or repeated accepted work;
- final digest;
- operator interventions outside the declared supervisor;
- elapsed time;
- session/API/tool-call counts when available;
- inspectability of attempt history and checkpoint identity.

Token and timing comparisons are valid only when worker context and enabled tools are equivalent. A kanban worker with its normal board contract and full tools is not an efficiency control against a direct CLI agent restricted to one tool and told to ignore repository/user rules. Report such usage as directional, not causal.

## Interpreting retry limits

Empirically verify retry semantics rather than inferring them from flag names. Record the implementation version and whether the allowance counts retries or total runs. Choose limits within the global budget; do not automatically retry integrity, permission, policy, source-authority, or human-decision blockers.

## Ledger defects exposed by the comparison

A harness workaround cannot establish that the real ledger is dependable. If a complex quoted multiline ticket fails while a simple description succeeds, inspect serialization through shell variables and delimited formats. Preserve complete documents through file-backed transactions and verify exact body preservation, destination state, source removal, lock release, and cleanup against the repaired candidate before using the result as architectural evidence. Keep trial logs and project-specific findings private.

## Decision rule

One successful controlled recovery trial supports routing guidance, not universal replacement:

- prefer a supervised lightweight ledger for one accountable assistant operating a long stateful programme;
- prefer kanban when independent profile claims, queue ownership, role lanes, cancellation, dependencies, or built-in retry semantics are genuinely needed;
- require an active supervisor in either pattern;
- run additional scenarios—container restart, transient command failure, permanent blocker, dependency release, and duplicate dispatch—before making fleet-wide hard-replacement claims.
