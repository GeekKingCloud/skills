# Editorial Model

Use this helper to decide what the mix should do before building filters or automation.

## Track Roles

Classify roles from behavior across the full source, not labels alone.

- `commentary/mic`: speech-shaped bursts, sentence gaps, breaths, pauses, changing delivery, and capture-level shifts.
- `background/system`: program audio such as game, desktop, music, video, call audio, or other continuous source bed.
- `existing mix`: combined commentary plus background. Preserve it as an original stream when useful, but do not remix from it when separate lanes exist.

Required role evidence:

- mic-only or low-background commentary;
- commentary over active background;
- background-only or no-commentary spans;
- weak or buried commentary under background;
- loud, recovered, hot, or late commentary;
- section boundaries where one lane changes behavior.

If selected mic would omit recoverable speech found in another non-mix lane, the map is wrong.

## Commentary First

Build a stable commentary lane before balancing background.

1. Pick an ordinary-speaking reference from healthy or best-captured commentary spans.
2. Exclude silence, mic floor, breaths without speech body, obvious yells, and true whispers from that reference.
3. Split sustained capture regimes when ordinary speech body materially shifts.
4. Raise weak regimes toward the reference when recoverable.
5. Trim hot regimes when they would make the viewer turn volume down.
6. Preserve expressive range inside each regime.
7. Do not lift mic floor or empty noise to fake parity.

A weak regime can be lower than ideal only when lifting it would create a worse listener problem such as noise, harshness, clipping, or obvious artifacts. State that as source-limited or tradeoff evidence.

## Background Placement

After commentary is usable, place the background under it.

- Establish a baseline bed level before ducking.
- During ordinary active commentary, orient around a background body roughly `7-8 dB` under the repaired commentary body. Treat this as a starting reference, not a pass/fail threshold; listener-risk windows, transition behavior, and background naturalness override the number.
- Keep the background hearable under normal commentary.
- Use shallow smooth bed riding as polish, not as the main way to create separation.
- Let exciting background moments breathe when speech remains clear.
- If a background rise masks speech, lift the mic with it first when comfortable headroom exists.
- If further mic lift would become uncomfortable, restrain that detected background event or section.
- Do not crush the whole background to solve a few loud events.
- Do not let the bed surge loudly between phrases.

## Transition Behavior

Major mic-regime boundaries are listener-risk moments.

Check:

- last healthy phrases before the boundary;
- first recoverable phrases after the boundary;
- starts and tails after pauses;
- the first sustained low section after a drop;
- recovery from weak to healthy or hot sections.

Correction should happen at the next coherent phrase. Long fades that hide slow recovery are failures.

## Candidate Strategy

A valid strategy is a source-aware plan, not just a filter graph.

Acceptable strategy elements include:

- regime-level mic gain or trim;
- smooth phrase-aware automation;
- shallow background riding;
- local background event restraint;
- mic-follow for detected background rises when headroom exists;
- gentle limiting for headroom.

High-risk elements require explicit checks:

- dynamic normalization;
- companders or compressors;
- gates, expanders, denoisers;
- aggressive sidechain ducking;
- whole-file loudness normalization;
- fixed-gain-only repair on shifting sources.

Reject a strategy that makes the mix pass by hiding the background, flattening dynamics, lifting silence, or ignoring weak commentary.
