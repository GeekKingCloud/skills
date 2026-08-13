---
name: recollect
description: Reconstruct creator thoughts from recorded gameplay.
---

# Recollect

Use this skill when a creator wants to remember what they said, noticed, liked, disliked, expected, or changed their mind about while playing a game demo or similarly bounded preview build. The deliverable is source-grounded working notes for the creator—not review copy, a publishable preview, marketing prose, or an independent judgment of the game.

The workflow has two reusable stages:

1. **Transcribe:** acquire or accept the media, then produce a timestamped transcript with uncertainty preserved.
2. **Reconstruct:** turn that transcript into creator-memory notes, audit them against the transcript, and refine the notes without retranscribing.

Run transcription-only from source media or captions. Run notes-only from a usable timestamped transcript; media is optional and improves verification but is not required.

## Modes

Choose the modes before acting:

- **Input mode:** public media URL, local media, or supplied transcript.
- **Evidence mode:** transcript only or transcript plus media spot-checks. Do not imply audio or visual verification in transcript-only mode.
- **Action mode:** transcribe only, notes only, or both stages.
- **Recollection depth:** quick recall or full recollection.
- **Delivery mode:** inline notes, saved transcript and notes, or both.

### Ask for recollection depth at intake

Unless the caller already selected a mode, ask one short outcome-based question before transcription or reconstruction:

- **Quick recall:** a compact briefing with roughly 12–20 core notes, optimized for fast memory reset and editorial triage.
- **Full recollection:** richer working notes with specific moments, systems, comparisons, tensions, and a useful timestamp index, optimized for preparing to write later.

Do not ask for an abstract numeric verbosity score. If the caller says only “use Recollect,” default to **full recollection** for creator-preview or article preparation and **quick recall** when they explicitly request concise, condensed, direct, brief, or triage-oriented output. State the selected mode in the artifact header.

The depth choice changes only Stage 2. A usable transcript is reusable: switching modes must regenerate notes from the same transcript rather than retranscribing or returning an artifact produced under the previous mode. Give the new artifact a mode-specific filename and provenance line so stale output cannot be mistaken for a rerun.

Ask other questions only when the source, creator voice, requested stage, or privacy boundary cannot be inferred safely. A public video supplied for analysis authorizes retrieval for this task, not account-cookie export, publication, or unrelated channel access.

## Non-Negotiable Boundary

Recover the creator's perspective; do not replace it.

- Do not write the preview, review, verdict, headline, introduction, conclusion, recommendation, score, or publishable pull quote in this workflow. If the caller later asks for prose, finish and deliver the notes first; treat writing as a separate task with separate instructions.
- Do not improve the creator's opinions into stronger claims.
- Do not convert uncertainty, jokes, questions, predictions, or first impressions into settled fact.
- Do not attribute game dialogue, narration, chat, subtitles, or another speaker to the creator.
- Do not supplement the creator's account with outside reviews or promotional claims. External metadata may verify names and spellings, never manufacture an opinion.
- Keep the raw transcript and downloaded media private. Deliver or publish them only when the caller explicitly requests it and is authorized to distribute the material.

## Stage 1: Transcribe

Skip this stage when a usable timestamped transcript is supplied. Record that the transcript is caller-supplied and preserve its original wording.

### 1. Confirm the source

Record the title, creator/channel when applicable, source URL or local path, duration, language, and whether captions exist. Verify likely speech-recognition ambiguities in names before selecting the source.

**Done when:** one exact source is identified and its duration/language are plausible.

### 2. Acquire the least media needed

Use this fallback order:

1. Platform-provided human transcript or captions.
2. Platform-provided automatic captions, labelled as automatic.
3. Creator-supplied transcript or original media.
4. Public audio-only retrieval from the supplied media URL.
5. Local audio extraction from an authorized local video.

If ordinary public retrieval is blocked, try another documented public player/client route only when it does not require bypassing access controls. Do not export browser cookies, defeat a CAPTCHA, use private account state, or route through an unapproved proxy merely to avoid asking for the source. If no clean route exists, ask the caller for the original upload or audio.

Prefer audio-only retrieval. Preserve the source untouched, work in private scratch, record duration and a checksum, and verify the decoded audio before transcription.

**Done when:** a caption source or playable audio artifact covers the complete source duration.

### 3. Produce a timestamped transcript

Use an accurate local speech recognizer when captions are absent or poor. Prefer segment timestamps; word timestamps are useful for targeted repair but are not required in the final readable transcript. Supply the expected language rather than relying on auto-detection when known.

Distinguish speakers conservatively:

- label creator speech only when the voice is reasonably identifiable;
- mark clear game dialogue, narration, or other speakers separately when useful;
- otherwise use neutral labels such as `Uncertain speaker` rather than guessing.

Preserve disfluencies only when they change meaning or reveal hesitation. Remove repeated filler for readability, but never rewrite an opinion. Mark uncertain words, names, and inaudible spans explicitly.

When saving the transcript, use a portable artifact such as `transcript.md`:

