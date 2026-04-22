# Reusable Skills

A collection of reusable skills. Each top-level folder is a skill package with a required `SKILL.md` entry point and optional supporting context.

See `AGENT.md` for repository conventions and `STYLE.md` for authoring rules.

- **recover** — Reconstruct interrupted work from recent chats, workspace artifacts, and temp files, then realign on the right thread and next steps.

  ```
  npx skills@latest add GeekKingCloud/skills/recover
  ```

- **handoff** — Capture a restart-safe handoff for unfinished work, including the end goal, current workflow stage, completed work, blockers, and exact next steps for the next coding agent.

  ```
  npx skills@latest add GeekKingCloud/skills/handoff
  ```
