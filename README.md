# Reusable Skills

A collection of reusable skills. Each top-level folder is a skill package with a required `SKILL.md` entry point and optional supporting files such as references, assets, helpers, templates, and examples.

See `AGENTS.md` for repository conventions and `STYLE.md` for authoring rules.

- **recover** — Recover interrupted coding work from chats, handoffs, workspace artifacts, and temp files, then realign on the next step.

  ```
  npx skills@latest add GeekKingCloud/skills/recover
  ```

- **handoff** — Capture restart-safe handoff notes for unfinished work, including goal, status, blockers, artifacts, and exact next steps.

  ```
  npx skills@latest add GeekKingCloud/skills/handoff
  ```

- **crucible** — Implement plans to release-ready state through a sub-agent-heavy loop with tests, peer review, cleanup, security and docs/comment sweeps, and roast-gated remediation.

  ```
  npx skills@latest add GeekKingCloud/skills/crucible
  ```

- **feedback** — Review collaboration history deeply, then produce evidence-bound feedback on prompting, handoffs, corrections, failures, and agent-side rules.

  ```
  npx skills@latest add GeekKingCloud/skills/feedback
  ```

- **roast** — Harshly review a codebase, PR, module, or directed target with security-first, evidence-backed findings, severity, fixes, and a grade.

  Defaults to a serious strict-teacher tone. Ask for a snarky, mean, comedy,
  burn, putdown, or savage roast to switch the presentation style while keeping
  findings evidence-backed and actionable.

  ```
  npx skills@latest add GeekKingCloud/skills/roast
  ```
