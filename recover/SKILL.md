---
name: recover
description: Recover interrupted coding work by reconstructing the active task from session context, handoffs, workspace artifacts, logs, temp files, and repo state, then decide whether to continue, ask for one confirmation, or produce a restart-safe recovery note. Use when work needs to resume after a timeout, crash, bad response, stalled command, machine restart, context loss, partial handoff, or multiple possible threads.
---

# Recover

Resume interrupted work by rebuilding enough context to act without making the user reconstruct the task from memory.

## Quick start

When asked to recover:
1. Read nearby instructions first, such as `AGENTS.md`, repo guides, and any current handoff note.
2. Build an evidence inventory from conversation/session context, workspace artifacts, logs, commands, diffs, and recent files.
3. Identify candidate interrupted tasks and rank them by evidence strength.
4. Pick a recovery mode: continue, ask one confirmation, offer a choice list, or stop with insufficient evidence.
5. State facts, guesses, risks, and the recommended next step separately.
6. Once aligned, leave recovery mode and continue normal execution.

If the user refers to "this chat", "the other chat", "the crashed chat", or similar, treat chat/session history as the primary source of truth when available.

## Evidence inventory

Collect concrete signals before asking broad questions. Prefer sources that explain both the goal and where execution stopped.

Check, when available:
- current conversation, visible summaries, session indexes, or chat transcripts
- handoff notes, recovery notes, TODO files, plans, issue or PR text, and task descriptions
- command output, failing test logs, terminal scrollback, build artifacts, temp files, scratch files, and generated reports
- `git status`, focused diffs, changed filenames, recent commits, stashes, and branch names
- recently modified files, package scripts, test files, migrations, and docs touched by the suspected task

For stalled or interrupted commands, verify whether the command is still running when the environment exposes that state. Avoid starting duplicate long-running work unless the target task and command safety are clear.

Repo state is strong evidence for what changed, but it is not always proof of the user's intended task. If session evidence and repo evidence disagree, say so before choosing.

Avoid destructive cleanup during recovery. Do not delete temp files, reset branches, revert changes, or overwrite partial work unless the user explicitly asks.

## Rank candidates

Create candidate task threads when more than one recovery target is possible. Keep this implicit and brief when there is only one obvious thread. For each candidate, track:
- `Signal`: what points to this task
- `Stage`: discovery, implementation, validation, review, handoff, or unknown
- `Last known action`: the latest concrete command, file edit, failure, or decision
- `Confidence`: high, medium, low, or insufficient
- `Risk`: what could go wrong if this is the wrong thread

Use only these confidence labels: `high`, `medium`, `low`, or `insufficient`. Use `high` only when multiple signals agree on the same goal and next step, or the user clearly identifies the thread. Use `medium` when the likely task is clear but the next step or success criteria is not. Use `low` when the task is plausible but evidence is thin or conflicting. If confidence falls between two labels, choose the lower label and explain why.

## Guide the user back in

Choose one mode:

### Continue

Continue without asking when:
- the target task is high confidence
- the next action is low risk and reversible
- repo instructions and success criteria are available

First give a compact recovery summary, then act.

### Confirm

Ask one targeted confirmation when:
- the likely task is medium confidence
- the next action could waste meaningful time if wrong
- success criteria, scope, or permission is missing

Ask the smallest question that unlocks progress. Include the recommended default. The confirmation should be an actual question, not only a recommended action.

### Offer choices

Offer 2-5 choices when multiple plausible tasks remain. For each choice, include one evidence line and a proposed first action. Ask the user to pick one or restate the goal.

If the latest session evidence clearly prioritizes one thread but other dirty work exists, recommend the prioritized thread and ask a targeted confirmation instead of presenting all threads as equal.

### Stop

Stop and ask for better context when:
- no candidate has real evidence
- every next step would be risky, destructive, or likely to overwrite partial work
- required session artifacts are inaccessible and repo state is too ambiguous
- the user asks to recover private or unavailable history that cannot be inspected

Do not fill the gap with generic project advice. State what was checked and what specific artifact or answer would unblock recovery.

## Recovery summary

Give the user a compact status readout:
- likely topic
- likely goal
- likely workflow stage
- recent progress or partial changes
- probable blocker, interruption, or failure mode
- confidence level
- recommended next step

Separate facts from guesses. Use phrases like `I found`, `It looks like`, and `My best guess is`. Label evidence sources explicitly, for example `session log`, `handoff`, `git diff`, `test output`, or `modified file`.

Use `templates/RECOVER.md` as the output skeleton.

For the `Confirmation` section, either ask one direct question with a recommended default or write `No confirmation needed` with the reason.

## Alignment rules

- do not pretend certainty when evidence is weak
- do not force the user to reconstruct everything from scratch
- always offer a concrete starting point or recommended next step
- prefer a short confirmation question over a long interview
- if multiple plausible threads exist, ask before committing to one narrative
- if session evidence is ambiguous, partial, or conflicts with repo evidence, confirm the likely thread before giving a confident recovery summary
- protect user work; preserve partial files and unrelated changes
- once the user confirms or corrects the thread, treat that correction as authoritative
- once aligned, switch from recovery into normal execution

## Quality bar

A good recovery run lets a fresh coding agent answer:
- What was the interrupted task?
- What evidence supports that answer?
- What changed already?
- What was the last known blocker or interruption?
- What is uncertain?
- What is the safest next action?

If the recovered thread should be handed to another session, write the recovery note in the template and include exact paths, commands, logs, and next steps.
