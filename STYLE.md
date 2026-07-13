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
- Treat `SKILL.md` plus frontmatter `name` and `description` as the required portable contract.
- Keep visible root-level directories reserved for skills. Put repo-level branding and presentation files in `.assets/`.
- Store supporting material in well-named subdirectories such as:
  - `references/` for longer factual or background material
  - `assets/` for static resources consumed by the skill's output, such as document templates, images, fonts, fixtures, or boilerplate
  - `helpers/` for smaller helper Markdown files
  - `templates/` for reusable output skeletons
- Use `examples/` only when concrete sample inputs or outputs improve trigger behavior, output expectations, or forward-testing.
- Existing `context/` folders may remain, but prefer `references/` for new reference material.
- Omit `agents/openai.yaml` and similar client-specific metadata unless the repository intentionally adopts that metadata for all skills.
- Keep the structure minimal. Add folders only when they serve the skill.
- Template filenames must match the parent skill name in uppercase form, preserving kebab-case. Examples: `feedback/templates/FEEDBACK.md`, `handoff/templates/HANDOFF.md`.

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

## Report And Review Skill Contracts

Report, audit, review, recovery, feedback, and handoff skills need sharper mode boundaries than ordinary execution skills. Define the boundaries once in the skill's own domain language; do not copy this section into every skill as boilerplate.

For these skills, `SKILL.md` should make clear:

- `Scope mode`: what target is being reviewed or reconstructed, such as a whole project, changed files, one workflow, one artifact, the current conversation, a date range, or a saved handoff.
- `Evidence mode`: what evidence can support conclusions, such as source plus live/rendered behavior, source only, live/rendered only, artifact only, transcript/log only, summary-derived evidence, or unavailable evidence.
- `Action mode`: whether the skill should only report, ask one alignment question, continue implementation, remediate findings, save a file, run a gate loop, or stop because evidence is insufficient.
- `Output mode`: whether the result belongs inline, in a saved Markdown file, in a reusable report template, in a review comment, or in a handoff or recovery note.
- `Score or grade behavior`: what is scored, what is not scored, how `N/A` differs from `Not assessed`, and what grade caps or confidence limits apply when evidence is missing or weak.
- `Stop or ask behavior`: when to stop, ask for confirmation, summarize only, continue without asking, mark the run incomplete, or recommend a narrower follow-up.

Report-facing templates should contain report sections and placeholders only. Keep authoring instructions, hidden process notes, and mode-selection rules in `SKILL.md`, helpers, or references unless the final reader genuinely needs to see them.

Do not let a report silently widen its scope or convert evidence limits into observed defects. Separate facts, evidence limits, inferences, recommendations, and unresolved risks. Do not claim official compliance, guaranteed rankings, guaranteed retrieval, certification, release readiness, or production safety unless the skill's defined scope and evidence mode actually support that claim.

## Cross-Skill Composition

Prefer plain-language composition over formal dependency metadata. Do not add machine-readable dependency fields unless the repository adopts a shared schema for every skill.

When a skill leans on another skill, describe the relationship in the parent skill's body and reflect any reportable result in the parent skill's template. Use these terms consistently:

- `Work source`: input that defines the parent skill's work queue, such as a plan, review, current-state inspection, or another skill's findings.
- `Default core gate`: expected in the skill's normal success path, but skippable with evidence and final-report disclosure.
- `Optional adjunct gate`: relevant only for specific target surfaces or caller requests.
- `Fallback pass`: what to do when the referenced skill is unavailable.

For each relationship, state:

- whether it is a work source, default core gate, optional adjunct gate, or fallback pass
- when to run it
- when to skip it
- what unresolved findings block the parent workflow
- what to report when it ran, was skipped, or was unavailable

Do not make optional capabilities look mandatory in frontmatter descriptions. Keep frontmatter focused on the parent skill's primary trigger; put optional adjunct rules in the body where the conditions can be precise.

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

- `feedback/templates/FEEDBACK.md`
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

## Updating an existing skill

When editing a skill:

- preserve the original purpose unless the change is intentional
- clean up stale or contradictory wording
- describe only the current skill contract; remove legacy names, aliases, migration maps, and compatibility guidance for earlier versions of the skill
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
