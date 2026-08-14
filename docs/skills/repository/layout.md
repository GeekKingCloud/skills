# Repository Layout

Read this when adding, moving, renaming, or removing a skill package or repository-level file.

## What lives here

- Each visible top-level folder except `docs/` is one skill.
- Every skill folder must contain a `SKILL.md` at its root.
- Supporting material should live inside the skill folder, not at the repository root.
- Dot-prefixed root folders are repo infrastructure, not skills.
- Repo-level branding and presentation files live in `.assets/`.
- Repository-wide guidance has three entry surfaces:
  - `README.md` lists the published skills for people browsing and installing them.
  - `AGENTS.md` is the compact agent routing shim.
  - `docs/skills/` holds the folded guidebook and task-oriented skill map.

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
- `docs/` is the only visible root-level non-skill folder; repository guidance lives under `docs/skills/`. Use `.assets/` for repo presentation assets and do not add other visible non-skill roots without an explicit repository-wide reason.
- Keep skill categories as README/catalog organization only. Do not create visible grouping folders such as `development/`, `assessment/`, or `workflow/`; nested skill folders make discovery and install paths less predictable.
- Put novelty or tone-only skills under a README/catalog category such as `Just For Fun`; keep them as normal top-level skill folders, not nested category folders.
- `references/` is for longer factual or background material the skill may lean on.
- `assets/` is for static resources consumed by the skill's output, such as document templates, images, fonts, fixtures, or boilerplate.
- `helpers/` is for smaller supporting Markdown files that belong to the parent skill.
- `templates/` is for reusable output skeletons when a skill needs them.
- `examples/` is optional and only for concrete sample inputs or outputs that improve trigger behavior, output expectations, or forward-testing.
- Existing `context/` folders may remain, but prefer `references/` for new reference material.
- `agents/openai.yaml` and similar client-specific metadata files are optional and should be omitted unless this repository adopts them consistently.
- Template filenames must match the parent skill name in uppercase form, preserving kebab-case. Examples: `coach/templates/COACH.md`, `handoff/templates/HANDOFF.md`.
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

- `coach/templates/COACH.md`
- `handoff/templates/HANDOFF.md`

Do not create empty `templates/` folders. Keep workflow notes, tone files, and checklists in `helpers/`, not `templates/`.
