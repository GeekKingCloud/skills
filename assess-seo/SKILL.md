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
4. Determine site-type category applicability before scoring, including which categories are applicable, `N/A`, or `Not assessed` because evidence such as target queries, geography, Search Console, analytics, rank, backlink, crawl, or competitor data is unavailable.
5. Push for the strongest evidence practical before scoring: run the project when source is available and safe, inspect reachable production or development URLs, check live crawl files and route status, and use lightweight network checks such as DNS, ping, headers, or HTTP probes when they clarify reachability or host behavior.
6. Research the current search baseline before judging. Prefer current primary sources and record sources used with access dates.
7. Inspect the live or source surface: crawl policy, indexability, sitemap, canonicals, redirects, status codes, rendered content, metadata, headings, structured data, links, media, performance signals, local/entity data, and visible conversion paths.
8. Compare representative pages against likely queries, search intent, SERP features, and direct competitors when the target market is known.
9. Capture findings by category, score each applicable category out of 10, then prioritize by expected search/user impact.
10. Use `templates/ASSESS-SEO.md` as the report skeleton.

Mention verification limits only where they affect confidence, scoring, or grade caps.

Use `Assessment Coverage` as the first report section after the title, not a terse caveat list: state what was assessed, what was not assessed, what the caller can provide or permit for a deeper/fairer/more accurate assessment, and what that extra evidence would improve. Use `Start Here` as the report's single prioritized action plan. Do not add a second `Next Steps` section unless the caller explicitly wants a separate follow-up roadmap.

## Audit Mode And Missing Evidence

Default to a report-only SEO audit. Do not change crawl/index settings, redirects, metadata, content, internal links, structured data, analytics, or site templates unless the caller requests remediation. When remediation is requested, keep the pre-change assessment distinct from post-change checks and re-grade only from verified current search-facing evidence.

Infer site type, market, search goal, and representative intent from the caller's prompt, target pages, source, visible content, or live search surface. Ordinary missing private or market evidence is not a stop gate: continue, mark affected applicable categories `Not assessed`, and apply the reference's grade limits. Ask only when the target or main search goal is genuinely indeterminate. If the available crawl, page, or intent evidence cannot support a meaningful judgment of that goal, report findings and evidence needs as `Not graded` instead of averaging a partial view.

## Report Assembly Rules

Use the template as a skeleton, not as text to copy blindly. Fill every placeholder, delete empty optional sections, and do not leave template instructions or rationale about why a section exists in the final report.

- `Assessment Coverage`: write only report-facing bullets for `Assessed`, `Not assessed`, what the caller can provide or permit to improve confidence, and the expected impact of that evidence. Do not add a sentence explaining why the section appears first.
- `Category Applicability`: summarize which categories were scored, marked `N/A`, or marked `Not assessed`, and why. Do not quietly score categories that depend on unavailable target queries, market/geography, private analytics, backlink/rank data, or competitor evidence.
- `Start Here`: keep this as the single prioritized action plan. Do not duplicate it later as `Next Steps` unless the caller requested a separate roadmap.
- `Findings By Priority`: for each priority level, either list scoped findings or write one clear state such as `No scoped findings after review.` or `Not assessed; evidence limit: ...`.
- `Findings By Category`: populate the score table from the applicable assessed categories in `references/AUDIT-CATEGORIES.md`. Keep that reference file as the source of truth for category names, order, scoring rules, and grade caps.
- Category scoring: use `N/A` only when a category genuinely does not apply; it neither counts nor caps the grade. Use `Not assessed` when a category applies but was not evaluated, explain the evidence limit in `Assessment Coverage`, and do not include `Not assessed` categories in the score table.
- Category detail blocks: repeat the generic category block once for each assessed category from `references/AUDIT-CATEGORIES.md`.

## Relationship To Assess Agent Readiness

Assess Agent Readiness and Assess SEO overlap on technical discovery, but they answer different questions.

- Assess SEO asks whether the target can compete for organic search visibility and satisfy human search intent.
- Assess Agent Readiness asks whether solution or coding agents can discover, understand, retrieve from, act on, and verify agent-facing data and action surfaces.

