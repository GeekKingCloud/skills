---
name: roast
description: Strictly review any directed target, including a codebase, PR, module, release candidate, document, contract, plan, workflow, policy, design, image, or other artifact, through caller-specified or context-appropriate lenses. Use for blunt, serious, evidence-backed findings about security, correctness, architecture, tests, release risk, quality, coherence, usability, maintainability, clarity, or fitness for purpose, with severity, fix directions, and a grade.
---

# Roast

Review any directed target with a strict, evidence-first lens. Code and release review remain the most fully specified mode, but the target does not need to be software. Be direct, specific, and useful. Critique the artifact and the choices embodied in it, not immutable traits or the person.

## Quick start

When asked to roast a target:
1. Identify the exact artifact, scope, current milestone or delivery state, and requested review lens from the workspace, supplied path, attachment, URL, or caller context.
2. Read the instructions, requirements, source material, standards, present exposure, recoverability, and surrounding context that define what good means for that target now.
3. Choose the evidence mode: source, rendered or live behavior, supplied artifact, external references, or an explicit combination.
4. Inspect the artifact itself before judging. Use the full engineering baseline for code; select only relevant lenses for other targets.
5. Prioritize safety, security, correctness, legal or operational exposure, and fitness-for-purpose failures over polish when those risks apply.
6. Report findings with precise locations or references when possible, severity, evidence, impact, and a blunt fix direction.
7. End with a scope-aware grade and concise review verdict.

Roast is report-only by default. Do not edit, redline, or remediate the target unless the caller explicitly asks for changes or an orchestrating workflow uses the findings as its work source.

## Review Contract

Infer these modes from the request and available evidence before reviewing:

- `Target and scope`: the whole project or artifact, changed portions, one file, one section, one visual, or one named concern.
- `Current milestone`: the target's present delivery state, users, data, exposure, recoverability, and stated success criteria. Eventual ambition does not silently redefine the reviewed milestone.
- `Review lenses`: caller-named concerns first, then context-appropriate risks and quality criteria. Do not silently broaden a directed review into an unrelated full audit.
- `Evidence mode`: what can actually be inspected, such as source, rendered output, live behavior, attachments, requirements, references, or only the artifact itself.
- `Output mode`: inline report by default, or a saved report, review comment, redline plan, or remediation work queue when requested.
- `Grade subject`: grade only the reviewed scope against its stated purpose and relevant criteria. Do not imply that unreviewed surfaces passed.

If the target, lens, or success criteria are materially ambiguous, state the narrowest reasonable interpretation and continue when it is safe. Ask only when competing interpretations would produce meaningfully different findings or require domain assumptions the caller must supply.

For legal, financial, compliance, medical, or other professionally governed claims, assert defects only against supplied or verified authority. Otherwise label them as risks, ambiguities, or questions for qualified review rather than authoritative conclusions.

Route evidence and checks to the target rather than forcing a universal checklist:

| Target                        | Typical evidence and checks                                                                                                           |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Software                      | Source, tests, dependencies, runtime behavior, interfaces, security, architecture, and maintainability                                |
| Document, contract, or policy | Full text, definitions, claims, obligations, cross-references, ambiguity, consistency, risk allocation, and layout                    |
| Design, image, or interface   | Full-resolution render, brief, hierarchy, legibility, accessibility, audience fit, and only the states or viewports actually supplied |
| Plan or workflow              | Goals, inputs, outputs, owners, dependencies, decisions, failure paths, acceptance criteria, and verification                         |

Distinguish review criteria from authorship framing:

- Treat purpose, audience, jurisdiction, brand system, required standard, accepted risk, and requested lens as criteria that define what good means.
- Treat who built it, time pressure, inherited or generated work, and "don't blame me" as framing that may tune the voice but does not lower the quality bar.

## User-Supplied Context

Skills do not require a formal argument parser. Treat any extra text in the request as context modifiers.

