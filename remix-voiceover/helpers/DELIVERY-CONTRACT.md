# Delivery Contract

Use this helper before creating any beside-source output or final report.

## Artifact Permission Matrix

Use this matrix:

```text
confidence_label | artifact_mode | beside_source_mux_allowed
listener-accepted | final-deliverable | yes
independently-verified-ready-for-listener-test | caller-test-mux | yes
producer-checked-candidate | scratch-candidate | no by default
preview-with-known-risks | scratch-candidate or preview-mux | preview only with explicit approval
blocked/source-limited | scratch-candidate | no
blocked | scratch-candidate | no
```

No other beside-source write is allowed.

The following do not clear mux delivery:

- structural mux correctness alone;
- producer comfort;
- `producer-checked-candidate`;
- `iteration-incomplete`;
- unresolved `ambiguous listener-risk`;
- unresolved proof-lineage gaps;
- diagnostic-composite or mixed-baseline source lineage when separate source lanes exist;
- pending evidence reviewer required for caller-test readiness;
- exact-path write approval;
- caller-test instructions written after the mux exists.

If the best candidate is `producer-checked-candidate` or `preview-with-known-risks`, stop before beside-source mux unless the caller explicitly approves a preview after seeing the risk summary.

A `caller-test-mux` is allowed when independent read-only evidence review found no evidence blocker, unresolved listener-risk work item, pending required evidence reviewer, or lineage/proof issue. It is not final. Label it clearly as ready for caller listening, not accepted.

Independent clearance for `caller-test-mux` must cover source/track role map, blind-spot set, listener-risk worst-window evidence, staged-repair summary, control-stress windows and control-surface audit when automation is used, and proof/mux lineage. A proof-only reviewer cannot clear caller-test mux.

For audible failure classes such as aggressive ducking, hot bed, over-loud background, pumping, mic waviness, bed surge, or transition recovery, independent clearance must inspect representative rendered worst-window audio evidence or mark the unreviewed class as unresolved listener risk. This is caller-test evidence review, not final human listener acceptance.

Human listener acceptance is not required for `caller-test-mux`; it is the purpose of caller testing. Lack of human listening blocks only `final-deliverable`. Do not downgrade a clean, independently reviewed caller-test candidate to `scratch-candidate` solely because the producing agent and sub-agents cannot perform human acceptance.

## Preview Mux

A preview mux is allowed only when:

- the caller requested a preview up front; or
- the caller approves a preview after the report states why the candidate is not final-ready.

Label preview outputs as preview/risky. Never present them as final, ready, accepted, or verified.

Approval to write a path is not approval that the audio is ready. Preview approval must mention preview/risk explicitly or follow a risk summary that asks for preview approval.

## Video Output

For any beside-source video:

- use the caller-facing filename `<source-stem>-REMIX-VOICEOVER.<source-container-ext>` unless the caller explicitly provides another exact output path;
- do not append artifact modes or confidence labels such as `-CALLER-TEST`, `-PREVIEW`, `-READY`, or `-FINAL` to caller-facing beside-source outputs;
- stream-copy original video;
- put remixed audio first/default;
- preserve original audio streams afterward when possible;
- verify duration, stream order, default flags, codec/container metadata, and copied-video identity where practical;
- verify final remix audio matches the promoted candidate.

## Cleanup

Keep scratch lean, but do not delete proof needed to explain the result.

Report:

- artifact root;
- retained candidate and proof;
- removed bulky intermediates;
- cleanup method;
- whether cleanup was verified by inspection or only claimed.

After an interrupted or stalled render, also report render process cleanup status and partial-candidate disposition. A partial candidate directory without completed audio, manifest, and lineage proof may be kept as failure evidence, but it cannot be reported as the retained strongest candidate.

If the caller requires separate cleanup approval, do not delete retained proof or candidate artifacts without that approval.

## Final Report Claims

Every material claim must be backed by current-run evidence.

Template fields must not be blank. Use an exact value, `NONE`, or `NOT RUN - reason`. Avoid unsupported words such as `passed`, `checked`, `looks good`, or `verified` unless the same line includes artifact id plus evidence path or hash.

Report:

