# Adversarial Validation

Use this helper after source evidence exists and before any candidate is accepted.

## Validation Mindset

Assume the candidate can pass its own proof while still sounding bad.

The validation job is to attack the candidate's assumptions:

- What did the detector exclude?
- What did the route map miss?
- What windows were never listened to or measured?
- What did reviewers inspect versus trust?
- What would make a viewer stop watching?

Candidate proof is defendant evidence. Neutral source evidence and adversarial blind-spot checks decide whether the proof is credible.

## Candidate Manifest

Every retained candidate needs an immutable `candidate_manifest.json`.

Include:

- candidate id and path;
- source path and source hash when practical;
- stream map and role map;
- render command or render script path/hash;
- selected streams and excluded streams;
- candidate hash, codec, duration, and headroom;
- proof file paths and proof input data;
- verifier script or procedure used;
- blind-spot audit path;
- exception summary;
- reviewer status and whether reviewers were independent/read-only;
- final mux path/hash when promoted;
- cleanup status and retained artifacts;
- whether cleanup was verified by inspection or only claimed by the producer.

Every proof table should reference the candidate id or hash. A final report that cites proof without a manifest is incomplete.

If full source hashing is impractical, record a substitute source fingerprint: absolute path, size, modified time, duration, stream layout, codec metadata, and hashes of sampled start/end chunks when practical.

## Mandatory Blind-Spot Audit

Build and inspect a candidate-independent blind-spot set from raw source evidence. Include:

- weak-mic/loud-bed clusters;
- inactive detector spans with recurring mic peaks or phrase-shaped movement;
- first drop after healthy commentary;
- long quiet or buried middle regimes;
- late recovery or hot sections;
- background-only sections with raw bed present;
- phrase starts and tails after pauses;
- caller-provided examples converted into full-file failure classes;
- any sustained region skipped by candidate proof;
- a random or adversarial sample of inactive/background-active windows selected without the candidate's accepted active mask, thresholds, or mix settings.

For each cluster, classify:

- `recoverable commentary`;
- `true no-commentary`;
- `source-limited/unrecoverable`;
- `ambiguous listener-risk`.

Any `recoverable commentary` or `ambiguous listener-risk` cluster must appear in final validation. It cannot be excluded by the same detector that controlled the mix.

Unresolved `ambiguous listener-risk` is blocking for final delivery. It is not enough to list those spans as caller-test instructions after writing the beside-source file. Either render a materially different candidate that clears them, classify them as source-limited with raw-window evidence and a reason class, or stop with a scratch candidate.

If exceptions are used, report them separately from passes. Excused failures remain visible evidence. If excused windows cluster in one regime or make up a material share of active or suspect commentary, the candidate needs human listener acceptance or must be downgraded.

`source-limited` is a classification, not a threshold escape. Each source-limited cluster needs raw-window evidence and a reason class such as absent mic, clipped speech, indistinguishable noise, raw bed absent, or ambiguous bleed. Threshold math alone cannot clear a source-limited exception.

## Disproof Checks

Reject or downgrade a candidate when any are true:

- processed output in a blind spot is essentially raw background or existing mix while mic evidence remains recoverable;
- the active-commentary mask excludes sustained weak commentary without raw proof;
- gap metrics pass only on selected active windows;
- ordinary speech body differs materially across sustained regimes without a source-limited reason;
- background is near commentary level during sustained speech;
- background disappears under ordinary commentary;
- background surges between phrases;
- mic starts or tails are swallowed;
- transition recovery sounds or measures slow;
- healthy/recovered speech becomes hot, harsh, clipped, or recessed to compensate for weak sections;
- the mix reaches a target gap by flattening mic and bed into a near-constant ratio;
- proof tables contain unresolved expressions, placeholders, object dumps, previous-candidate data, or missing scalar values;
- exception labels hide repeated or clustered failures;
- `source-limited` labels are assigned from thresholds without raw-window evidence and reason classes;
- unresolved listener-risk windows remain in weak, buried, transition, late-recovery, phrase-start, or phrase-tail regions;
- a listener-risk, blind-spot, or proof reviewer was requested but has not returned;
- rejected candidates, bulky scratch media, or missing cleanup summaries remain without a reason.

