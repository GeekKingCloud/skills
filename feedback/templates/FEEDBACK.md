# Coding-Agent Collaboration Feedback Report

## Evidence Reviewed

- Sources:
- Review type: Deep cross-session coding-agent communication review
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
  - User communication move:
  - Agent response effect:
  - Teachable rewrite:
  - Limitations:

- **E2:** [Source and scope]
  - Can prove:
  - User communication move:
  - Agent response effect:
  - Teachable rewrite:
  - Limitations:

## Learning Summary

[Two to five sentences on the biggest communication patterns, why they affect coding-agent output, and the highest-impact habits to change or preserve.]

## Generalization Boundary

[State exactly which tasks, repos, session summaries, transcripts, or artifacts this feedback can generalize across, and which it cannot.]

## Confidence Model

- Available corpus: [High / Medium / Low]
- Sample depth: [High / Medium / Low]
- Evidence fidelity: [Transcript/log / Detailed summary / Summary-derived / One-sided]
- Overall confidence:
- Pattern confidence notes:
- If confidence is below high, evidence reason: [missing transcripts / narrow corpus / summary-only evidence / one-sided evidence / inaccessible sources]

## Communication Strengths To Preserve

- **Evidence:** [E1, E2, or omit this item if no reviewed evidence supports it]
  **Observed habit:** [Concrete user communication behavior]
  **Agent response effect:** [How this improves coding-agent behavior, speed, risk control, or verification]
  **Why it works:** [The collaboration mechanism]
  **Keep doing this when:** [Task/context]
  **Example to reuse:** `[Prompt, correction, verification, or handoff pattern]`

## Communication Friction And Repair Habits

- **Evidence:** [E1, E2, or omit this item if no reviewed evidence supports it]
  **Observed pattern:** [Concrete communication pattern]
  **What tends to go wrong:** [Agent/user collaboration failure]
  **Impact:** [Rework, wrong assumptions, slowdowns, token waste, weak verification, or trust loss]
  **Repair habit:** [Specific user-side communication change]
  **Matching agent adaptation:** [What future agents should do]
  **Confidence:** [High / Medium / Low]

## Highest-Impact Collaboration Habits

[Up to three evidence-supported changes.]

1. [Habit]
   - Evidence basis: [E1, E2]
   - Current pattern:
   - Why it changes agent behavior:
   - Better pattern:
   - Example wording:
   - Use when:
   - Do not overuse when:
   - Durable encoding: [prompt habit / repo guidance / AGENTS.md-style block / skill rule / handoff pattern / project doc / not needed]
   - Expected improvement: [faster work / fewer corrections / lower token waste / stronger verification / safer autonomy]
   - Agent response rule:
   - Agent capability nuance:

## Prompting, Context, Correction, Verification, And Handoff Habits

1. [Specific communication change]
   - Evidence basis: [E1, E2]
   - Observed user-agent pattern:
   - Inferred need:
   - Replacement habit:
   - Use when:
   - Example wording:

2. [Specific communication change]
   - Evidence basis: [E1, E2]
   - Observed user-agent pattern:
   - Inferred need:
   - Replacement habit:
   - Use when:
   - Example wording:

## Future-Agent Guardrails The User Can Encode

1. [Specific rule future agents should follow]
   - Evidence basis: [E1, E2]
   - Inferred need:
   - Trigger:
   - Where the user can encode it: [prompt / repo guidance / AGENTS.md-style instruction file / skill / handoff / project doc / test]
   - Suggested durable wording:
   - Expected future-agent behavior:

2. [Specific rule future agents should follow]
   - Evidence basis: [E1, E2]
   - Inferred need:
   - Trigger:
   - Where the user can encode it: [prompt / repo guidance / AGENTS.md-style instruction file / skill / handoff / project doc / test]
   - Suggested durable wording:
   - Expected future-agent behavior:

## Repo Guidance Worth Encoding

- **Evidence:** [E1, E2, or omit if no durable repo/project rule is justified]
  **Target:** [existing repo guidance file / AGENTS.md-style instruction file / project doc / skill / no durable target visible]
  **Why this belongs outside the chat:** [Repeated pattern or future-agent risk]
  **Suggested wording:**
  ```md
  [Concrete instruction block]
  ```
  **Ask before applying:** [Yes / No, depending on user authorization and repo context]

## Reusable Prompt And Correction Patterns

Include only prompt patterns that directly answer an evidence-supported friction or strength. Do not include generic prompt advice just because it is usually useful.

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
Use the `feedback` skill for a deep cross-session communication review. If there is not enough cross-task history to produce evidence-bound communication feedback, say that and list what inputs would unlock the review.
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
If this correction is likely to recur, propose the exact repo guidance, AGENTS.md-style instruction block, skill, handoff, or project-doc wording that would prevent it next time.
```

## Recommended Durable Updates

- [Doc, skill, template, or workflow update]
  - Evidence basis:
  - Trigger:
  - Expected improvement:

## Caveats

- [What the report could not verify]
- [Where conclusions may be biased by limited evidence]
