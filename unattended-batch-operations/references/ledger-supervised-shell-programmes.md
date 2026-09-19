# Ledger-supervised shell programmes

Consider this optional pattern when one assistant needs a ledger to supervise long sequential work. A finite inventory and progress file may be enough; do not introduce a product or worker per phase merely because this reference lists one. Task scope, privacy/content rules, owner approvals, stop/pause instructions, and one global time/effort/retry budget govern all dispatch and recovery. No independent review, runtime test, or infrastructure qualification is implied.

## Architecture

- **Owner-facing control plane:** accepts steering, reports milestones, and remains responsible for recovery.
- **Lightweight project ledger:** A local ticket ledger records ordered tasks, dependencies, comments, checkpoints, and terminal status.
- **Bounded shell workers:** fresh agent processes execute one coherent phase at a time under explicit resource/time limits.
- **Durable workspace:** accepted outputs and enough progress/evidence to resume are the source of truth between contexts; add manifests and hashes only where artifact identity or acceptance requires them.

The ledger does not own worker lifetime, retries, or supervision. The assistant does. Do not add a second global execution queue unless independent profiles truly need claims or ownership transfer.

## Phase design

Choose coherent chunks that reduce the remaining deliverable within the available context and budget. The following are possible phases, not required cards or mandatory gates:

1. intake and safe extraction;
2. inventory and analysis;
3. bounded processing batches;
4. holistic review and repair;
5. runtime/package verification;
6. delivery and readback.

After each phase, record:

- exact accepted artifact identity;
- completed gates and evidence paths;
- first missing gate;
- any safe-to-reuse worker outputs;
- whether authority or scope changed.

## Recovery loop

When a worker ends unexpectedly:

1. inspect the real process state; do not trust a stale status alone;
2. classify the stop as worker-lifetime exhaustion, substantive failure, authority blocker, or ambiguous/corrupt state;
3. for worker-lifetime exhaustion, verify the worker is gone and accepted checkpoints are intact;
4. comment the recovery decision in the ledger;
5. if authority remains unchanged and global budget remains, launch a bounded worker for the missing work; never reset retry allowances through a fresh identity;
6. verify a live PID/run handle and fresh progress signal;
7. continue productively within that budget; stop at completion, an owner pause, exhausted allowance, or a genuine blocker. A completion notification does not authorize an automatic successor chain.

Never restart completed batches merely because context ended. Never treat a notification, timeout card, or saved checkpoint as recovery by itself.

## Choosing against kanban

Prefer this pattern over a durable multi-agent kanban dispatcher when:

- one assistant owns the whole outcome;
- execution is sequential and stateful;
- the filesystem already carries strong checkpoints;
- fresh workers are interchangeable continuations rather than independent owners;
- queue-level claim transfer adds more failure states than value.

Choose kanban instead when separate profiles need independent claims, parallel lanes, ownership transfer, review roles, or queue-native cancellation/retry semantics.

## Incident-derived pitfalls

- A user saying “put these in your kanban list” may describe ordering rather than mandate a particular execution engine. Clarify architecture from the workload, not the noun.
- A small per-task retry limit may block a checkpointable programme; choose limits deliberately within the global allowance rather than automatically increasing them.
- Passive Channel/task notifications do not wake an accountable supervisor unless a real responder or watchdog is wired to act.
- Split a card when its actual context or time demand warrants it; consolidate tiny cards when setup, review, and handoff dominate useful progress. Do not add review or runtime phases absent a task requirement.
