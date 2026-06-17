---
name: remix-voiceover
description: Repair commentary-over-background audio or video with separate mic/commentary and background/system tracks into a listener-first REMIX-VOICEOVER output, using fresh source evidence, editorial mix planning, adversarial validation, copied video, preserved original audio, cleanup, and honest confidence labels.
---

# Remix Voiceover

Use this when a recording has separate commentary/mic and background/system audio and needs a repaired voiceover-style mix.

The goal is not to satisfy a verifier. The goal is a file a viewer can watch without losing the commentary, losing the background, hearing obvious pumping, or wondering whether the audio broke.

Before rendering, read:

- `helpers/EDITORIAL-MODEL.md` for stream mapping, commentary repair, background placement, and mix decisions.
- `helpers/ADVERSARIAL-VALIDATION.md` for evidence integrity, reviewers, confidence labels, and final report requirements.
- `templates/REMIX-VOICEOVER.md` when writing the final report.

## Operating Principle

Treat every run as an editorial repair with adversarial validation.

- The source evidence describes the file.
- The editorial plan explains what the mix should do.
- The candidate proves what it actually did.
- The adversarial review tries to prove why the candidate could still sound bad.
- The final report labels the result honestly.

Never let the candidate define the only evidence frame used to accept itself. A detector, route map, proof packet, or reviewer summary can be useful, but it is not ground truth.

## Non-Negotiable Outcome

A candidate is not acceptable unless all are true:

- The remix uses separate mic/commentary and background lanes when they exist, not the existing combined mix.
- Commentary remains the priority wherever recoverable speech exists.
- Sustained mic capture regimes are found from the whole source, including quiet, weak, recovered, intermittent, and hot sections.
- Weak or buried commentary is not excluded just because a speech detector marks it inactive.
- The background remains present and natural under normal commentary, not crushed or switched on and off.
- Major commentary-level transitions recover quickly and do not leave a section sounding broken.
- The proof is for the exact retained candidate or final output.
- Reviewer or local adversarial checks inspect likely blind spots, not only the candidate's reported pass windows.
- Each retained candidate has an immutable manifest tying source identity, selected streams, render settings, candidate hash, proof inputs, proof outputs, verifier status, and cleanup status together.
- No unresolved recoverable-commentary or ambiguous listener-risk cluster remains in weak, buried, transition, or late-recovery regions.
- Any required listener-risk reviewer has returned. A pending reviewer is a stop condition, not a reason to proceed locally.

If any condition fails, do not call the result successful. Render a materially different candidate, stop with the best scratch candidate and its risks, or report blocked.

## Fresh Run Rules

- Start from the raw source every time unless the caller explicitly asks to verify or promote a named artifact.
- Use a fresh scratch/artifact folder and record source path, start time, output mode, and scratch path.
- Do not reuse old candidates, route maps, detector thresholds, proof windows, settings, or timestamps as solution inputs.
- Treat caller-provided timestamps as examples of failure classes. Use them to guide full-file detection, never as hand-authored fix ranges.
- During testing, render audio-only candidates first. Mux video only after a candidate is useful enough to recommend for caller listening, or after the caller explicitly asks for a preview despite disclosed risks.
- For video inputs, copy the original video unchanged.
- Add the remixed audio as the first/default audio stream and preserve original audio streams afterward when possible.
- Keep scratch lean and write a cleanup summary before finishing.

## Required Workflow

### 1. Build Neutral Source Evidence

Before choosing a mix strategy, map the source independently of any candidate:

- identify every audio stream as `0:a:N` and container stream number;
- classify likely `commentary/mic`, `background/system`, and `existing mix`;
- measure full-file rolling behavior for the separate mic and background lanes;
- identify healthy, weak, recovered, hot, intermittent, silence/noise, and background-only regions;
- build a suspect-blind-spot set: weak-mic/loud-bed clusters, detector-uncertain spans, inactive/background-active samples selected without the candidate's accepted active mask or mix settings, first drops after healthy speech, late recoveries, starts/tails after pauses, and caller-seeded examples as failure classes.

This evidence is neutral. It exists to challenge the candidate later. Do not tune it after seeing whether a candidate passed.

### 2. Write An Editorial Plan

Write a compact plan before rendering:

- chosen stream roles and why the existing mix is excluded or preserved only as an original;
- commentary regimes and intended treatment for each;
- ordinary-speaking reference and comfortable mic ceiling;
- background baseline and hearable floor;
- when shallow bed riding is allowed;
- when mic-follow is allowed for background rises;
- what source-limited areas cannot be fixed;
- what blind spots the candidate must survive.

