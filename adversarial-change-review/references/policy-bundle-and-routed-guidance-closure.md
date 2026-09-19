# Policy bundle and routed-guidance closure

Use this when an in-scope authority rule has multiple active representations that can disagree. Apply only the surfaces actually affected and the checks justified by the task, real risk, and budget. This reference does not require a machine policy, CLI, package build, mutation suite, or independent reviewer for a prose-only skill edit.

## Review matrix

For each changed authority requirement, trace its relevant active representations. The following is a menu, not a requirement to exercise absent or unaffected surfaces:

1. **Machine-readable policy** — YAML/JSON IDs, inheritance, activation/default semantics, and every explicitly required review dimension.
2. **Primary guidance** — README, architecture contract, and main Skill decision point.
3. **Routed execution guidance** — references loaded later for inventory, assembly, runtime, packaging, or publication.
4. **CLI surface** — defaults, accepted values, persisted configuration, help, human-readable discovery, and machine-readable discovery.
5. **Regression evidence** — prove defaults, invalid values, independent option combinations, and package-installed behavior.

## Counterexamples

- Do not accept a complete Markdown description when the versioned profile checklist omits a required concept. If YAML is a named policy bundle, consumers may follow its IDs rather than prose. Test profile semantics, including inheritance, not merely keyword presence in a reference document.
- Do not stop after checking the prominent upfront decision. Follow every routed reference into later execution stages. A runtime guide that says an approved replacement may be included can collapse a required ladder such as `inventory -> replacement -> runtime inclusion`, even when the main Skill described all three correctly.
- Treat two policy axes as independent only after probing both directions and the default: A-opt-in/B-default and A-default/B-opt-in. Reject implementations where one selection silently implies the other.
- Distinguish policy recording from implemented automation. A CLI may validly persist a judgment-heavy Skill policy without implementing OCR or editorial work, but capability wording must not imply a deterministic subsystem that does not exist.

## Proportionate verification

Where the corresponding machine or package contract exists and is in scope, prefer focused assertions over broad prose snapshots:

- parse YAML/JSON and assert required concepts and additive inheritance;
- exercise CLI defaults, explicit combinations, invalid choices, and both text/JSON discovery;
- inspect the built/installed artifact to prove the changed Skill, references, profiles, and CLI ship together;
- add a narrow routed-guidance regression only for authorization boundaries whose drift could trigger costly or unauthorized work.

### Mutation-test routed authorization assertions

A green substring assertion is weak when the same phrase appears in several sections. If verifying that evaluator is part of the task, a mutation of the owning clause while leaving duplicates intact can reveal the gap. Scope a necessary assertion to the stage that owns the authority rather than searching the whole file; do not add mutations for every routed prose edit by default.

For exact-candidate approval ladders, test every conjunct separately: named policy selection, separate replacement authorization, separate runtime-inclusion authorization, exact replacement bytes, and binding to the current candidate. Also run a global deletion control for the candidate-binding qualifier. If removing `current candidate` everywhere still leaves the test green because it checks only `exact bytes`, the regression does not protect the full contract.

### Strict read-only exact-digest reviews

When the review contract forbids sandboxes, mutation scripts, or commands outside a narrow allowlist:

- reproduce the staged-diff digest with the exact stated serialization before inspection and again after all allowed gates;
- scope Markdown assertions to the owning headings (for example, pre-OCR inspection, runtime assembly, and the main Skill runtime step) so duplicate wording elsewhere cannot satisfy them;
- inspect CLI defaults and argument plumbing in both directions to prove independent policy axes, even if focused tests assert only one explicit combination;
- establish package closure from package inclusion rules, the installed-copy path, routed-reference inventory, and the allowed build result; do not claim direct wheel-content inspection unless it was permitted and performed;
- if the parent supplies grounded mutation evidence, treat it as supporting evidence and label it separately from checks run by the current reviewer—never imply the reviewer independently ran forbidden mutations.
