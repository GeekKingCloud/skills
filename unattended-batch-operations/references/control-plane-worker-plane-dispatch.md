# Control Plane, Queue, and Worker Lifetime

Use this reference only when the authorized task creates or changes durable production worker infrastructure that must outlive its control plane. A finite batch arriving through chat or an API does not by itself trigger this architecture. Existing infrastructure can be used within its known limits; do not install services, add a dispatcher, or run restart drills to qualify an ordinary job. The task's scope, operating model, approvals, and global budget govern the applicable gates below.

## Durable architecture test

Separate three owners:

1. **Control plane** — accepts owner messages, creates/cancels work, reports status, and delivers terminal results.
2. **Work ledger** — stores immutable intent, dependencies, comments/checkpoints, claims, retries, and terminal state.
3. **Worker lifetime boundary** — owns the complete process tree, deadlines, resource limits, cancellation, and cleanup.

A ticket system solves only item 2. A subprocess with a new Unix session is still not an independent lifetime boundary when it remains in the control plane's systemd cgroup. Conversely, an isolated worker without a durable ledger can survive a gateway restart yet duplicate or lose semantic state.

## Intake routing

For the durable infrastructure being designed, route work needing that infrastructure through its canonical ledger. Its intake should:

- write a self-contained task contract with source pointers, authority, unchanged behavior, acceptance evidence, and an idempotency key;
- subscribe the originating channel/thread to terminal events;
- return the work ID promptly rather than retaining the whole programme in chat context;
- treat later owner messages as comments, supersession, or explicit cancellation against that ID.

Make conversation cancellation and background-task cancellation distinguishable, with an explicit operation bound to the task/run identity. This distinction must not override owner intent: honor an owner stop/pause directed at the work, never automatically resume it, and clarify ambiguous targets before further dispatch.

## Worker requirements

When independent worker lifetime is a requirement, launch under a task-owned host boundary outside the messaging gateway's service cgroup. On systemd hosts, use a named transient service or equivalent with:

- task/run-bound identity and a read-back MainPID/control group;
- `RuntimeMaxSec`, `MemoryMax`, `TasksMax`, bounded stop grace, and control-group cleanup;
- a separate inactivity deadline based on durable progress or heartbeat, not PID liveness;
- exactly one terminal state and a final receipt;
- verified empty cgroup after completion, cancellation, or timeout.

Start conservatively with one heavyweight worker per constrained owner-facing host. Queue depth and execution concurrency are separate controls.

## Queue and executor composition

Prefer one canonical top-level ledger rather than parallel shadow boards. Domain executors may maintain richer internal artifacts when they remain subordinate to the top-level task:

- a project-local ticket manager can own implementation tickets and dependencies;
- a planning pipeline can create durable specifications and ticket batches;
- a coding executor can own worktrees, retries, verification, and integration evidence;
- the top-level ledger still owns owner-visible status, cancellation, and final delivery.

Do not use a software-delivery pipeline universally for research, business operations, or simple analysis merely because it has tickets. Route by workload class.

## Verify the selected implementation

Inspect the installed queue and worker launcher before relying on lifecycle guarantees. A detached child or new Unix session may remain inside the control plane's service group. A ledger records work; it does not itself provide an independent worker lifetime. Verify current source and supported extension points rather than assuming a custom external worker lane is configuration-only or supported end to end.

## Minimum acceptance matrix

Qualify the durability guarantees actually promised by the changed infrastructure with disposable tasks. The matrix below applies to a system promising all these behaviors, not to every batch. Run destructive restart/reboot or live-channel checks only with explicit authority and isolation; otherwise report those guarantees unverified:

1. Channel/control-plane message intake remains responsive while the worker runs.
2. The worker's cgroup is outside the gateway's cgroup.
3. Restarting the gateway does not stop or duplicate the worker.
4. Terminal delivery is retained while the gateway is unavailable and is delivered after reconnect.
5. A normal conversation stop leaves the worker unchanged.
6. Explicit task cancellation stops the exact unit, closes the ledger run, and leaves its cgroup empty.
7. Killing the worker causes one bounded reconciliation path, never concurrent duplicate execution.
8. Provider stalls exhaust a retry/wall-time budget, checkpoint, and block visibly.
9. Host reboot recovers queued/running state without replaying ambiguous side effects.
10. Storage/resource admission limits refuse new heavy work before owner-channel health is threatened.

If any gate is unproved, report the architecture as a candidate or pilot—not deployed protection.
