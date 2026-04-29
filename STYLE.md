# Skill Style Guide

Use this guide when creating or updating any skill in this repository.

## Core principles

- Keep every skill easy to scan and easy to execute.
- Prefer concrete instructions over abstract advice.
- Separate facts, guesses, and recommended next steps.
- Keep examples realistic and aligned with the actual workflow.
- Stay agent agnostic. Skills should not depend on a specific named product or model.

## Naming and layout

- Use a lowercase kebab-case folder name for each skill.
- Match the folder name and frontmatter `name` unless there is a strong reason not to.
- Put the required `SKILL.md` at the root of the skill folder.
- Store supporting reference material in well-named subdirectories such as:
  - `context/` for background docs and reference notes
  - `helpers/` for smaller helper Markdown files
  - `templates/` for reusable output formats
  - `examples/` for concrete sample inputs or outputs
- Keep the structure minimal. Add folders only when they serve the skill.

## Required `SKILL.md` pieces

Every `SKILL.md` should include:

1. YAML frontmatter with at least:
   - `name`
   - `description`
2. A clear title.
3. A short explanation of when to use the skill.
4. Concrete execution guidance.
5. Any quality bar, checklist, or template needed to apply the skill reliably.

## Frontmatter guidance

- `name` should be short and stable.
- `description` should explain the purpose, trigger conditions, and intended outcome in plain language.
- Keep descriptions vendor-neutral and reusable across tools and environments.

Example:

```md
---
name: recover
description: Reconstruct interrupted work from recent context and workspace artifacts, then realign on the next step.
---
```

## Writing style

- Use direct, imperative language.
- Prefer short sections with descriptive headings.
- Optimize for the next reader to act quickly without extra interpretation.
- Make uncertainty explicit.
- Use templates only when they improve consistency.

## Agent-agnostic language

Do not tie a skill to a named assistant, model, or vendor. When you need a neutral actor term, prefer `coding agent`.

Avoid:

- `Use when <product-name> needs to resume...`
- `Ask <assistant-name> to summarize...`
- `This skill is for <tool-name> sessions...`

Prefer:

- `Use when a coding agent needs to resume interrupted work...`
- `Use when interrupted work needs to be resumed...`
- `Use when a summary is needed before handoff...`
- `Use when the current session lacks enough context...`

## Helpers

If a skill needs smaller helper files:

- Put them under the parent skill's `helpers/` directory.
- Keep each helper narrowly scoped.
- Store helpers as ordinary Markdown files such as `helpers/TRIAGE-CHECKLIST.md`.
- Do not model helpers as nested standalone skills.
- Document helper usage from the parent skill when the relationship is not obvious.

## Context files

Use `context/` for information that supports the skill but should not clutter the main instructions.

Good uses:

- domain notes
- command references
- policy reminders
- examples too detailed for the main `SKILL.md`

Context files should:

- have stable, descriptive names
- stay focused on one topic each
- avoid repeating the full skill instructions

## Updating an existing skill

When editing a skill:

- preserve the original purpose unless the change is intentional
- clean up stale or contradictory wording
- keep examples and templates in sync with the current instructions
- update `README.md` if the top-level skill list changes
- check for product-specific references and replace them with neutral language

## Review checklist

Before finishing a change, confirm:

- the folder name matches the skill name
- `SKILL.md` exists at the skill root
- frontmatter is present and accurate
- supporting files live under the skill folder
- wording is agent agnostic
- the skill can be understood without hidden context
