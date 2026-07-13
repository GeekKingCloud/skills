# Delivery Rules

Use this helper after `rv verify` writes a passing `promotion_manifest.json`. Delivery is part of proof, not a file-copy afterthought.

## Contract Path

- Deliver to `<source-stem>-REMIX-VOICEOVER.<source-extension>` beside the source.
- If the caller supplied an exact non-contract output path, pass the verbatim caller text with `--exact-output-request`.
- Never invent suffixes such as ready, preview, caller-test, final, or candidate.
- Quote caller-supplied paths literally in the report.
- Never overwrite or modify the source recording.

Command:

```text
python remix-voiceover/scripts/rv.py deliver --manifest <promotion_manifest.json> --source <source> --output <contract-path>
```

Use `--allow-overwrite` only after overwrite approval:

```text
python remix-voiceover/scripts/rv.py deliver --manifest <promotion_manifest.json> --source <source> --output <contract-path> --allow-overwrite
```

## Awaiting Overwrite

An existing contract output is not a repair blocker.

- Keep working in scratch until `promotion_manifest.json` passes.
- Run `deliver` without `--allow-overwrite`.
- Accept `delivery.json` with `status: awaiting-overwrite`, `output_written: false`, and `next_action: approve overwrite` as a legal end state.
- Report `Run status: caller-test-ready` and `Artifact mode: scratch-candidate`.
- Name the exact next action as overwrite approval.
- Do not choose an alternate caller-facing filename.

`validate-stop` accepts this state when the delivery hash chain points to the promoted candidate and the delivery manifest records awaiting-overwrite.

## Mux Rules

`rv deliver` owns muxing.

- Remix audio is first and default.
- Original audio streams are preserved after the remix.
- Video is stream-copied when the source has video.
- Retain the source container and extension. Select a verified lossless remix codec compatible with that container: FLAC for Matroska/native FLAC, ALAC for MP4-family containers, and float PCM for WAV. This is a codec choice for the new repaired program, never a container conversion.
- Multiplex containers retain copied source video, original audio, subtitles, and attachments. Native single-program audio containers such as FLAC and WAV contain the repaired program only; the source file remains untouched beside the output and delivery proof must say so explicitly.
- Audio-only sources remain supported.
- The delivery manifest records stream order, output hash, candidate hash, and decoded remixed-audio hash equality.
- A diagnostic composite made from an existing mix or prior candidate can be evidence only; never deliver it for caller testing.

Do not run ad-hoc mux commands to bypass `deliver`. If `deliver` refuses, run the repair commands it prints.

## Report Rules

Write the caller report from `templates/REMIX-VOICEOVER.md`.

- Use exact values, `NONE`, or `NOT RUN - <reason>`; leave no blank fields.
- Include the exact machine-checked labels from the template: `Run status:`, `Artifact mode:`, `Source:`, `Output:`, `Candidate sha256:`, `Promotion manifest:`, `Analysis:`, `Render plan:`, `Stop state:`, `Runnable manifest work remains:`, `External blocker:`, `Outcome class:`, `Limitation owner:`, `Limitation evidence:`, `Recommended fix:`, `Informational rows:`, `Bed balance reconciliation:`, `Preferred mic/bed gap dB:`, `Delivered meaningful-bed gap distribution:`, `Gap widening reason:`, `Remaining safe uniform bed lift dB:`, and `Source file preserved:`.
- Set `Candidate sha256:` to `promotion_manifest.json` `candidate.sha256`.
- Set `Source:` to the exact `render_manifest.json.source_path` (or `delivery.json.source_path`).
- Set `Output:` to the exact `delivery.json.output_path`; without a delivery manifest use `NOT RUN - no delivery manifest`.
- Set `Promotion manifest:` to `<promotion path> sha256=<canonical JSON hash> status=<status>` exactly.
- Set `Analysis:` to `<promotion.analysis_path> sha256=<promotion.analysis_sha256>` and `Render plan:` to the analogous plan values exactly.
- Set `Stop state:` to `NOT RUN - generated after report validation`. The validation command hashes the finished report into `stop_state.json`, avoiding a circular self-hash claim.
- Copy the four outcome fields from `promotion_manifest.json.outcome`. Do not assign failure ownership in prose.
- Set `Informational rows:` to compact JSON with the row count and sorted unique `failure_class` values from passing promotion rows that carry a `failure_class`, for example `{"count": 2, "failure_classes": ["bed_underused_disclosure", "gap_preference_disclosure"]}`. `validate-stop` checks this summary against the manifest.
- Set `Bed balance reconciliation:` to the exact sorted JSON `proof` object from the single `bed_yield_necessity` promotion row, or `NONE` only when no bed lane exists. Do not duplicate the label or summarize planner prose; `deliver` requires the proof inventory and `validate-stop` compares this line to verifier-owned evidence.
- Copy the four readable bed-balance lines from that same verifier-owned proof: preferred gap, exact common-window distribution, controlling failure, and remaining candidate-safe uniform lift. Use `NONE` or the explicit not-run reason emitted by the proof rules; `validate-stop` cross-checks every value.
- Set `Runnable manifest work remains:` to `yes - <failure_class>: <next_action>` when a failing row has `action_scope: current-plan`; otherwise use `NONE`.
- Cite sidecar paths and hashes for material claims.
- Include `Rails adjustments:` and `Non-default analyze parameters:` headline lines when the promotion manifest records those surfaces. Role and boundary overrides are unsupported and must never appear in a passing plan.
- When `promotion_manifest.json` records `peak_control.enabled: true`, include and exactly cross-check `Peak control enabled:`, `Peak control mechanism:`, `Peak control declared ceiling dBTP:`, `Peak control pre mic sha256:`, `Peak control post mic sha256:`, `Peak control worst regime BODY delta dB:`, `Peak control global duty:`, `Peak control worst regime duty:`, and `Peak control max contiguous run seconds:`. Copy the values from the manifest; do not recompute or round them differently.
- Include `Exact output request:` with the verbatim caller quote when `delivery.json` records `exact_output_request`.
- Keep caller-facing summary short and separate from proof details.
- Do not claim final delivery unless the caller explicitly finalized; for `Run status: delivered-final`, include `Finalization evidence:` with a quoted caller finalization line and use a `delivery.json` where `output_written` is true.

Stop validation command:

```text
python remix-voiceover/scripts/rv.py validate-stop --report <scratch>/REMIX-VOICEOVER-report.md --manifest <promotion_manifest.json> --delivery <delivery.json> --json-out <scratch>/stop_state.json
```

If there is no delivery because work stopped before delivery, omit `--delivery`. `iteration-incomplete` is valid only for machine-owned `toolkit-limited` or `external-blocked` outcomes with no current-plan action. `blocked-terminal` is valid only for machine-owned `source-terminal` evidence.

## Packet And Cleanup

- Keep `probe.json`, `analysis.json`, `render_plan.json`, sibling `plan_validation.json`, `render_manifest.json`, `promotion_manifest.json`, `delivery.json`, `stop_state.json`, and promoted candidates until the transaction reaches a terminal state.
- After successful delivery and passing stop validation, run guarded `rv cleanup` and verify the transaction root is absent before responding. This successful-run cleanup needs no separate approval because the command hash-verifies the final output and refuses to delete outside scratch.
- Retain proof and candidates for awaiting-overwrite, scratch-only, failed, or blocked outcomes unless the caller explicitly requests cleanup.
- After an interrupted render, report cleanup and partial-candidate disposition.
- Treat a partial candidate without manifest lineage as failure evidence, not the strongest candidate.
