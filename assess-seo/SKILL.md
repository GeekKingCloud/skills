---
name: assess-seo
description: Classic SEO readiness audit for websites, landing pages, documentation, local-business sites, ecommerce pages, or content libraries. Use when the caller wants evidence-backed assessment of crawl/index foundations, search intent, on-page metadata, content quality, internal linking, structured data, local/entity signals, performance/page experience, analytics evidence, competitive visibility, prioritized fixes, and clear separation from agent-readiness or ranking guarantees.
---

# Assess SEO

Audit whether a public web surface is ready to earn and sustain organic search visibility for human searchers. Focus on crawl/index foundations, query intent, page relevance, content usefulness, snippets, internal links, structured data, local/entity clarity, performance, measurement, and competitive search context.

Assess SEO is not a ranking guarantee, traffic forecast, paid search audit, brand strategy review, legal compliance review, accessibility audit, or agent-readiness certification. Use evidence-backed language and distinguish directly observed issues from opportunities, hypotheses, and items that need Search Console, analytics, backlink, or rank-tracking access.

## Quick Start

When asked to use Assess SEO:

1. Identify the target site, page set, business, market, geography, content type, and search goals.
2. Read local project context first when source is available, such as `AGENTS.md`, README files, CMS docs, route files, SEO config, content templates, structured data, sitemap generation, redirects, and analytics docs.
3. Determine the evidence mode: `Source + live`, `Source only`, `Live only`, or `Artifact only`.
4. Research the current search baseline before judging. Prefer current primary sources and record sources used with access dates.
5. Inspect the live or source surface: crawl policy, indexability, sitemap, canonicals, redirects, status codes, rendered content, metadata, headings, structured data, links, media, performance signals, local/entity data, and visible conversion paths.
6. Compare representative pages against likely queries, search intent, SERP features, and direct competitors when the target market is known.
7. Capture findings by category, score each applicable category out of 10, then prioritize by expected search/user impact.
8. Use `templates/ASSESS-SEO.md` as the report skeleton.

Mention verification limits only where they affect confidence, scoring, or grade caps.

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

## Audit Categories

Use these categories as the default pass list, in this order. Omit categories that clearly do not apply, and add target-specific categories when the researched platform requires them.

### Crawl, Indexing, And Technical Foundation

Inspect:
- `robots.txt`, sitemap files, indexability, canonical tags, redirects, status codes, broken links, duplicate routes, pagination, hreflang, and faceted navigation
- crawlable rendered HTML, JavaScript rendering risks, SSR/static fallbacks, blocked assets, and soft 404 behavior
- URL structure, migration state, redirect chains, mixed protocols, trailing-slash variants, and environment leakage

Judge whether search engines can discover, crawl, render, index, and consolidate the right pages.

### Search Intent And Query Coverage

Inspect:
- target queries, implied audience, funnel stage, geography, and task intent
- page-to-query fit, topic gaps, cannibalization, thin coverage, and mismatched landing pages
- SERP features, competing result types, commercial/local/informational intent, and likely answer formats

Judge whether the site has the right pages for the searches it wants to win.

### On-Page Metadata And Snippet Readiness

Inspect:
- title tags, meta descriptions, headings, canonical display names, Open Graph/Twitter metadata, and visible page summaries
- snippet clarity, uniqueness, truncation risk, query relevance, dates, prices, availability, reviews, and entity naming
- duplicate or missing titles/descriptions and templates that produce weak search snippets

Judge whether search results can present the page clearly and attract qualified clicks.

### Content Quality, Usefulness, And Trust

Inspect:
- main content depth, originality, helpfulness, accuracy, freshness, authorship, citations, expertise signals, and source provenance
- thin pages, boilerplate-heavy pages, AI-generated or duplicated content risks, doorway patterns, and unsupported claims
- media alternatives, FAQs, comparisons, examples, policies, and practical user task completion

Judge whether the content deserves to satisfy the search intent better than alternatives.

### Information Architecture And Internal Linking

Inspect:
- navigation, breadcrumbs, hub pages, related links, footer/header links, orphan pages, crawl depth, and anchor text
- category/tag taxonomy, faceted paths, pagination, topic clusters, and duplicate internal routes
- important pages that lack internal prominence or contextual links

Judge whether users and crawlers can understand page relationships and priority.

