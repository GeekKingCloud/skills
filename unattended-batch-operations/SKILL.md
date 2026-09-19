---
name: unattended-batch-operations
description: "Use for long multi-item unattended jobs. Front-load gates."
metadata:
  version: 1.1.0
---

# Unattended Batch Operations

Complete a finite batch with useful results, durable progress, and no avoidable routine approval interruptions. Front-load predictable decisions; continue within that authority; stop at completion, an owner pause, an exhausted budget, or a genuine blocker. Unattended does not mean unlimited or unsupervised.

## Agree the finite outcome

Use the owner request and governing project rules to establish:

- the input inventory and requested result, including exclusions and per-item exceptions;
- source authority, privacy/content limits, approved working and delivery locations;
- the output form and any packaging, transfer, or notification already authorized;
- one accountable owner, a single writer for shared accepted state, and an appropriate execution approach;
- a global time/effort/retry budget, acceptance evidence, and a useful terminal report.

Use established defaults and supplied answers. Ask one compact intake question only for missing decisions that materially affect safety, authority, cost, or the deliverable. Do not ask the owner to choose ordinary implementation details. Settle predictable conditional choices together; input containers do not automatically dictate output containers. Inspect only the shallow metadata needed before any required content-processing approval.

Record enough private durable state to identify the exact items and resume safely. A short inventory and progress file may suffice; no universal manifest, receipt schema, ledger product, service, or watchdog is required. Use hashes, source pointers, or richer provenance when ambiguous identity, destructive work, or an exact-candidate acceptance contract makes them necessary.

Batch approval covers the listed items and approved actions, not later additions, new recipients/providers, publication, materially different costs, or changed safety/content facts. User authorization does not bypass platform, credential, sandbox, payment, or permission controls. Do not assume authority to spend or delegate from a request to work unattended.

## Execute for useful progress

Choose coherent chunks that advance the remaining deliverable rather than maximizing stage or worker counts. Reuse accepted work. Checkpoint at useful item or phase boundaries with completed results, remaining scope, failures, and the next action; preserve unique outputs before retiring temporary worker storage.

Use one writer for accepted results and progress. If workers are authorized, give them clear goals, canonical input, permitted changes, exclusions, inherited evidence, a share of the remaining global budget, and return locations. Verify their outputs before marking items accepted; a worker summary is not delivery evidence. Do not reset time, retry, or review allowances by starting a new worker, successor, or differently named task.

Track actual backlog reduction against total overhead. If repeated repair, preservation, or handoff produces little useful progress, diagnose once and change the batch design within scope. Do not automatically chain completion notifications into another acceptance-only task. Continue productive in-scope work without asking after every milestone, but stop when the global budget is exhausted or recovery has no new evidence.

Maintain supervision appropriate to the chosen executor. Before claiming work will continue after the turn, freshly verify a concrete active execution handle and task-specific progress, plus the available completion/stall reporting path. A plan, checkpoint, notification subscription, or PID alone is not proof of continuing work. Reuse an earlier healthy handle; do not relaunch solely to create a current-turn handle. Without a verified executor, say paused or blocked.

## Interruption, pause, and recovery

The latest owner instruction controls. **An explicit stop, pause, or report-only request forbids automatic resumption.** Preserve completed work and report its state; renewed authorization does not itself prove a previously looping workflow is repaired.

After an assistant-side interruption, inspect live handles and durable artifacts before acting. Keep a healthy executor; if replacement is needed, first establish that the prior writer is gone or safely fenced. Reconcile late outputs and ambiguous external side effects before retrying. Resume only the missing work within unchanged authority and the remaining global budget, then verify fresh progress. If state, ownership, safety, or authority is ambiguous, preserve evidence and pause rather than guessing.

After an owner-stopped loop is explicitly reopened, identify the loop's cause, reconcile one finite remaining-work inventory, and choose a bounded milestone that changes the failing pattern. Report actual coverage gained, not dispatch activity. Do not reprocess accepted items or invent extra approval gates to occupy another worker.

## Verify and finish

Choose evidence that matches the deliverable and real risk. A small tracer or dry run is useful when it resolves a material execution uncertainty; it is not a mandatory ritual for every batch. Honor named project checks and any required independent review without importing an extra review workflow.

Verify results from the actual delivered form when packaging could change them. For external writes, read back the exact target before claiming success; after an ambiguous send/upload, reconcile before repeating it. Exact-candidate review evidence stays bound to its inputs; changed inputs require affected checks, not automatic repetition of unrelated acceptance or a fresh reviewer round.

Give every item a truthful state such as complete, blocked, failed, timed out, cancelled, or interrupted. Reconcile totals with the inventory. Report useful results and their locations, verification performed, concrete failures, preserved partial work, and any decision needed. Use the approved notification destination; worker completions are internal bookkeeping, not a reason to send repeated status messages. Do not claim completion from activity or silently describe paused work as continuing.

## Situational references, not default infrastructure

All references are subordinate to the task's scope, authority, threat model, and global budget. Load one only for the capability actually needed; its example gates do not become independent requirements for ordinary batches.

- `references/live-handle-interruption-recovery.md` — reconciling an actual interruption.
- `references/ledger-supervised-shell-programmes.md` — optional lightweight coordination when one assistant supervises sequential workers.
- `references/sequential-kanban-overnight-runs.md` and `references/project-ledger-to-execution-queue.md` — only when independent claims or queue semantics are needed.
- `references/containerised-ledger-executor-comparison.md` — only for an authorized executor comparison, not a prerequisite to choosing a simple approach.
- `references/control-plane-worker-plane-dispatch.md` — only when the task creates or changes durable production worker infrastructure. In that scope, preserve process ownership, resource/deadline controls, cancellation, restart safety, and bounded recovery. Use the systemd procedure only if actually designing/changing that boundary; do not restart production or install services merely to qualify a finite batch. Existing infrastructure may be used within its known limits without requalifying it for every job.
- `references/game-localization-batch-intake.md` — only for that domain, under its governing content and approval rules. Localization-specific eligibility, receipts, and schema parity are not general batch requirements.
