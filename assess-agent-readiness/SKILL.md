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

Use Assess SEO as an optional adjunct only when the caller asks for classic SEO readiness, search growth, human organic traffic, keyword coverage, SERP competitiveness, title/meta optimization, local SEO, content strategy, backlinks, rankings, or traffic opportunity. For targets that are not public-search-facing, or when the caller only wants agent-readiness, omit Assess SEO from the report entirely.

Blocking behavior:

- Do not let `llms.txt` or other AI-oriented files compensate for broken conventional crawl foundations. Missing or broken `robots.txt`, sitemap discovery, indexability, canonicalization, redirects, structured data, or crawlable content can be an Assess Agent Readiness finding when it impairs agentic discovery, and it should be handed to Assess SEO when classic SEO impact is in scope.
- Do not expand Assess Agent Readiness into keyword research, SERP strategy, backlink review, local profile optimization, CTR-focused snippets, traffic forecasting, or ranking predictions. Recommend Assess SEO for those paths.
- Do not fail or lower an Assess Agent Readiness audit solely because Assess SEO was skipped or unavailable.

If classic SEO readiness or human organic-search performance is materially relevant to the user's agent-readiness question, add a short note recommending Assess SEO as a separate audit. If Assess SEO actually runs or directly affects an agent-readiness finding, report that evidence and its impact. Otherwise, do not mention Assess SEO in the final report.

## Required Audit Workflow

When asked to use Assess Agent Readiness:

1. Identify the target folder, URL, app, API, tool, documentation set, or artifact.
2. Read local instructions and product context first, such as `AGENTS.md`, `README.md`, API docs, OpenAPI specs, MCP docs, CLI docs, SDK docs, robots/crawl policy, sitemap files, and product docs.
3. Determine the system type, target users, target agents, public/private boundary, action surfaces, authentication model, and likely agent tasks.
4. Push for the strongest evidence practical before scoring: run the project when source is available and safe, inspect reachable production or development URLs, check live crawl/docs/API surfaces, and use lightweight network checks such as DNS, ping, headers, or HTTP probes when they clarify reachability or host behavior.
5. Research current agent-readiness sources before judging. Prefer current primary sources and say when a convention is emerging or disputed.
6. Inspect the implementation or live surface: routes, crawl policy, docs, content structure, metadata, structured data, APIs, schemas, tool protocols, auth, errors, examples, and handoff signals.
7. Capture findings by category, score each applicable category out of 10, then prioritize by agent/user impact.
8. Use `templates/ASSESS-AGENT-READINESS.md` as the report skeleton.

Mention verification limits only where they affect confidence, scoring, or grade caps.

Use `Assessment Coverage` as the first report section after the title, not a terse caveat list: state what was assessed, what was not assessed, what the caller can provide or permit for a deeper/fairer/more accurate assessment, and what that extra evidence would improve. Use `Start Here` as the report's single prioritized action plan. Do not add a second `Next Steps` section unless the caller explicitly wants a separate follow-up roadmap.

## Report Assembly Rules

Use the template as a skeleton, not as text to copy blindly. Fill every placeholder, delete empty optional sections, and do not leave template instructions or rationale about why a section exists in the final report.

- `Assessment Coverage`: write only report-facing bullets for `Assessed`, `Not assessed`, what the caller can provide or permit to improve confidence, and the expected impact of that evidence. Do not add a sentence explaining why the section appears first.
- `Start Here`: keep this as the single prioritized action plan. Do not duplicate it later as `Next Steps` unless the caller requested a separate roadmap.
- `Findings By Priority`: for each priority level, either list scoped findings or write one clear state such as `No scoped findings after review.` or `Not assessed; evidence limit: ...`.
- `Findings By Category`: populate the score table from the applicable assessed categories in `references/AUDIT-CATEGORIES.md`. Keep that reference file as the source of truth for category names, order, scoring rules, and grade caps.
- Category scoring: use `N/A` only when a category genuinely does not apply. Use `Not assessed` when a category applies but was not evaluated, explain the evidence limit in `Assessment Coverage`, and do not include `Not assessed` categories in the score table.
- Category detail blocks: repeat the generic category block once for each assessed category from `references/AUDIT-CATEGORIES.md`.

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
- Assess SEO status only when it is materially relevant, actually run, or directly affects an agent-readiness finding

Treat `llms.txt` as an optional emerging convention. Do not fail a system solely for missing `llms.txt` when the target has strong conventional crawlability, structured content, and agent-facing docs. Do treat it as a missed readiness opportunity when LLM-friendly orientation is important and no equivalent exists.

## Audit Categories, Prioritization, And Scoring

Use `references/AUDIT-CATEGORIES.md` as Assess Agent Readiness's source of truth for the category map, priority definitions, score rubric, final score rules, and grade-cap rules. Do not duplicate those definitions in `SKILL.md`; keep this file focused on execution flow, evidence expectations, report structure, boundaries, and when to consult the reference.

When running an audit, load that reference before the category pass, then adapt only for target-specific categories that the researched platform or user request clearly requires. Keep `N/A` and `Not assessed` handling aligned with the reference, and summarize skipped or limited categories in the report's `Assessment Coverage` section instead of scattering caveats throughout the report.

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
