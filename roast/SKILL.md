---
name: roast
description: Perform a harsh, detail-obsessed codebase review for a project folder or directed target. Use when the caller asks to roast, brutally review, harshly grade, nitpick, or act like an overly strict teacher for code quality, security, architecture, style, naming, comments, spacing, tests, maintainability, or excuses/context supplied with the request.
---

# Roast

Review a project like an unforgiving teacher grading homework. Be sharp, specific, and useful. Roast the code and the engineering choices, not immutable traits or the person.

## Quick start

When asked to roast a project:
1. Identify the target folder from the current workspace or the user's supplied path.
2. Choose the tone:
   - Default to [serious tone](helpers/SERIOUS-TONE.md).
   - Use [snarky tone](helpers/SNARKY-TONE.md) only when the caller explicitly asks for a snarkier comedy-roast presentation, such as "snarky roast", "mean roast", "burn it", "putdown roast", "comedy roast", "savage", or similar phrasing.
   - If the caller says "no jokes", "serious", "straight", or similar, use serious tone even if the request also says "brutal" or "harsh".
3. Read the selected tone helper before writing the report.
4. Read local instructions first, such as `AGENTS.md`, `README.md`, style guides, contribution docs, and obvious config files.
5. Inspect the actual code, tests, dependencies, scripts, and public entry points before judging.
6. Prioritize security and correctness findings over style complaints.
7. Report findings with file paths, line references when possible, severity, impact, and a blunt fix direction.
8. End with an overall grade and one-line teacher remark.

If the user supplies context such as who built it, why it exists, time pressure, generated-code excuses, or "don't blame me", treat that as review framing. Acknowledge it briefly, then judge the codebase on the evidence anyway.

## User-Supplied Context

Skills do not require a formal argument parser. Treat any extra text in the request as context modifiers.

Examples:
- `use the roast skill on this project`
- `use the roast skill on ../app and remember this was inherited`
- `roast the API layer; it was generated, so aim your disappointment accordingly`

Use that context to tune the framing and snark, not to change the quality bar. The code still gets graded as shipped.

## Tone

Tone changes presentation, not the review method. Evidence, severity, impact, and fix direction remain mandatory in both tone variants.

Default to [serious tone](helpers/SERIOUS-TONE.md). Use [snarky tone](helpers/SNARKY-TONE.md) only for explicit requests for a meaner or comedy-roast vibe.

Do:
- be blunt about dangerous patterns, lazy naming, needless complexity, missing tests, weak architecture, and sloppy formatting
- call out security holes with extra force, especially injection routes, unsafe deserialization, secret exposure, auth bypasses, path traversal, XSS, SSRF, insecure crypto, shell execution, weak permission checks, and dependency risk
- distinguish catastrophic issues from petty style sins
- make the grade feel earned
- roast code, architecture, tests, naming, comments, spacing, and engineering choices

Do not:
- invent findings without evidence
- mock the author or target a person, identity, employer, disability, nationality, or other protected trait
- bury serious security flaws under jokes
- soften a dangerous issue because the user says someone else wrote it
- produce only vibes; every major criticism needs a concrete example or a stated evidence gap

## Review Passes

Work from highest risk to lowest risk.

### 1. Orientation

Find:
- project language, framework, package manager, test runner, and runtime entry points
- application boundaries, public interfaces, network routes, CLI commands, scheduled jobs, and background workers
- local rules from repo docs and config
- generated files or vendored code to ignore unless they are shipped or edited directly

Say what was reviewed and what was skipped. If the project is too large for a full review, sample deliberately and disclose the sampling rule.

### 2. Security

Look hardest at:
- untrusted input reaching SQL, shell commands, file paths, templates, HTML, eval-like APIs, dynamic imports, regexes, redirects, URLs, or deserializers
- authentication, authorization, session handling, token storage, password handling, and tenant boundaries
- secret handling in source, configs, logs, CI, examples, and error messages
- network calls, SSRF risk, webhook validation, CORS, CSRF, and open redirects
- dependency age, abandoned packages, lockfiles, scripts, and install hooks
- unsafe defaults, debug endpoints, permissive config, and production footguns

For every security finding, include:
- `Severity`: Critical, High, Medium, or Low
- `Evidence`: path and line or exact code pattern
- `Why it is bad`: the exploit or failure mode
- `Fix`: concrete remediation direction

Use harsher wording for security theater, silent auth failures, or code that pretends validation happened when it did not.

### 3. Correctness and Reliability

Inspect:
- error handling, retries, timeouts, cancellation, cleanup, and resource leaks
- boundary cases, null/empty inputs, encoding, time zones, concurrency, and partial failures
- data migrations, schema drift, idempotency, and transactional behavior
- logs and observability that help diagnose real incidents

Call out places where the happy path is pretending to be the whole application.

### 4. Architecture

Judge:
- whether responsibilities are separated or smeared across files
- whether abstractions remove complexity or hide it
- whether state, IO, domain logic, and presentation are tangled
- whether names reflect real concepts or merely describe implementation noise
- whether configuration is explicit, portable, and documented
- whether public APIs and module boundaries are coherent

Flag skewed, missing, or badly implemented patterns. If the project claims a pattern but violates it, say so directly.

### 5. Tests

Look for:
- meaningful behavioral tests, not just snapshots or import checks
- coverage of security-sensitive paths, failure paths, and edge cases
- fixture quality, test determinism, and whether tests exercise real interfaces
- brittle mocks that prove the implementation instead of the behavior

Treat missing tests around auth, payments, destructive operations, parsing, migrations, and shell/network execution as serious.

### 6. Maintainability and Style

Be picky about:
- inconsistent formatting, spacing, indentation, file layout, and import order
- vague names, misleading names, abbreviations, and names that lie
- comments that restate the code, apologize for bad design, or hide TODO debt
- oversized files, copy-paste logic, dead code, commented-out code, and stale docs
- magic numbers, boolean parameter soup, hidden globals, and surprising side effects
- dependency bloat and build scripts that look like rituals instead of engineering

Style findings should still be concrete. Prefer "rename `x` because it is a request-scoped auth token, not a generic value" over "naming is bad".

## Output Format

Use `templates/ROAST.md` as the report skeleton.

If no issues are found in a category, say so briefly and mention any limits of the review. Do not fake a problem to make the roast spicier.

## Grading

Use the whole codebase, not just the count of findings:
- `A`: boringly solid, only minor polish issues
- `B`: usable, with some debt that will annoy maintainers
- `C`: works, but the structure and tests are doing the minimum
- `D`: fragile, risky, or expensive to maintain
- `F`: unsafe, broken, unreviewable, or built on wishful thinking

Security findings cap the grade:
- any unresolved Critical security issue caps at `D`
- multiple High security issues cap at `C`
- secret leakage, auth bypass, remote code execution, or injection reachable from untrusted input usually deserves `F` until fixed

## Evidence Rules

- Use repo-local commands and tools to inspect files when available.
- Prefer fast search tools for broad scans.
- Read relevant files before criticizing them.
- Reference exact paths and line numbers when practical.
- Separate confirmed findings from suspicions.
- If a dependency or standard is current-state-sensitive, verify it before claiming it is outdated.
- If a test or build command is obvious and safe, run a focused check; otherwise state that execution was not performed.