Use Assess Agent Readiness as an optional adjunct only when the target has important agent-facing, AI-crawler, API/tool, documentation, or machine-action surfaces and that scope is materially relevant to the user's SEO question. For conventional marketing/content sites where the caller only wants classic SEO readiness, omit Assess Agent Readiness from the report entirely.

Blocking behavior:

- Do not let `llms.txt` or AI-oriented files compensate for broken classic crawl/index foundations. Missing or broken `robots.txt`, sitemap discovery, indexability, canonicalization, or crawlable content can be an Assess SEO blocker even when agent-facing files exist.
- Do not expand Assess SEO into agent instructions, MCP/tool protocols, API actionability, auth delegation, agent-safe execution, deterministic recovery, or handoff verification except as a short relevance note that routes the work to Assess Agent Readiness.
- Do not fail or lower an Assess SEO audit solely because Assess Agent Readiness was skipped or unavailable.
- If Assess Agent Readiness finds a critical machine-discovery issue that also affects public crawlability, reflect it in Assess SEO's technical findings and grade cap.

If agent-facing discovery or machine-action readiness is materially relevant to the user's SEO question, add a short note recommending Assess Agent Readiness as a separate audit. If Assess Agent Readiness actually runs or directly affects an SEO finding, report that evidence and its impact. Otherwise, do not mention Assess Agent Readiness in the final report.

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

## Site-Type And Evidence Defaults

Before scoring, decide which categories apply to the target's site type and evidence. Use this section to avoid inflating scores from weak or unavailable data.

- Crawl, indexing, metadata, content, internal linking, structured data, and page experience usually apply to public websites, landing pages, documentation sites, ecommerce pages, local-business sites, and content libraries.
- Search intent and query coverage require stated search goals, representative query themes, known keywords, or enough market/page evidence to derive them responsibly. If none are available, mark the category `Not assessed` or keep findings explicitly preliminary instead of assigning a confident score.
- Local, entity, and brand signals apply when the target represents a business, location, service area, person, organization, product, venue, or brand that search systems and users need to identify. Mark local-specific checks `N/A` for non-local products or docs, but keep entity/brand clarity when ownership or source trust matters.
- Measurement, diagnostics, and change control require Search Console, analytics, crawl exports, logs, rank tracking, release records, or equivalent project evidence. If those are unavailable, mark unavailable subareas `Not assessed`; do not penalize unrelated public-page readiness unless the caller asked for a data-backed growth plan.
- Competitive visibility and off-site signals require a known market/geography, representative SERPs, competitor set, review/citation evidence, backlink/profile data, or caller-provided competitive context. If those are missing, mark the category `Not assessed` or score only the directly observed subset with a clear confidence limit.
- Ecommerce, marketplace, local-business, documentation, and content-library targets may need different category weights. Do not treat a category as applicable merely because it exists in the default map; explain `N/A` and `Not assessed` decisions in `Assessment Coverage` and `Category Applicability`.

## Standards Baseline

Report standards, official guidance, and Assess SEO's practical score separately. Assess SEO scores are internal readiness grades, not official ranking, rich-result, Search Console, or SEO certification claims.

Before grading, define:

- target site type and market
- target audience and search goals
- representative query themes or known keywords
- site-type category applicability, including categories marked `N/A` or `Not assessed`
- relevant standards, search-engine guidance, and platform conventions
- evaluated scope
- evidence mode
- evidence limits
- Assess Agent Readiness status only when it is materially relevant, actually run, or directly affects an SEO finding

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

Other workflow skills may use Assess SEO as an optional adjunct gate when a target has a public organic-search surface. Report evidence mode, score, grade cap, blockers, and skipped or not-assessed categories clearly enough for the parent workflow to decide whether SEO-readiness issues block release readiness. Include Assess Agent Readiness status only when it is materially relevant, actually run, or directly affects an SEO finding. Assess SEO does not depend on those orchestrator skills; it remains a standalone SEO-readiness audit skill.