- skill version used;
- skill source path and instruction bundle hash when practical;
- source/output paths;
- confidence label and human-listening status;
- exact track map;
- render lineage and candidate manifest;
- source-lane lineage mode, including whether any previous candidate, existing mix, or muxed output was used as an audio substrate;
- aggregate promotion proof status, including all required gate files and their pass/fail/not-run states;
- staged-repair summary when automation, sidechain curves, generated filters, local bed restraint, phrase controls, or overlay control are used;
- raw phrase extraction when transition, weak, buried, detector-uncertain, or source-limit rows require phrase-local evidence;
- control-surface audit when automation, sidechain curves, generated filters, local bed restraint, or overlay control are used;
- aggregate proof dependency map showing which gate outputs consumed the control-surface audit hash;
- bed baseline and local-restraint summary, including whether separation came from stable bed placement or frequent/deep ducking;
- candidate count and pivots;
- source evidence coverage;
- blind spots checked and classifications;
- failed-gate work queue and attempted pivots;
- remaining risks and source-limited spans;
- reviewer topology and limits;
- mux status and cleanup status.

If the result is only a scratch candidate, say that. If it is blocked, say what exact evidence or work would unblock it.

The reported confidence label must come from the aggregate promotion proof, not from an individual broad-balance manifest. If any required gate has failed, missing, stale, or not-run evidence, keep the artifact at `scratch-candidate` unless the preview path is explicitly approved.

Report result fields must be derived from the canonical artifact permission matrix. Do not handwrite unrelated values for confidence label, run status, artifact mode, caller-test readiness, deliverable status, and beside-source mux permission.

Gate-specific proof is required for caller-test mux. If transition, speech-envelope, overducking, or mic-alignment evidence is only a placeholder, only an aggregate row, or a proxy for another verifier, the required gate is failed as `verifier-insufficient` even if the aggregate proof says `pass`. Repair the verifier and rerun review before writing beside-source output.

If transition or source-limit evidence says raw phrase extraction is still required, the report cannot classify the row as source-limited, source-limit-suspect, or residual listener risk. Report it as `raw-phrase-extraction-missing` or `verifier-insufficient`, run the extraction, and reclassify before caller-test mux. A report must not call proxy/fixed-frame evidence `raw_phrase_extraction`; if only proxy evidence exists, say direct raw phrase extraction was not run and explain the concrete blocker or run it before stopping.

If the retained render uses automation or generated filters, caller-test mux also requires a passing staged-repair summary, a passing control-surface audit, and aggregate proof that dependent gates consumed those hashes. If the candidate skipped the chunk-baseline stage, has no compact exception queue, or treats whole-runtime automation as the primary repair, it is `strategy-order-violation` or `dense-automation-primary` and cannot be muxed. If overducking or bed-envelope evidence says there is only global bed trim, no bed movement, or no hysteresis needed while the actual render contains per-window bed controls, the candidate is `verifier-insufficient` and cannot be muxed.

Caller-test mux also requires sustained-regime mic alignment and section-overgain proof. A report cannot claim "sections still out of alignment: NONE" from selected hard-window rows only. The proof must cover each sustained recoverable commentary regime and must not leave caller-test-relevant peak, crest, limiter, or artifact checks as `NOT RUN`.

If caller testing reports that a promoted mux has slow transition recovery, unrecovered level drop, mic waviness, bed collapse, aggressive ducking, over-loud background, or section misalignment, reopen the evidence packet as a verifier failure. The next update must explain which gate incorrectly passed and tighten or rerun that gate before another promotion attempt.

If caller testing explicitly identifies one section as the desired target relationship, that section becomes the accepted reference section for the next run. If caller testing instead says a section is broken, repaired, closest-so-far, or only acceptable compared with worse failures, do not make it the reference. A subsequent caller-test mux is not allowed until section-overgain, mic-alignment, transition, and speech-envelope gates explicitly show that the complained-about sections were repaired against the accepted reference or a derived comfortable speech target.

If the run is `iteration-incomplete`, follow the stop-state validity rules in `ITERATION-LOOP.md` exactly. Delivery reporting should state the retained scratch candidate, exact next action, work item preventing terminal status, and valid external stop reason. If source-limit proof, local reconstruction, or mechanism reset is named as the next action but not attempted, the report must show the external blocker that prevented that attempt.

For `listener-accepted`, include listener identity or role, exact windows listened, sample/full-output path, acceptance wording and timestamp, and confirmation that producer local checks did not substitute for human acceptance.
