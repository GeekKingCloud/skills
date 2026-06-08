# Audit Categories

Use this file as Assess SEO's default category map. Omit categories that do not apply, add target-specific categories when needed, and keep scoring separate from official ranking or search-engine claims.

## Contents

- Crawl, Indexing, And Technical Foundation
- Search Intent And Query Coverage
- On-Page Metadata And Snippet Readiness
- Content Quality, Usefulness, And Trust
- Information Architecture And Internal Linking
- Structured Data And Rich Result Eligibility
- Local, Entity, And Brand Signals
- Performance, Mobile, And Page Experience
- Measurement, Diagnostics, And Change Control
- Competitive Visibility And Off-Site Signals
- Priority Mapping
- Category Score Rubric
- Final Score Rules

## Crawl, Indexing, And Technical Foundation

Check whether search engines can discover, crawl, render, index, and consolidate the right pages.

Inspect:

- `robots.txt`, sitemap files, indexability, canonical tags, redirects, status codes, broken links, duplicate routes, pagination, hreflang, and faceted navigation
- crawlable rendered HTML, JavaScript rendering risks, SSR/static fallback, blocked assets, and soft 404 behavior
- URL structure, migration state, redirect chains, mixed protocols, trailing-slash variants, and environment leakage

## Search Intent And Query Coverage

Check whether the site has the right pages for the searches it wants to win.

Inspect:

- target queries, implied audience, funnel stage, geography, and task intent
- page-to-query fit, topic gaps, cannibalization, thin coverage, and mismatched landing pages
- SERP features, competing result types, commercial/local/informational intent, and likely answer formats

## On-Page Metadata And Snippet Readiness

Check whether search results can present the page clearly and attract qualified clicks.

Inspect:

- title tags, meta descriptions, headings, canonical display names, Open Graph/Twitter metadata, and visible page summaries
- snippet clarity, uniqueness, truncation risk, query relevance, dates, prices, availability, reviews, and entity naming
- duplicate or missing titles/descriptions and templates that produce weak search snippets

## Content Quality, Usefulness, And Trust

Check whether the content deserves to satisfy the search intent better than alternatives.

Inspect:

- main content depth, originality, helpfulness, accuracy, freshness, authorship, citations, expertise signals, and source provenance
- thin pages, boilerplate-heavy pages, AI-generated or duplicated content risks, doorway patterns, and unsupported claims
- media alternatives, FAQs, comparisons, examples, policies, and practical user task completion

## Information Architecture And Internal Linking

Check whether users and crawlers can understand page relationships and priority.

Inspect:

- navigation, breadcrumbs, hub pages, related links, footer/header links, orphan pages, crawl depth, and anchor text
- category/tag taxonomy, faceted paths, pagination, topic clusters, and duplicate internal routes
- important pages that lack internal prominence or contextual links

## Structured Data And Rich Result Eligibility

Check whether structured data accurately clarifies entities and can qualify for relevant search features.

Inspect:

- Schema.org JSON-LD, microdata, RDFa, entity consistency, required/recommended fields, and page-type fit
- product, local business, organization, article, FAQ, breadcrumb, review, event, job, software, course, or documentation schema when relevant
- validation errors, spammy markup, content/markup mismatch, and unsupported rich-result expectations

## Local, Entity, And Brand Signals

Check whether search systems and users can identify who or what the site represents.

Inspect:

- business name, address, phone, service area, hours, locations, staff, credentials, reviews, maps/profile consistency, and local landing pages
- organization/person/product entity clarity, sameAs links, knowledge graph cues, brand naming, and reputation evidence
- inconsistent NAP data, missing location context, weak trust pages, and unclear ownership

## Performance, Mobile, And Page Experience

Check whether organic visitors can use the page comfortably after clicking from search.

Inspect:

- mobile usability, Core Web Vitals evidence, loading behavior, image/video weight, layout shifts, intrusive interstitials, ads, consent banners, and font/render blocking
- template-level performance issues and page types most likely to affect organic entry pages
- lab data, field data, or observed interaction limits depending on available evidence

## Measurement, Diagnostics, And Change Control

Check whether the team can measure organic visibility and detect regressions.

Inspect:

