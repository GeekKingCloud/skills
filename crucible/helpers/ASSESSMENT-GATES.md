# Assessment Gates

Read this helper only when the caller asks Crucible to pair with assessment skills, or when the plan or changed surface makes `assess-accessibility`, `assess-agent-readiness`, or `assess-seo` relevant.

Use these skills as optional adjunct gates. They are not hard dependencies for every Crucible run, and they must be skipped with a short reason when irrelevant.

## Shared Assessment Gate Rules

Use the Crucible Review Gate Loop for every assessment gate that runs.

Classify every assessment finding as:
- `actionable in scope`
- `external or owner-blocked`
- `unverifiable with current access`
- `explicitly accepted`

Loop only on actionable Critical, High, and Medium findings. Do not keep rerunning a gate solely because its grade is capped by documented external, owner-blocked, or unverifiable conditions. After actionable fixes are exhausted, treat the gate as `capped` rather than failed when the remaining above-Low findings are outside Crucible's current ability to change or verify.

For capped gates, report:
- evidence for the cap
- why Crucible cannot resolve or verify it from the current workspace
- who or what would unblock it
- whether the cap affects release readiness
- the exact next step

Do not use `external`, `owner-blocked`, or `unverifiable` as an escape hatch for findings that can be fixed or tested in the current workspace. When in doubt, attempt the narrowest reasonable fix or verification once, then classify the remaining cap from evidence.

## Assessment Gate Order

When more than one assessment gate applies, run them before roast in this default order:

1. `assess-accessibility`
2. `assess-seo`
3. `assess-agent-readiness`

Run Assess Accessibility first when UI, document, or human-facing workflow surfaces apply, because accessibility fixes can change markup, semantics, forms, labels, focus behavior, and generated output that later gates inspect.

Run Assess SEO before Assess Agent Readiness when both apply, because classic crawl/index foundations such as `robots.txt`, sitemap discovery, indexability, canonicalization, and crawlable content are prerequisites for many agent-facing discovery paths.

Run Assess Agent Readiness after applicable SEO work so the agent-facing layer is assessed on top of the final crawl/index baseline. Skip irrelevant assessment gates with short reasons.

## Assess Accessibility Gate

Relationship type: optional adjunct gate.

Run the sibling `assess-accessibility` skill when the plan or changed surface touches UI, frontend components, forms, public websites, generated documents, PDFs, emails, design systems, human-facing output, or user-facing workflows. Also run it when the caller explicitly asks for accessibility hardening.

Skip Assess Accessibility for backend-only, infrastructure-only, internal refactor-only, test-only, or non-user-facing work unless the caller explicitly asks for it.

If the `assess-accessibility` skill is unavailable but the target has an accessibility surface, perform a smaller evidence-backed accessibility pass and disclose that the actual skill was unavailable.

Treat Assess Accessibility output as an accessibility release gate when it runs:
- Use the Review Gate Loop until Assess Accessibility produces a Grade A or equivalent high result, or is documented as externally capped, and no unresolved actionable finding remains above Low or nitpick level.
- Fix unresolved `Critical`, `High`, and `Medium` Assess Accessibility findings before release readiness, unless the caller explicitly accepts the risk.
- Fix `Low` or nitpick findings when cheap, clarifying, or confidence-building.

Report the Assess Accessibility gate status as `run`, `skipped`, `unavailable`, or `capped`. Include the skip reason, fallback note, final grade or equivalent status, rerun evidence when available, and any unresolved accessibility findings.

## Assess Agent Readiness Gate

Relationship type: optional adjunct gate.

Run the sibling `assess-agent-readiness` skill when the plan or changed surface touches public websites, documentation, APIs, SDKs, CLIs, MCP or tool surfaces, agent-facing instructions, automation workflows, structured content, crawl policy, or agent-readable content. Also run it when the caller explicitly asks for agent-readiness hardening.

Skip Assess Agent Readiness for backend-only, infrastructure-only, internal refactor-only, test-only, or non-agent-facing work unless the caller explicitly asks for it.

If the `assess-agent-readiness` skill is unavailable but the target has an agent-facing surface, perform a smaller evidence-backed agent-readiness pass and disclose that the actual skill was unavailable.

Treat Assess Agent Readiness output as an agent-readiness release gate when it runs:
- Use the Review Gate Loop until Assess Agent Readiness produces a Grade A or equivalent high result, or is documented as externally capped, and no unresolved actionable finding remains above Low or nitpick level.
- Fix unresolved `Critical`, `High`, and `Medium` Assess Agent Readiness findings before release readiness, unless the caller explicitly accepts the risk.
- Fix `Low` or nitpick findings when cheap, clarifying, or confidence-building.

Report the Assess Agent Readiness gate status as `run`, `skipped`, `unavailable`, or `capped`. Include the skip reason, fallback note, final grade or equivalent status, rerun evidence when available, and any unresolved agent-readiness findings.

## Assess SEO Gate

Relationship type: optional adjunct gate.

Run the sibling `assess-seo` skill when the plan or changed surface touches public websites, landing pages, marketing pages, documentation pages, ecommerce pages, local-business pages, crawl/index configuration, structured data, metadata, internal linking, content templates, sitemap generation, redirects, or other organic-search surfaces. Also run it when the caller explicitly asks for SEO hardening.

Skip Assess SEO for backend-only, infrastructure-only, internal refactor-only, test-only, authenticated-only, non-public, or non-search-facing work unless the caller explicitly asks for it.

If the `assess-seo` skill is unavailable but the target has an organic-search surface, perform a smaller evidence-backed SEO-readiness pass and disclose that the actual skill was unavailable.

Treat Assess SEO output as an SEO-readiness release gate when it runs:
- Use the Review Gate Loop until Assess SEO produces a Grade A or equivalent high result, or is documented as externally capped, and no unresolved actionable finding remains above Low or nitpick level.
- Fix unresolved `Critical`, `High`, and `Medium` Assess SEO findings before release readiness, unless the caller explicitly accepts the risk.
- Fix `Low` or nitpick findings when cheap, clarifying, or confidence-building.
- Do not let AI-oriented files such as `llms.txt` compensate for broken classic crawl/index foundations such as `robots.txt`, sitemap discovery, indexability, canonicalization, or crawlable content.

Report the Assess SEO gate status as `run`, `skipped`, `unavailable`, or `capped`. Include the skip reason, fallback note, final grade or equivalent status, rerun evidence when available, and any unresolved SEO-readiness findings.
