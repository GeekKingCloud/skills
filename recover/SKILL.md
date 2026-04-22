---
name: recover
description: Recover interrupted coding work by reconstructing likely context from recent chats, workspace artifacts, and temp files, then realigning with the user on direction and next steps. Use when Codex needs to resume after a timeout, bad response, stalled operation, machine restart, lost thread, or multiple partial conversations and must figure out which task to continue.
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

## Rebuild context

Check concrete artifacts first:
- recent conversation history or available thread summaries
- recent handoff notes, if any exist
- recently modified files and git diff or status
- temp files, scratch notes, logs, and generated outputs
- open issues, PRs, commands, or test failures referenced nearby

Prefer signals that explain both what the work was and where it stopped.

## Guide the user back in

If the topic is unclear:
- propose 2-5 plausible recovery options
- include one-line evidence for each option
- ask the user to pick one or restate the goal

If the topic is mostly clear:
- present a concise recovery summary
- call out assumptions explicitly
- ask targeted follow-up questions only for missing direction, constraints, or success criteria

## Recovery summary

Give the user a compact status readout:
- likely topic
- likely goal
- likely workflow stage
- recent progress or partial changes
- probable blocker, interruption, or failure mode
- recommended next step

Separate facts from guesses. Use phrases like `I found`, `It looks like`, and `My best guess is`.

## Alignment rules

- do not pretend certainty when evidence is weak
- do not force the user to reconstruct everything from scratch
- always offer a concrete starting point or recommended next step
- prefer a short confirmation question over a long interview
- once aligned, switch from recovery into normal execution

## Template

```md
## Recovery Summary
- Likely topic: ...
- Goal: ...
- Current stage: ...
- Evidence: ...
- Open uncertainty: ...
- Recommended next step: ...

Question: Is this the thread you want to resume?
```
