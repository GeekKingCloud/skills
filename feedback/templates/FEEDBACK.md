# Agent Feedback Report

## Evidence Reviewed

- Sources:
- Review type: Deep cross-session collaboration history review
- Time or project scope:
- Task/session coverage:
- Agent or tool contexts represented:
- Available corpus:
- Sample depth:
- Evidence fidelity:
- Overall confidence:
- Privacy boundary:
- Details intentionally omitted:
- Missing evidence:

## Evidence Sufficiency Decision

- Decision: [Enough for report / Preliminary due to evidence fidelity / Preliminary only / Incomplete run / Not enough evidence]
- Reason:
- Generalization boundary:
- Better inputs needed:

## Evidence Inventory

- **E1:** [Source and scope]
  - Can prove:
  - Limitations:

- **E2:** [Source and scope]
  - Can prove:
  - Limitations:

## Executive Summary

[Two to five sentences on the biggest collaboration patterns and highest-impact changes.]

## Generalization Boundary

[State exactly which tasks, repos, session summaries, transcripts, or artifacts this agent feedback can generalize across, and which it cannot.]

## Confidence Model

- Available corpus: [High / Medium / Low]
- Sample depth: [High / Medium / Low]
- Evidence fidelity: [Transcript/log / Detailed summary / Summary-derived / One-sided]
- Overall confidence:
- Pattern confidence notes:
- If confidence is below high, evidence reason: [missing transcripts / narrow corpus / summary-only evidence / one-sided evidence / inaccessible sources]

## What Is Working

- **Evidence:** [E1, E2, or omit this item if no reviewed evidence supports it]
  **Observed:** [Concrete pattern]
  **Inferred:** [What this suggests about collaboration]
  **Why it helps:** [Effect on coding-agent work]
  **Recommended:** [Specific habit to preserve]

## Friction Patterns

- **Evidence:** [E1, E2, or omit this item if no reviewed evidence supports it]
  **Observed:** [Concrete pattern]
  **Inferred:** [Likely collaboration issue]
  **Impact:** [How it causes rework, wrong assumptions, slowdowns, or trust loss]
  **Confidence:** [High, Medium, or Low]
  **Recommended:** [User-side change and matching agent-side adaptation]

## Top Changes

[Up to three evidence-supported changes.]

1. [Specific change]
   - Evidence basis: [E1, E2]
   - Why this matters:
   - When to use it:
   - Example prompt: `[Example wording]`
   - Agent response rule:
   - Agent capability nuance:

## How The User Can Communicate Better

1. [Specific behavior change]
   - Evidence basis: [E1, E2]
   - Inferred need:
   - Recommended change:
   - Use when:
   - Example:

2. [Specific behavior change]
   - Evidence basis: [E1, E2]
   - Inferred need:
   - Recommended change:
   - Use when:
   - Example:

## Agent-Side Rules To Encode

1. [Specific rule future agents should follow]
   - Evidence basis: [E1, E2]
   - Inferred need:
   - Trigger:
   - Where the user can encode it: [prompt / AGENTS.md / skill / handoff / project doc / test]
   - Expected future-agent behavior:

2. [Specific rule future agents should follow]
   - Evidence basis: [E1, E2]
   - Inferred need:
   - Trigger:
   - Where the user can encode it: [prompt / AGENTS.md / skill / handoff / project doc / test]
   - Expected future-agent behavior:

## Better Prompt Patterns

History access for agent feedback:
```text
Use the `feedback` skill for a deep cross-task communication review. You may inspect [allowed histories, summaries, handoffs, repo docs, tickets]. Do not generalize from the current conversation alone. Separate available corpus, sample depth, evidence fidelity, and confidence per finding.
```

Repo or scope boundary:
```text
[Target repo/folder]. Stay within [boundary]. Do not widen into [excluded scope] unless you ask first.
```

Evidence sufficiency:
```text
Use the `feedback` skill for a deep cross-session collaboration review. If there is not enough cross-task history to produce evidence-bound agent feedback, say that and list what inputs would unlock the review.
```

Stop, audit, or continue correction:
```text
Stop modifying files. Switch to audit mode and report what changed, what evidence supports it, and what remains uncertain.
```

Verification expectation:
```text
Before editing, state the success check. After editing, run the narrowest meaningful verification and report exactly what passed or could not be run.
```

Durable update:
```text
If this correction is likely to recur, propose the exact AGENTS.md, skill, handoff, or project-doc wording that would prevent it next time.
```

## Recommended Durable Updates

- [Doc, skill, template, or workflow update]

## Caveats

- [What the report could not verify]
- [Where conclusions may be biased by limited evidence]
