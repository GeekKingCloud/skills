# Transition Recovery

Use this helper when raw source evidence shows a mic capture-level change, drop, recovery, hot shift, or caller-example transition.

This phase owns the boundary. Broad section averages, aggregate rows, and proxy checks cannot clear transition recovery.

Transition recovery is the boundary-local form of chunk realignment. Detecting the sudden capture-level change is special; the repair target is still the same ordinary-speaking target used for the neighboring commentary chunks.

Do not treat every chunk seam as a transition. A chunk boundary is a transition only when source evidence shows a capture-level change, recovery, hot shift, weak-to-healthy shift, or caller-example failure class. Ordinary editorial seams require stitch regression proof, not transition recovery rows.

## Repair Goal

Correct capture-level transitions at the next coherent recoverable phrase.

- Detect the last stable phrase before the change.
- Detect the first recoverable phrase after the change.
- Bring that first recoverable phrase near the accepted or provisional ordinary-speaking target quickly enough that the listener does not think the audio broke.
- Prefer regime-boundary gain steps, short ramps, phrase-window support, or local automation over slow whole-section normalization.
- If the post-boundary chunk is weak, repair that chunk and its first coherent phrase together instead of using a separate transition-only loudness target.
- Preserve starts and tails.
- Keep the background stable; do not make the bed swell, vanish, or follow the mic dip.

If the first detected micro-window is too short for confident speech measurement, scan to the next coherent phrase before classifying the transition. Do not mark a capture-level transition `not_applicable` while its row still says the phrase was not recovered.

If exact boundary evidence requires phrase-local extraction, perform that extraction before classifying source limits or promotion status. A row whose raw evidence says `requires phrase-local extraction`, `unknown`, or equivalent is `verifier-insufficient` until the raw phrase is measured or the boundary is reclassified as an ordinary stitch seam.

## Failure Classes

Keep a transition blocking when:

- first phrases after the step remain shifted down;
- recovery takes several seconds of normal speech;
- the first repaired phrase is over-hot, masked, muffled, clipped, or missing starts/tails;
- evidence is only a broad average, aggregate row, or proxy from another gate;
- evidence says phrase-local extraction is still required;
- the row says `NOT RECOVERED` and was waived as `not_applicable`.

## Evidence

Emit transition checks:

```text
transition_id | boundary_type | transition_basis | raw_phrase_evidence | raw_pre_body_db | raw_post_body_db | repaired_first_phrase_body_db | repaired_early_post_body_db | target_reference_db | seconds_to_recovery | bed_body_during_recovery_db | gap_during_recovery_db | phrase_start_tail_class | loudness_artifact_class | action | status
```

Clearing evidence compares raw mic, raw bed, previous best candidate, and new candidate for each boundary. Include seconds-to-recovery and phrase-start/tail preservation.

Use the canonical `boundary_type` enum from `REGIME-MAPPING.md`: `capture-level-transition|recovery-transition|hot-shift|caller-example-transition|weak-regime-boundary|ordinary-stitch-seam|background-regime-boundary`.

Only `capture-level-transition`, `recovery-transition`, `hot-shift`, and `caller-example-transition` belong to transition recovery. `weak-regime-boundary` belongs to section realignment, phrase-region support, and weak-commentary proof unless raw source evidence upgrades it to a transition type. `ordinary-stitch-seam` rows should be verified by chunk/stitch regression unless candidate evidence proves the seam behaves like a transition. `background-regime-boundary` belongs to background-balance proof unless it coincides with a source-evidenced commentary transition.
