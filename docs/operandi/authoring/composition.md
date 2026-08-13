# Cross-Skill Composition

Read this when one skill consumes another skill's output, uses another skill as a gate, or needs a fallback when another skill is unavailable.

## Skill Relationships

Prefer plain-language composition over formal dependency metadata. Do not add machine-readable dependency fields unless the repository adopts a shared schema for every skill.

When a skill leans on another skill, describe the relationship in the parent skill's body and reflect any reportable result in the parent skill's template. Use these terms consistently:

- `Work source`: input that defines the parent skill's work queue, such as a plan, review, current-state inspection, or another skill's findings.
- `Default core gate`: expected in the parent skill's normal success path, but skippable with evidence and final-report disclosure.
- `Optional adjunct gate`: relevant only for specific target surfaces or caller requests.
- `Fallback pass`: the local review or workflow to perform when the referenced skill is unavailable.

For each relationship, state:

- whether it is a work source, default core gate, optional adjunct gate, or fallback pass
- trigger conditions that make it apply
- skip conditions that make it irrelevant
- what unresolved findings block the parent workflow
- what to report when it ran, was skipped, or was unavailable

Do not make optional capabilities look mandatory in frontmatter descriptions. Keep frontmatter focused on the parent skill's primary trigger; put optional adjunct rules in the body where the conditions can be precise.
