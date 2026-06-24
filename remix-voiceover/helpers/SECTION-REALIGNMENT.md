# Section Realignment

Use this helper when recoverable commentary regimes do not share one comfortable normal-speaking level.

This phase owns the mic/commentary body level before background placement. Do not use bed ducking, final loudness normalization, limiting, or compression to hide unresolved mic-section mismatch.

Apply this per chunk. The repair unit is a sustained commentary regime, not the whole file, unless source evidence proves there is only one stable regime.

## Repair Goal

Build a stable commentary lane first:

1. Estimate ordinary speech body per sustained mic regime.
2. Exclude silence, mic floor, breath-only dips, obvious yells, true whispers, and source-limited noise-floor spans from the ordinary-speaking estimate.
3. Align weak, healthy, recovered, hot, over-forward, and late regimes toward the accepted or provisional target from `REFERENCE-TARGET.md`.
4. Raise weak recoverable chunks with chunk-level gain, short boundary ramps, and phrase-window repair.
5. Trim hot/recovered/over-forward chunks toward the same target while preserving expressive peaks.
6. Lower the common target if weak sections cannot reach it without artifacts.

Do not lift mic floor or empty noise to fake parity.

Promotion-grade section realignment requires two layers of proof:

- sustained-regime proof for every recoverable section, including weak/problem, healthy, recovered, hot, late, and transition-adjacent sustained regions;
- phrase/blind-spot proof for hard windows, starts/tails, and transitions inside those sections.

Sparse phrase rows cannot substitute for sustained-regime proof. A row with less than enough active speech to represent the section is diagnostic only; it may prove a local hard window, but it cannot clear the whole section. If the middle/problem regime spans minutes, the verifier must summarize enough active-speech phrases across that regime to show the section's normal speaking body is aligned, or mark the section `speaking-level-misalignment`, `weak-commentary-buried`, `raw-phrase-extraction-missing`, or `source-limited-unproven`.

## Anti-Overgain Rules

Reject or repair a candidate when:

- first, weak/problem, recovered, hot, late, or end regimes have mismatched normal-speaking body after repair;
- already-loud sections become the reference instead of being trimmed;
- peaks pass numerically but the voice sounds harsh, clipped, limited, saturated, or muffled;
- whole-file normalization makes healthy sections uncomfortable after weak sections are repaired;
- background placement is based on an over-hot mic reference.

If a repaired weak/problem regime is near the comfortable target but other regimes are too loud, the next pivot is hot-regime trim, common-target reduction, or section-level realignment.

Do not solve this by applying the weak-section lift to every chunk. That creates loud first or recovered sections and means the chunk plan failed.

## Late Recovery

When a mic recovers after a weak section, compare recovered normal speech against the accepted or provisional target, not raw recovered mic strength.

- trim recovered speech body toward the target;
- restore bed floor and bed-under-speech relationship toward the target;
- treat huge mic/bed gaps in recovered sections as overducking or section misalignment until proven source-limited;
- preserve the target section and the repaired weak/problem section as regression checks.

## Evidence

Emit mic alignment checks:

```text
regime | representative_windows | raw_speech_body_db | repaired_speech_body_db | target_reference_db | delta_from_reference_db | gain_or_trim_db | floor_lift_db | peak_after_dbfs | loudness_artifact_class | listener_class | action
```

For sustained-regime rows, include coverage fields:

```text
regime | section_start | section_end | active_phrase_count | active_speech_seconds | section_coverage_basis | repaired_speech_body_db | target_reference_db | delta_from_reference_db | status | failure_class | action
```

Emit section over-gain checks:

```text
regime | representative_windows | target_reference_db | repaired_speech_body_db | delta_from_reference_db | peak_after_dbfs | crest_or_limiter_notes | artifact_class | action
```

A candidate fails when a recoverable regime remains shifted down, remains over-forward, takes several seconds after transition to reach the target, or reaches the target by becoming harsh, clipped, limited, saturated, or muffled. It also fails when section-overgain proof says peak or crest checks are required but `NOT RUN`, unless the candidate is kept scratch-only with that verifier gap named as the next action.