### Structured Data And Rich Result Eligibility

Inspect:
- Schema.org JSON-LD, microdata, RDFa, entity consistency, required/recommended fields, and page-type fit
- product, local business, organization, article, FAQ, breadcrumb, review, event, job, software, course, or documentation schema when relevant
- validation errors, spammy markup, content/markup mismatch, and unsupported rich-result expectations

Judge whether structured data accurately clarifies entities and can qualify for relevant search features.

### Local, Entity, And Brand Signals

Inspect:
- business name, address, phone, service area, hours, locations, staff, credentials, reviews, maps/profile consistency, and local landing pages
- organization/person/product entity clarity, sameAs links, knowledge graph cues, brand naming, and reputation evidence
- inconsistent NAP data, missing location context, weak trust pages, and unclear ownership

Judge whether search systems and users can identify who or what the site represents.

### Performance, Mobile, And Page Experience

Inspect:
- mobile usability, Core Web Vitals evidence, loading behavior, image/video weight, layout shifts, intrusive interstitials, ads, consent banners, and font/render blocking
- template-level performance issues and page types most likely to affect organic entry pages
- lab data, field data, or observed interaction limits depending on available evidence

Judge whether organic visitors can use the page comfortably after clicking from search.

### Measurement, Diagnostics, And Change Control

Inspect:
- Search Console, analytics, rank tracking, crawl exports, server logs, sitemap submission, redirect maps, release process, changelogs, and SEO QA
- conversion events, goal tracking, attribution caveats, annotations, monitoring, and regression checks
- missing data needed to prioritize, verify, or debug SEO changes

Judge whether the team can measure organic visibility and detect regressions.

### Competitive Visibility And Off-Site Signals

Inspect:
- visible SERP competitors, backlink/profile evidence when available, reviews, citations, marketplaces, directories, social/profile consistency, and content differentiation
- direct competitors' page types, content depth, snippets, schema, local presence, and authority cues
- off-site gaps that affect trust, entity clarity, or ability to compete

Judge whether the site is positioned against the results it must displace.

## Prioritization

Prioritize by expected search/user impact:

- `Critical`: likely blocks crawling, indexing, consolidation, or trust for core organic pages; creates serious spam/manual-action risk; or makes the audit's main search goal impossible to evaluate.
- `High`: materially weakens core query coverage, snippets, content usefulness, internal authority flow, local/entity clarity, or measurement.
- `Medium`: affects important secondary pages, repeated templates, visibility confidence, page experience, or prioritization.
- `Low`: polish or narrow-scope issue with limited search impact.

For each finding, include:

- `Category`
- `Priority`
- `Evidence`
- `Search/user impact`
- `Why it matters`
- `Fix direction`
- `Confidence`

Use file paths, URLs, route names, rendered text, metadata values, schema excerpts, crawl results, SERP observations, screenshots, or data-export references where practical. Separate confirmed findings from likely risks.

## Grading And Scoring

Grade practical SEO readiness, not general product quality or official search-engine conformance.

Score only applicable categories. Mark categories that genuinely do not apply as `N/A` and exclude them from the average. Mark categories that apply but were not evaluated as `Not assessed`, exclude them from the average, and explain the evidence limit. Every assessed score must cite the strongest evidence and the main reason the score is not higher.

Calculate the final Assess SEO score as the average of applicable assessed category scores, rounded to one decimal.

Map the final Assess SEO score to a letter grade:

- `A`: 9.0-10
- `B`: 8.0-8.9
- `C`: 7.0-7.9
- `D`: 6.0-6.9
- `F`: 0-5.9

Apply grade caps after averaging:

- any unresolved `Critical` finding applies a grade cap of `F`
- any core crawl/index category scored `0-3` applies a grade cap of `D`
- missing live evidence for a public website applies a grade cap of `B`
- missing rendered-page evidence for a JavaScript-heavy site applies a grade cap of `C` when it prevents judging indexable content
- missing Search Console/analytics/backlink/rank data can cap only the affected measurement, off-site, or competitive categories unless the caller asked for a data-backed growth plan
- unsupported ranking, traffic, or competitor claims must be removed or marked as hypotheses; do not inflate scores from unverified assumptions

Report the cap as one field: `Grade cap: None` when no cap applies, or `Grade cap: <cap>, <reason>` when a cap applies.

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
