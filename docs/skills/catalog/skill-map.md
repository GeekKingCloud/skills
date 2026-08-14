# Skill Map

Use this map to choose what to load before opening individual `SKILL.md` files. Categories are navigation only: every skill remains a directly installable top-level package.

This is a manually maintained routing view derived from the visible top-level packages and their authoritative `SKILL.md` files. Update it with `README.md` whenever a skill is added, renamed, removed, reclassified, or given a material cross-skill relationship.

## Choose By Task

| Need                                                                       | Start with                                                        | Add or switch when...                                                                                    |
| -------------------------------------------------------------------------- | ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| Execute substantial work through bounded create-review-verify-repair loops | `crucible`                                                        | Use `roast` as Crucible's broad-quality gate when its route calls for it.                                |
| Produce a strict, report-only review with findings and a grade             | `roast`                                                           | Feed findings to `crucible` only when remediation is authorized.                                         |
| Audit one public-facing quality domain                                     | `assess-accessibility`, `assess-agent-readiness`, or `assess-seo` | Run multiple assessments only when the target and caller scope require distinct lenses.                  |
| Find an earlier coding-agent conversation                                  | `scour`                                                           | Move to `recover` when the goal is to reconstruct and continue interrupted work.                         |
| Resume interrupted or transferred work                                     | `recover`                                                         | Use `handoff` before a planned pause; use `scour` only when the source conversation must first be found. |
| Preserve restart-safe work state                                           | `handoff`                                                         | Use `recover` in the receiving or resumed session.                                                       |
| Improve how a caller works with coding agents                              | `coach`                                                           | Use evidence from available collaboration history; do not substitute generic prompt advice.              |
| Reconstruct creator commentary from recorded gameplay                      | `recollect`                                                       | Choose quick or full notes according to the requested depth.                                             |
| Repair commentary-over-background media                                    | `remix-voiceover`                                                 | Keep source media untouched and follow its deterministic analysis/verification path.                     |
| Apply opt-in cosmic-horror narration                                       | `eldritch`                                                        | Activate only on an explicit style request and keep copy-pasteable artifacts clean.                      |

## Families

### Iterative Work And Review

- `crucible` — execution and convergence across substantial directed work.
- `roast` — strict evidence-backed report-only review by default.

### Assessment

- `assess-accessibility` — accessibility across perception, interaction, semantics, content, and responsive behavior.
- `assess-agent-readiness` — discoverability, authoritative retrieval, action surfaces, safety, recovery, and agent-facing documentation.
- `assess-seo` — classic crawl/index, intent, on-page, content, linking, structured-data, performance, and measurement readiness.

### Workflow And Continuity

- `scour` — locate prior coding-agent conversations.
- `recover` — reconstruct state and safely continue interrupted work.
- `handoff` — save restart-safe active state before transfer or pause.
- `coach` — derive evidence-bound collaboration coaching and reusable improvements.

### Creator And Media Utilities

- `recollect` — reconstruct a creator's recorded gameplay thoughts without ghostwriting the final piece.
- `remix-voiceover` — measure, repair, render, and verify commentary-over-background audio or video.

### Just For Fun

- `eldritch` — explicit opt-in narration mode; never a default workflow requirement.

## Crucible And Roast

These skills are complementary but not a mandatory public bundle.

- Choose **Roast alone** for a strict report-only review. Roast does not remediate by default and does not depend on Crucible.
- Choose **Crucible alone** for substantial authorized execution when its selected route validly omits Roast or uses the documented fallback because Roast is unavailable.
- Choose **Crucible with Roast** when the work should be executed and then pass a broad-quality gate, or when a whole-target Roast should create the remediation queue. Crucible owns route selection, finding disposition, remediation, reruns, and readiness reporting; Roast owns the independent findings and grade.
- Keep the Challenger role inside Crucible separate from Roast. They answer different questions and require distinct passes even if one sub-agent performs them sequentially.

Read [`../../../crucible/SKILL.md`](../../../crucible/SKILL.md), then its routed `helpers/ROAST-GATE.md`, for the authoritative route and reporting rules. Read [`../../../roast/SKILL.md`](../../../roast/SKILL.md) for review scope, evidence, grading, and report-only boundaries.

## Common Continuity Chains

- **Planned pause:** `handoff` now, then `recover` in the next session.
- **Unknown prior session:** `scour` to identify it, then `recover` if continuation is requested.
- **History-based improvement:** `coach`; use `scour` only if the relevant history must first be located.

## Installation Contract

Install individual skills from their top-level path:

```text
npx skills@latest add GeekKingCloud/skills/<skill-name>
```

Do not insert catalog families into the path. For example, use `GeekKingCloud/skills/roast`, not `GeekKingCloud/skills/iterative-work-and-review/roast`.
