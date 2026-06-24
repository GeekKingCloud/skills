# Reference Target

Use this helper after source evidence identifies commentary regimes and before rendering a repair.

This phase owns the target. Later phases should not invent a new target to make their local gate pass.

## Accepted Reference

Use an accepted reference only when caller or reviewer evidence explicitly says a section has the desired mic/background relationship.

Do not choose an accepted reference from:

- the loudest raw capture regime;
- a section the caller described as broken, repaired, closest-so-far, problematic, or only better than worse failures;
- a weak/problem section that became acceptable only after heavy repair;
- a section that passes because the bed is muted, crushed, or absent.

Record:

```text
section_id | reference_status | why_chosen | mic_body_db | bed_body_db | gap_db | bed_floor_db | mic_envelope_notes | bed_envelope_notes | protected_regression_windows
```

## Provisional Comfortable Target

If no accepted reference exists after measurable evidence exists, derive a provisional comfortable target.

Prefer a section or candidate region with:

- stable ordinary speech body;
- hearable bed under speech;
- no overducking or bed collapse;
- no masking;
- no harshness, clipping, limiting, saturation, muffling, or section over-gain;
- stable mic and bed envelopes.

Mark it provisional and keep it open to reviewer challenge. Do not leave both `accepted_reference_section=NONE` and `provisional_reference_anchor=NONE` after measurable candidates exist.

Challenge the provisional target against the whole repaired recording before promotion:

- it must not be so quiet that a sustained weak/problem section can pass while the caller would still describe commentary as low;
- it must not be chosen from a damaged weak section, a tiny phrase snippet, or a section that only clears because the background was lowered heavily;
- it must be compared against healthy, weak/problem, recovered, hot, and late sustained regimes after repair;
- if sustained regimes several dB apart all pass, the target or tolerance is wrong.

## Target Use

Use the accepted or provisional target to drive the rest of the run:

- weak recoverable regimes move up toward the target without lifting floor noise;
- hot, recovered, over-forward, or late regimes move down toward the same comfortable target;
- the bed relationship moves toward the target relationship unless raw source proves the bed is absent or intentionally quiet;
- the target section becomes a regression check.

If lifting a weak/problem regime to the target causes noise, harshness, clipping, limiting, muffling, or excessive gain, lower the common speech target or prove a source limit. Do not raise healthy sections to match the damaged regime.

## Clearing Evidence

Target selection is usable only when the report includes:

- accepted reference section or provisional anchor;
- why the target was chosen;
- mic body, bed body, gap, bed floor, and envelope notes;
- protected regression windows;
- how each recoverable regime should move relative to that target.

A target is not promotion-usable when its proof is only selected hard windows, phrase snippets, or blind spots. Those are challenge rows; the target also needs sustained-regime evidence.
