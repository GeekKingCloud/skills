# Live-handle recovery after assistant interruption

Use this to reconcile an actual tool-call ceiling, context compaction, gateway restart, assistant crash, or other interruption that did **not** come from the owner. Recovery is conditional on unchanged authority, a valid checkpoint, single-writer ownership, and remaining global budget. It does not authorize a new service, watchdog, worker chain, or restart qualification. Owner stop/pause/report-only instructions always take precedence.

## Decision table

| Observed state                                      | Action                                                                                                                                    |
| --------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| Handle alive, state advancing                       | Reattach/observe and continue from the current gate. Do not relaunch.                                                                     |
| Handle alive, waiting for a supervisory probe/input | Send the already-authorized next probe/input immediately; then verify fresh state.                                                        |
| Handle alive, no progress, concrete stall evidence  | Preserve diagnostics, stop only the task-owned process tree, clean stale runtime state, and relaunch from the first missing durable gate. |
| Handle exited, durable checkpoint valid             | Resume only within unchanged authority and remaining global budget; verify the prior writer is gone before replacement.                   |
| Handle unknown                                      | Inspect the process/session registry, relevant endpoint/port, and durable ledger before claiming it stopped or continues.                 |
| Owner said stop/pause/report-only                   | Do not resume. Honor the latest owner direction.                                                                                          |

## Minimum inspection

Use the strongest available direct evidence:

- tracked background-process session and exit status;
- OS process table/process tree;
- service/job/run ID and current state;
- bound health/debug endpoint or application protocol;
- durable checkpoint and most recent completed gate;
- timestamped output or state mutation proving forward movement.

A process being alive proves only lifetime. It does not prove that the workflow is progressing. Conversely, an assistant turn ending does not prove that the process died.

Resolve the executor's actual working directory and output root from its launch record or task contract before looking for progress. An unchanged canonical directory does not establish a stall when the worker writes in an isolated worktree. Keep that worktree alive while any handed-off child still depends on it; before retiring it, preserve unique results into the canonical private root and verify the retained artifacts. A manifest is useful when the artifact contract needs one, not mandatory for every batch.

Reconcile each late stage independently: external draft creation, completion-report preparation, and email dispatch are separate states. A missing report while its owning writer is still active is pending, not proof of failed publication or failed delivery. After an interrupted send, inspect the established outbox/receipt and exact remote object before retrying; resume only the missing stage and retain its existing deduplication identity.

## Recovery acceptance

Recovery is successful only after a fresh observation shows one of:

- the awaited probe/input was accepted and application state changed;
- a new checkpoint or gate completed;
- a fresh heartbeat/output timestamp advanced;
- the relaunched executor is bound to the intended candidate/checkpoint and has begun the missing gate.

If the next action is authorized, unambiguous, and within the remaining global budget, resume rather than creating an avoidable status-only handoff. If the owner requested report-only or pause, or the budget is exhausted, preserve work and report the paused state without resuming.

## Pitfalls

- Killing a healthy reusable process merely because context was lost.
- Reporting “still running” from PID existence while the program is idle awaiting supervision.
- Treating infrastructure interruption as owner cancellation.
- Replaying already accepted work instead of continuing at the first missing gate.
- Claiming recovery from relaunch alone without fresh forward evidence.
