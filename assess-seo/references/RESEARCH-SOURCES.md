# Research Sources

Use this file as Assess SEO's starting source map. Refresh sources during each audit because search guidance, SERP features, structured data eligibility, and crawler behavior change over time.

## Source Rules

- Initial baseline checked: 2026-05-22.
- Prefer primary sources and official documentation.
- Record access dates in the final report.
- Distinguish accepted standards from proposals, conventions, vendor guidance, and commentary.
- Do not claim a source guarantees ranking, retrieval, snippets, traffic, or conversions unless the source explicitly says so.

## Core Sources

### Google SEO Starter Guide

- Source: https://developers.google.com/search/docs/fundamentals/seo-starter-guide
- Use for: broad SEO fundamentals, making content discoverable, useful content, links, snippets, media, promotion, and measurement concepts.
- Treat as: official Google guidance, not a ranking checklist or guarantee.

### Google Crawling And Indexing

- Source: https://developers.google.com/search/docs/crawling-indexing
- Use for: crawlability, indexing controls, `robots.txt`, sitemaps, canonicalization, redirects, JavaScript SEO, internationalization, and site moves.
- Treat as: official Google documentation for controlling discovery and indexing behavior.

### Google Robots Documentation

- Source: https://developers.google.com/search/reference/robots_txt
- Use for: how Google interprets `robots.txt`, crawler access rules, caching, unsupported fields, and sitemap hints.
- Treat as: official Google implementation guidance for robots rules.

### Robots Exclusion Protocol

- Source: https://www.rfc-editor.org/rfc/rfc9309
- Use for: `robots.txt` syntax and crawler access policy.
- Treat as: accepted internet standard for robots exclusion behavior.

### Google Sitemaps Documentation

- Source: https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview
- Use for: sitemap discovery, large-site discovery, alternate formats, submission, and sitemap limits.
- Treat as: established search/crawler infrastructure, not a guarantee of indexing.

### Google Structured Data

- Source: https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data
- Use for: structured data eligibility, rich-result behavior, required/recommended fields, validation, and policy.
- Treat as: official Google guidance for search features, not a guarantee that a rich result will appear.

### Schema.org

- Source: https://schema.org/
- Use for: structured data vocabulary, entities, JSON-LD, microdata, and RDFa.
- Treat as: widely used structured data vocabulary, not proof that every field is used by every search system.

### Google Search Essentials And Spam Policies

- Source: https://developers.google.com/search/docs/essentials
- Use for: technical requirements, spam policies, key best practices, and practices that can harm search visibility.
- Treat as: official quality and policy guidance.

### Google Helpful Content Guidance

- Source: https://developers.google.com/search/blog/2022/08/helpful-content-update and https://developers.google.com/search/docs/fundamentals/creating-helpful-content
- Use for: helpful content, people-first content, expertise, trust signals, and content quality framing.
- Treat as: guidance for evaluating content quality, not a direct scoring formula.

### Core Web Vitals And Page Experience

- Source: https://web.dev/vitals/ and https://developers.google.com/search/docs/appearance/page-experience
- Use for: performance, responsiveness, visual stability, mobile usability, and page-experience considerations.
- Treat as: official/practical guidance; evaluate with available field and lab evidence.

### Bing Webmaster Guidelines

- Source: https://www.bing.com/webmasters/help/webmaster-guidelines-30fba23a
- Use for: Bing crawling, indexing, quality, links, content, and abuse guidance when Bing visibility matters.
- Treat as: official Bing guidance.

### Google Business Profile And Local Search

- Source: https://support.google.com/business/
- Use for: local-business profile basics, eligibility, locations, hours, service areas, reviews, and business identity.
- Treat as: official Google Business Profile support documentation.

### Assess Agent Readiness Skill

- Source: `assess-agent-readiness/SKILL.md` from the repository root
- Use for: agent-facing discovery, AI-crawler, `llms.txt`, machine-readable orientation, action surfaces, and handoff evidence when those are in scope.
- Treat as: adjacent local workflow, not a replacement for classic SEO audit categories.
- Boundary: route agent instructions, API/tool actionability, MCP/OpenAPI execution surfaces, auth delegation, deterministic recovery, and handoff verification to Assess Agent Readiness instead of expanding Assess SEO.

## Useful Secondary Checks

- Search Console documentation for impressions, clicks, indexing reports, sitemaps, removals, enhancements, and URL inspection.
- Analytics documentation for organic traffic, conversions, attribution caveats, and event tracking.
- Platform docs for WordPress, Shopify, Webflow, Next.js, Astro, ReactPress, documentation generators, and ecommerce systems when the target uses them.
- Crawl tools, log files, rank trackers, backlink tools, and CMS exports when the caller provides them.
- Competitor SERPs, local packs, shopping results, review platforms, directories, and marketplaces when market comparison is requested.

## Research Questions Per Audit

- What organic search outcome does the caller care about: discovery, traffic, qualified leads, ecommerce revenue, local actions, documentation retrieval, or brand/entity clarity?
- Which pages or templates are organic entry points?
- Which representative queries and geographies matter?
- Which search-engine guidance is directly applicable, and which observations are only hypotheses?
- Are Search Console, analytics, crawl logs, rank tracking, or backlink data available?
- Are agent-facing discovery surfaces materially in scope, requiring an Assess Agent Readiness adjunct pass or a separate audit recommendation?
