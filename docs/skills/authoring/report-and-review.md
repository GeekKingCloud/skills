# Report And Review Skills

Read this when authoring or reviewing an audit, report, review, recovery, feedback, or handoff skill.

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
