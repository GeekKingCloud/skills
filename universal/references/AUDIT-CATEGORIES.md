# Audit Categories

Use this file as the default category map for Universal audits. Omit categories that do not apply to the target, and add platform-specific categories when the research baseline requires them.

## Visual Perception

Check whether users can perceive information without relying on ideal color vision, high contrast displays, perfect lighting, or designer-preferred themes.

Inspect:

- text and non-text contrast
- foreground/background combinations in all states
- hover, focus, active, selected, disabled, error, warning, and success states
- color-only meaning
- charts, maps, heatmaps, icons, badges, labels, and status indicators
- transparency, overlays, background images, gradients, dark mode, high contrast mode, and forced colors

## Typography And Scaling

Check whether text remains readable when users resize, zoom, localize, or rely on OS text settings.

Inspect:

- font size, line height, text density, and spacing
- browser zoom, OS font scaling, Dynamic Type, and large text settings
- truncation, clipping, fixed-height containers, and overflow
- long words, localization expansion, mixed scripts, and narrow viewports
- headings, hierarchy, labels, helper text, and dense data displays

## Responsive And Mobile Use

Check whether core workflows remain usable on constrained screens and non-mouse input.

Inspect:

- small-screen reflow, portrait and landscape behavior, and responsive breakpoints
- touch target size, spacing, and reachable placement
- gestures without alternatives
- virtual keyboard behavior, safe-area insets, sticky UI, overlays, modals, drawers, and bottom sheets
- zoom-blocking, fixed viewport assumptions, horizontal scrolling, and content hidden off-screen

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
- language declarations and multilingual content when relevant

## Priority Mapping

Classify findings by user impact:

- `Critical`: blocks a core workflow for a disability group or assistive-technology path.
- `High`: makes a core workflow substantially harder, error-prone, or unreliable.
- `Medium`: affects important secondary workflows, repeated use, comprehension, or comfort.
- `Low`: polish issue with limited impact or a narrow context.

For each finding, capture category, priority, evidence, affected users, impact, fix direction, and confidence.
