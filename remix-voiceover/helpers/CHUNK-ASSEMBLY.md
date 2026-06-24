# Chunk Assembly

Use this helper after source evidence maps commentary regimes and before the first render.

This phase owns the production shape. Treat the audio like an edit made from repaired sections, not one full-track automation problem.

## Default Strategy

Build the first serious candidate as chunk assembly unless source evidence proves one stable mic regime.

1. Split the commentary lane into sustained mic-regime chunks.
2. Estimate ordinary-speaking body level for each chunk.
3. Repair each chunk toward the shared accepted or provisional speaking target.
4. Trim chunks that are too hot or over-forward; do not raise the whole file to match a damaged weak chunk.
5. Stitch chunks with short transparent ramps, crossfades, or phrase-aware boundary support.
6. Place the background after commentary alignment, using a stable per-chunk bed baseline and local event restraint.
7. Render one full-duration candidate only after the chunk plan is explicit.

Full-file filters are still allowed as implementation details inside a chunk, or as final assembly polish. They are not the default repair model for multi-regime commentary.

## Staged Repair Contract

Use this order for multi-regime commentary:

1. `stage1-chunk-baseline`: render a full-duration candidate from compact editorial chunks, per-chunk mic gain/trim, short boundary ramps, and stable per-chunk bed baselines.
2. `stage2-exception-queue`: convert failed gates from the chunk baseline into a small exception queue with representative windows, common cause, protected chunks, and clearing evidence.
3. `stage3-bounded-automation`: use phrase, transition, local reconstruction, overlay, or bed restraint automation only for the exception queue, not the whole recording.

A later automated candidate must name its parent chunk-baseline candidate, the exception rows it targets, the chunks it must preserve, and the proof that automation did not become the primary repair surface. If there is no parent staged chunk baseline, the candidate is strategy-invalid for promotion.

Do not use dense automation to discover the mix. Use dense analysis to discover chunks, then render the mix from those chunks. Automation is allowed to repair named exceptions after the baseline exists. When the named exception requires local reconstruction, overlay, or intelligibility-first fallback, follow `LOCAL-RECONSTRUCTION.md` before another full render.

Do not use fixed-width time bins as chunks unless source evidence proves the bin contains one stable mic regime. A fixed 30-second or 60-second bin that crosses a capture-level drop, recovery, hot shift, or detector-uncertain phrase region is an invalid chunk and must be split.

Do not swing to the opposite failure mode. A chunk map is not a per-second gain-control table. If the map has hundreds or thousands of tiny rows, mostly one-second rows, or rapidly alternates between `noise`, `weak`, `ordinary`, and `bed-floor` labels, it is probably detector/control data, not an editorial chunk map. Merge it into phrase/regime chunks and store dense gain or bed automation in a separate control file.

Likewise, an `automation_control` table with hundreds or thousands of rows over most of the runtime is not a replacement for chunk assembly. It is valid only when it is explicitly derived from the staged chunk baseline and limited to named exception windows, ramps, holds, or sparse local support. Otherwise fail the strategy as `dense-automation-primary`.

## Chunk Map

Emit a chunk map before rendering:

```text
chunk_id | start | end | source_regime | boundary_basis | ordinary_speech_body_db | target_body_db | planned_gain_or_trim_db | mic_ceiling_db | artifact_risk | bed_plan | boundary_in | boundary_out | regression_windows
```

Chunk boundaries should come from source evidence, not caller-specific timestamps. Caller examples are failure classes that help select boundaries and checks across the whole source.

Keep the map compact: one row per sustained source regime plus explicit boundary rows when needed. Do not turn chunk mapping into a dense per-second table unless the source actually changes that often.

Every chunk needs a `boundary_basis`, such as `level-step`, `speech-body-shift`, `detector-uncertain-transition`, `background-regime-change`, `phrase-region`, `source-stable-span`, or `reviewer-supplemental-boundary`. A map where most boundaries are simply `every-60s`, `fixed-window`, `one-second-analysis`, or `coarse-bin` fails chunk-map validity.

Before rendering, validate the map:

- no chunk crosses a detected capture-level transition without an explicit split;
- no chunk mixes hot/over-forward speech with weak/recoverable speech in the same ordinary-speaking estimate;
- transition-adjacent chunks have separate first-phrase and sustained-post-transition proof windows;
- chunk labels match the evidence inside the chunk, not the average of incompatible regions.
- the map is not so dense that it functions as detector flicker or per-second automation.
- a staged chunk baseline will be rendered and evaluated before any dense automation candidate is promoted.

## Stitching Rules

- Keep chunk edits time-aligned with the source.
- Use short ramps or crossfades at regime boundaries; do not leave several seconds of normal speech below target.
- Preserve phrase starts and tails around boundaries.
- If the first post-boundary active span is too short, scan to the next coherent phrase before judging recovery.
- Treat boundary windows as regression windows for both mic level and bed behavior.

Transition recovery is chunk realignment at a boundary. It is not a separate broad algorithm.

## Bed After Mic

Do not let bed ducking define the commentary repair.

- First make the commentary chunk sound like the same speaker at a comfortable normal-speaking level.
- Then place the bed under that repaired commentary.
- Use stable bed baselines per chunk.
- Use shallow local event restraint only when the bed masks speech.
- Do not make the bed follow mic breaths, detector flicker, phrase gaps, or repaired mic gain movement.

## Failure Response

When a candidate fails:

- If sections are mismatched, revise the chunk gains/trims, not the whole-file loudness.
- If a boundary recovers slowly, repair the boundary chunk or first coherent phrase, not the whole middle section.
- If a chunk-map row averages over the failed boundary, split the row first; do not tune gain on the invalid row.
- If the chunk map turns into hundreds of micro-chunks, merge into phrase/regime chunks first; do not debug thousands of row-level blockers as if each row were a separate editorial problem.
- If the bed pumps, separate bed floor preservation from speech-triggered event restraint.
- If an automated candidate passes local metrics but review blocks control-surface or listener-risk proof, do not keep bounding the same dense control surface. Return to the staged chunk baseline and express the successful behavior as a smaller exception queue.
- If metrics pass but listening feedback reports waviness, section drift, or overgain, reopen the chunk map and boundary proof.

Do not keep tuning a global normalizer, sidechain, limiter, or detector threshold when the failure is caused by chunk mismatch.

If the repair loop is getting long, simplify the next attempt: freeze the best baseline, revise only the failed chunk or boundary, preserve already-good chunks, and rerun the smallest proof that can catch regressions.

## Evidence

Promotion evidence must include:

- chunk map used for the retained candidate;
- chunk-map validity proof;
- chunk density summary, including chunk count, median duration, and whether dense automation was stored separately;
- per-chunk raw and repaired ordinary-speaking body;
- gain/trim applied to each chunk;
- boundary/stitch windows and transition checks;
- bed baseline/floor per chunk;
- proof that hot/recovered chunks were trimmed to the shared target when needed;
- proof that weak chunks were lifted without harshness, clipping, limiting, saturation, muffling, or floor lift.
- staged-repair summary linking any automated candidate to its parent chunk baseline, targeted exception windows, protected chunks, automation coverage, and strategy validity.
