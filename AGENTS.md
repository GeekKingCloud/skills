# Repository Guide

This repository stores reusable skills.

## What lives here

- Each top-level folder is one skill.
- Every skill folder must contain a `SKILL.md` at its root.
- Supporting material should live inside the skill folder, not at the repository root.
- Root-level docs explain repository-wide expectations:
  - `README.md` lists the published skills.
  - `STYLE.md` defines how to create and update skills.
  - `AGENTS.md` explains how to work in this repository.

## Expected shape

Use a simple, predictable structure:

```text
skill-name/
  SKILL.md
  context/
    REFERENCE.md
  helpers/
    HELPER-NAME.md
  templates/
    SKILL-NAME.md
  examples/
    EXAMPLE.md
```

## Structure rules

- The folder name is the skill name and should be lowercase kebab-case.
- `SKILL.md` is required and is the entry point for the skill.
- `context/` is for reference material the skill may lean on.
- `helpers/` is for smaller supporting Markdown files that belong to the parent skill.
- `templates/` is for reusable output skeletons when a skill needs them.
- `examples/` is for concrete sample inputs or outputs.
- Template filenames must match the parent skill name in uppercase form, preserving kebab-case. Examples: `feedback/templates/FEEDBACK.md`, `handoff/templates/HANDOFF.md`.
- Only create directories that the skill actually uses. Avoid empty scaffolding.

## Helpers

Some skills may need smaller helper files for specialized subtasks. When that happens:

- Put them under the parent skill's `helpers/` directory.
- Store each helper as a focused Markdown file such as `helpers/CHECKLIST.md`.
- Keep helpers tightly scoped to the parent skill's needs.
- Do not treat helper files as standalone top-level skills.

## Templates

Use `templates/` only for reusable output skeletons that the skill asks the coding agent to follow. Name each template after the parent skill in uppercase form, preserving kebab-case.

Examples:

- `feedback/templates/FEEDBACK.md`
- `handoff/templates/HANDOFF.md`

Do not create empty `templates/` folders. Keep workflow notes, tone files, and checklists in `helpers/`, not `templates/`.

## Working in this repo

- Start by reading the target skill's `SKILL.md`.
- Keep context and examples close to the skill that uses them.
- Update `README.md` when adding, renaming, or removing a top-level skill.
- Follow `STYLE.md` for naming, tone, structure, and update rules.

## Language rules

Keep the repository tool- and vendor-neutral:

- Do not mention specific assistants, models, or products in skills or docs.
- Avoid phrases like `Use when <product-name>...`, `Ask <assistant-name> to...`, or similar product-specific wording.
- Prefer neutral terms such as `coding agent`, `caller`, `workflow`, `workspace`, or `session` when needed.
- Write guidance so it still makes sense if the skill is used in a different tool later.
