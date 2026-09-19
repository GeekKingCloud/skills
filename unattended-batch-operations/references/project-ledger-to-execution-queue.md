# Bridging project ticket ledgers into a canonical execution queue

Use this pattern **only** when a separate global queue is already justified by independent profile claims, ownership transfer, queue-native retry/cancellation, or parallel execution lanes. It is not the default for one long stateful programme owned by one assistant; for that case, use `ledger-supervised-shell-programmes.md` and keep the project ledger lightweight.

Use the bridge when a planning/import tool creates project-local tickets but a separate global queue genuinely must own claims, retries, cancellation, worker lifetime, and owner-visible delivery.

## Ownership boundary

- The **project ticket ledger** owns ticket text, dependencies, project-local status/comments, and domain receipts.
- The **global execution queue** owns runnable tasks, claims, attempts, retries, runtime limits, cancellation, subscriptions, and terminal delivery.
- A planning/import tool may populate the project ledger; it is not automatically the runtime scheduler.
- Use one global queue task per project ticket. A parent card may summarize the programme but should not loop through execution tickets.

One task per ticket preserves fresh context, dependency gating, independent claims/retries/cancellation, bounded runtime, audit history, and delivery. A parent worker loop recreates a weaker scheduler, accumulates context, and makes one crash or retry revisit unrelated completed work.

## Stable identity

Do not map by source-import IDs or display/numeric ticket IDs unless the target ledger explicitly guarantees them as immutable global identities. Importers commonly treat incoming IDs as batch-local references and assign new local numbers.

Prefer the target ledger's immutable ticket UUID plus an opaque project/ledger identity. Persist:

- project/ledger identity;
- target ticket UUID;
- global task ID;
- source/spec digest and protocol version;
- dependency mapping;
- import/activation receipt.

Keep this mapping in private queue/controller state outside the project tree when writing it into the source repository would leak operational routing or create source churn.

## Quiescent import and activation

Serialize import/sync under a project-scoped lock. Import the entire graph as non-runnable first, resolve every dependency, validate missing/cyclic/self dependencies, then activate eligible roots in one transaction. Never expose partially imported roots as runnable while dependent tasks or edges are still absent.

A crash-safe import must resume from receipts rather than create duplicates. Duplicate execution events may race; dependency edge insertion and activation must be idempotent.

## Drift policy

- Before first claim, explicit resync may update task text/digest/dependencies while preserving identity.
- After execution starts, source/spec drift fails closed. Do not silently mutate the contract beneath an active or completed attempt.
- A worker rereads the exact target ticket by UUID and verifies the expected digest before substantive work.
- Task bodies should carry only opaque locator, digest, dependency information, protocol version, and worker contract—not private planning content copied unnecessarily into another database.

## Dual-ledger completion ordering

Do not mark both ledgers complete independently without an ordering/recovery protocol.

A safe default:

1. checkpoint artifacts and Definition-of-Done evidence;
2. write the project-ledger completion and durable receipt;
3. verify/read back that receipt;
4. mark the global queue task complete and allow dependents to promote.

If the worker crashes between steps 2 and 4, retry reconciles the receipt and performs only the missing queue transition. It must not rerun substantive side effects. If the project-ledger write or verification fails, keep the global task nonterminal/retryable or blocked; do not promote dependents.

## Minimum acceptance matrix

- import into a nonempty ledger proves source IDs differ from assigned numeric IDs but UUID mapping remains correct;
- repeated import/sync creates no duplicate global tasks or dependency edges;
- crash after graph creation but before activation resumes safely;
- no task is runnable before the full dependency graph validates;
- pre-start edit resyncs; post-start drift blocks;
- two concurrent bridge attempts serialize or converge idempotently;
- crash after project completion but before queue completion reconciles without rerunning work;
- queue retry/cancel does not corrupt project status;
- dependency promotion occurs only after verified dual-ledger completion;
- task bodies/events/logs do not leak ticket content beyond the declared boundary;
- one ticket runs in one fresh worker context; the optional programme parent never executes tickets itself.
