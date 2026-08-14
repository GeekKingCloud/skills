# Supporting Files

Read only the sections relevant to support material being added or changed.

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

## Templates

Use `templates/` for reusable output skeletons, not general guidance. A template file should be something the coding agent can follow as the shape of the skill's final output.

Template naming rule:

- Match the parent skill name.
- Use uppercase filenames.
- Preserve kebab-case if the skill name contains hyphens.

Examples:

- `coach/templates/COACH.md`
- `handoff/templates/HANDOFF.md`

Do not use generic names like `REPORT.md` or `SUMMARY.md` when the template belongs to a specific skill. Do not create empty `templates/` folders.

## References

Use `references/` for information that supports the skill but should not clutter the main instructions. Existing `context/` folders may remain; do not rename them just for conformity.

Good uses:

- domain notes
- command references
- policy reminders

Reference files should:

- have stable, descriptive names
- stay focused on one topic each
- avoid repeating the full skill instructions

For fast-moving, research-first skills:

- cite current primary sources where practical
- distinguish accepted standards from proposals, conventions, vendor guidance, and commentary
- avoid score or grade wording that implies official certification, guaranteed ranking, guaranteed retrieval, or compliance unless the skill actually performs that formal evaluation
- state source access dates and evidence limits in the final output

## Assets

Use `assets/` for static files the skill consumes or adapts as output resources.

Good uses:

- document, slide, or code templates
- images, fonts, icons, fixture files, or boilerplate
- lookup data or schemas used as resources rather than instructions

Do not put general workflow guidance in `assets/`.

Repo-level branding and presentation assets belong in the root `.assets/` folder. Do not put repo-level logos, screenshots, or social previews in a visible root-level folder that could be mistaken for a skill.

## Examples

Use `examples/` only when concrete sample prompts, inputs, outputs, or before/after artifacts materially improve trigger behavior, output expectations, or forward-testing. Do not add examples merely to match a folder pattern. Do not put examples under `context/` unless they are part of a larger reference document.

Examples should:

- be realistic enough to guide future output
- avoid sensitive or machine-specific details unless they are intentionally part of the example
- stay close to the skill that uses them
- not replace the reusable output skeleton in `templates/`

## Skill size and decomposition

Keep `SKILL.md` focused on when to use the skill, the execution path, and the quality bar. Split supporting material out when the entry point becomes hard to scan.

Use:

- `templates/` for reusable output skeletons
- `helpers/` for tone variants, checklists, or workflow notes
- `references/` for background/reference material
- `assets/` for output resources and static skill inputs
- `examples/` for sample inputs and outputs

For skills with multiple templates, use `SKILL-NAME.md` as the primary template and `SKILL-NAME-VARIANT.md` for variants.
