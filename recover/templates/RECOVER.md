# Recovery Summary

## Recovery Contract
- Scope mode: [one task, thread, session, workspace, or ranked candidates]
- Evidence mode: [session/transcript, task state, workspace/repository, scratch/runtime, handoff/summary, or explicit subset]
- Recovery type: [semantic continuation, verified native resume, or status reconstruction]
- Action mode: [observe-only, summarize, confirm, offer choices, continue, or stop]
- Output mode: [inline summary, or authorized saved recovery note; observe-only must be inline]
- Snapshot time: [time and time zone]
- Thread confidence: [high, medium, low, or insufficient]
- Continuation confidence: [high, medium, low, or insufficient]
- Overall confidence: [the lower of thread and continuation confidence]

## Likely Thread
- Topic: [task or thread]
- Intended outcome: [source-authored goal]
- Stage: [discovery, implementation, validation, review, handoff, or unknown]
- Source session/task: [title, identifier, or unavailable]
- Source status: [active, inactive, or unknown, with evidence]

## Recovery Locations
- Session/context source: [path, sanitized locator, export, index, or unavailable]
- Session working directory: [path, sanitized locator, or unknown]
- Target workspace/repository: [path or sanitized locator, branch/HEAD, and dirty-state summary]
- Scratch/runtime sources: [paths, sanitized locators, or none found]

## Evidence
- [source and freshness] - [signal and what it supports]

## Recovered Trajectory

### Past
- Goal and constraints: [originating objective, caller decisions, and boundaries]
- Completed: [known work, decisions, commands, commits, or verification]
- Rejected or superseded paths: [approach and why, or unknown]

### Present
- Last completed action: [latest proven completed step]
- Interrupted or in-progress action: [action and interruption type]
- Current state: [partial implementation, artifacts, active hypothesis, blocker, or failure]

### Intended Future
- Source-authored plan: [remaining ordered steps supported explicitly or strongly by source evidence]
- First unperformed action: [exact continuation boundary]
- Success check: [expected proof or definition of done]
- Stop rule: [condition for stopping, asking, or declaring completion]
- Open questions or review findings: [items still requiring resolution]

### Supported Inferences
- [destination reconstruction that is evidence-supported but not source-authored, or none]

## Evidence Limits And Conflicts
- [stale, conflicting, inaccessible, inferred, or unverified state]
- Non-transferable state: [hidden context, process/tool handles, unsaved terminal state, credentials, or native resume limits]

## Safety And Permission Boundaries
- Source approvals: [historical evidence only]
- Current authorization: [what the caller currently permits]
- Coordination risk: [live-session, concurrent-write, duplicate-work, or process risk]
- Fresh confirmation required for: [mutating, destructive, publishing, external, credentialed, or takeover action]

## Risk
- [what could go wrong if the recovery guess or continuation is wrong]

## Destination Recommendation
1. [safest concrete next action, kept separate from the recovered source plan]

## Confirmation
[Ask one direct question with the recommended default, or write `No confirmation needed` with the reason.]
