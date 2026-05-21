---
name: universal
description: Accessibility-focused audit of a codebase, interface, app, document workflow, or UI surface. Use when the caller wants accessibility reviewed across colors used together, contrast, typography, scaling, responsive/mobile behavior, keyboard/focus access, semantics, forms, motion, dynamic content, and user-impact priorities, with project-specific research first and a practical grade plus next steps.
---

# Universal

Audit accessibility as a first-class product quality concern. Stay focused on whether real users with different vision, motor, cognitive, language, device, and assistive-technology needs can perceive, understand, navigate, and operate the system.

This is not a roast. Use direct, evidence-backed language without jokes, contempt, or performative harshness.

## Quick Start

When asked to use Universal:

1. Identify the target folder, surface, or artifact from the caller's request.
2. Read local instructions and product context first, such as `AGENTS.md`, `README.md`, design-system docs, platform docs, contribution docs, and obvious config files.
3. Determine the project type, tech stack, target platforms, likely users, input methods, rendering formats, and assistive-technology surface.
4. Research the applicable accessibility standards and platform guidance before judging. Prefer current primary sources.
5. Inspect the actual implementation: components, styles, design tokens, routes/screens, rendered markup where available, forms, state changes, content, and responsive behavior.
6. Capture findings by accessibility category, then prioritize by user impact.
7. Use `templates/UNIVERSAL.md` as the report skeleton.

Do not include test coverage or accessibility tooling gaps as standing categories unless the caller explicitly asks for them. Mention verification limits only where they affect confidence in the audit.

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

## Audit Categories

Use these categories as the default pass list. Omit categories that clearly do not apply, and add project-specific categories when the researched platform requires them.

### Visual Perception

Inspect:
- text and non-text color contrast
- foreground/background combinations across states
- hover, focus, active, selected, disabled, error, and success states
- color-only meaning
- charts, maps, heatmaps, badges, labels, and status indicators
- dark mode, high-contrast mode, forced-colors mode, and transparency effects when relevant

Look for places where color, contrast, opacity, background imagery, or state styling makes information hard to perceive.

### Typography And Scaling

Inspect:
- font sizes, line height, letter spacing, and text density
- user font scaling, browser zoom, OS text settings, and dynamic type behavior
- truncation, clipping, fixed-height containers, and overflow
- long words, localization expansion, mixed scripts, and narrow viewports
- readable hierarchy without using headings only as visual decoration

Flag text that only works at the designer's preferred viewport, font, language, or zoom level.

### Responsive And Mobile Use

Inspect:
- small-screen layout, portrait and landscape behavior, and reflow
- touch target size and spacing
- gestures without alternatives
- fixed viewport assumptions
- sticky headers, modals, drawers, bottom sheets, and overlays
- virtual keyboard interactions and safe-area insets when relevant

Focus on whether core workflows remain operable on constrained screens and non-mouse input.

### Keyboard And Focus

Inspect:
- complete keyboard access for interactive controls
- visible focus indicators
- logical tab order and focus return after dialogs or route changes
- skip links, landmarks, and bypass mechanisms
- focus traps, hidden focusable elements, and keyboard dead ends
- custom widget keyboard behavior against platform expectations

Treat blocked keyboard operation as high impact unless the target platform genuinely has no keyboard or switch-control equivalent.

### Semantics And Assistive Technology

Inspect:
- semantic elements, roles, names, states, and values
- heading structure, landmarks, labels, descriptions, and alternative text
- custom controls that should expose native semantics
- dialogs, menus, tabs, comboboxes, grids, live regions, and disclosure widgets
- screen-reader-only text and visually hidden content
- redundant, misleading, or harmful ARIA

Prefer native semantics over ARIA. Flag ARIA that tries to fix markup while breaking the accessibility tree.

### Forms And Error Recovery

Inspect:
- labels, instructions, required fields, grouping, and help text
- error identification, error prevention, and recovery paths
- input format hints and validation timing
- autocomplete, password managers, and one-time-code workflows
- disabled states, loading states, and destructive confirmations

Judge whether users can complete forms without relying on color, memory, pointer precision, or hidden context.

### Motion, Timing, And Change

Inspect:
- animation, parallax, flashing, autoplay, and reduced-motion handling
- time limits, auto-refresh, carousels, toasts, and disappearing messages
- loading states, skeletons, async updates, and live announcements
- route transitions and focus movement after dynamic updates

Flag motion or timing that removes control, hides information, or creates vestibular, seizure, cognitive, or screen-reader problems.

### Content And Comprehension

Inspect:
- button and link names
- headings, page titles, labels, and empty states
- instructions, error copy, status messages, and confirmation text
- jargon, ambiguity, reading load, and content that assumes insider knowledge
- language declarations and multilingual content when relevant

Treat unclear content as an accessibility issue when it blocks understanding or recovery.

## Prioritization

Prioritize by user impact, not implementation convenience:

- `Critical`: blocks a core workflow for a disability group or assistive-technology path.
- `High`: makes a core workflow substantially harder, error-prone, or unreliable.
- `Medium`: affects important secondary workflows, repeated use, comprehension, or comfort.
- `Low`: polish issue with limited impact or a narrow context.

For each finding, include:
- `Category`
- `Priority`
- `Evidence`
- `Who is affected`
- `Why it matters`
- `Fix direction`
- `Confidence`

Use line references, component names, selectors, screen names, or screenshots where practical. Separate confirmed findings from likely risks.

## Grading

Grade accessibility readiness, not general code quality:

- `A`: accessible patterns are systematic, adaptable, and verified by implementation evidence.
- `B`: mostly accessible, with fixable gaps that do not block most core workflows.
- `C`: usable for some users, but accessibility depends on luck, defaults, or isolated good components.
- `D`: common disability, device, or assistive-technology paths are blocked or fragile.
- `F`: core workflows are inaccessible, misleading, or impossible to evaluate from the implementation.

Do not award an `A` if the audit lacked enough rendered or platform-specific evidence to judge core workflows.

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
