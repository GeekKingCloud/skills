---
name: assess-accessibility
description: Accessibility audit of a codebase, interface, app, document workflow, or UI surface. Use when the caller wants project-specific accessibility research, standards baseline, color/contrast, typography, scaling, mobile/responsive behavior, keyboard/focus access, semantics, forms, motion, dynamic content, user-impact priorities, per-category scores, and a practical final grade with next steps.
---

# Assess Accessibility

Audit accessibility as a first-class product quality concern. Stay focused on whether real users with different vision, motor, cognitive, language, device, and assistive-technology needs can perceive, understand, navigate, and operate the system.

This is not a roast. Use direct, evidence-backed language without jokes, contempt, or performative harshness.

## Required Audit Workflow

When asked to use Assess Accessibility:

1. Identify the target folder, URL, app, surface, or artifact from the caller's request.
2. Read local instructions and product context first, such as `AGENTS.md`, `README.md`, design-system docs, platform docs, contribution docs, and obvious config files.
3. Determine the project type, tech stack, target platforms, likely users, input methods, rendering formats, and assistive-technology surface.
4. Push for the strongest evidence practical before scoring: run the project when source is available and safe, inspect reachable production or development URLs, check representative routes/screens, and use lightweight network checks such as DNS, ping, headers, or HTTP probes when they clarify reachability or host behavior.
5. Research the applicable accessibility standards and platform guidance before judging. Prefer current primary sources.
6. Inspect the actual implementation or running surface: components, styles, design tokens, routes/screens, rendered markup where code is available, forms, state changes, content, and responsive behavior.
7. Capture findings by accessibility category, score each applicable category out of 10, then prioritize by user impact.
8. Use `templates/ASSESS-ACCESSIBILITY.md` as the report skeleton.

Do not include test coverage or accessibility tooling gaps as standing categories unless the caller explicitly asks for them. Mention verification limits only where they affect confidence in the audit.

Use `Assessment Coverage` as the first report section after the title, not a terse caveat list: state what was assessed, what was not assessed, what the caller can provide or permit for a deeper/fairer/more accurate assessment, and what that extra evidence would improve. Use `Start Here` as the report's single prioritized action plan. Do not add a second `Next Steps` section unless the caller explicitly wants a separate follow-up roadmap.

## References

- Read `references/RESEARCH-SOURCES.md` before auditing when the target platform, standards, or source list is not already obvious from the current request and local project docs.
- Read `references/AUDIT-CATEGORIES.md` when planning or running the category pass, especially for UI-heavy projects with multiple surfaces.
- Keep `SKILL.md` as the execution path; use reference files for expanded source and category details.

## Research First

Start every audit by building a project-specific research baseline. Do not assume web guidance applies unchanged to native apps, PDFs, emails, terminal UIs, games, kiosks, admin tools, or generated documents.

Use the most relevant sources for the target:

- W3C WCAG 2.2 and W3C's "How to Meet WCAG" quick reference for web content and web-like UI.
- W3C WAI-ARIA Authoring Practices Guide when custom widgets, dialogs, menus, tabs, comboboxes, grids, trees, or live regions appear.
- MDN accessibility guidance for HTML, CSS, JavaScript, ARIA, keyboard interaction, and browser behavior.
- Platform human-interface guidance for native apps, including Apple accessibility guidance, Android accessibility guidance, Material Design accessibility guidance, and Microsoft accessibility guidance when relevant.
- Section 508, EN 301 549, procurement requirements, or organization policy only when the product context makes compliance scope relevant.
- Project-local design-system rules, brand rules, content standards, and component documentation.

In the final report, list the sources actually used. If live research was unavailable, say that clearly and treat standards-sensitive claims as lower confidence.

## Standards Baseline

Report standards alignment separately from Assess Accessibility's practical score. Assess Accessibility scores are not WCAG conformance claims, certifications, VPATs, or legal compliance findings.

Before grading, define:
- target standard or platform guidance
- target level or status model
- evaluated scope
- evidence mode
- evidence limits

