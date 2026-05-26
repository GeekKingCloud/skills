---
name: assess-seo
description: Classic SEO readiness audit for websites, landing pages, documentation, local-business sites, ecommerce pages, or content libraries. Use when the caller wants evidence-backed assessment of crawl/index foundations, search intent, on-page metadata, content quality, internal linking, structured data, local/entity signals, performance/page experience, analytics evidence, competitive visibility, prioritized fixes, and clear separation from agent-readiness or ranking guarantees.
---

# Assess SEO

Audit whether a public web surface is ready to earn and sustain organic search visibility for human searchers. Focus on crawl/index foundations, query intent, page relevance, content usefulness, snippets, internal links, structured data, local/entity clarity, performance, measurement, and competitive search context.

Assess SEO is not a ranking guarantee, traffic forecast, paid search audit, brand strategy review, legal compliance review, accessibility audit, or agent-readiness certification. Use evidence-backed language and distinguish directly observed issues from opportunities, hypotheses, and items that need Search Console, analytics, backlink, or rank-tracking access.

## Required Audit Workflow

When asked to use Assess SEO:

1. Identify the target site, page set, business, market, geography, content type, and search goals.
2. Read local project context first when source is available, such as `AGENTS.md`, README files, CMS docs, route files, SEO config, content templates, structured data, sitemap generation, redirects, and analytics docs.
3. Determine the evidence mode: `Source + live`, `Source only`, `Live only`, or `Artifact only`.
4. Push for the strongest evidence practical before scoring: run the project when source is available and safe, inspect reachable production or development URLs, check live crawl files and route status, and use lightweight network checks such as DNS, ping, headers, or HTTP probes when they clarify reachability or host behavior.
5. Research the current search baseline before judging. Prefer current primary sources and record sources used with access dates.
6. Inspect the live or source surface: crawl policy, indexability, sitemap, canonicals, redirects, status codes, rendered content, metadata, headings, structured data, links, media, performance signals, local/entity data, and visible conversion paths.
7. Compare representative pages against likely queries, search intent, SERP features, and direct competitors when the target market is known.
8. Capture findings by category, score each applicable category out of 10, then prioritize by expected search/user impact.
9. Use `templates/ASSESS-SEO.md` as the report skeleton.

Mention verification limits only where they affect confidence, scoring, or grade caps.

Use `Assessment Coverage` as the first report section after the title, not a terse caveat list: state what was assessed, what was not assessed, what the caller can provide or permit for a deeper/fairer/more accurate assessment, and what that extra evidence would improve. Use `Start Here` as the report's single prioritized action plan. Do not add a second `Next Steps` section unless the caller explicitly wants a separate follow-up roadmap.

## Relationship To Assess Agent Readiness

Assess Agent Readiness and Assess SEO overlap on technical discovery, but they answer different questions.

- Assess SEO asks whether the target can compete for organic search visibility and satisfy human search intent.
- Assess Agent Readiness asks whether agents and agentic crawlers can discover, understand, act on, and verify the system.

Use Assess Agent Readiness as an `Optional adjunct gate` when the target has important agent-facing, AI-crawler, API/tool, documentation, or machine-action surfaces. Skip Assess Agent Readiness when the target is a conventional marketing/content site and the caller only wants classic SEO readiness. If Assess Agent Readiness is unavailable but agent-facing discovery is relevant, run a fallback pass covering agent/crawler orientation, `llms.txt` or equivalent, structured content extractability, and action-surface clarity.

Blocking behavior:

- Do not let `llms.txt` or AI-oriented files compensate for broken classic crawl/index foundations. Missing or broken `robots.txt`, sitemap discovery, indexability, canonicalization, or crawlable content can be an Assess SEO blocker even when agent-facing files exist.
- Do not expand Assess SEO into agent instructions, MCP/tool protocols, API actionability, auth delegation, agent-safe execution, deterministic recovery, or handoff verification except as a short relevance note that routes the work to Assess Agent Readiness.
- Do not fail an Assess SEO audit solely because Assess Agent Readiness was skipped or unavailable. Report the skip reason and whether agentic readiness remains unassessed.
- If Assess Agent Readiness finds a critical machine-discovery issue that also affects public crawlability, reflect it in Assess SEO's technical findings and grade cap.

Final-report evidence when Assess Agent Readiness is used, skipped, or unavailable:

- `Assess Agent Readiness adjunct: Ran/Skipped/Unavailable`
- `Reason: ...`
- `Impact on Assess SEO score: None/technical finding/grade cap/lower confidence`

## References

- Read `references/RESEARCH-SOURCES.md` before auditing when the source list is not already obvious from the request and local project docs.
- Read `references/AUDIT-CATEGORIES.md` when planning or running the category pass.
- Keep `SKILL.md` as the execution path; use reference files for expanded source and category details.

## Research First

Start every audit with a current research baseline because search guidance, SERP features, structured data eligibility, and crawler behavior change over time.

Use the most relevant sources for the target:

