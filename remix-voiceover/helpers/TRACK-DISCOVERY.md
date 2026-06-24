# Track Discovery

Use this helper to identify source roles before mixing.

## Role Candidates

Classify each audio stream by behavior across the full source, not labels alone.

- `commentary/mic`: speech-shaped bursts, sentence gaps, breaths, pauses, changing delivery, and capture-level shifts.
- `background/system`: game, desktop, music, video, call audio, or other continuous program bed.
- `existing mix`: combined commentary plus background. Preserve it as an original stream when useful, but do not remix from it when separate lanes exist.

## Evidence To Collect

For every audio stream, collect enough evidence to compare:

- codec, channel layout, duration, title/metadata;
- full-file loudness/peak summaries;
- rolling short-window RMS/peak or equivalent;
- active/silent distribution;
- examples of mic-only or low-background commentary;
- commentary over active background;
- background-only spans;
- weak or buried commentary under background;
- hot/recovered commentary;
- section boundaries where one lane changes behavior.

Emit a stream-role evidence table:

```text
stream_id | container_stream | title | likely_role | evidence_for | evidence_against | risk | selected_for_mix
```

Include risks such as mic bleed in the background track, existing mix mistaken for background, desktop/system audio that already contains commentary, multiple mic-like tracks, or recoverable speech found outside the chosen mic lane.

Use `ffprobe`, `ffmpeg` filters such as `astats`/`volumedetect`, audio libraries, or equivalent tools. Tool choice is open; evidence shape is not.

## Decision Rules

- If a selected mic lane would omit recoverable speech found in another non-mix lane, the map is wrong.
- If a selected background lane contains substantial commentary body, prove it is not the existing mix before using it as the bed.
- If the existing mix is the only recoverable source, state that separate-lane remix is unavailable and downgrade the run.
- If stream labels conflict with measured behavior, trust measured behavior and report the mismatch.

## Anti-Loopholes

Reject a candidate before audio-quality review if:

- the render graph uses the existing mix as a remix source while separate lanes exist;
- the render log maps the wrong stream number;
- source roles are inferred from labels only;
- proof tables use container stream numbers ambiguously;
- candidate evidence cannot be tied back to selected source streams.