- Search Console, analytics, rank tracking, crawl exports, server logs, sitemap submission, redirect maps, release process, changelogs, and SEO QA
- conversion events, goal tracking, attribution caveats, annotations, monitoring, and regression checks
- missing data needed to prioritize, verify, or debug SEO changes

## Competitive Visibility And Off-Site Signals

Check whether the site is positioned against the results it must displace.

Inspect:

- visible SERP competitors, backlink/profile evidence when available, reviews, citations, marketplaces, directories, social/profile consistency, and content differentiation
- direct competitors' page types, content depth, snippets, schema, local presence, and authority cues
- off-site gaps that affect trust, entity clarity, or ability to compete

## Priority Mapping

Classify findings by expected search/user impact:

- `Critical`: likely blocks crawling, indexing, consolidation, or trust for core organic pages; creates serious spam/manual-action risk; or makes the audit's main search goal impossible to evaluate.
- `High`: materially weakens core query coverage, snippets, content usefulness, internal authority flow, local/entity clarity, or measurement.
- `Medium`: affects important secondary pages, repeated templates, visibility confidence, page experience, or prioritization.
- `Low`: polish or narrow-scope issue with limited search impact.

For each finding, capture category, priority, evidence, search/user impact, rationale, fix direction, and confidence.

## Category Score Rubric

Score each applicable category out of 10 after reviewing findings and evidence.

- `10`: no meaningful issues found; strong evidence across relevant pages, templates, search goals, metadata, content, crawl/index signals, and measurement.
- `8-9`: minor issues only; no core organic visibility barriers.
- `6-7`: moderate issues affecting repeated templates, secondary query coverage, content confidence, internal linking, snippets, or measurement.
- `4-5`: serious issues affecting core pages, query fit, indexability, trust, local/entity clarity, or competitive viability.
- `1-3`: major blockers for crawling, indexing, consolidation, user trust, or ability to satisfy target search intent.
- `0`: category cannot be meaningfully used or evaluated because of a blocking SEO readiness failure.

Use `N/A` only when a category genuinely does not apply to the target site type or search goal. Use `Not assessed` when a category applies but was not evaluated because the needed evidence is unavailable. Exclude `N/A` and `Not assessed` categories from the final average and explain evidence limits. Do not assign confident scores to search intent, competitive visibility, off-site signals, local signals, or measurement categories from weak inference alone.

Category applicability notes:

- `Search Intent And Query Coverage` is `Not assessed` when no search goals, representative query themes, known keywords, market, or page-to-query evidence is available.
- `Local, Entity, And Brand Signals` is `N/A` for purely internal, non-public, or non-entity-bearing surfaces; local-specific checks are `N/A` for non-local sites, but entity/source clarity can still apply to documentation, products, and organizations.
- `Measurement, Diagnostics, And Change Control` is `Not assessed` for private data-dependent subareas when Search Console, analytics, logs, crawl exports, rank tracking, or release evidence is unavailable.
- `Competitive Visibility And Off-Site Signals` is `Not assessed` when market/geography, representative SERPs, competitor set, backlink/profile data, reviews/citations, or caller-provided competitive context is unavailable.

Every assessed category score must include a one-line rationale naming the strongest evidence and the main reason the score is not higher.

## Final Score Rules

Calculate the final Assess SEO score as the average of applicable assessed category scores, rounded to one decimal.

Map the final score to a letter grade:

- `A`: 9.0-10
- `B`: 8.0-8.9
- `C`: 7.0-7.9
- `D`: 6.0-6.9
- `F`: 0-5.9

Apply grade caps after averaging:

- Any unresolved `Critical` finding applies a grade cap of `F`.
- Any core crawl/index category scored `0-3` applies a grade cap of `D`.
- Missing live evidence for a public website applies a grade cap of `B`.
- Missing rendered-page evidence for a JavaScript-heavy site applies a grade cap of `C` when it prevents judging indexable content.
- Missing Search Console, analytics, backlink, or rank data caps only the affected measurement, off-site, or competitive categories unless the caller asked for a data-backed growth plan.
- Missing target queries, geography, competitor context, or private performance data should normally produce `Not assessed` categories or lower confidence, not guessed scores.
- Unsupported ranking, traffic, or competitor claims must be removed or marked as hypotheses.

Report the cap as one field: `Grade cap: None` or `Grade cap: <cap>, <reason>`.