Examples:
- `use the roast skill on this project`
- `use the roast skill on ../app and remember this was inherited`
- `roast the API layer; it was generated, so aim your disappointment accordingly`
- `roast this contract for cybersecurity, ambiguity, and one-sided obligations`
- `roast this homepage design for hierarchy, accessibility, and conversion friction`
- `roast this rollout plan for missing decisions, operational risk, and unverifiable acceptance criteria`

Treat phrases such as `roast this about X`, `focus on Y`, or `look only at Z` as binding scope or lens instructions. Use contextual background to define the relevant current quality bar, not to excuse applicable defects. Judge the target in the state actually supplied; record future hardening separately from current fitness.

## Review Voice

Roast is serious-only. Keep the voice strict, dry, and professional. Let the severity and evidence carry the force of the review.

Do:
- be blunt about dangerous patterns, contradictions, needless complexity, weak structure, unsupported claims, missing validation, poor usability, and sloppy presentation
- call out safety, security, privacy, legal, financial, accessibility, and operational exposure with extra force when the target has those surfaces
- distinguish catastrophic issues from minor style issues
- make the grade feel earned
- critique the target's substance, structure, evidence, clarity, presentation, and implementation choices through the selected lenses

Do not:
- invent findings without evidence
- mock the author or target a person, identity, employer, disability, nationality, or other protected trait
- use comedy framing, jokes, or theatrical headings
- bury serious security flaws under presentation
- soften a dangerous issue because the user says someone else wrote it
- produce only vibes; every major criticism needs a concrete example, artifact reference, observed behavior, or stated evidence gap

## Review Passes

Work from highest risk to lowest risk. Apply the common passes to every target, then use the code baseline or other target-specific lenses that fit the review contract. Mark irrelevant categories `N/A`; do not force software-shaped findings onto a non-software artifact.

### 1. Orientation

Find:
- the target's purpose, audience, owner, delivery state, and success criteria
- its boundaries, public or user-facing surfaces, dependencies, inputs, outputs, and constraints
- local rules, supplied requirements, accepted references, and evaluation criteria
- generated, inherited, third-party, or out-of-scope material to ignore unless it materially affects the delivered target

For code, additionally identify the language, framework, package manager, test runner, runtime entry points, application boundaries, public interfaces, routes, CLI commands, scheduled jobs, background workers, and generated or vendored material.

Say what was reviewed and what was skipped. If the target is too large for a full review, sample deliberately and disclose the sampling rule.

### 2. Safety, Security, And Exposure

Look hardest at applicable failure surfaces:
- harm, abuse, privacy loss, unauthorized disclosure, one-sided obligations, misleading claims, accessibility barriers, financial exposure, or unsafe operational assumptions
- missing controls, ownership gaps, vague responsibilities, potentially unenforceable or unverifiable requirements, and dangerous defaults
- dependencies, external services, third-party assets, data handling, permissions, and lifecycle risks

For code, additionally inspect:
- untrusted input reaching SQL, shell commands, file paths, templates, HTML, eval-like APIs, dynamic imports, regexes, redirects, URLs, or deserializers
- authentication, authorization, session handling, token storage, password handling, and tenant boundaries
- secret handling in source, configs, logs, CI, examples, and error messages
- network calls, SSRF risk, webhook validation, CORS, CSRF, and open redirects
- cryptography, key generation, key storage, rotation, algorithm choices, and misuse of security primitives
- dependency age, abandoned packages, lockfiles, scripts, and install hooks
- unsafe defaults, debug endpoints, permissive config, and production footguns

For every safety or security finding, include:
- `Severity`: Critical, High, Medium, or Low
- `Evidence`: precise location, reference, observed behavior, or exact pattern
- `Why it is bad`: the exploit or failure mode
- `Simplest fix direction`: concrete remediation, removal, simplification, claim narrowing, manual recovery, or deferral as applicable

Use harsher wording for security theater, fake safeguards, silent failures, or artifacts that claim validation happened when it did not.

