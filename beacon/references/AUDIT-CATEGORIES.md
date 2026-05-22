# Audit Categories

Use this file as Beacon's default category map. Omit categories that do not apply, add target-specific categories when needed, and keep scoring separate from official standards claims.

## Contents

- Discovery And Crawl Policy
- Agent Instructions And Orientation
- Content Extractability And Semantics
- Action Surfaces And Protocols
- Auth, Permissions, And Safety
- Error Recovery And Determinism
- Documentation Freshness And Examples
- Handoff And Verification
- Priority Mapping
- Category Score Rubric
- Final Score Rules

## Discovery And Crawl Policy

Check whether agents can find the right public or authorized surfaces.

Inspect:

- `robots.txt`, crawler allow/deny rules, and AI crawler policy
- sitemaps, docs indexes, public route maps, canonical URLs, redirects, status codes, and broken links
- `llms.txt`, Markdown variants, text exports, and low-boilerplate indexes when present
- JavaScript rendering, SSR/static fallback, pagination, localization, and duplicate routes

## Agent Instructions And Orientation

Check whether a new agent can understand what the system is and how to work with it.

Inspect:

- `AGENTS.md`, README, quick starts, task guides, capability maps, and docs entrypoints
- setup, run, test, build, deploy, auth, and environment instructions
- ownership boundaries, examples, known limitations, and "when to use this" guidance

## Content Extractability And Semantics

Check whether agents can extract accurate meaning without brittle scraping.

Inspect:

- semantic HTML, headings, metadata, canonical tags, structured data, and Schema.org
- main-content separation, boilerplate, hidden critical content, PDFs/images-only content, and script-only content
- dates, authorship, source provenance, entities, summaries, FAQs, and citation clarity

## Action Surfaces And Protocols

Check whether agents can perform useful work through stable interfaces.

Inspect:

- OpenAPI or equivalent specs, API docs, SDKs, CLIs, webhooks, and examples
- MCP tools, resources, prompts, manifests, and integration docs
- sandbox/test mode, dry-run support, sample payloads, idempotency, side effects, and versioning
- browser-only workflows that lack API/tool alternatives

## Auth, Permissions, And Safety

Check whether agents can act safely and within intended boundaries.

Inspect:

- auth flows, scopes, tokens, tenant boundaries, consent, and user delegation
- crawler policy, rate limits, terms, attribution, and allowed-use guidance
- destructive-action safeguards, payment/order/booking boundaries, rollback paths, and approval points
- secrets in docs, examples, configs, logs, fixtures, and generated output

## Error Recovery And Determinism

Check whether agents can recover from failure without guessing.

Inspect:

- machine-readable errors, status codes, retries, rate-limit headers, timeouts, and pagination
- stable IDs, stable URLs, version compatibility, validation errors, partial failure behavior, and duplicate prevention
- status pages, incident messages, deprecation notices, and recovery instructions

## Documentation Freshness And Examples

Check whether docs are current and executable enough for agents to rely on.

Inspect:

- changelogs, release notes, migration guides, deprecation notes, and versioned docs
- runnable examples, SDK examples, cURL examples, sample payloads, fixtures, and test apps
- stale commands, stale screenshots, old endpoint names, and docs-to-implementation drift

## Handoff And Verification

Check whether agents can prove work and hand control back safely.

Inspect:

- receipts, confirmations, audit logs, transaction IDs, status endpoints, and downloadable records
- human review checkpoints, support paths, escalation routes, rollback instructions, and reconciliation guidance
- post-action state visibility, notifications, and evidence suitable for final user reports

## Priority Mapping

Classify findings by agent/user impact:

- `Critical`: blocks or endangers a core agent workflow, causes unsafe actions, or makes output likely to be materially wrong.
- `High`: makes a core workflow unreliable, opaque, unsafe, or difficult to automate.
- `Medium`: affects important secondary workflows, repeated use, recovery, freshness, or confidence.
- `Low`: polish or narrow-scope issue with limited agent impact.

For each finding, capture category, priority, evidence, affected agent/user path, impact, fix direction, and confidence.

## Category Score Rubric

Score each applicable category out of 10 after reviewing findings and evidence.

- `10`: no meaningful issues found; strong evidence across relevant routes, docs, APIs/tools, auth states, and recovery paths.
- `8-9`: minor issues only; no core agent workflow barriers.
- `6-7`: moderate issues affecting repeated use, secondary workflows, recovery, or confidence.
- `4-5`: serious issues affecting core workflows for some agents or task types.
- `1-3`: major blockers for discovery, understanding, safe action, or verification.
- `0`: category cannot be meaningfully used or evaluated because of a blocking readiness failure.

Use `N/A` only when a category genuinely does not apply. Use `Not assessed` when a category applies but was not evaluated. Exclude `N/A` and `Not assessed` categories from the final average and explain evidence limits.

Every assessed category score must include a one-line rationale naming the strongest evidence and the main reason the score is not higher.

## Final Score Rules

Calculate the final Beacon score as the average of applicable assessed category scores, rounded to one decimal.

Map the final score to a letter grade:

- `A`: 9.0-10
- `B`: 8.0-8.9
- `C`: 7.0-7.9
- `D`: 6.0-6.9
- `F`: 0-5.9

Apply grade caps after averaging:

- Any unresolved `Critical` finding applies a grade cap of `F`.
- Any category scored `0-3` applies a grade cap of `D`.
- Missing live evidence for important runtime action surfaces applies a grade cap of `B`.
- Missing API/tool execution evidence for an action-oriented product applies a grade cap of `C`.
- Incomplete crawl, blocked docs, missing credentials, or inaccessible discovery paths can apply a grade cap of `B` or lower when they prevent judging important agent workflows.

Report the cap as one field: `Grade cap: None` or `Grade cap: <cap>, <reason>`.
