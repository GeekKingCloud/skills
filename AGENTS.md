# Skills Repository Guide

This repository stores reusable, individually installable skills. Treat this file as the routing shim into the Skills Guidebook under [`docs/skills/`](docs/skills/README.md); do not read every guide for every task.

## Start Here

1. Read the target skill's `SKILL.md` before changing it.
2. Use the routing table below to load only the repository guidance relevant to the work.
3. Preserve visible top-level skill directories and their direct install paths.
4. Update `README.md` and the catalog map when adding, renaming, removing, or reclassifying a skill.
5. Verify the changed skill and repository map before finishing.

## Guidance Map

| When you are...                                                                     | Read                                                                         |
| ----------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| Adding, moving, renaming, or removing a package or repo-level file                  | [`docs/skills/repository/layout.md`](docs/skills/repository/layout.md)                     |
| Working in the repo or checking repository-wide language                            | [`docs/skills/repository/workflow.md`](docs/skills/repository/workflow.md)                 |
| Creating a skill or editing its entry point, frontmatter, prose, or output contract | [`docs/skills/authoring/foundations.md`](docs/skills/authoring/foundations.md)             |
| Editing an audit, report, review, recovery, feedback, or handoff skill              | [`docs/skills/authoring/report-and-review.md`](docs/skills/authoring/report-and-review.md) |
| Defining or changing a relationship between skills                                  | [`docs/skills/authoring/composition.md`](docs/skills/authoring/composition.md)             |
| Adding or changing helpers, templates, references, assets, or examples              | [`docs/skills/authoring/supporting-files.md`](docs/skills/authoring/supporting-files.md)   |
| Maintaining, renaming, or reviewing an existing skill                               | [`docs/skills/authoring/maintenance.md`](docs/skills/authoring/maintenance.md)             |
| Choosing a skill or understanding families and combinations                         | [`docs/skills/catalog/skill-map.md`](docs/skills/catalog/skill-map.md)                     |

## Hard Boundaries

- Each visible top-level directory other than `docs/` is a skill package and must contain `SKILL.md`; dot-prefixed directories are repository infrastructure.
- Keep skill packages top-level. Categories belong in the catalog, not in nested install paths.
- Do not change a skill's purpose, procedure, or output contract during a documentation-only reorganization.
- Keep instructions agent- and vendor-neutral.
- Follow the nearest nested `AGENTS.md` if one is added later; it may narrow this guide for its subtree.
