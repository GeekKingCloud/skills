---
name: assess-agent-readiness
description: Agent-readiness audit for websites, apps, APIs, tools, documentation, or codebases. Use when the caller wants research-first assessment of discoverability, crawl policy, agent instructions, structured content, API/tool actionability, MCP/OpenAPI surfaces, docs freshness, safety boundaries, handoff evidence, and practical next steps for coding agents or agentic crawlers, while keeping classic SEO growth and ranking work separate.
---

# Assess Agent Readiness

Audit how ready a system is for coding agents, agentic crawlers, and agent-mediated user workflows. Focus on whether an agent can discover the system, understand what it offers, choose safe actions, execute or hand off work, recover from errors, and cite or verify results.

This is not an SEO guarantee, AI search certification, crawler compliance claim, MCP certification, OpenAPI certification, or ranking prediction. Use direct, evidence-backed language and distinguish accepted standards from emerging conventions.

## Relationship To Assess SEO

Assess Agent Readiness and Assess SEO overlap on technical discovery, but they answer different questions.

- Assess Agent Readiness asks whether agents and agentic crawlers can discover, understand, use, and verify a system.
- Assess SEO asks whether a public web surface is ready to earn organic search visibility for human searchers.

Use Assess SEO as an `Optional adjunct gate` when the caller asks for classic SEO readiness, search growth, human organic traffic, keyword coverage, SERP competitiveness, title/meta optimization, local SEO, content strategy, backlinks, rankings, or traffic opportunity. Skip Assess SEO when the target is not public-search-facing or the caller only wants agent-readiness.

Blocking behavior:

- Do not let `llms.txt` or other AI-oriented files compensate for broken conventional crawl foundations. Missing or broken `robots.txt`, sitemap discovery, indexability, canonicalization, redirects, structured data, or crawlable content can be an Assess Agent Readiness finding when it impairs agentic discovery, and it should be handed to Assess SEO when classic SEO impact is in scope.
- Do not expand Assess Agent Readiness into keyword research, SERP strategy, backlink review, local profile optimization, CTR-focused snippets, traffic forecasting, or ranking predictions. Recommend Assess SEO for those paths.
- Do not fail an Assess Agent Readiness audit solely because Assess SEO was skipped or unavailable. Report the skip reason and whether classic SEO readiness remains unassessed.

Final-report evidence when Assess SEO is used, skipped, or unavailable:

- `Assess SEO adjunct: Ran/Skipped/Unavailable`
- `Reason: ...`
- `Impact on Assess Agent Readiness score: None/discovery finding/grade cap/lower confidence`

## Quick Start

When asked to use Assess Agent Readiness:

1. Identify the target folder, URL, app, API, tool, documentation set, or artifact.
2. Read local instructions and product context first, such as `AGENTS.md`, `README.md`, API docs, OpenAPI specs, MCP docs, CLI docs, SDK docs, robots/crawl policy, sitemap files, and product docs.
3. Determine the system type, target users, target agents, public/private boundary, action surfaces, authentication model, and likely agent tasks.
4. Research current agent-readiness sources before judging. Prefer current primary sources and say when a convention is emerging or disputed.
5. Inspect the implementation or live surface: routes, crawl policy, docs, content structure, metadata, structured data, APIs, schemas, tool protocols, auth, errors, examples, and handoff signals.
6. Capture findings by category, score each applicable category out of 10, then prioritize by agent/user impact.
7. Use `templates/ASSESS-AGENT-READINESS.md` as the report skeleton.

Mention verification limits only where they affect confidence, scoring, or grade caps.

## References

- Read `references/RESEARCH-SOURCES.md` before auditing when the target platform, standards, or source list is not already obvious from the request and local project docs.
- Read `references/AUDIT-CATEGORIES.md` when planning or running the category pass.
- Keep `SKILL.md` as the execution path; use reference files for expanded source and category details.

## Research First

Start every audit with a current research baseline. The agent-readiness field is moving quickly, and many practices are proposals rather than stable requirements.

Use the most relevant sources for the target:

- Google Search Central guidance for generative AI search, crawling, indexing, structured content, and technical SEO fundamentals.
- web.dev agent-friendly website guidance when evaluating browser-agent behavior, semantic UI, stable layouts, DOM structure, and accessibility-tree signals.
- RFC 9309 and search-engine documentation for `robots.txt`, crawl policy, indexing, and sitemap behavior.
- `llms.txt` as an emerging Markdown convention for LLM-friendly site orientation, not a required standard or guaranteed retrieval signal.
- `AGENTS.md` when evaluating repository or coding-agent instructions.
- OpenAPI and API documentation guidance when evaluating API action surfaces.
- MCP documentation when evaluating tool, resource, prompt, or agent integration surfaces.
- Schema.org and structured data guidance when evaluating semantic content.
- Project-local docs, SDKs, changelogs, examples, status pages, support docs, and policy pages.

