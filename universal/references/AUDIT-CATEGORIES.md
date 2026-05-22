# Audit Categories

Use this file as the default category map for Universal audits. Omit categories that do not apply to the target, and add platform-specific categories when the research baseline requires them.

## Contents

- Keyboard And Focus
- Semantics And Assistive Technology
- Forms And Error Recovery
- Visual Perception
- Responsive And Mobile Use
- Typography And Scaling
- Motion, Timing, And Change
- Content And Comprehension
- Priority Mapping
- Category Score Rubric
- Final Score Rules

The default category order is the report order. It starts with barriers most likely to block operation, then moves into perception, layout, comfort, and comprehension.

## Keyboard And Focus

Check whether users can operate the system without a mouse or precise pointer.

Inspect:

- full keyboard access to all interactive controls
- visible focus indicators
- logical tab order and reading order
- skip links, landmarks, and bypass mechanisms
- focus traps, hidden focusable elements, keyboard dead ends, and focus return
- expected key behavior for custom widgets

## Semantics And Assistive Technology

Check whether the UI exposes useful structure, names, roles, states, and values.

Inspect:

- native semantic elements and platform controls
- accessible names, descriptions, roles, states, values, and relationships
- heading structure, landmarks, regions, labels, and alternative text
- dialogs, menus, tabs, accordions, comboboxes, grids, trees, disclosures, and live regions
- visually hidden content, screen-reader-only labels, and ARIA that overrides native behavior

Prefer native semantics over ARIA. Treat incorrect ARIA as a defect, not a harmless annotation.

## Forms And Error Recovery

Check whether users can complete, correct, and recover from input tasks.

Inspect:

- labels, instructions, help text, required fields, fieldsets, and grouping
- validation timing, input format hints, and error messages
- error summaries, focus movement, and recovery paths
- autocomplete, password managers, one-time-code flows, and input modes
- disabled states, destructive actions, confirmations, loading states, and partial submission failures

## Visual Perception

Check whether users can perceive information without relying on ideal color vision, high contrast displays, perfect lighting, or designer-preferred themes.

Inspect:

- text and non-text contrast
- foreground/background combinations in all states
- hover, focus, active, selected, disabled, error, warning, and success states
- color-only meaning
- charts, maps, heatmaps, icons, badges, labels, and status indicators
- transparency, overlays, background images, gradients, dark mode, high contrast mode, and forced colors

## Responsive And Mobile Use

Check whether core workflows remain usable on constrained screens and non-mouse input.

Inspect:

- small-screen reflow, portrait and landscape behavior, and responsive breakpoints
- touch target size, spacing, and reachable placement
- gestures without alternatives
- virtual keyboard behavior, safe-area insets, sticky UI, overlays, modals, drawers, and bottom sheets
- zoom-blocking, fixed viewport assumptions, horizontal scrolling, and content hidden off-screen

## Typography And Scaling

Check whether text remains readable when users resize, zoom, localize, or rely on OS text settings.

Inspect:

- font size, line height, text density, and spacing
- browser zoom, OS font scaling, Dynamic Type, and large text settings
- truncation, clipping, fixed-height containers, and overflow
- long words, localization expansion, mixed scripts, and narrow viewports
- headings, hierarchy, labels, helper text, and dense data displays

## Motion, Timing, And Change

Check whether the system gives users control over movement, timing, and updates.

Inspect:

- animation, parallax, transitions, flashing, autoplay, and auto-advancing content
- reduced-motion behavior
- time limits, auto-refresh, session expiry, disappearing messages, toasts, and carousels
- loading states, skeletons, async updates, route changes, and live announcements
- focus movement after dynamic changes

## Content And Comprehension

Check whether users can understand instructions, controls, state, and recovery steps.

Inspect:

- button and link names
- headings, page titles, labels, empty states, status text, and confirmation text
- instructions, error copy, warnings, destructive-action copy, and success messages
- jargon, ambiguity, reading load, idioms, insider knowledge, and inconsistent terms
- user-facing discovery paths, including navigation, site search, breadcrumbs, footer links, HTML sitemaps, and route findability
- language declarations and multilingual content when relevant

## Priority Mapping

Classify findings by user impact:

- `Critical`: blocks a core workflow for a disability group or assistive-technology path.
- `High`: makes a core workflow substantially harder, error-prone, or unreliable.
- `Medium`: affects important secondary workflows, repeated use, comprehension, or comfort.
- `Low`: polish issue with limited impact or a narrow context.

For each finding, capture category, priority, evidence, affected users, impact, fix direction, and confidence.

## Category Score Rubric

Score each applicable category out of 10 after reviewing findings and evidence. Keep priority separate from score: priority describes the most urgent user impact; score summarizes category health.

- `10`: no meaningful issues found; strong evidence across relevant states, devices, input methods, and platform expectations.
- `8-9`: minor issues only; no core workflow barriers.
- `6-7`: moderate issues affecting repeated use, secondary workflows, comprehension, or comfort.
- `4-5`: serious issues affecting core workflows for some users.
- `1-3`: major blockers for a disability group, input method, or assistive-technology path.
- `0`: the category cannot be meaningfully used or evaluated because of a blocking accessibility failure.

Use `N/A` only when a category genuinely does not apply to the target. Use `Not assessed` when the category applies but was not evaluated. Exclude `N/A` and `Not assessed` categories from the final average, and explain evidence limits for every `Not assessed` category. Keep `Not assessed` categories out of the score table and list them underneath with a shared reason when the same evidence limit applies.

Every assessed category score must include a one-line rationale naming the strongest evidence and the main reason the score is not higher.

## Evidence Modes

Name the evidence mode before scoring:

- `Source + rendered`: code and running UI were both inspected.
- `Source only`: code was inspected, but the UI could not be rendered or interacted with.
- `Rendered only`: a live app, website, prototype, screenshot set, or document output was inspected without source code.
- `Artifact only`: a static file, image, PDF, email, export, or recording was inspected without interactive access.

Missing source code is not a grade cap by itself. It lowers confidence, limits cause analysis, and usually makes fix directions less specific. Score rendered-only audits on observed behavior, reachable states, and available accessibility evidence.

For websites without source code, missing XML sitemaps, blocked route discovery, unavailable credentials, or inaccessible pages are evidence limits when they prevent a complete crawl. Do not score a missing XML sitemap as a user accessibility defect by itself. Score weak user-facing discovery when important pages or workflows cannot be found through navigation, search, breadcrumbs, footer links, an HTML sitemap, or equivalent information architecture.

## Final Score Rules

Calculate the final Universal score as the average of applicable assessed category scores, rounded to one decimal.

Map the final score to a letter grade:

- `A`: 9.0-10
- `B`: 8.0-8.9
- `C`: 7.0-7.9
- `D`: 6.0-6.9
- `F`: 0-5.9

Apply grade caps after averaging:

- Any unresolved `Critical` finding applies a grade cap of `F`.
- Any category scored `0-3` applies a grade cap of `D`.
- Missing rendered or platform evidence for an interactive product applies a grade cap of `B`.
- Missing assistive-technology evidence for a UI-heavy product applies a grade cap of `C`.
- Incomplete crawl or blocked route discovery can apply a grade cap of `B` or lower when important public or user-facing workflows could not be inventoried.

Apply the most restrictive grade cap when multiple caps apply: `F` beats `D`, `D` beats `C`, and `C` beats `B`. Report the cap as one field: `Grade cap: None` when no cap applies, or `Grade cap: <cap>, <reason>` when a cap applies.
