---
name: handoff
description: Capture restart-safe handoff notes for unfinished work so a future coding agent can resume without rediscovering the whole problem. Use when work needs to transfer cleanly because of context rot, token pressure, machine restarts, session changes, or any pause where the goal, current workflow stage, completed work, blockers, and next steps must be preserved.
---

# Handoff

Create a concise handoff for the next coding agent. Optimize for fast restart, not prose.

## Quick start

When asked to hand off work:
1. Rebuild the current state from source artifacts before writing the note.
2. State the end goal and current workflow stage in plain language.
3. Record what is complete, what is in progress, and what stopped the work.
4. Include exact file paths, commands, tests, and blockers.
5. Be explicit about uncertainty; do not imply work was finished when it was only planned.

## Gather facts

Check the workspace instead of relying on memory:
- relevant files and diffs
- commands already run and their outcomes
- tests run, skipped, or still failing
- branch state and uncommitted changes when relevant
- decisions, assumptions, and open questions

## Write the handoff

Prefer short sections with concrete facts:
- `Goal`: the final outcome the work is aiming for
- `Workflow Stage`: discovery, implementation, validation, review, or another precise phase
- `Status`: where the work stopped and why a handoff is needed
- `Completed`: changes already made or verified
- `In Progress`: the latest hypothesis, partial implementation, or active debugging thread
- `Next Steps`: ordered actions the next coding agent should take first
- `Artifacts`: important files, commands, PRs, issues, logs, or screenshots
- `Risks`: blockers, uncertainties, and places where the next coding agent should be careful

## Quality bar

Make the note useful to a fresh reader with no hidden context:
- reference real paths and identifiers
- mention exact errors or failing checks when relevant
- separate facts from guesses
- prefer imperative next steps over vague suggestions
- keep it skimmable; dense notes are better than long narratives

## Output format

Use `templates/HANDOFF.md` as the output skeleton.
