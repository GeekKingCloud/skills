# Skill Authoring Foundations

Read this when creating a skill or changing its entry point, frontmatter, prose, table formatting, or output contract.

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
- Treat `SKILL.md` plus frontmatter `name` and `description` as the required portable contract.
- Keep visible root-level directories reserved for skills except the folded repository guide at `docs/operandi/`. Put repo-level branding and presentation files in `.assets/`.
- Store supporting material in well-named subdirectories such as:
  - `references/` for longer factual or background material
  - `assets/` for static resources consumed by the skill's output, such as document templates, images, fonts, fixtures, or boilerplate
  - `helpers/` for smaller helper Markdown files
  - `templates/` for reusable output skeletons
- Use `examples/` only when concrete sample inputs or outputs improve trigger behavior, output expectations, or forward-testing.
- Existing `context/` folders may remain, but prefer `references/` for new reference material.
- Omit `agents/openai.yaml` and similar client-specific metadata unless the repository intentionally adopts that metadata for all skills.
- Keep the structure minimal. Add folders only when they serve the skill.
- Template filenames must match the parent skill name in uppercase form, preserving kebab-case. Examples: `coach/templates/COACH.md`, `handoff/templates/HANDOFF.md`.

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
- `description` should front-load trigger words, task intent, important boundaries, and intended outcome in plain language.
- Keep descriptions brief but not lossy; do not remove context that affects correct skill selection.
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
- Use templates only when they improve consistency. Do not create a `templates/` folder for a skill that has no reusable output skeleton.

## Markdown tables

- Treat each contiguous table as a grid and pad every cell so the unescaped `|` delimiters form straight vertical columns in the Markdown source.
- Compute widths from the widest cell in each column and reflow the whole table when any cell changes; do not align rows individually by eye.
- Keep one space between each delimiter and its cell content, and extend separator-row dashes to the same source width while preserving alignment colons.
- Escape a literal pipe inside a cell as `\|` so it does not split the table.
- Apply this source alignment to tables in root documentation, skill entry points, helpers, references, templates, and examples.

## Output quality

Every skill must define enough output rules for a coding agent to produce useful work without generic filler.

At minimum, each skill should make clear:

- the expected final-output shape, directly or through a template
- what evidence, verification, or uncertainty must be reported
- when the coding agent should stop, refuse, or ask for more context
- how to avoid unsupported sections, placeholders, or boilerplate
- what belongs in the skill instructions versus a template, helper, context file, or example

If a skill has multiple output modes, keep the main path clear in `SKILL.md` and move reusable variants into support files.
