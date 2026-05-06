---
name: recover
description: Recover interrupted coding work by reconstructing likely context from recent chats, workspace artifacts, and temp files, then realigning on direction and next steps. Use when work needs to resume after a timeout, bad response, stalled operation, machine restart, lost thread, or multiple partial conversations and the next step is unclear.
---

# Recover

Resume an interrupted task by rebuilding context, surfacing likely threads, and confirming direction with the user.

## Quick start

When asked to recover:
1. Scan available context before asking broad questions.
2. Offer a short list of likely recent tasks when more than one candidate exists.
3. State the best guess about the interrupted work and the evidence behind it.
4. Ask only the minimum questions needed to confirm direction.
5. Treat the user's correction as authoritative.

If the user refers to "this chat", "the other chat", "the crashed chat", or similar, treat chat/session history as the primary source of truth when available.

## Rebuild context

Check concrete artifacts first, in this order when available:
- actual local session/chat transcripts, session indexes, or thread summaries
- recent handoff notes, if any exist
- temp files, scratch notes, logs, and generated outputs
- recent commands, test failures, issues, or PRs referenced nearby
- recently modified files and git diff or status

Prefer signals that explain both what the work was and where it stopped.

Repo state is supporting evidence, not the primary source of truth for conversational recovery when session artifacts are available.

## Guide the user back in

If the topic is unclear:
- propose 2-5 plausible recovery options
- include one-line evidence for each option
- ask the user to pick one or restate the goal

If the topic is mostly clear:
- present a concise recovery summary
- call out assumptions explicitly
- ask targeted follow-up questions only for missing direction, constraints, or success criteria

If session evidence and repo evidence point to different threads, say so plainly and ask before choosing one.

## Recovery summary

Give the user a compact status readout:
- likely topic
- likely goal
- likely workflow stage
- recent progress or partial changes
- probable blocker, interruption, or failure mode
- recommended next step

Separate facts from guesses. Use phrases like `I found`, `It looks like`, and `My best guess is`.
When possible, label evidence sources explicitly, for example `I found in the session log` and `I found in the repo`.

Use `templates/RECOVER.md` as the output skeleton.

## Alignment rules

- do not pretend certainty when evidence is weak
- do not force the user to reconstruct everything from scratch
- always offer a concrete starting point or recommended next step
- prefer a short confirmation question over a long interview
- if multiple plausible threads exist, ask before committing to one narrative
- if session evidence is available, confirm the likely thread before giving a confident recovery summary
- once aligned, switch from recovery into normal execution
