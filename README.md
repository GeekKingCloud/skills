# Reusable Skills

A collection of reusable skills. Each top-level folder is a skill package with a required `SKILL.md` entry point and optional supporting context.

See `AGENTS.md` for repository conventions and `STYLE.md` for authoring rules.

- **recover** — Reconstruct interrupted work from recent chats, workspace artifacts, and temp files, then realign on the right thread and next steps.

  ```
  npx skills@latest add GeekKingCloud/skills/recover
  ```

- **handoff** — Capture a restart-safe handoff for unfinished work, including the end goal, current workflow stage, completed work, blockers, and exact next steps for the next coding agent.

  ```
  npx skills@latest add GeekKingCloud/skills/handoff
  ```

- **feedback** — Review available collaboration history between a user and coding agents, then produce evidence-bound feedback on communication patterns, gaps, and practical ways to work better together without inventing unsupported history.

  ```
  npx skills@latest add GeekKingCloud/skills/feedback
  ```

- **roast** — Perform a harsh, detail-obsessed codebase review for a project folder or directed target, with extra force on security holes, architecture problems, tests, maintainability, style, naming, comments, spacing, and user-supplied excuses.

  Defaults to a serious strict-teacher tone. Ask for a snarky, mean, comedy,
  burn, putdown, or savage roast to switch the presentation style while keeping
  findings evidence-backed and actionable.

  ```
  npx skills@latest add GeekKingCloud/skills/roast
  ```
