# Audio Engineering Basis

Use this reference when choosing targets, deciding whether gain is clean, interpreting masking, or documenting a quality limitation. `scripts/rv/audio-policy.json` is the runtime authority for the house audio rails it defines. Numeric values in this reference describe external guidance unless explicitly identified otherwise.

## Dialogue anchor

- Measure representative typical dialogue. Do not use whispers, shouts, or brief expressive events as the normalization anchor. ATSC A/85 explicitly separates typical dialogue from shouting and whispering for long-form measurement.
- Preserve the relative shape of ordinary speech, whispers, shouts, and emotional peaks. AES loudness guidance favors transparent linear gain and warns that excessive peak limiting reduces clarity and can increase fatigue.
- Treat `processed_mic_active_speech_lufs.preferred` in the runtime audio policy as this workflow's commentary anchor, not a universal standard. Current primary references use different delivery targets: AES TD1008 recommends about `-18 LUFS` for speech-anchored internet audio, EBU R 128 uses `-23 LUFS` for broadcast production, and ATSC A/85 uses `-24 LKFS` when no delivery requirement is known.

Primary references:

- AES TD1008, *Recommendations for Loudness of Internet Audio Streaming and On-demand Distribution*: https://aes.org/wp-content/uploads/2024/01/20210924_TD1008_v3.13.pdf
- ATSC A/85, *Techniques for Establishing and Maintaining Audio Loudness*: https://www.atsc.org/wp-content/uploads/2025/06/A85-2013-with-Corrigendum-No-1.pdf
- EBU R 128 loudness guidance: https://tech.ebu.ch/loudness

## Gain quality

There is no universal gain value at which artifacts begin. Linear gain changes level; it does not repair or worsen source SNR by itself. Judge feasibility from the source and the complete render:

- speech-to-floor separation before and after a suspected capture step;
- whether speech and the non-speech floor moved together;
- processed noise-floor audibility at the proposed common target;
- true peak, clipping, and downstream codec headroom;
- limiter duty, duration, attenuation, and effect on speech body;
- a reviewed A/B sample when a quality limitation or unusually large lift is discussed.

Treat `clean_mic_gain_ceiling_db.default` in the runtime audio policy as an evidence threshold. Above it, require regime-specific headroom and quality evidence. Do not treat it as a physical distortion ceiling.

Classify a common-level step only from behavior. If typical speech and the floor move together while their separation stays stable, a large clean restoration may be possible. If speech falls without a matching floor change, lifting it also exposes the floor. Do not label a step "digital" or "analog" unless source metadata proves the cause.

AES TD1008 recommends partial rather than full upward normalization when the limiting required for the full target would cause unacceptable degradation. It recommends `-1 dBTP` at lossy codec input; this workflow's hard ceiling is defined by `true_peak_dbtp.max` in the runtime audio policy. ATSC's `-2 dBTP` guidance is a valid more-conservative delivery choice.

## Commentary over background

No primary standard defines one universal commentary-over-background gap. Broadband LUFS gap is an operational proxy; masking also depends on spectrum, timing, and content.

- Place the repaired commentary first.
- Choose the loudest background baseline that satisfies the workflow's sustained masking rails.
- Keep the preferred median gap as an optimization target, not proof by itself.
- Allow brief, source-natural peaks such as jump scares or emphatic game dialogue.
- Lower the background as far as needed for commentary intelligibility. A large gap is a disclosure and quality tradeoff, not automatically a promotion failure.
- Never raise or flatten quiet background moments merely to make a gap statistic look uniform.

AES TD1009 treats dialogue as the anchor and describes intelligibility as dependent on competing sound and frequency-dependent masking rather than one fixed broadband difference:

- AES TD1009, *Improving Dialogue Intelligibility in Media*: https://www.aes.org/wp-content/uploads/2025/12/5297fea6-25ba-4865-92f6-dc1d0ba52ce4.pdf

## Subjective quality boundary

Objective metrics can prove lineage, level, peaks, shape preservation, noise exposure, and the absence of known artifacts. They cannot prove that a restored noisy passage sounds good.

When subjective review is available, judge separately:

1. commentary/speech quality;
2. background/noise quality;
3. overall listener quality.

This follows the three-scale structure of ITU-T P.835. A coding agent without audio playback must not invent a listening verdict; it may produce an objectively cleared caller-test candidate and leave final listener acceptance to the caller.

- ITU-T P.835: https://www.itu.int/rec/T-REC-P.835/en