In the final report, list the sources actually used. If live research was unavailable, say that clearly and treat standards-sensitive claims as lower confidence.

## Evidence Modes

Use one evidence mode:

- `Source + live`: code, config, docs, or specs were inspected with a running website, API, app, or tool.
- `Source only`: code, config, docs, or specs were inspected without live verification.
- `Live only`: a public website, app, API, or tool was inspected without source.
- `Artifact only`: docs, exports, specs, screenshots, recordings, or static files were inspected without interactive access.

Missing source code is not a grade cap by itself. Missing live behavior, unreachable APIs, blocked crawl discovery, missing auth context, or unavailable tool execution can lower confidence or cap the grade when they prevent judging important agent workflows.

## Standards Baseline

Report standards and conventions separately from the practical Assess Agent Readiness score. Assess Agent Readiness scores are internal readiness grades, not official SEO, AI search, crawler, protocol, API, or compliance claims.

Before grading, define:

- target system type
- relevant standards, specs, and conventions
- target agents or agent tasks
- evaluated scope
- evidence mode
- evidence limits
- Assess SEO adjunct status when classic SEO readiness is relevant

Treat `llms.txt` as an optional emerging convention. Do not fail a system solely for missing `llms.txt` when the target has strong conventional crawlability, structured content, and agent-facing docs. Do treat it as a missed readiness opportunity when LLM-friendly orientation is important and no equivalent exists.

## Audit Categories

Use these categories as the default pass list, in this order. Omit categories that clearly do not apply, and add target-specific categories when the researched platform requires them.

### Discovery And Crawl Policy

Inspect:
- `robots.txt`, crawl directives, crawler allow/deny intent, and AI crawler policy
- sitemap files, route indexes, canonical URLs, redirects, status codes, and broken links
- public route discovery through navigation, in-page links, docs indexes, and search results
- `llms.txt`, Markdown variants, text exports, and low-boilerplate indexes when present
- JavaScript rendering, SSR/static fallbacks, pagination, locale routing, and duplicate content

Judge whether an agent can find the right public or authorized surfaces without guessing.

### Agent Instructions And Orientation

Inspect:
- `AGENTS.md`, README, quick starts, docs landing pages, capability maps, and task-oriented guides
- setup, run, test, build, deploy, authentication, and environment instructions
- "what can this system do" and "when should I use it" guidance
- repo structure, ownership boundaries, examples, and known limitations
- API/tool orientation for non-human or automated consumers

Judge whether a new agent can quickly understand the system and act without rediscovering basic context.

### Content Extractability And Semantics

Inspect:
- semantic HTML, headings, main content separation, metadata, and structured data
- Schema.org, JSON-LD, Open Graph, canonical metadata, and entity clarity
- boilerplate-to-content ratio, hidden critical content, PDFs/images-only content, and script-only content
- localized content, dates, authorship, source provenance, and citation clarity
- concise answerable sections, summaries, FAQs, and machine-readable context where useful

Judge whether agents can extract accurate meaning without fragile scraping or hallucination-prone inference.

### Action Surfaces And Protocols

Inspect:
- OpenAPI or equivalent API descriptions, endpoint docs, schemas, SDKs, CLIs, webhooks, and examples
- MCP servers, tools, resources, prompts, manifests, or agent-specific integration docs when present
- sandbox/test modes, sample credentials, dry-run support, and local/dev workflows
- action preconditions, inputs, outputs, side effects, idempotency, and versioning
- form and browser-only workflows that lack an API or tool alternative

Judge whether agents can do useful work through stable interfaces instead of brittle browser emulation.

### Auth, Permissions, And Safety

Inspect:
- auth flows, scopes, tokens, tenant boundaries, consent, and user delegation
- crawler policy, rate limits, abuse controls, and bot contact/escalation paths
- destructive-action boundaries, confirmation requirements, payment/order/booking safeguards, and rollback paths
- privacy, data retention, terms, attribution, and allowed-use policy for automated access
- secret handling in docs, examples, configs, and logs

Judge whether agents can act safely and within intended permission boundaries.

### Error Recovery And Determinism

Inspect:
- machine-readable errors, status codes, retry guidance, pagination, cursors, timeouts, and rate-limit headers
- deterministic examples, stable identifiers, stable URLs, and version compatibility
- validation errors, partial failures, idempotency keys, duplicate prevention, and recovery instructions
- observability, status pages, deprecation notices, and incident messaging

Judge whether agents can recover from failure without guessing or repeating unsafe actions.

### Documentation Freshness And Examples

Inspect:
- docs freshness, changelogs, release notes, deprecation notes, migration guides, and versioned docs
- runnable examples, SDK examples, cURL examples, sample payloads, and test fixtures
- stale screenshots, old command names, old endpoint names, and unsupported flows
- docs-to-implementation drift and missing examples for core workflows