- provenance header: source, duration, language, transcript method, and evidence limits;
- one segment per line as `[HH:MM:SS–HH:MM:SS] Speaker: text`;
- neutral speaker labels when identity is uncertain;
- inline uncertainty markers such as `[unclear]` or `[likely: name]`;
- a short uncertainty ledger for passages that could change the notes.

**Done when:** the transcript covers the full source and timestamps increase monotonically. When audio is available, spot-check obvious names and high-impact uncertain passages; otherwise record the transcript-only limitation.

### 4. Validate transcription quality

Check at minimum:

- opening, middle, and closing speech;
- every passage later used for strong praise, criticism, comparison, or final sentiment;
- names, mechanics, genres, other games, developers, platforms, and numbers;
- scores, ratings, recommendation language, and any movement within a rating band;
- suspicious repetitions, hallucinated silence, missing long spans, and speaker confusion.

Do not silently normalize an uncertain proper noun from context. Record the machine wording and likely correction. Verify it against audio before using the correction without qualification when audio is available; otherwise retain the uncertainty label. For an unclear spoken score, keep the machine wording, contextual best reading, and confidence/audio-check status. Preserve deliberation such as `high four` becoming `four`; the movement is often more useful than the number alone.

When audio and game sound overlap, lower confidence rather than silently repairing from context. Keep a short uncertainty ledger for passages that could materially change the notes.

**Done when:** material claims can be traced to intelligible transcript evidence, and unresolved uncertainty is visible.

## Stage 2: Reconstruct Creator-Memory Notes

This stage must work from any timestamped transcript, including one produced in an earlier run. Use `templates/RECOLLECT.md` to select the depth-specific output template.

### 1. Read for chronology before themes

Read the entire transcript once in time order. Build a compact reaction timeline before grouping anything. Capture:

- opening expectations, prior knowledge, and stated context;
- first reactions to presentation, controls, mechanics, story, or tone;
- discoveries and misunderstandings;
- moments of delight, surprise, frustration, confusion, boredom, or relief;
- predictions, comparisons, and questions;
- corrections or changes of mind;
- closing sentiment and appetite for the full game.

Do not judge importance from emotional wording alone. Repeated mild friction may matter more than one dramatic joke.

**Done when:** the notes can show how the creator's view developed rather than only what topics appeared.

### 2. Separate evidence classes

Classify each candidate note:

- **Direct reaction:** the creator explicitly states an opinion or feeling.
- **Observed experience:** the creator describes what happened during play.
- **Interpretation:** a cautious synthesis supported by multiple passages.
- **Open question:** uncertainty the creator raises or leaves unresolved.
- **Changed view:** an initial reaction followed by a correction, learned response, or revised rating.
- **Visual/context note:** observable only from media inspection, never transcript-only evidence.

Use first-person wording only for faithful paraphrases of direct creator speech. Mark interpretation as interpretation. Never present silence or lack of comment as an opinion.

### 3. Preserve opinion-bearing detail

Favor notes that help the creator recover their own mental state:

- what specifically triggered the reaction;
- whether it was immediate, repeated, or revised;
- the creator's own comparison or analogy;
- concrete examples from play;
- tension between two reactions;
- what remained unresolved because it was only a demo.

Compress procedural gameplay that carries no reaction. Retain mechanical description when it explains praise, concern, confusion, pacing, or expected audience fit.

### 4. Build notes at the selected depth

Use `templates/RECOLLECT-QUICK.md` for quick recall and `templates/RECOLLECT-FULL.md` for full recollection. Both modes preserve fidelity, chronology, changed views, timestamps, and uncertainty; depth changes coverage and retrieval detail, not evidentiary standards.

#### Quick recall

Target roughly 12–20 substantive bullets. Keep one thought per bullet, usually one sentence, with a timestamp or compact timestamp range. Optimize for learning the creator’s overall view in a few minutes.

Produce, in this order:

1. **Quick memory reset:** four to six bullets capturing the overall arc without inventing a verdict.
2. **Expectation-to-end arc:** two to four chronological bullets when change over time adds value.
3. **What landed.**
4. **Reservations and friction.**
5. **What changed during play.**
6. **Comparisons and audience signals.**
7. **Questions and uncertainties.**

Merge related examples into the strongest representative point. Include **Specific systems and moments** only when omission would distort the creator’s view. Do not add a timestamp index unless the caller requests it.

#### Full recollection

Target roughly 30–60 substantive bullets as useful—not a quota. Optimize for restoring enough texture that the creator can prepare an article later without repeatedly reopening the transcript.

Use the same core sections as quick recall, then add non-duplicative detail where supported:

- specific systems and moments that triggered reactions;
- secondary praise, friction, comparisons, jokes, and unresolved questions that may matter during writing;
- encounter-level detail when individual attempts changed the creator’s understanding;
- a compact **Useful timestamp index** for the strongest writing or review windows;
- a separate transcript-uncertainty ledger when several material passages need qualification.

Full does not mean exhaustive chronology. Compress neutral traversal, repeated exclamations, incidental off-topic speech, and attempts that did not alter the opinion arc.

#### Rules shared by both depths

