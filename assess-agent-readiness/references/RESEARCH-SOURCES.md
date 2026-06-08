# Research Sources

Use this file as Assess Agent Readiness's starting source map. Refresh sources during each audit because agent-readiness practices change quickly.

## Source Rules

- Initial baseline checked: 2026-05-22.
- Prefer primary sources and official documentation.
- Record access dates in the final report.
- Distinguish accepted standards from proposals, conventions, vendor guidance, and commentary.
- Do not claim a source guarantees ranking, retrieval, citation, or crawler behavior unless the source explicitly says so.

## Core Sources

### Google Generative AI Search Guidance

- Source: https://developers.google.com/search/docs/fundamentals/ai-optimization-guide
- Use for: crawlability, indexing, technical SEO, structured content, AI search guidance, and what Google says not to over-focus on.
- Current baseline: Google's guidance says existing SEO and crawlability fundamentals remain relevant for generative AI search. It also says `llms.txt` and other special AI text files are not required for Google generative AI search.

### Agent-Friendly Website Guidance

- Source: https://web.dev/articles/ai-agent-site-ux
- Use for: browser-mediated solution-agent behavior, screenshots, raw HTML, accessibility-tree signals, stable layouts, semantic actionable elements, labels, and visible action state.
- Treat as: current vendor guidance and practical best practice, not a general standard or certification model.

### Robots Exclusion Protocol

- Source: https://www.rfc-editor.org/rfc/rfc9309
- Use for: `robots.txt` behavior and crawler access policy.
- Treat as: accepted internet standard for robots exclusion behavior.

### Sitemaps

- Source: https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview
- Use for: route discovery, index hints, large-site discovery, and crawl completeness.
- Treat as: established search/crawler infrastructure, not a guarantee of indexing.

### llms.txt

- Source: https://llmstxt.org/
- Use for: emerging LLM-friendly Markdown site orientation and curated links.
- Treat as: proposal/convention, not a general standard and not a guaranteed signal for major AI systems.
- Audit note: missing `llms.txt` is not automatically a failure. It can be a readiness gap when the target needs LLM-friendly orientation and no equivalent exists.

### AGENTS.md

- Source: https://agents.md/
- Use for: repository-level instructions for coding agents.
- Treat as: open convention for coding-agent context and workflow guidance.

### Model Context Protocol

- Source: https://modelcontextprotocol.io/
- Use for: agent-facing tools, resources, prompts, MCP servers, clients, manifests, and integration surfaces.
- Treat as: protocol documentation for exposing systems to AI applications and agents.

### OpenAPI

- Source: https://www.openapis.org/
- Use for: machine-readable REST API descriptions, endpoint schemas, request/response shapes, and docs generation.
- Treat as: established API description specification family.

### Schema.org

- Source: https://schema.org/
- Use for: structured data vocabulary, entity description, JSON-LD, microdata, and RDFa.
- Treat as: widely used structured data vocabulary, not proof that a search or AI system will use every field.

### Assess SEO Skill

- Source: `assess-seo/SKILL.md` from the repository root
- Use for: generic search-crawler discovery, classic SEO readiness, human organic-search visibility, search intent, keyword coverage, snippets, local/entity SEO, performance/page experience, measurement, competitive visibility, rankings, and traffic opportunity.
- Treat as: adjacent local workflow, not a replacement for Assess Agent Readiness's agent-readiness audit categories.

## Useful Secondary Checks

- Search documentation for JavaScript SEO, structured data, canonical URLs, pagination, and internationalization when auditing websites.
- API docs for endpoint inventory, schemas, response fields, filtering, sorting, pagination, freshness, auth, scopes, rate limits, idempotency, errors, versioning, and webhooks when auditing data or action surfaces.
- Data exports, feeds, bulk-download docs, SDK reference docs, and schema references when the target's main value is data retrieval rather than page reading.
- SDK docs, CLIs, changelogs, examples, and sample apps when auditing developer-facing tools.
- Status pages, support docs, incident history, and deprecation notices when auditing reliability and recovery.

## Research Questions Per Audit

- What solution or coding-agent profile is realistic for this system: browser-mediated research agent, API/tool consumer, repository agent, documentation agent, or a caller-specific workflow?
- What is the agent trying to retrieve, decide, update, purchase, book, compare, generate, or verify for the user?
- Is the target primarily content retrieval, task execution, developer tooling, commerce, support, or operations?
- Do public, authenticated, read-only, and write/action surfaces need separate scoring because evidence or capability differs materially?
- Which standards are actually applicable, and which are only speculative conventions?
- Are there public and authorized/private surfaces that need separate scoring?
- What evidence is unavailable, and does that limit the grade or only lower confidence?
- Is classic SEO readiness materially in scope, requiring an Assess SEO adjunct pass or a separate audit recommendation?