- Google Search Central for crawling, indexing, ranking systems, spam policies, structured data, JavaScript SEO, internationalization, and Search Console concepts.
- Bing Webmaster documentation when Bing visibility matters.
- Schema.org and search-engine structured data guidance when evaluating semantic markup and rich-result eligibility.
- web.dev guidance and field or lab performance data when evaluating Core Web Vitals and page experience.
- Platform-specific docs for CMS, ecommerce, local-business, documentation, or framework SEO behavior.
- Search Console, analytics, rank-tracking, log files, backlink tools, and CMS data when the caller provides them.
- Project-local docs, routes, content models, redirects, sitemap generation, release notes, and SEO plugins.

In the final report, list the sources actually used. If live research or private data was unavailable, say that clearly and treat ranking, demand, backlink, and traffic claims as lower confidence.

## Evidence Modes

Use one evidence mode:

- `Source + live`: code, config, docs, or CMS/source artifacts were inspected with a running website.
- `Source only`: code, config, docs, or CMS/source artifacts were inspected without live verification.
- `Live only`: a public website was inspected without source.
- `Artifact only`: docs, exports, screenshots, crawl exports, Search Console screenshots, analytics exports, recordings, or static files were inspected without interactive access.

Missing Search Console, analytics, backlink, rank-tracking, or server-log access is not a grade cap by itself. It lowers confidence or prevents scoring categories that depend on those data sources. Missing live crawl evidence can cap the grade when technical indexability or rendered content cannot be verified.

## Standards Baseline

Report standards, official guidance, and Assess SEO's practical score separately. Assess SEO scores are internal readiness grades, not official ranking, rich-result, Search Console, or SEO certification claims.

Before grading, define:

- target site type and market
- target audience and search goals
- representative query themes or known keywords
- relevant standards, search-engine guidance, and platform conventions
- evaluated scope
- evidence mode
- evidence limits
- Assess Agent Readiness adjunct status when agent-facing readiness is relevant

Avoid claiming that any fix guarantees rankings, traffic, citations, snippets, or AI retrieval.

## Audit Categories, Prioritization, And Scoring

Use `references/AUDIT-CATEGORIES.md` as Assess SEO's source of truth for the category map, priority definitions, score rubric, final score rules, and grade-cap rules. Do not duplicate those definitions in `SKILL.md`; keep this file focused on execution flow, evidence expectations, report structure, boundaries, and when to consult the reference.

When running an audit, load that reference before the category pass, then adapt only for target-specific categories that the researched platform or user request clearly requires. Keep `N/A` and `Not assessed` handling aligned with the reference, and summarize skipped or limited categories in the report's `Assessment Coverage` section instead of scattering caveats throughout the report.

## Live Or Black-Box Targets

Assess SEO can audit a public website without source code, but evidence changes.

For live-only targets:

- discover public routes through navigation, footer links, sitemap files, robots hints, indexed search results, crawl tools, and in-page links
- inspect response codes, redirects, canonical tags, metadata, headings, rendered text, structured data, mobile behavior, and representative templates
- compare visible SERPs only when searches are allowed and geography/personalization limits are stated
- avoid claiming implementation causes when only external behavior is visible
- record geography, device, personalization, login state, crawler limits, blocked routes, and unavailable private data as evidence limits
- score only observed behavior and reachable states

## Boundaries

Do not:

- claim guaranteed rankings, traffic, snippets, indexing, rich results, citations, conversions, or AI retrieval
- treat `llms.txt` or AI-specific files as replacements for `robots.txt`, sitemaps, crawlable HTML, canonicals, or structured data
- confuse SEO readiness with accessibility, agent readiness, paid search, brand strategy, public relations, legal compliance, or conversion-rate optimization
- perform an agent-readiness audit, MCP/OpenAPI actionability review, coding-agent instruction review, agent safety review, or handoff-verification review inside Assess SEO unless the caller explicitly asks for a lightweight note and you clearly recommend Assess Agent Readiness for the full pass
- invent Search Console, analytics, backlink, rank, or competitor data without evidence
- recommend cloaking, doorway pages, scraped content, link schemes, hidden text, or bypassing robots, auth, rate limits, or terms
- bury technical indexability blockers under content or marketing recommendations

Do:

- distinguish observed facts from recommendations and hypotheses
- state review scope and evidence limits
- connect findings to realistic search intents and user outcomes
- prefer primary sources and current documentation
- give a practical first-fix sequence
- recommend Assess Agent Readiness when agent-facing discovery or machine-action readiness is materially in scope

## Orchestrator Use

Other workflow skills may use Assess SEO as an optional adjunct gate when a target has a public organic-search surface. Report evidence mode, score, grade cap, blockers, Assess Agent Readiness adjunct status, and skipped or not-assessed categories clearly enough for the parent workflow to decide whether SEO-readiness issues block release readiness. Assess SEO does not depend on those orchestrator skills; it remains a standalone SEO-readiness audit skill.
