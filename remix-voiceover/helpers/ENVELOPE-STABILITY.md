# Envelope Stability

Use this helper when the mic cuts in and out, the bed breathes with speech, phrase starts/tails are lost, or detector-uncertain spans keep blocking promotion.

This phase owns movement over time. The mix should not pass by producing a good average while sounding wavy.

## Mic Continuity

The repaired mic should sound like one continuous speaker.

- Avoid gain curves that follow breath dips, detector flicker, consonant gaps, phrase-tail uncertainty, or second-by-second noise.
- Prefer stable chunk or phrase-region gain over sample/frame/second-level gain movement when ordinary speaking volume is the target.
- Do not let denoisers, gates, expanders, companders, or dynamic normalizers swallow starts, tails, or short low-energy words.
- Preserve normal pauses and low-energy phrase parts.
- If caller feedback reports mic waviness, reopen speech-envelope stability and section alignment.

## Phrase-Region Repair

When per-second gain holds miss starts, tails, or detector-uncertain active speech, switch to phrase-region repair:

- build a source-agnostic phrase map from evidence rows, detector output, raw mic energy, and candidate failures;
- group continuous speech into phrase regions;
- bridge short gaps caused by breaths, consonants, or detector uncertainty;
- apply stable mic treatment across the whole phrase;
- keep bed control smoother than speech control;
- use the previous best candidate as a regression baseline.

Do not treat "not easy in the current filter graph" as a failed attempt. Build scratch automation when needed.

## Bed Envelope

The background should not breathe with the mic.

- Smooth bed control across phrases and short pauses.
- Use hysteresis, hold windows, phrase-level regions, or event-level bed restraint instead of frame-by-frame sidechain tracking.
- Prefer a stable bed baseline plus sparse event restraint over phrase-by-phrase cuts across most speech.
- Do not use raw mic RMS as the direct bed envelope when the mic has dips, detector uncertainty, breaths, or intermittent phrase tails.
- If the mic lane dips briefly inside an otherwise stable speech regime, repair or ignore the dip for bed-control purposes; do not make the bed bounce around it.
- If speech clarity requires local ducking, keep it shallow enough that the bed remains naturally present unless the alternative is masked speech.
- If speech improves but the bed collapses, try a phrase-bed-floor pivot.
- If the commentary itself is stable but the bed sounds wavy, repair the bed control surface. Do not make new mic gain movement just to satisfy a bed-envelope metric.
- If the renderer uses automation or a generated filter graph, measure bed movement from that same control surface. Do not report `global trim only`, `none`, or `not_needed` when the retained render contains per-window bed controls.

## Evidence

Emit speech-envelope checks:

```text
window | regime | active_speech_seconds | phrase_region | mic_gain_movement_db | start_tail_class | detector_basis | listener_class | action
```

Emit bed-envelope checks:

```text
window | regime | bed_gain_movement_db | mic_movement_basis | hold_or_hysteresis_used | bed_floor_db | listener_class | action
```

`raw-shaped-envelope-movement` is not an automatic pass. Use it only when raw and candidate evidence show the repair did not amplify the movement and the movement does not create audible waviness.

Bed-envelope evidence is insufficient when it only inspects output averages and ignores the automation that created them. If actual bed controls change by phrase, event, or window, include control-region count, maximum bed cut, cut duty cycle, and smoothing/hold basis. A mismatch between proof and render control data is `verifier-insufficient`.