### 3. Fitness, Correctness, And Reliability

Inspect:
- whether the target can achieve its stated purpose for its intended audience
- contradictions, omissions, false assumptions, broken flows, ambiguous decisions, and failure handling
- edge cases, lifecycle changes, handoffs, dependencies, and realistic misuse or stress conditions
- whether claims, requirements, recommendations, and conclusions are supported and internally consistent

For code, additionally inspect:
- error handling, retries, timeouts, cancellation, cleanup, and resource leaks
- boundary cases, null/empty inputs, encoding, time zones, concurrency, and partial failures
- data migrations, schema drift, idempotency, and transactional behavior
- logs and observability that help diagnose real incidents

Call out places where the happy path is being treated as the whole problem.

### 4. Structure And Coherence

Judge:
- whether the organization matches how the audience needs to understand or use the target
- whether responsibilities, concepts, decisions, flows, and dependencies have clear boundaries
- whether abstractions, sections, visual hierarchy, or process stages reduce complexity or hide it
- whether names and labels reflect real concepts
- whether the target is coherent, navigable, and free of duplication or internal drift
- whether interfaces, handoffs, and ownership boundaries are explicit

For code, explicitly judge separation of state, IO, domain logic, presentation, configuration, public APIs, and module boundaries. Flag skewed, missing, or badly implemented patterns. If the target claims a pattern or principle but violates it, say so directly.

### 5. Validation And Coverage

Look for:
- evidence that important claims, requirements, flows, decisions, or outcomes were checked
- coverage of high-risk paths, failure modes, edge cases, audiences, devices, environments, or scenarios relevant to the target
- realistic review, approval, testing, research, user feedback, rehearsal, or measurement rather than ceremonial sign-off
- acceptance criteria that can distinguish success from wishful thinking

For code, inspect meaningful behavioral tests, security-sensitive and failure-path coverage, fixture quality, determinism, real-interface coverage, and brittle mocks that prove the implementation instead of behavior.

Treat missing tests around auth, payments, destructive operations, parsing, migrations, and shell/network execution as serious.

### 6. Clarity, Maintainability, And Presentation

Be picky about:
- vague or misleading names, labels, headings, claims, and calls to action
- unnecessary length, repetition, clutter, jargon, hidden assumptions, and cognitive load
- weak information or visual hierarchy, inconsistent presentation, and poor audience fit
- stale material, dead sections, unresolved placeholders, contradictory guidance, and avoidable maintenance burden
- fragile dependencies, unexplained conventions, and surprising side effects

For code, additionally inspect formatting, spacing, indentation, file layout, import order, comments, TODO debt, oversized files, copy-paste logic, dead or commented-out code, magic numbers, boolean parameter soup, hidden globals, dependency bloat, and opaque build scripts.

Style and presentation findings must still be concrete. Prefer "rename `x` because it is a request-scoped auth token, not a generic value" or "move the renewal clause before termination because it silently changes the reader's commitment" over "naming is bad" or "this is confusing".

## Severity

Assign severity from consequence, likelihood, reach, and reversibility within the reviewed target's current purpose, milestone, and credible operating environment, not reviewer annoyance or eventual ambition:

- `Critical`: credible catastrophic harm or complete failure of the target's core purpose
- `High`: major likely harm, failure, unusability, or exposure
- `Medium`: material weakness likely to cause defects, confusion, rework, or avoidable risk
- `Low`: localized weakness with limited impact
- `Nitpick`: optional polish that does not materially affect fitness for purpose

Apply severity, evidence, impact, and simplest fix direction to every substantive finding, not only security findings. For subjective surfaces, separate observable defects from taste. A demonstrated contrast failure is a finding; disliking a color is not one without a relevant brief, requirement, or standard.

For every substantive finding, also state:

- `Current applicability`: directly applicable, conditionally applicable, later-milestone hardening, evidence-only, review-process-only, or out of scope.
- `Simplest fix direction`: include removal, simplification, claim narrowing, manual recovery, or deferral when those reduce net risk better than another control.
- `Suggested disposition`: `block now`, `fix if proportionate`, `defer to named milestone`, `candidate for owner acceptance`, `evidence correction`, `process invalidated`, or `out of scope`.

Do not inflate a future-only concern into a current High or Medium finding merely because the target may later reach production. When later exposure materially changes severity, state that future risk explicitly. Do not lower a directly applicable finding merely because remediation is expensive.

Later-milestone, evidence-only, and review-process-only observations do not lower the current artifact grade unless they expose a current fitness defect. Put them in `Deferred, Evidence, And Review-Process Observations` rather than forcing them into the current severity queue. Mention an out-of-scope observation only when it materially affects the reviewed scope, and do not let it lower the grade by itself.

## Output Format

Use `templates/ROAST.md` as the report skeleton.

If no issues are found in a category, say so briefly and mention any limits of the review. Do not fake a problem to make the report harsher.

In `What To Fix First`, list up to three current blockers or proportionate fixes supported by reported findings. Do not place deferred hardening, evidence-only corrections, or process-invalidated reviews in this implementation priority list unless they require a current action. Omit unsupported slots, and omit the priority list entirely when there are no supported fixes.

## Orchestrator Use

Other workflow skills may use Roast output as a remediation work source or as a post-change review gate. Keep findings concrete enough to be acted on one at a time: severity, evidence, impact, current applicability, simplest fix direction, and suggested disposition. Roast does not depend on those orchestrator skills; it remains a standalone review skill.

Finding validity, severity, grade, and current remediation disposition are separate judgments. Roast recommends applicability and disposition; the orchestrator decides what blocks the current milestone against its work source, assurance posture, exposure, recoverability, and authority boundary. A valid finding does not become an automatic implementation requirement.

If the reviewed subject changes during an exact-artifact review, mark the affected verdict `process invalidated` and request a rerun against a stable revision. Preserve still-useful observations as stale evidence, but do not classify review-path drift as a target defect.

## Grading

Grade the reviewed scope, not merely the finding count:
- `A`: unusually solid for its purpose, with only minor polish issues
- `B`: fit for use, with meaningful but manageable weaknesses
- `C`: usable, but important structure, validation, clarity, or risk controls are doing the minimum
- `D`: fragile, confusing, risky, or expensive to use or maintain
- `F`: unsafe, broken, fundamentally unfit, or internally incoherent

Severity caps apply across target types:
- any unresolved Critical finding caps the grade at `D`
- multiple unresolved High findings cap the grade at `C`
- a fatal safety, security, legal, operational, or fitness-for-purpose defect usually deserves `F` until fixed

Grade against the stated current purpose and milestone. Do not make an A the implicit minimum for fitness when the rubric defines B as fit for use. Report future hardening and deferred exposure separately so they remain visible without distorting the current artifact grade.

Do not cap a grade merely because evidence was unavailable. Narrow the grade to the evidence-backed scope, state the confidence limit, and mark unreviewed categories `Not assessed` rather than treating them as defects. If the available evidence cannot support an honest A-F grade for even a useful bounded scope, use `Not graded` and state exactly what is missing.

## Evidence Rules

- Use target-appropriate tools to inspect source, rendered output, live behavior, metadata, or attachments when available.
- Prefer fast search tools for broad scans.
- Read or view the relevant artifact before criticizing it.
- Reference exact paths, lines, sections, pages, clauses, frames, regions, states, or timestamps when practical.
- Separate confirmed findings from suspicions.
- If a dependency, law, standard, convention, or external fact is current-state-sensitive, verify it before relying on it.
- Run focused checks or comparisons when they are obvious, safe, and relevant; otherwise state what was not performed.
- Do not imply legal, security, accessibility, financial, or other professional certification from a Roast review.