Judge whether docs are current enough for agents to rely on during execution.

### Handoff And Verification

Inspect:
- receipts, confirmations, audit logs, status endpoints, transaction IDs, and downloadable records
- human review checkpoints, approval flows, support routes, escalation paths, and rollback instructions
- post-action state visibility, notifications, and reconciliation guidance
- reportable evidence an agent can return to the user after completing work

Judge whether agents can prove what happened and hand control back to a user safely.

## Prioritization

Prioritize by agent/user impact:

- `Critical`: blocks or endangers a core agent workflow, causes unsafe actions, or makes agent output likely to be materially wrong.
- `High`: makes a core workflow unreliable, opaque, unsafe, or difficult to automate.
- `Medium`: affects important secondary workflows, repeated use, recovery, freshness, or confidence.
- `Low`: polish or narrow-scope issue with limited agent impact.

For each finding, include:

- `Category`
- `Priority`
- `Evidence`
- `Who or what is affected`
- `Why it matters`
- `Fix direction`
- `Confidence`

Use file paths, URLs, endpoint names, schemas, route names, screenshots, or response examples where practical. Separate confirmed findings from likely risks.

## Grading And Scoring

Grade practical agent readiness, not general product quality or official standards conformance.

Score only applicable categories. Mark categories that genuinely do not apply as `N/A` and exclude them from the average. Mark categories that apply but were not evaluated as `Not assessed`, exclude them from the average, and explain the evidence limit. Every assessed score must cite the strongest evidence and the main reason the score is not higher.

Calculate the final Assess Agent Readiness score as the average of applicable assessed category scores, rounded to one decimal.

Map the final Assess Agent Readiness score to a letter grade:

- `A`: 9.0-10
- `B`: 8.0-8.9
- `C`: 7.0-7.9
- `D`: 6.0-6.9
- `F`: 0-5.9

Apply grade caps after averaging:

- any unresolved `Critical` finding applies a grade cap of `F`
- any applicable category scored `0-3` applies a grade cap of `D`
- missing live evidence for a system with important runtime action surfaces applies a grade cap of `B`
- missing API/tool execution evidence for an action-oriented product applies a grade cap of `C`
- incomplete crawl, blocked docs, missing credentials, or inaccessible discovery paths can apply a grade cap of `B` or lower when they prevent judging important agent workflows

Report the cap as one field: `Grade cap: None` when no cap applies, or `Grade cap: <cap>, <reason>` when a cap applies.

## Live Or Black-Box Targets

Assess Agent Readiness can audit a live website, app, API, or tool without source code, but the evidence changes.

For live-only targets:

- discover public routes through navigation, footer links, sitemap files, robots hints, indexed search results, docs indexes, `llms.txt`, and in-page links
- inspect response codes, headers, metadata, structured data, canonical URLs, rendered text, docs indexes, and public API/tool descriptions
- test sample API/tool calls only when credentials and permission are available
- avoid claiming implementation causes when only external behavior is visible
- record credentials, geography, feature flags, rate limits, robots policy, blocked routes, and authentication limits as evidence limits
- score only observed behavior and reachable states

## Boundaries

Do not:

- claim official agent-readiness certification
- claim guaranteed ranking, citation, retrieval, or crawler behavior
- treat `llms.txt` as required by Google or any other system without source-specific evidence
- treat `llms.txt` or AI-oriented files as replacements for `robots.txt`, sitemaps, crawlable HTML, canonicals, redirects, or structured data
- perform keyword research, backlink review, local SEO/profile optimization, SERP strategy, or ranking/traffic forecasts inside Assess Agent Readiness unless the caller explicitly asks for a lightweight note and you clearly recommend Assess SEO for the full pass
- confuse human accessibility with the Assess Agent Readiness scope
- invent API/tool support without evidence
- recommend bypassing auth, rate limits, robots policy, or terms of service
- bury safety and consent risks under discovery or SEO language

Do:

- distinguish accepted standards from proposals and conventions
- state review scope and evidence limits
- connect findings to realistic agent tasks and user outcomes
- prefer primary sources and current documentation
- give a practical first-fix sequence
- recommend Assess SEO when classic SEO readiness or human organic-search performance is materially in scope
- recommend live API/tool/browser checks when source evidence is insufficient

## Orchestrator Use

Other workflow skills may use Assess Agent Readiness as an optional adjunct gate when a target has an agent-facing surface. Report evidence mode, score, grade cap, blockers, and skipped or not-assessed categories clearly enough for the parent workflow to decide whether agent-readiness issues block release readiness. Assess Agent Readiness does not depend on those orchestrator skills; it remains a standalone agent-readiness audit skill.
