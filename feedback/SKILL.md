---
name: feedback
description: Review available collaboration history between a user and coding agents, then produce evidence-bound feedback on communication patterns, gaps, and practical ways to work better together. Use when the user wants a retrospective on agent collaboration, prompting habits, handoff quality, failure patterns, or how to give coding agents better context without inventing unsupported history.
---

# Feedback

Review the available collaboration record and give practical, evidence-bound feedback on how the user and coding agents can work together better.

## Quick start

When asked for collaboration feedback:
1. Inventory what history and artifacts are actually available.
2. State what cannot be accessed or verified.
3. Decide whether the evidence is enough for a report before analyzing patterns.
4. Read enough evidence to identify repeated patterns, not isolated moments.
5. Separate facts, interpretations, and recommendations.
6. Give the user concrete communication improvements and matching agent-side adaptations.

If there is not enough evidence to produce reliable feedback, say so plainly and ask for better inputs. Never pretend to have read history that is unavailable.

## Evidence sources

Use only sources that are available in the current workspace or explicitly provided by the user:
- the active conversation
- user-provided transcripts, exports, notes, or examples
- handoff notes, project plans, review reports, and repo guidance files
- local session summaries, memory files, or logs only when the user has asked for history-based feedback and the source is already exposed to the session
- issue, pull request, commit, or ticket discussions only within the repo, project, account, or thread the user named or clearly authorized

Do not claim access to private chats, hidden history, inaccessible memories, or external systems. If a source would materially improve the report but is unavailable, list it under missing evidence.

Do not browse broad local histories just because they exist. If the requested scope is unclear, ask before reading sensitive or unrelated collaboration records.

When using summaries or memory files, label them as summary-derived, cite their scope or date when available, and do not infer exact wording, intent, or chronology unless the underlying transcript or log supports it.

## Collection pass

Create a compact evidence inventory before drawing conclusions.

For each source, track:
- `Evidence ID`: a short label such as `E1`, `E2`, or `Handoff A`
- `Source`: transcript, memory summary, handoff note, issue, repo doc, or active conversation
- `Scope`: repo, project, thread, or date range when known
- `What it can prove`: the type of collaboration behavior it supports
- `Limitations`: missing agent replies, summary-only evidence, unclear dates, one-sided notes, or narrow scope

Sample across different interaction types when available:
- successful sessions
- failed or corrected sessions
- scope changes or stop/audit/continue moments
- handoffs and recovery attempts
- repeated repo-guidance or verification issues

Require every claimed pattern to cite at least one evidence ID. If a pattern cannot be tied to reviewed evidence, do not include it as a finding.

## Evidence sufficiency

Before writing the main report, decide whether the evidence supports the requested depth.

Use `Enough for report` when the evidence supports multiple concrete patterns and includes enough user-agent exchange detail to distinguish user communication from agent behavior.

Use `Preliminary only` when the evidence is real but thin. Label recommendations as first-pass guidance.

Use `Not enough evidence` when there are no actual examples of user-agent collaboration, no accessible history, or only the current request is available.

Use `High confidence` when:
- multiple conversations or artifacts show the same pattern
- examples include both user requests and agent responses
- the reviewed material covers successful and difficult interactions

Use `Medium confidence` when:
- evidence is real but narrow
- patterns are plausible but mostly come from one project, one session, or one failure mode
- recommendations should be treated as first-pass guidance

Use `Low confidence` when:
- examples are anecdotal or one-sided
- the report would mostly be generic advice

Assign confidence to the overall report and to individual patterns when their evidence strength differs.

If only the current request is available and there are no examples of user-agent exchanges, do not produce collaboration pattern feedback. Say: `I do not have enough collaboration history to give evidence-bound feedback. I can give a generic collaboration checklist, or you can provide transcripts, summaries, project handoffs, or examples.`

If confidence is low but evidence exists, keep the report short, label it as preliminary, and tell the user what evidence would make it useful.

## Review focus

Look for patterns in both sides of the collaboration.

User-side patterns:
- how goals, scope, and boundaries are stated
- whether success criteria and verification expectations are clear
- how corrections, interruptions, and priority changes are communicated
- what context is usually missing when work goes wrong
- which prompt shapes produce the best agent behavior

Agent-side patterns:
- where agents over-assume, over-broaden, or stop too early
- where agents fail to read repo guidance or available artifacts
- whether agents report uncertainty honestly
- whether agents verify outcomes against the user's actual goal
- which durable instructions should be written into repo docs or reusable skills

Treat feedback as a collaboration audit, not a user-blame exercise.

## Output guidance

Use the report template in `templates/REPORT.md` when the user wants a full report or when the evidence is substantial.

If the evidence sufficiency decision is `Not enough evidence`, stop after the insufficiency response. Do not fill a full report with generic coaching.

For smaller requests, answer with:
- evidence reviewed
- confidence
- strongest patterns
- highest-impact user improvements
- highest-impact agent adaptations
- missing evidence, if any

Make recommendations concrete. Prefer examples such as:
- `Say the target repo and the exact boundary up front.`
- `Name the success check before implementation starts.`
- `When correcting an agent, state whether to stop, audit, or continue.`
- `Ask the agent to write durable repo guidance when the same correction repeats.`

Avoid vague advice such as `be more clear` unless it is paired with a specific replacement behavior.

## Quality bar

- Never lie about available history.
- Never turn generic collaboration advice into claimed history.
- Do not overfit to one frustrated exchange.
- Do not expose sensitive transcript details unnecessarily.
- Paraphrase by default; quote only when exact wording is the evidence.
- Redact private paths, names, tokens, and unrelated details when they are not needed.
- Quote sparingly; summarize patterns unless exact wording matters.
- Separate `Observed`, `Inferred`, and `Recommended`.
- Tie each claimed pattern to evidence.
- Include agent-side fixes as well as user-side suggestions.
- Mark confidence and missing evidence clearly.
- Prefer changes that reduce future coordination cost, such as prompt templates, repo guidance updates, or handoff rules.
