---
name: remix-voiceover
description: Recover OBS-style voiceover recordings with separate mic and game/system tracks. Use when the goal is a listenable mic-over-game output, copied video, same-folder REMIX-VOICEOVER file, and clean temporary scratch handling without heavyweight proof bureaucracy.
---

# Remix Voiceover

Use this for OBS-style recordings with separate mic and game/system audio where the default audio should become a clear, pleasant mic-over-game mix. The goal is not to pass a checker. The goal is a video a viewer can listen to without straining, riding volume, or losing either the voice or the game.

## Permissions

- Before track-role decisions or candidate rendering, ask: "Approve reviewer-backed mode for this remix? If approved, I will use subagents/reviewers to challenge track roles, acceptance windows, mix choices, and final sanity. If not approved or unavailable, I will continue locally and report that no reviewers were used."
- Do not treat the skill text itself as reviewer approval. Do not proceed past source/stream inspection until the reviewer decision is explicit. If reviewer-backed mode is not approved, continue local-only and say so.
- If the final output path is outside the writable workspace, create and verify scratch candidates first when practical, then ask for exact approval to write `<source-stem>-REMIX-VOICEOVER<suffix>` beside the source. Scratch analysis does not replace final-path approval.

## Non-Negotiables

- Output beside the source as `<source-stem>-REMIX-VOICEOVER<suffix>`.
- Copy video unchanged with stream copy: no resize, re-encode, transcode, fps change, pixel-format change, or video compression.
- Make the remix the first/default audio track.
- Preserve useful original audio tracks after the remix, with originals non-default.
- Use scratch/temp for work files. Delete bulky scratch media before finishing; keep only small text notes/proof.
- Build candidates from the source file for this run. Do not reuse, promote, or tune from an older candidate unless the caller explicitly asks for reuse.

## Track Roles

First convert every audio stream into full-file timeline datapoints. Record stream IDs as both `0:a:N` and `Stream #0:N`.

Use the datapoints to classify:

- `mic`: sparse speech, natural silence between speech, usually not continuous music/game.
- `game/system`: continuous or near-continuous gameplay/system audio.
- `existing mix`: continuous audio that resembles a combined mic+game track.

For generic OBS labels, prefer the common pattern that Track1 may be an existing mix and later tracks may be mic/game, but prove it from datapoints. If a separate mic/game pair exists, mix from those separate tracks, not from an existing combined mix. If roles remain ambiguous, stop before final output.

## Balance Model

Treat the mix as two bounded lanes:

- Set a usable active-speech lane first, then place game below it.
- Account for long-form mic gain drift before gap balancing. If intro or late speech is healthy but the middle is much quieter, that usually means the capture level changed. The mix should keep sustained conversation in a consistent listener lane without flattening whispers, yells, or short expressive changes.
- During recoverable speech-over-game, target a mic-over-game median near `+8.5 dB`.
- Do not use mean alone. A few easy windows must not hide buried speech.
- Important recoverable overlap windows should usually stay at or above about `+6.5 dB`.
- Gap alone is not enough: active speech needs usable absolute loudness before game balance is judged. Use level checks as sanity checks, not hard gates. Speech in the high `-20s dBFS` is often usable; speech around `-37 dBFS` is probably too quiet even if the gap passes.
- During speech, game should sit under the mic while staying audible and natural. Do not make the game bed the reference if that leaves speech too quiet.
- Low mic level alone is recoverable. Mark speech source-limited only when the raw mic is absent, clipped beyond repair, indistinguishable from noise, or not actually speech.

The mic may rise and fall naturally, and silence should remain silent. Do not gate/chop syllables, lift silent mic noise into a floor, or make the mic abruptly drop after an intro. If the mic sounds harsh, strained, distorted, or over-gained, lower the game ceiling instead of pushing mic gain harder.

The game should stay present. Ducking is allowed only as shallow, smooth help; it must not turn the game mute-like during speech or let game-only sections blast back in with sudden jumps.

## Pitfalls To Account For

- A hot intro, quiet middle, and hot late section is a failed listener experience even if selected broad-section medians look acceptable.
- Fixed speech thresholds can hide weak recoverable speech. Detect active speech relative to the local mic section, and include weak/low-tail speech instead of only loud active seconds.
- Narrow proof windows can pass while adjacent speech fails. Check around caller-reported transitions and the low-tail of recoverable speech: p10/p25 gap and loudness, seconds where game still beats mic, and seconds where speech cuts in or out.
- Gate-like or cliff-shaped compand/expander curves can make weak speech pop in and out. Be especially careful with pre-gain gates on known weak mic material; use denoise/gating only after proving it does not reduce recoverable speech in the weakest windows.

## Acceptance Windows

Choose windows from the raw source before processing, then keep those same windows through candidate checks. Do not choose important windows from processed output thresholds like "mic is already loud"; that hides the failures this skill exists to fix.

Within each window, measure the active speech portions. Silence, pauses, intro-only speech, or game-only spans must not improve the mic-over-game score.

Include at least:

- start and early gameplay
- post-intro transition after the first 30-90 seconds, especially where capture levels change after an initially good mic
- rolling windows around any caller-reported drop, such as `00:44`, and any later level return, such as `36:31`
- caller-disputed timestamps
- weakest recoverable speech under game
- loud game under speech
- middle and late gameplay
- broad active-speech section checks across the file, including before and after any sustained mic-level return
- game-only and silence/noise sections
- one random speech-over-game overlap

For each recoverable overlap window, ask: would a viewer understand the voice here without turning volume up? If no, revise the mix. A candidate can have source-limited weak spots, but do not redefine buried recoverable speech as source-limited just to finish.

## Build And Verify

- Build a full-file mix from the chosen mic and game tracks. Do not rely on isolated snippets for stateful filters or sidechain behavior.
- Prefer bounded game-level control and smooth automation over aggressive mic gain, deep sidechain compression, or many hard cuts.
- Verify the encoded candidate audio, not only pre-encode stems. Leave headroom and avoid clipping/overs.
- Check the fixed acceptance windows for mic gap, active speech loudness, game presence, abrupt jumps, chopped speech, and mute-like ducking.
- Check broad processed active-speech medians and low-tail values by section: intro, post-intro, middle, late, and any caller-disputed transition. Overall `mean_volume`, max peak, headroom, or a few selected proof windows are not proof that the voice stays usable through the file.
- Confirm the final file still has copied video, default remix audio first, and preserved original tracks after it.

Do not promote the final output yet when the track map is unproven, copied video would be lost, active recoverable speech is still too quiet, the mic drops/chops abruptly, the processed mic lane has sustained section-to-section volume swings that would make the viewer change playback volume, game disappears under normal speech, or the result passes numbers but is still likely bad to listen to. Revise the scratch candidate until those are cleared, then render or promote the final output.

Candidate loops should diagnose, not brute-force. After two candidates fail the same axis, change the strategy or get reviewer help instead of only nudging numbers. Do not run more than about five candidate renders unless the caller or reviewers explicitly choose to continue; report the best candidate and the remaining blocker instead.

Final report: source path, output path, track map, short mix strategy, candidate count, broad section speech-lane medians, worst checked windows, weakest remaining source-limited spots, video-copy status, scratch cleanup status, whether reviewers were used, and whether any human listening happened. Do not claim listener validation if nobody listened.
