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

## Project-Local Sources

Always look for local source-of-truth documents:

- `AGENTS.md`, `README.md`, contribution docs, and product docs
- design-system docs, Storybook, component catalogs, token files, brand guidelines, and content style guides
- accessibility statements, VPATs, compliance notes, user research, analytics, supported browser/device matrices, and localization docs
- platform-specific files such as native app manifests, theme files, accessibility resource files, document templates, email templates, or PDF generation code

## Research Output

Record:

- sources used
- standards or platform expectations that apply
- standards or platform expectations that do not apply and why
- target users, assistive technologies, input methods, devices, and rendering formats
- evidence limits that make a finding lower confidence

Do not cite sources that were not actually read or checked during the audit.
