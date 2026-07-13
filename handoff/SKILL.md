---
name: handoff
description: Capture restart-safe handoff notes for unfinished work in a reachable HANDOFF.md file by default. Use when pausing, transferring, or resuming after context loss, token pressure, machine restart, session change, or any stop that needs goal, status, blockers, artifacts, and next steps preserved.
---

# Handoff

Create a concise handoff for the next coding agent. Optimize for fast restart, not prose.

## Quick start

When asked to hand off work:
1. Rebuild the current state from source artifacts before writing the note.
2. State the end goal and current workflow stage in plain language.
3. Record what is complete, what is in progress, and what stopped the work.
4. Record tests and blockers; include exact file paths and commands only when continuation needs them.
5. Classify the destination visibility as ignored/local, tracked, shared, or public, then sanitize secrets and unnecessary private details.
6. Write the handoff to a reachable `HANDOFF.md` by default, then report the path.
7. Be explicit about uncertainty; do not imply work was finished when it was only planned.

## Gather facts

Check the workspace instead of relying on memory:
- relevant files and diffs
- commands already run and their outcomes
- tests run, skipped, or still failing
- branch state and uncommitted changes when relevant
- decisions, assumptions, and open questions

## Choose the file location

Default to a user-reachable file named `HANDOFF.md`:

- Use the explicit target repo, project folder, or workspace root when the caller names one.
- Otherwise use the current working directory if it is the obvious active workspace.
- Do not default to hidden tool scratch paths, temp UUID folders, client-specific runtime folders, or other locations a user is unlikely to open directly.
- If multiple plausible roots exist, no writable project root is available, or the request only asks for handoff text without a clear workspace, ask one short location question before writing.
- If a same-task `HANDOFF.md` already exists, update it in place.
- If `HANDOFF.md` exists but appears to describe unrelated work, ask before replacing it; offer to append a dated section or write a clearly named adjacent file such as `HANDOFF-<topic>.md`.
- After writing, state the final path and whether the file was created, updated, appended, or intentionally not written.

Use the most exposed applicable visibility level. Remove secrets and unnecessary private details, and preserve exact paths or commands only when they are required to continue. Do not require blanket confirmation for a normal tracked handoff; ask only when necessary sensitive content or shared/public visibility creates an actual disclosure risk.

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
- reference real paths and identifiers only when continuation needs them
- mention exact errors or failing checks when relevant
- separate facts from guesses
- prefer imperative next steps over vague suggestions
- keep it skimmable; dense notes are better than long narratives

## Output format

Use `templates/HANDOFF.md` as the output skeleton.
