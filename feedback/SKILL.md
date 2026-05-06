---
name: feedback
description: Run a deep review of available collaboration history between a user and coding agents, then produce evidence-bound feedback on communication patterns, gaps, and practical ways to get better results from agents. Use when the user wants a retrospective on agent collaboration, prompting habits, handoff quality, failure patterns, or how to give coding agents better context without inventing unsupported history.
---

# Feedback

Run a deep review of the available collaboration record across tasks, projects, and sessions, then give practical, evidence-bound feedback on how the user can get better results from coding agents. The primary goal is to help the user learn how to communicate more effectively with coding agents in general, including new agent versions whose needs and failure modes may differ.

Full-depth review is the only normal route, not an optional premium route. Do not give a quick, lightweight, or medium-depth collaboration report. If the user explicitly scopes the request to a narrow artifact such as the current conversation, one transcript, one PR, or one repo, do a full-depth review of that narrower scope. If broad history is available, inspect it deeply enough to support the requested generalization. Do not lower confidence because the workflow chose not to dig; keep working, or say the run is incomplete and do not present it as the finished feedback report.

## Quick start

When asked for collaboration feedback:
1. Treat the request as a cross-session history review unless the user explicitly asks for feedback on the current conversation only.
2. Inventory what history and artifacts are actually available.
3. Build a full-depth sampling plan across repos, task types, successful sessions, corrected sessions, handoffs, and underlying transcripts/logs where available.
4. Inspect enough history to support high-quality feedback, not merely a plausible report. When transcript/log paths are available and accessible, use them for any finding that depends on exact wording, chronology, or agent/user behavior.
5. State what cannot be accessed or verified.
6. Decide whether the evidence is enough to generalize before analyzing patterns.
7. Read enough evidence to identify repeated patterns, not isolated moments.
8. Separate corpus coverage, sample depth, evidence fidelity, and confidence.
9. Separate facts, interpretations, and recommendations.
10. Give the user concrete communication improvements and agent-side rules to encode in prompts, skills, repo guidance, or handoffs.

If there is not enough evidence to produce reliable feedback, say so plainly and ask for better inputs. Never pretend to have read history that is unavailable. If there is enough available history but the current run has not inspected it deeply, continue the inspection instead of producing a lower-confidence finished report. If time, permission, context, or tool limits prevent full inspection, say the run is incomplete and list the blocker; do not treat insufficient digging as a valid confidence reason.

Do not let a single active conversation drive the report unless the user explicitly scoped the request that way. A current-thread-only report is usually not useful for this skill's main purpose.

## Full-depth run standard

For general feedback, inspect enough independent history to make the report genuinely useful:
- at least 8 to 12 independent task histories, summaries, transcripts, handoffs, ticket threads, or equivalent artifacts when available
- at least 4 different repos, projects, or work domains when available
- at least 2 successful sessions and 2 failed, corrected, interrupted, or recovery sessions when available
- at least one example each of terse prompting, detailed prompting, correction/redirect, and verification or handoff work when available
- underlying session logs or transcripts for any pattern that depends on exact wording, tone, chronology, or model/version nuance

If the available corpus is smaller than this, inspect all relevant accessible history and state the corpus limit. If the corpus is large but the run does not meet this standard, continue reviewing until it does. If continuing is blocked by missing access, context limits, unavailable transcripts, or tool constraints, label the output `Incomplete run` and stop with missing evidence and next steps instead of presenting a finished report.

## Evidence sources

Use only sources that are available in the current workspace or explicitly provided by the user:
- the active conversation
- user-provided transcripts, exports, notes, or examples
- handoff notes, project plans, review reports, and repo guidance files
- local session summaries, memory files, or logs only when the user has asked for history-based feedback and the source is already exposed to the session
- issue, pull request, commit, or ticket discussions only within the repo, project, account, or thread the user named or clearly authorized

Prefer sources that expose multiple user-agent exchanges across time. Use the active conversation mainly for immediate corrections, calibration, and examples of the current agent's behavior.

Do not claim access to private chats, hidden history, inaccessible memories, or external systems. If a source would materially improve the report but is unavailable, list it under missing evidence.

Do not browse broad local histories just because they exist. For a general collaboration-feedback request, first look for exposed indexes, summaries, handoffs, repo guidance, or user-provided history that clearly relate to prior coding-agent work. If the available index points to relevant session summaries or transcript paths, follow those references deeply enough to meet the full-depth run standard. If the scope is unclear or would require reading sensitive or unrelated records, ask before expanding.

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
- terse prompts, detailed prompts, and corrective follow-ups
- different agent versions or tool environments when the source makes that distinction visible

Require every claimed pattern to cite at least one evidence ID. If a pattern cannot be tied to reviewed evidence, do not include it as a finding.

For a general user-improvement report, the full-depth run standard is required. If fewer than three independent evidence sources or fewer than two different tasks are available, the output must either be narrowly scoped to that task or decline to generalize.

## Evidence sufficiency

Before writing the main report, decide whether the evidence itself supports the requested generalization. Run depth is not a legitimate reason to lower confidence in a finished report; it is a reason to keep reviewing or to stop with `Incomplete run`.

Use `Enough for report` when the evidence supports multiple concrete patterns across tasks and includes enough user-agent exchange detail to distinguish user communication from agent behavior.

