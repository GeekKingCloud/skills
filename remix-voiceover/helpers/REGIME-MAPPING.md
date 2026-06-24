# Regime Mapping

Use this helper to turn raw track evidence into the repair map.

## Commentary Regimes

Map the commentary/mic lane into sustained behavior classes:

- healthy ordinary speech;
- weak but recoverable speech;
- buried speech under active background;
- intermittent phrase starts/tails;
- quiet true no-speech or mic floor;
- recovered/hot speech;
- over-forward or uncomfortable speech;
- clipped, distorted, or source-limited speech.

Do not let one speech detector define all activity. Weak commentary can be recoverable even when a detector marks it inactive.

Emit a mic-regime map:

```text
start | end | regime_label | speech_body_level | normal_speaking_reference | delta_from_reference | floor_level | peak_behavior | envelope_stability | confidence | examples
```

Use practical labels such as `healthy`, `weak-but-recoverable`, `buried`, `intermittent`, `hot`, `over-forward`, `late-recovery`, `noise-only`, and `unknown-listener-risk`.

`delta_from_reference` is a repair target, not just a description. Negative and positive deltas both matter. If a recoverable regime remains shifted down from the same speaker's normal talking level, or remains much hotter than the other repaired regimes, keep iterating or prove source limits. Use `envelope_stability` to flag mic pumping, cutting in/out, or detector-shaped gain.

## Transition Regions

Mark listener-risk regions around:

- first drop after healthy commentary;
- first recoverable phrases after a capture-level change;
- weak middle regimes;
- recovery from weak to healthy or hot speech;
- loud or recovered regimes that remain over-forward after weaker regimes are repaired;
- starts and tails after pauses;
- late active sections and end tails.

Correction should happen at the next coherent phrase. Slow fades that leave speech buried for several seconds are failures.

Classify boundary type before creating transition work. Use this canonical `boundary_type` enum across regime maps, transition checks, source-limit proof, and reviewer packets:

- `capture-level-transition`: sudden mic body change, drop, recovery, or hot shift;
- `recovery-transition`: boundary where a damaged, weak, or buried regime returns to a healthier capture level;
- `hot-shift`: boundary into or out of a sustained over-forward, recovered-hot, or harsh commentary regime;
- `caller-example-transition`: caller-reported failure class found in source-wide evidence;
- `weak-regime-boundary`: boundary into or out of sustained weak/buried commentary without enough source evidence to classify it as a capture-level transition;
- `ordinary-stitch-seam`: editorial chunk seam without source evidence of a capture-level change;
- `background-regime-boundary`: bed/source change that does not itself imply mic transition recovery.

Only `capture-level-transition`, `recovery-transition`, `hot-shift`, and `caller-example-transition` should become transition-recovery blockers. `weak-regime-boundary` rows are repaired through section realignment, phrase-region support, and weak-commentary proof unless raw source evidence upgrades that boundary to one of the transition types. Ordinary stitch seams should be protected by chunk/stitch regression proof so the verifier does not manufacture dozens of transition failures from a compact chunk map.

Mark both sides of the transition:

- the last stable phrase before the change;
- the first recoverable phrase after the change;
- any short dips inside an otherwise stable regime that should not drive background automation;
- the first background-active span after the change.

Emit transition checks:

```text
boundary | boundary_type | before_regime | after_regime | boundary_basis | last_stable_phrase | first_recoverable_phrase | recovery_time | mic_body_before_after | mic_delta_from_reference_after | bed_body_before_after | speech_envelope_stability | bed_envelope_stability | failure_class | candidate_action
```

Use `speech_envelope_stability` and `bed_envelope_stability` to flag whether the candidate stayed stable through the transition or created audible mic/bed waviness.

## Background Regimes

Map the background/system lane into:

- normal bed;
- background-only stretches;
- loud events while speech is active;
- quiet/horror or intentional low-bed sections;
- music-heavy sections;
- raw-bed absent or source-limited sections.

Background-only sections matter because overducked mixes often sound good under speech but dead between phrases, or the reverse.

## Blind-Spot Set

Build a candidate-independent blind-spot set before rendering. Include:

- weak-mic/loud-bed clusters;
- inactive detector spans with recurring mic peaks or phrase-shaped movement;
- first drops after healthy commentary;
- long weak or buried regimes;
- late recovery and hot sections;
- background-only sections with raw bed present;
- phrase starts and tails after pauses;
- random inactive/background-active windows selected without candidate thresholds;
- caller examples converted into source-wide failure classes that are searched across the whole recording.

Before the first render, write `blindspots.json` or equivalent with:

- source hash or fingerprint;
- selection seed when random sampling is used;
- selection method;
- per-regime minimum counts;
- caller-example-derived failure classes;
- blind-spot manifest hash.

Do not remove or replace blind spots after seeing candidate results. Add reviewer-requested supplemental windows in a separate file.

For each blind spot, classify after candidate review:

- `recoverable commentary`;
- `true no-commentary`;
- `source-limited/unrecoverable`;
- `ambiguous listener-risk`.

`source-limited` requires raw-window or raw-phrase evidence and a reason class such as absent mic, clipped speech, indistinguishable noise, raw bed absent, or ambiguous bleed. Threshold math alone is not enough.

Do not classify a span as `source-limit-suspect` just because the verifier has not extracted the raw phrase. `requires phrase-local extraction`, missing raw phrase evidence, or unknown boundary evidence is a verifier gap and immediate work item, not a source-limit claim.

For each source-limited claim, record:

```text
window | boundary_type | raw_mic_evidence | raw_phrase_evidence | raw_bed_evidence | processed_candidate_evidence | reason_class | listened_or_measured | why_next_pivot_cannot_recover
```
