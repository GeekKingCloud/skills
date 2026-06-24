# Background Balance

Use this helper after commentary regimes have a target and the mic repair plan exists.

This phase owns bed placement. The bed should stay present and natural under commentary; it should not be crushed into silence to make the mic pass.

## Baseline Placement

- Establish a stable bed baseline after the commentary chunks have been aligned.
- During ordinary commentary, use a bed body roughly `7-8 dB` under repaired commentary body as a starting reference, not a fixed pass/fail number.
- The baseline should make ordinary background sit naturally under ordinary speech before any ducking or event restraint is applied.
- Do not set a near-full-volume bed baseline just to keep the background hearable, then rely on phrase cuts to protect the mic.
- If the raw bed is already loud, the stable baseline usually needs a meaningful trim. If the bed is quiet, raise it only until it is hearable without forcing the mic into harsh gain or limiting.
- A numeric gap is not enough. The bed baseline, absolute bed comfort, local cut depth, and amount of time spent under local restraint all matter.
- Record the source- or reference-relative baseline decision before local restraint: raw bed body, repaired mic body, target relationship, chosen bed baseline, and why that baseline is comfortable. Do not use fixed universal thresholds as the proof.
- When an accepted reference exists, use its bed floor, bed-under-speech body, and bed movement as the target relationship.
- When only a provisional reference exists, use its bed relationship temporarily and re-check that it did not pass only because the bed was muted.
- Keep background hearable under normal commentary.
- Use shallow smooth bed riding as polish, not the main way to create separation.
- Keep the bed baseline stable per chunk. It may differ by source background regime, but it must not be driven by mic breaths, detector flicker, or short phrase gaps.
- If bed control needs automation, attach it to the staged exception queue from `CHUNK-ASSEMBLY.md`; do not generate whole-runtime bed control as the first strategy.

## Events And Masking

Let exciting background moments breathe only while speech remains clear.

- If a background rise masks speech, lift the repaired mic locally with it first when comfort/headroom allows.
- If further mic lift would be uncomfortable, restrain that background event or section.
- Restrain the local event instead of lowering the whole bed when masking is local.
- Do not let the bed surge loudly between phrases.

## Anti-Overducking

Reject or repair a candidate when:

- the baseline bed is hot and speech clarity is created mainly by many local bed cuts;
- local bed restraint covers a large share of active commentary instead of isolated masking events;
- local bed restraint is applied across most of the recording before a stable per-chunk bed baseline has been proven;
- local bed cuts are deep enough or frequent enough that the bed pumps even if it remains measurable;
- background is audible only when nobody talks;
- background disappears under ordinary commentary;
- background competes with speech and then vanishes under speech;
- bed gain follows mic dips, breaths, detector flicker, or phrase gaps;
- bed gain follows the repaired mic chunk envelope so tightly that the mix pumps or waves;
- bed surges between phrases;
- processed bed readings are near digital silence during ordinary commentary unless raw source proves the bed is absent;
- separation was achieved by crushing the bed instead of repairing mic regimes.
- separation was achieved by pushing mic gain high enough to fight an over-loud bed instead of lowering the bed baseline.

## Evidence

Emit balance checks:

```text
window | regime | commentary_body_db | background_body_db | gap_db | bed_floor_db | event_class | listener_class | action
```

The gap is invalid if it is measured only on detector-approved speech. Include weak, buried, transition, phrase-start, phrase-tail, and detector-uncertain windows from the neutral blind-spot set.

When the render uses automation, also emit a control-surface audit:

```text
candidate_id | candidate_hash | raw_bed_body_db | repaired_mic_body_db | target_bed_relationship | bed_baseline_decision | bed_base_min_db | bed_base_max_db | bed_base_avg_db | bed_extra_min_db | bed_extra_max_db | bed_cut_ge_6db_seconds | bed_cut_ge_10db_seconds | bed_cut_duty_cycle | control_region_count | controlled_speech_seconds | max_local_restraint_db | mic_gain_max_db | mic_gain_ceiling_hit_count | control_surface_class | status | failure_class | action
```

Fail `control_surface_class=high-bed-baseline`, `aggressive-ducking-primary`, `dense-automation-primary`, `strategy-order-violation`, or `control-surface-verifier-gap` when the measured control surface shows a hot bed baseline plus frequent/deep local cuts, whole-runtime automation as the primary repair, or when the verifier's bed-movement claim disagrees with the actual automation, filter graph, or render script.

When `aggressive-ducking-primary` fails, the next candidate goal must reset the bed-control surface before adding more phrase support on top of the same bed behavior. Reduce the stable bed baseline or local-restraint duty cycle, protect already clear speech windows, and prove the bed remains present under ordinary commentary. Do not treat a candidate as a useful listener-test baseline when broad balance passes only because the bed is cut for a large share of active commentary.
