# Run Setup

Use this helper before probing or rendering.

## Output Shape

Clarify the requested output shape from the caller's words:

- `audio-only`: produce a scratch, caller-test, or final audio artifact according to artifact-mode gates.
- `muxed-video`: produce a beside-source `-REMIX-VOICEOVER` output only after the artifact-mode matrix allows it.
- `verification-only`: inspect a named artifact without re-rendering unless the caller asks.
- `skill-validation`: test the skill itself with fresh-context workers and hidden holdouts.

If the caller asks for a normal repair, start with `audio-only` scratch candidates. Do not mux video until the delivery contract allows it.

## Artifact Mode

Separate output shape from confidence:

- `scratch-candidate`: retained scratch audio only.
- `preview-mux`: beside-source mux with disclosed known risks and explicit preview approval.
- `caller-test-mux`: audio-only or beside-source mux independently cleared for caller listening, but not listener-accepted.
- `final-deliverable`: listener-accepted output.

Report the artifact mode explicitly. A `caller-test-mux` may be useful and worth the caller's time, but it is not final.

## Sub-Agents

At startup, request permission to use sub-agents/reviewers if permission is not already explicit. Use parent-orchestrated reviewers; do not assume a child worker can spawn its own reviewers.

Suggested roles:

- source/track reviewer;
- blind-spot reviewer;
- listener-risk reviewer;
- proof/mux reviewer;
- cleanup reviewer.

Reviewer packets should be read-only and source-grounded. Give reviewers raw source evidence, blind-spot lists, candidate manifests, and the specific question they must answer. Do not give them the producer's desired conclusion.

Listener-risk review is required whenever the source or candidate has weak/buried commentary, transition regions, detector-uncertain spans, or unresolved ambiguous windows. If an independent reviewer is unavailable, the run cannot exceed `producer-checked-candidate` and cannot create a caller-test mux.

If reviewers are unavailable, continue producer-side repair unless the caller asked for independent-only validation. Produce scratch candidates and a repair ledger, but do not promote beyond `producer-checked-candidate` or create beside-source output without explicit preview approval.

`listener-accepted` requires caller acceptance or another identified human listener. The producing coding agent cannot be the accepting listener.

## Freshness

- Start from raw source every time unless the caller explicitly asks to verify or promote a named artifact.
- Use a fresh scratch folder.
- Record skill version, skill source path, instruction bundle hash when practical, source path, source fingerprint or hash, start time, output mode, scratch path, selected streams, and excluded streams.
- Do not reuse old candidates, proof windows, settings, route maps, or timestamps as solution inputs.
- Treat old failures as failure classes, not repair ranges.

## Path Safety

- Treat caller-supplied source and output paths as literal file paths, not shell text.
- Prefer argument arrays, literal-path APIs, or carefully quoted command arguments when invoking media tools.
- Resolve output paths before writing and confirm they are the approved scratch path, the approved exact path, or the delivery-contract beside-source path.
- Never overwrite the original source file or delete source media during cleanup.

## Source And Output Contract

For video inputs:

- copied video must remain unchanged in beside-source output;
- remixed audio should be first/default;
- original audio streams should be preserved after the remix when possible;
- same-folder mux naming must use `<source-stem>-REMIX-VOICEOVER.<source-container-ext>` unless the caller explicitly provides another exact output path;
- artifact modes and confidence labels such as `caller-test`, `preview`, `ready`, or `final` belong in the report, not in invented caller-facing filename suffixes.

Keep deletion of large scratch artifacts separate from final write approval when the caller has asked for that boundary.
