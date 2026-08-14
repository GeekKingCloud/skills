# Skills Guidebook

This directory is the folded repository guide. The root [`AGENTS.md`](../../AGENTS.md) is the always-read routing shim; these documents are loaded progressively according to the task.

## Repository

- [`repository/layout.md`](repository/layout.md) — package shape, top-level installability, repository files, helpers, and templates.
- [`repository/workflow.md`](repository/workflow.md) — repository work sequence and agent-neutral language.

## Authoring

- [`authoring/foundations.md`](authoring/foundations.md) — core skill format, frontmatter, writing, Markdown tables, and output quality.
- [`authoring/report-and-review.md`](authoring/report-and-review.md) — mode and evidence contracts for report-oriented skills.
- [`authoring/composition.md`](authoring/composition.md) — work sources, gates, adjuncts, fallbacks, and cross-skill relationships.
- [`authoring/supporting-files.md`](authoring/supporting-files.md) — helpers, templates, references, assets, examples, and decomposition.
- [`authoring/maintenance.md`](authoring/maintenance.md) — update rules and final review checklist.

## Catalog

- [`catalog/skill-map.md`](catalog/skill-map.md) — task-first map of every skill family and the established Crucible/Roast combination.

## Source-Of-Truth Order

1. The target skill's `SKILL.md` owns that skill's trigger, workflow, boundaries, and output contract.
2. Routed authoring guides own repository-wide conventions.
3. `README.md` is the human-facing catalog and installation surface.
4. The catalog map helps selection and composition but does not override a skill.

When these disagree, fix the lower-authority summary rather than silently changing the skill contract.