Default web and web-like targets to WCAG 2.2 AA unless project docs, legal scope, procurement context, or the caller specifies another target. For non-web products, use the relevant platform guidance. Use ACR/VPAT-style support statuses only when compliance or procurement context applies.

Use one of these evidence modes:
- `Source + rendered`: code and running UI were both inspected.
- `Source only`: code was inspected, but the UI could not be rendered or interacted with.
- `Rendered only`: a live app, website, prototype, screenshot set, or document output was inspected without source code.
- `Artifact only`: a static file, image, PDF, email, export, or recording was inspected without interactive access.

## Audit Categories, Prioritization, And Scoring

Use `references/AUDIT-CATEGORIES.md` as Assess Accessibility's source of truth for the category map, priority definitions, score rubric, final score rules, and grade-cap rules. Do not duplicate those definitions in `SKILL.md`; keep this file focused on execution flow, evidence expectations, report structure, boundaries, and when to consult the reference.

When running an audit, load that reference before the category pass, then adapt only for target-specific categories that the researched platform or user request clearly requires. Keep `N/A` and `Not assessed` handling aligned with the reference, and summarize skipped or limited categories in the report's `Assessment Coverage` section instead of scattering caveats throughout the report.

## App Or Website Without Source Code

Assess Accessibility can audit a live app, website, prototype, or document workflow without source code, but the evidence changes. Use browser, device, screenshot, system accessibility, and interaction tools available in the session. If a needed tool is unavailable, say so and mark affected categories as `Not assessed` or lower confidence.

For source-unavailable targets:
- research the product context, platform, expected users, and applicable standard before interacting with it
- discover public routes through visible navigation, footer links, site search, `sitemap.xml`, robots hints, indexed search results, and in-page links when available
- inspect rendered DOM, computed styles, accessibility tree, keyboard behavior, responsive breakpoints, and browser console output when browser tools are available
- use screenshots or visual inspection for contrast, layout, truncation, zoom, reflow, focus visibility, and motion
- use keyboard-only walkthroughs for every core workflow that can be reached
- use screen reader, platform accessibility inspector, or browser accessibility-tree tools when available
- avoid claiming implementation causes when only rendered behavior is visible
- record credentials, permissions, geography, feature flags, blocked routes, and authentication limits as evidence limits
- score only observed behavior and reachable states; do not infer hidden screens, account types, or implementation quality
- make fix directions behavior-level when source is unavailable, such as "expose this control as a button with a programmatic name" rather than naming a component or file
- cap only for evidence that is actually missing, such as no keyboard walkthrough, no responsive/device pass, no accessibility-tree or assistive-technology pass, or blocked core flows
- keep `Not assessed` categories out of the score table and list them underneath with a shared reason when the same evidence limit applies

Do not treat a missing XML sitemap as an accessibility failure by itself; XML sitemaps primarily support crawlers, not end users. Treat it as an audit evidence limit when it prevents a complete route inventory. Treat missing or weak user-facing discovery as an accessibility issue when users cannot reasonably find important pages, workflows, support paths, policies, or content through navigation, search, breadcrumbs, footer links, an HTML sitemap, or equivalent information architecture.

## Boundaries

Do not:
- claim full accessibility conformance from code inspection alone
- reduce the audit to color contrast only
- invent findings without evidence
- overgeneralize web rules to non-web platforms
- bury user impact behind standards jargon
- use roast tone, insults, or comedy framing

Do:
- state review scope and evidence limits
- connect findings to affected users and workflows
- name the standard or platform expectation when it materially supports the finding
- give a practical first-fix sequence
- recommend manual assistive-technology or device checks when code evidence is insufficient

## Orchestrator Use

Other workflow skills may use Assess Accessibility as an optional adjunct gate when a target has an accessibility-relevant surface. Report evidence mode, score, grade cap, blockers, and skipped or not-assessed categories clearly enough for the parent workflow to decide whether accessibility issues block release readiness. Assess Accessibility does not depend on those orchestrator skills; it remains a standalone accessibility audit skill.