Prefer simple, source-aware gain and shallow smooth bed control. Use dynamic processors only when their failure modes are checked: lifted silence, chopped syllables, slow recovery, pumping, harsh peaks, and lost background.

### 3. Render A Candidate

Render a full-file audio candidate that implements the plan. A generic normalizer, fixed gain, or sidechain graph is only valid when the source evidence shows one stable regime.

For each candidate, save compact proof:

- immutable `candidate_manifest.json` with candidate id, source path/hash when practical, stream map, render command or script path/hash, candidate path/hash, proof files, verifier inputs, verifier outputs, reviewer status, final mux linkage, and cleanup state;
- render lineage and stream maps;
- processed mic and processed background evidence where possible;
- headroom and duration checks;
- regime parity checks;
- transition recovery checks;
- background-under-commentary and background-only checks;
- blind-spot checks from the neutral source evidence.

Do not rank candidates by aggregate risk count alone. A lower risk count does not matter if the remaining risks are concentrated in listener-critical weak commentary, transition recovery, late recovery, phrase starts/tails, or buried speech. One unresolved listener-critical cluster is enough to block delivery.

### 4. Try To Disprove The Candidate

Before any confidence label, run the adversarial checks in `helpers/ADVERSARIAL-VALIDATION.md`.

The candidate fails if it passes only because:

- weak commentary was marked inactive;
- excluded windows were never inspected;
- selected windows look good while whole regimes still sound wrong;
- the background is audible only when nobody talks;
- the background competes with speech then vanishes under speech;
- the mix is a near-constant ratio that destroys natural dynamics;
- the proof packet, reviewer packet, or final report hides unresolved risk.
- unresolved `ambiguous listener-risk` windows are moved into caller-test notes instead of blocking delivery.
- a proof/listener-risk reviewer is requested but has not returned.

Use reviewers when available. Ask them to disprove stream roles, source evidence coverage, listener-risk windows, and confidence labels. A reviewer who only checks hashes, headroom, and proof consistency is not enough.

### 5. Decide Honestly

Use these labels:

- `listener-accepted`: a human listened to representative worst windows and accepted them.
- `independently-verified-ready-for-listener-test`: a read-only verifier or reviewer that did not tune or render the candidate found no blocking issue, but no human listener accepted the file.
- `producer-checked-candidate`: the producing agent's local checks found no blocking issue, but no independent verifier or human listener accepted the file.
- `preview-with-known-risks`: structurally safe and possibly useful, but known risks remain. This is not a deliverable label by default.
- `blocked/source-limited`: raw speech is absent, clipped beyond repair, or indistinguishable from noise in controlling areas.
- `blocked`: stream roles, tooling, evidence, candidate behavior, or permissions prevent a safe useful output.

Do not use `technical-only success` as a success claim. The producing agent cannot promote its own output above `producer-checked-candidate` without human listener acceptance or independent read-only verification.

`producer-checked-candidate` is not a deliverable label. It may only produce a retained scratch candidate and a report explaining why independent review or human listening is still needed. Do not write a beside-source final output for a producer-checked candidate unless the caller explicitly asks for a preview after seeing the unresolved risks.

If any blind-spot result is still classified as `ambiguous listener-risk`, or any recoverable-commentary cluster still has negative or near-zero mic-over-background gap, the candidate is `preview-with-known-risks` at best. Do not convert those windows into caller-test instructions for a final mux.

## Final Mux

Mux beside the source only after a candidate is externally cleared:

- `listener-accepted`
- `independently-verified-ready-for-listener-test`

If the best label is `producer-checked-candidate` or `preview-with-known-risks`, stop before final/beside-source mux by default. Keep the best candidate in scratch, report why it is not ready as a final deliverable, and ask whether the caller wants a preview mux anyway. A preview mux is allowed only when the caller explicitly requested a preview up front or approves one after seeing the downgrade reason.

Exact-path write approval does not override quality approval. If the candidate has unresolved listener-risk evidence, interpret write approval as permission to create a preview only after the caller has been told the downgrade reason. Never present that preview as final, ready, accepted, or verified.

For final video:

- stream-copy the original video;
- place remixed audio first/default;
- preserve original audio afterward when possible;
- verify video properties, stream order, duration, and default flags;
- preserve proof and cleanup summaries.

## Final Report

Use `templates/REMIX-VOICEOVER.md`. Keep the report short and evidence-bound.

If the file is only ready for the caller to test, call it that. Do not describe it as done.