Use `Preliminary due to evidence fidelity` when the run covers enough tasks but relies mostly on summaries rather than transcripts or logs. Broad recurring workflow patterns may still be credible; exact tone, chronology, or model/version nuance should remain bounded.

Use `Preliminary only` when the available evidence itself is real but thin, yet still covers more than the active conversation. Label recommendations as first-pass guidance and avoid broad claims about the user's general communication style.

Use `Not enough evidence` when there are no actual examples of user-agent collaboration, no accessible history, only the current request is available, or the reviewed material is too narrow to support the user's requested generalization.

Use `Incomplete run` when enough evidence likely exists but the workflow could not access or inspect it completely because of permissions, context limits, unavailable transcript paths, tool failures, or an explicit stop. This is not a finished feedback report. Include what was reviewed, what remains, and what access or time is needed to complete the full-depth review.

Use `High confidence` when:
- multiple conversations or artifacts show the same pattern
- examples include both user requests and agent responses
- the reviewed material covers successful and difficult interactions
- the reviewed material spans different tasks, repos, or agent/tool contexts

Use `Medium confidence` when:
- available evidence is real but the corpus itself is narrow because transcripts, tasks, repos, or difficult-session examples are missing or inaccessible
- patterns are plausible but the accessible evidence mostly comes from one project, one session, one tool context, or one failure mode
- recommendations should be treated as first-pass guidance because the evidence corpus is limited, not because the workflow chose a light scan

Use `Low confidence` when:
- examples are anecdotal or one-sided
- the report would mostly be generic advice
- the report relies mainly on the active conversation

Assign confidence to the overall report and to individual patterns when their evidence strength differs.

Do not collapse all evidence quality into one label. Report at least:
- `Available corpus`: high, medium, or low
- `Sample depth`: high, medium, or low
- `Evidence fidelity`: transcript/log, detailed summary, summary-derived, or one-sided
- `Pattern confidence`: high, medium, or low for each major finding

If only the current request or active conversation is available, do not produce general collaboration pattern feedback. Say: `I do not have enough cross-task collaboration history to give evidence-bound feedback. I can give a generic collaboration checklist, or you can provide transcripts, summaries, project handoffs, or examples from several tasks.`

If confidence is below high, the reason must be missing, inaccessible, narrow, summary-only, or one-sided evidence. Do not cite insufficient run depth as the reason for medium or low confidence in a completed report.

## Review focus

Look for patterns in both sides of the collaboration.

User-side patterns:
- how goals, scope, and boundaries are stated
- whether success criteria and verification expectations are clear
- how corrections, interruptions, and priority changes are communicated
- what context is usually missing when work goes wrong
- which prompt shapes produce the best agent behavior
- which prompt shapes help agents discover their own needed context quickly
- which details should be provided up front versus delegated to the agent to inspect
- how communication should vary for newer coding agents, less capable coding agents, stronger coding agents, and tool-limited environments

Agent-side rules to encode:
- where agents over-assume, over-broaden, or stop too early
- where agents fail to read repo guidance or available artifacts
- whether agents report uncertainty honestly
- whether agents verify outcomes against the user's actual goal
- which durable instructions should be written into repo docs or reusable skills
- where agents should ask for history, scope, examples, or success criteria before giving feedback
- what the current agent can infer about its own context needs and limits

Treat feedback as a collaboration audit, not a user-blame exercise. Sections about agent behavior should be framed as future-agent expectations only when they include a place the user can encode or trigger them, such as a prompt pattern, repo guidance, skill wording, handoff note, or project doc. Do not imply the user directly controls future agents at runtime.

## Output guidance

Use the report template in `templates/FEEDBACK.md` when the user wants a full report or when the evidence is substantial.

If the evidence sufficiency decision is `Not enough evidence`, stop after the insufficiency response. Do not fill a full report with generic coaching.

For narrowly scoped requests, still do a full-depth review of the requested scope and answer with:
- evidence reviewed
- confidence
- strongest patterns
- highest-impact user improvements
- agent-side rules to encode
- missing evidence, if any

For general improvement requests, include advice that is portable across coding-agent versions. Call out where the advice is capability-sensitive, such as giving more explicit boundaries to less capable agents or delegating more discovery to stronger agents that can inspect repositories and history safely.

Make recommendations concrete. Prefer examples such as:
- `Say the target repo and the exact boundary up front.`
- `Name the success check before implementation starts.`
- `When correcting an agent, state whether to stop, audit, or continue.`
- `Ask the agent to write durable repo guidance when the same correction repeats.`
- `Tell the agent what history it may inspect before asking for a communication retrospective.`
- `Ask the agent to state what context it needs before it gives broad collaboration advice.`

Avoid vague advice such as `be more clear` unless it is paired with a specific replacement behavior.

## Quality bar

- Never lie about available history.
- Never turn generic collaboration advice into claimed history.
- Do not overfit to one frustrated exchange.
- Do not turn the active conversation into a general user profile.
- Do not expose sensitive transcript details unnecessarily.
- Paraphrase by default; quote only when exact wording is the evidence.
- Redact private paths, names, tokens, and unrelated details when they are not needed.
- Quote sparingly; summarize patterns unless exact wording matters.
- Separate `Observed`, `Inferred`, and `Recommended`.
- Tie each claimed pattern to evidence.
- Include agent-side fixes as well as user-side suggestions.
- Mark confidence and missing evidence clearly.
- Prefer changes that reduce future coordination cost, such as prompt templates, repo guidance updates, or handoff rules.
