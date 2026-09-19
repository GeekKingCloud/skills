# Sequential kanban pattern for overnight multi-item runs

Use this pattern only when several expensive items genuinely require independent kanban workers, profile-level claims or ownership transfer, queue-native cancellation/retry, or parallel worker lanes followed by dependency-gated integration. Do **not** choose it merely because the owner describes an ordered “kanban list.” For one accountable assistant supervising a sequential stateful programme, prefer `ledger-supervised-shell-programmes.md`.

When kanban is justified, use this pattern when items must run one after another, each benefits from a fresh independent agent context, and a final integration or delivery step depends on all item work.

## What this pattern provides

- A durable SQLite ledger and dependency chain.
- One fresh worker context per item, preventing a single conversation from accumulating every corpus and review.
- Strict item serialization while still allowing bounded helper waves *inside* the active item.
- Terminal-state notification for completion or blockers.

kanban durability is not worker-process isolation. Default dispatcher workers still run under the gateway lifecycle. Do not claim gateway-restart survival unless a separate task-owned host boundary has passed the acceptance matrix in `control-plane-worker-plane-dispatch.md`.

## Intake and admission gates

Before creating cards:

1. Resolve the exact item list, source identities, private/public boundaries, output form, package authority, delegation ceiling, external delivery authority, and final proof.
2. Write one self-contained contract to durable private state. Cards should point to that file plus their narrow stage; do not duplicate a long contract across mutable card bodies.
3. Preflight archive member names without extraction, expanded byte totals, source integrity, free space, memory/swap, and active heavyweight processes.
4. Set an explicit free-space reserve. Budget for extracted source, candidate, package, and readback copies; serialize and retire only clearly disposable copies between items.
5. Record protected prior work and unrelated repository state that must remain unchanged.

## Board shape

Create a dedicated board for the workstream and chain cards linearly:

```text
item 1 → item 2 → item 3 → cross-item review → one delivery/report card
```

Each item card owns only one input and must reach a truthful terminal state before its child becomes ready. Keep the cross-item review separate so reusable-tool changes are assessed against all completed evidence rather than improvised mid-translation. Keep external upload in the final card so no incomplete artifact is transferred.

Useful card settings:

- `--workspace dir:<governing-repo>` so nearest project guidance loads;
- `--goal --goal-max-turns <bounded-number>` for multi-turn completion;
- a per-card `--max-runtime` measured for that item;
- omit a per-task retry override or use a bounded value greater than one for large checkpointable cards, so a recoverable worker-lifetime stop can continue automatically;
- use `--max-retries 1` only for short or non-idempotent work where any unsuccessful attempt genuinely requires diagnosis before another run;
- idempotency keys for every card.

## Safe creation order

Do **not** rely on `--initial-status blocked` to hold a root card with no parents. The dispatcher may promote a parentless blocked card to `ready` during normal promotion. A safer setup sequence is:

1. create the root without an assignee, or otherwise ensure it is non-spawnable;
2. create every dependent card and verify parent links;
3. subscribe the owner channel to **every** card whose terminal failure could halt the chain—not only the final delivery card;
4. inspect `kanban list --json` and `kanban context <id>` for the root and final card;
5. assign/promote the root only after the contract, links, subscriptions, coordination notes, and admission checks are complete;
6. run `kanban dispatch --dry-run --max 1 --json`, then the real dispatch;
7. verify `kanban show <root>` and `kanban runs <root>` report `running`, a run ID, PID, and heartbeat before ending the intake turn.

If the gateway dispatcher may tick automatically, minimize the interval between making the root spawnable and completing the explicit dispatch verification.

## Worker contract

For each item worker:

- freshly hash the exact input against the durable contract;
- checkpoint existing workflow artifacts rather than inventing a shadow state machine;
- allow bounded disjoint helper work only within the current item and current authority;
- keep one canonical integrator;
- stop all item-owned helpers, validators, runtimes, and disposable copies before completing the card;
- write a concise, sanitized reusable-findings artifact separately from private title/client data;
- complete or block the card truthfully—never mark done merely to release the child.

## Supervisory recovery loop

A dependency chain does not self-heal merely because cards, checkpoints, and channel subscriptions exist. The programme owner must retain a bounded supervision mechanism until the final card terminates.

For each terminal event or watchdog tick:

1. Read `kanban list`, the active card's `show`, and its `runs`; verify the worker PID before deciding it stopped.
2. Classify the stop:
   - **resumable lifetime exhaustion:** iteration/context budget, stale claim, gateway/host restart, or worker disappearance after a durable checkpoint;
   - **substantive blocker:** corrupt source/checkpoint, failed acceptance criterion with no bounded repair, new authority boundary, unsafe external action, or ambiguous candidate state.
3. For a resumable stop, confirm the previous worker is dead, free-space/resource gates still pass, and checkpoint evidence names the first missing gate.
4. Add a recovery comment that explicitly preserves accepted stages, unblock the same card (or create a narrowly scoped continuation card when the original card is too large), and dispatch one worker.
5. Verify `running`, a new run ID/PID, and a fresh heartbeat. Do not report recovery based only on an unblocked or ready card.
6. Let the original dependency chain continue only after the recovered card completes truthfully.

Illustrative command shape for a checkpointed iteration-budget stop; `queue-cli` is a placeholder, not an installed command. Map these operations and options to the selected queue's documented interface:

```bash
queue-cli --board "$BOARD" show "$TASK"
queue-cli --board "$BOARD" runs "$TASK"
# Verify the old PID is gone and checkpoint/resource gates pass.
queue-cli --board "$BOARD" unblock "$TASK" --reason \
  "Resume from intact checkpoint at the first missing gate; do not redo accepted stages"
queue-cli --board "$BOARD" dispatch --dry-run --max 1 --json
queue-cli --board "$BOARD" dispatch --max 1 --json
queue-cli --board "$BOARD" show "$TASK"
queue-cli --board "$BOARD" runs "$TASK"
```

`--failure-limit` does not necessarily override a task-level `--max-retries`; inspect the card's reported effective limit. If one continuation could again exceed its worker budget, decompose final runtime, editorial review, packaging/readback, and evidence into dependency-linked continuation cards rather than relying on repeated manual unblocks.

Owner-facing terminal notifications are alerts, not an executor. A status request should trigger live inspection and already-authorized safe recovery before the reply, unless the owner requested report-only, stop, or pause.

## Final verification

Before calling the programme launched:

- the board and card IDs are saved outside chat;
- all parent links are visible;
- later cards are `todo`, not independently `ready`;
- the root is the only running heavyweight card;
- terminal subscriptions exist;
- source and prior protected artifacts remain unchanged;
- the owner-facing response names the active execution handle and does not imply work continues from a plan alone.
