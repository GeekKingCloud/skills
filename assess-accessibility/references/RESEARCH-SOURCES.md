# Research Sources

Use this file to build the research baseline before judging an accessibility target. Prefer current primary sources and project-local documentation over memory or generic checklists.

## Core Web Sources

- W3C WCAG 2.2: use for success criteria, conformance framing, contrast, keyboard access, text resizing, reflow, error identification, target size, focus appearance, and non-text content.
- W3C How to Meet WCAG 2.2: use as the practical quick reference for techniques, failures, and filters by level.
- W3C WAI-ARIA Authoring Practices Guide: use for custom widget patterns such as dialogs, menus, tabs, accordions, comboboxes, grids, trees, and live regions.
- MDN Accessibility: use for implementation behavior in HTML, CSS, JavaScript, browser accessibility APIs, keyboard handling, and ARIA caveats.

## Platform Sources

- Apple Human Interface Guidelines accessibility sections: use for iOS, iPadOS, macOS, watchOS, tvOS, visionOS, Dynamic Type, VoiceOver, Reduce Motion, Increase Contrast, and platform interaction expectations.
- Android accessibility guidance: use for TalkBack, switch access, touch targets, font scaling, content descriptions, focus order, and platform controls.
- Material Design accessibility guidance: use when the product follows Material components, tokens, or interaction patterns.
- Microsoft accessibility and inclusive design guidance: use for Windows, Microsoft-flavored desktop UI, keyboard conventions, high contrast, forced colors, and inclusive design framing.

## Compliance Sources

Use compliance sources only when the product context makes them relevant:

- Section 508: United States federal procurement and ICT accessibility context.
- EN 301 549: European ICT accessibility procurement context.
- Organization accessibility policies, design-system requirements, or contractual acceptance criteria.

## Grading And Conformance

Do not invent an official accessibility score. Record standards alignment separately from Assess Accessibility's practical score.

- WCAG 2.x uses A, AA, and AAA conformance levels, not numeric grades. A web page must satisfy all applicable success criteria at the target level to conform. Source: https://w3c.github.io/wcag/understanding/conformance
- WCAG-EM provides an evaluation methodology and report structure. It supports consistent evaluation but does not add WCAG requirements or make a sampled audit automatically become a full conformance claim. Source: https://www.w3.org/WAI/test-evaluate/conformance/wcag-em/
- ACT defines a format and rules for consistent accessibility conformance testing. It supports test consistency and tool methodology; it is not an audit grade. Source: https://www.w3.org/WAI/standards-guidelines/act/
- ACR/VPAT reporting uses support statuses such as `Supports`, `Partially Supports`, `Does Not Support`, and `Not Applicable` against applicable standards. It is not a 0-10 score. Source: https://www.section508.gov/sell/acr-vpat-faq/
- WCAG 3 drafts describe Bronze, Silver, and Gold conformance concepts, but WCAG 3 is not the stable basis for Assess Accessibility grading unless the caller explicitly asks for draft-oriented analysis. Source: https://w3c.github.io/wcag3/guidelines/

For web and web-like products, default the target to WCAG 2.2 AA unless project docs, legal scope, procurement requirements, or caller context specify otherwise. For non-web products, use the relevant platform guidance and use ACR/VPAT-style statuses only when compliance context applies.

## Project-Local Sources

Always look for local source-of-truth documents:

- `AGENTS.md`, `README.md`, contribution docs, and product docs
- design-system docs, Storybook, component catalogs, token files, brand guidelines, and content style guides
- accessibility statements, VPATs, compliance notes, user research, analytics, supported browser/device matrices, and localization docs
- platform-specific files such as native app manifests, theme files, accessibility resource files, document templates, email templates, or PDF generation code

## Research Output

Record:

- sources used
- checked or accessed date for each time-sensitive source
- standards or platform expectations that apply
- standards or platform expectations that do not apply and why
- target level or status model
- target users, assistive technologies, input methods, devices, and rendering formats
- evidence limits that make a finding lower confidence

Do not cite sources that were not actually read or checked during the audit.