## Reviewer Roles

Use reviewers when available. Keep roles independent and adversarial.

- **Source reviewer:** challenges stream roles and neutral source coverage.
- **Blind-spot reviewer:** checks excluded and detector-uncertain regions before reading candidate pass claims.
- **Listener-risk reviewer:** checks worst windows for masking, pumping, missing starts/tails, crushed background, and transition problems.
- **Proof reviewer:** checks hashes, stream lineage, exact candidate identity, mux structure, and cleanup.

Reviewer packets should include raw source evidence and blind-spot lists before candidate success summaries. A reviewer who only validates the proof packet cannot clear listener risk.

Reviewer packets must be read-only. Do not give reviewers renderer rationale, intended fixes, or producer conclusions before they inspect source evidence, blind spots, and the candidate manifest.

If reviewers are unavailable, do the same roles locally and label the run `local-only`.

## Fresh-Context Testing

When testing the skill itself, use the freshest worker available.

Pass only:

- the skill path or byte-identical skill text;
- the raw source path;
- a realistic caller request;
- the requested output mode.

Do not pass:

- parent-discovered failure windows;
- expected fixes;
- previous candidate settings;
- hidden holdouts;
- reviewer conclusions;
- old proof packets unless the caller explicitly asks to verify them.

After the worker finishes, check hidden holdouts and other corpus files as parent validation. Do not feed those holdouts back to the same worker as targeted fixes.

Separate media repair from skill validation. A repair run can produce a caller-testable candidate. A skill-validation run additionally needs fresh-context execution, hidden holdouts selected after the candidate exists, and context-isolation disclosure. Do not claim the skill itself passed validation from a contaminated repair run.

After a material skill change, validate against the hardest available representative source first, then at least one track-role sanity source and one background-preservation source when available. Report untested corpus coverage as unverified.

## Confidence Labels

Use only these labels:

- `listener-accepted`: a human listened to representative worst windows and accepted them.
- `independently-verified-ready-for-listener-test`: a read-only verifier or reviewer that did not tune or render the candidate found no blocker, but no human accepted the file.
- `producer-checked-candidate`: the producer's local checks found no blocker, but no independent verifier or human accepted the file. This is not deliverable by default.
- `preview-with-known-risks`: structurally safe and possibly useful, but known risks remain. Stop before final/beside-source mux unless the caller explicitly requested or approves a preview after seeing the risk.
- `blocked/source-limited`: raw speech is absent, clipped beyond repair, or indistinguishable from noise in controlling areas.
- `blocked`: safe useful output is not possible with current evidence, tools, permissions, or stream roles.

Do not use `technical-only success` as a success claim. Without human listening or independent read-only verification, the best normal label is `producer-checked-candidate`, and the run must stop before beside-source mux unless the caller explicitly approves a preview after seeing the unresolved risk summary.

The producing agent's comfort is not enough to create a final/beside-source mux. If the agent or reviewer is not comfortable recommending listener testing, or if an independent read-only reviewer has not returned, label the candidate `preview-with-known-risks` or `producer-checked-candidate`, retain it in scratch, and stop for caller approval instead of writing the final output.

## Final Report Evidence

Report:

- source/output paths;
- confidence label and human-listening status;
- exact track map and render lineage;
- candidate count and pivot reasons;
- source evidence coverage;
- editorial plan summary;
- blind spots checked and classifications;
- remaining risks and source-limited spans;
- reviewer topology and limits;
- mux structure and cleanup status.

If the result is only ready for caller testing, state that plainly. If it is only a preview with known risks, do not present a final output path unless the caller explicitly approved a preview mux.
