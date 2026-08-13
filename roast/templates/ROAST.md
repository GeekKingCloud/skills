# Roast Report

Target: [path or project name]
Target type: [software, document, contract, policy, design, image, plan, workflow, or other]
Purpose / success criteria: [what the target is meant to accomplish]
Current milestone / delivery state: [what becomes true now, current users or exposure, and what remains future]
Recoverability: [how safely and cheaply the current state can be undone or corrected]
Context: [user-supplied framing, if any]
Scope: [what was inspected and what was skipped]
Review lenses: [caller-specified and context-appropriate lenses]
Evidence mode: [source, rendered/live behavior, artifact, references, or combination]
Evidence limits: [relevant material that was unavailable or not assessed]

## Findings

### Critical
- `[location or reference]` Finding title
  Severity: Critical
  Problem: [confirmed issue]
  Evidence: [path, line, section, clause, page, frame, region, state, timestamp, pattern, or observed behavior]
  Impact: [harm, exploit, failure mode, usability cost, or maintenance cost]
  Current applicability: [direct / conditional / later milestone / evidence-only / review-process-only / out of scope]
  Simplest fix direction: [fix, remove, simplify, narrow claim, use manual recovery, or defer]
  Suggested disposition: [block now / fix if proportionate / defer to named milestone / candidate for owner acceptance / evidence correction / process invalidated / out of scope]

### High
- `[location or reference]` Finding title
  Severity: High
  Problem: [confirmed issue]
  Evidence: [precise artifact reference or observed behavior]
  Impact: [harm, exploit, failure mode, usability cost, or maintenance cost]
  Current applicability: [direct / conditional / later milestone / evidence-only / review-process-only / out of scope]
  Simplest fix direction: [fix, remove, simplify, narrow claim, use manual recovery, or defer]
  Suggested disposition: [block now / fix if proportionate / defer to named milestone / candidate for owner acceptance / evidence correction / process invalidated / out of scope]

### Medium
- `[location or reference]` Finding title
  Severity: Medium
  Problem: [confirmed issue]
  Evidence: [precise artifact reference or observed behavior]
  Impact: [harm, exploit, failure mode, usability cost, or maintenance cost]
  Current applicability: [direct / conditional / later milestone / evidence-only / review-process-only / out of scope]
  Simplest fix direction: [fix, remove, simplify, narrow claim, use manual recovery, or defer]
  Suggested disposition: [block now / fix if proportionate / defer to named milestone / candidate for owner acceptance / evidence correction / process invalidated / out of scope]

### Low / Nitpicks
- `[location or reference]` Finding title
  Severity: [Low or Nitpick]
  Problem: [confirmed issue]
  Evidence: [precise artifact reference or observed behavior]
  Impact: [harm, exploit, failure mode, usability cost, or maintenance cost]
  Current applicability: [direct / conditional / later milestone / evidence-only / review-process-only / out of scope]
  Simplest fix direction: [fix, remove, simplify, narrow claim, use manual recovery, or defer]
  Suggested disposition: [block now / fix if proportionate / defer to named milestone / candidate for owner acceptance / evidence correction / process invalidated / out of scope]

## Deferred, Evidence, And Review-Process Observations

- `[location or reference]` Observation title
  Type: [later-milestone hardening / evidence-only / review-process-only / materially relevant out-of-scope observation]
  Evidence: [precise artifact reference or observed behavior]
  Why it remains visible: [future exposure, claim correction, rerun need, or effect on reviewed scope]
  Next milestone or action: [named later gate, evidence correction, stable-review rerun, or None]

## Lens Review

| Lens            | Status                           | Summary                             |
| --------------- | -------------------------------- | ----------------------------------- |
| [Relevant lens] | [Assessed, N/A, or Not assessed] | [Evidence-backed summary or reason] |
| [Relevant lens] | [Assessed, N/A, or Not assessed] | [Evidence-backed summary or reason] |

## Validation And Evidence
- [Checks performed, evidence limitations, confidence limits, and unreviewed surfaces]

## What To Fix First
1. [Highest-priority supported fix]

Grade: [A to F for the reviewed scope, or Not graded]
Grade basis: [why the evidence and findings earn this grade]
Grade cap: [cap reason, or None]
Confidence: [High, Medium, or Low, with reason]
Current-milestone fit assessment: [advisory: fit / blocked / fit with deferred hardening / not assessed]
Review verdict: [one concise evidence-backed verdict]