Omit unsupported sections rather than filling them with generic game-analysis boilerplate. Give each detailed point one canonical home. Elsewhere, omit it or add only a genuinely different function. The quick reset states the takeaway; later sections hold evidence and detail. Preserve a few useful verified quotes, but neither mode should make the creator reread the transcript in outline form.

### 5. Run the fidelity audit

Re-read the transcript against the draft notes. For every substantive bullet, ask:

- Is the timestamp relevant and accurate?
- Is this the creator's view, an observed event, or my inference?
- Did the wording preserve strength and uncertainty?
- Did a later correction supersede it?
- Did I confuse game dialogue with creator commentary?
- Is this useful for remembering the experience, or merely a plot/gameplay recap?

Then run four coverage passes:

- **Beginning:** expectations and initial read.
- **Middle:** repeated systems, friction, and developing comparisons.
- **End:** closing view, appetite, caveats, and unresolved questions.
- **Minority report:** tensions or counterexamples that complicate the dominant impression.

Finish with a mode-aware density pass. In quick recall, merge or remove every nonessential detail beyond about 20 substantive bullets. In full recollection, retain secondary details that could genuinely help later writing, while removing repeated evidence and neutral chronology; bullets beyond about 60 should be exceptional. Compress long encounter chronology to the creator's opinion arc—initial read, material correction, residual concern, and end-state judgment—unless individual attempts each changed the conclusion.

Revise the notes, not the transcript. Stop after the audit resolves concrete omissions or distortions; do not keep generating stylistic variants once the selected mode is faithful and useful. Verify that the artifact header names the selected mode and that a mode switch produced a newly generated, mode-specific artifact rather than returning an older file.

**Done when:** every substantive note is traceable, the opening-to-closing arc is represented, superseded impressions are labelled, and no section reads like ghostwritten preview prose.

## Output Rules

- Name the selected depth in the header: **Quick recall** or **Full recollection**.
- Use mode-specific filenames such as `notes-quick.md` and `notes-full.md`; never overwrite or relabel an older mode’s artifact as a fresh run.
- Use concise working-note language, not polished article paragraphs. Full recollection adds coverage and retrieval detail, not ornamental prose.
- Include timestamps for substantive reactions and examples. A timestamp range is better than a falsely precise instant.
- Quote sparingly; use exact quotes only when phrasing itself is useful and verified.
- Separate creator statements from cautious synthesis.
- Preserve conflicting reactions instead of forcing a verdict.
- State the evidence mode and transcription limitations at the top.
- If the source is too thin to support preview notes, say so and provide only what the transcript supports.

## Common Failure Modes

1. **Generic summary:** recaps the game but loses the creator. Fix by removing facts that do not explain a reaction.
2. **Opinion laundering:** turns tentative speech into a confident judgment. Restore modality such as `seemed`, `might`, `at this point`, or `I wasn't sure`.
3. **End-state flattening:** reports only the final reaction. Restore early expectations and the moments that changed them.
4. **Chronology dump:** lists every event. Group only after preserving the opinion arc.
5. **Timestamp decoration:** attaches a nearby timestamp that does not prove the bullet. Re-open the passage and correct or remove it.
6. **Speaker leakage:** attributes dialogue or narration to the creator. Relabel or drop uncertain material.
7. **Ghostwriting:** produces polished preview copy. Return to terse evidence-backed notes and questions.
8. **Tool overcommitment:** treats one downloader or recognizer as mandatory. Follow the acquisition ladder and report the actual route used.
9. **Evidence repetition:** repeats the same encounter or opinion across most sections. Keep one detailed account and make every other mention earn its place.
10. **Silent depth assumption:** produces a quick or full artifact without selecting the user-facing outcome. Ask once when not inferable; use the documented default when it is.
11. **Stale-mode delivery:** claims to test a revised mode but returns notes produced before the revision. Reconstruct from the reusable transcript, write a new mode-specific artifact, and identify its provenance in the header.
12. **False full mode:** treats “full” as permission for transcript-shaped chronology. Retain memory-bearing texture, not every event or utterance.

## Completion Checklist

- [ ] Recollection depth was selected explicitly or inferred from the documented default and recorded in the artifact
- [ ] Exact source, duration, language, and transcript provenance recorded
- [ ] Complete timestamped transcript available or supplied
- [ ] Material names and high-impact passages spot-checked when media is available; otherwise limitations are explicit
- [ ] Creator speech distinguished from other audio where possible
- [ ] Notes preserve expectations, evolution, tensions, and closing sentiment
- [ ] Praise, friction, comparisons, and questions are source-grounded
- [ ] Superseded impressions are labelled rather than silently merged
- [ ] Ratings and material proper nouns are audio-checked when available, or remain explicitly uncertain
- [ ] Detailed points have one canonical home and repeated encounter chronology is compressed
- [ ] Every substantive note has a relevant timestamp or explicit evidence limit
- [ ] Unsupported template sections are omitted
- [ ] Output depth matches the selected mode without weakening fidelity
- [ ] A mode switch reused the transcript but generated a new mode-specific notes artifact
- [ ] Output is working notes, not preview copy
- [ ] Raw media and transcript remain private unless authorized distribution was explicitly requested
