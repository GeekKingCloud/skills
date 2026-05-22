# Repository Guide

This repository stores reusable skills.

## What lives here

- Each top-level folder is one skill.
- Every skill folder must contain a `SKILL.md` at its root.
- Supporting material should live inside the skill folder, not at the repository root.
- Dot-prefixed root folders are repo infrastructure, not skills.
- Repo-level branding and presentation files live in `.assets/`.
- Root-level docs explain repository-wide expectations:
  - `README.md` lists the published skills.
  - `STYLE.md` defines how to create and update skills.
  - `AGENTS.md` explains how to work in this repository.

## Expected shape

Use a simple, predictable structure:

```text
skill-name/
  SKILL.md
  references/
    REFERENCE.md
  assets/
    RESOURCE-FILE
  helpers/
    HELPER-NAME.md
  templates/
    SKILL-NAME.md
```

Optional examples may live in `examples/` when they support trigger behavior, output expectations, or forward-testing.

## Structure rules

- The folder name is the skill name and should be lowercase kebab-case.
- `SKILL.md` is required and is the entry point for the skill.
- `SKILL.md` frontmatter must include `name` and `description`; treat those fields as the portable skill-selection contract.
- Do not create visible root-level non-skill folders. Use `.assets/` for repo presentation assets.
- Keep skill categories as README/catalog organization only. Do not create visible grouping folders such as `development/`, `assessment/`, or `workflow/`; nested skill folders make discovery and install paths less predictable.
- `references/` is for longer factual or background material the skill may lean on.
- `assets/` is for static resources consumed by the skill's output, such as document templates, images, fonts, fixtures, or boilerplate.
- `helpers/` is for smaller supporting Markdown files that belong to the parent skill.
- `templates/` is for reusable output skeletons when a skill needs them.
- `examples/` is optional and only for concrete sample inputs or outputs that improve trigger behavior, output expectations, or forward-testing.
- Existing `context/` folders may remain, but prefer `references/` for new reference material.
- `agents/openai.yaml` and similar client-specific metadata files are optional and should be omitted unless this repository adopts them consistently.
- Template filenames must match the parent skill name in uppercase form, preserving kebab-case. Examples: `feedback/templates/FEEDBACK.md`, `handoff/templates/HANDOFF.md`.
- Only create directories that the skill actually uses. Avoid empty scaffolding.

## Skill Relationships

Some skills intentionally reference other skills. Keep those relationships explicit in plain skill instructions and templates; do not add machine-readable dependency metadata unless the repository adopts a formal schema later.

Use these relationship types:

- `Work source`: the input that defines the parent skill's work queue, such as a plan, existing review, current-state inspection, or another skill's findings.
- `Default core gate`: a referenced skill or equivalent pass expected in the parent skill's normal success path, but skippable with evidence and final-report disclosure.
- `Optional adjunct gate`: a referenced skill or equivalent pass used only when the target surface makes it relevant.
- `Fallback pass`: the local review or workflow to perform when a referenced skill is unavailable.

When adding or updating a relationship, state:

- whether the relationship is a work source, default core gate, optional adjunct gate, or fallback pass
- trigger conditions that make the relationship apply
- skip conditions that make the relationship irrelevant
- blocking behavior for unresolved findings
- final-report evidence required when the relationship runs, is skipped, or is unavailable

Optional adjunct gates must not read as mandatory in frontmatter descriptions. Describe them in the body where their relevance rules, skip rules, and reporting requirements can be clear.

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
