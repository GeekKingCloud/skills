# Semantic Policy Negation Mutation Probes

Use this for a demonstrated or explicitly in-scope gap in an existing prose/Markdown evaluator. These are optional counterexample recipes, subordinate to the task, real risk, and verification budget—not instructions to add an evaluator to ordinary prose or execute every matrix. A wording sentinel may legitimately be limited; correct its claims rather than automatically growing a parser.

## Why deletion-only tests are insufficient

Substring tests can prove that vocabulary remains present while accepting the opposite policy. This is especially likely with:

- case-insensitive matching;
- unanchored patterns;
- `DOTALL` combined with `.*`;
- independent phrases that are never checked as one clause;
- required text that can still match inside `not`, `need not`, or a disclaimer saying the proposition is false.

A useful attribution control is to delete the required phrase first. If deletion fails but direct negation passes, the gate is wired correctly but semantically inadequate.

## Compact mutation matrix

For selected mutations, isolate and restore the candidate, and invoke the gate whose claimed protection is being checked. Separate disposable checkouts are an option, not a required checkout per sentence:

| Protected modality                    | Deletion control    | Direct-negation control                                              |
| ------------------------------------- | ------------------- | -------------------------------------------------------------------- |
| `must be outside boundary X`          | remove the clause   | `need not be outside boundary X`                                     |
| `Require boundary X`                  | remove the sentence | `Do not require boundary X`                                          |
| `must fail closed`                    | remove the clause   | `it is false that supervision must fail closed`                      |
| `verify that it is empty`             | remove the clause   | `do not verify that it is empty`                                     |
| `never terminate unrelated processes` | remove the clause   | `it is not true that one should never terminate unrelated processes` |

Also probe exception coupling: keep all expected nouns but separate the exception from one or more of its guards, or insert an unconditional escape clause between them.

### Obsolete-phrase blacklist trap

A regression that asserts both a new positive substring and the absence of the exact obsolete contradiction can still accept a semantically equivalent contradiction. Mutation-test the replacement policy itself, not only resurrection of the old bytes. A compact control is to retain the asserted predicate inside a false-claim wrapper, then state the forbidden duty in new words—for example: `The claim that an agent applies the safe defaults without interrupting the owner is false; the operator must ask about both policies.` If the gate stays green, its negative assertions protect wording rather than modality. This is especially important for clone-and-point contracts where `standard`/`preserve` are inferred defaults and only explicit opt-ins should interrupt the owner.

### Mandatory phrase retained, policy weakened

After direct negations are rejected, keep the exact protected phrase intact and add a low-effort weakening. This catches gates that were repaired only for a short synonym list:

- **Tail exception:** `must fail closed except when cleanup is inconvenient`.
- **Prefix exception:** `Except during diagnosis, supervision must fail closed` or `Except after timeout, verify that the boundary is empty`. Suffix-only forbidden patterns miss these while the protected phrase remains unchanged.
- **Guard escape:** `Require the boundary for detaching work, unless detachment is expected`.
- **Equivalent negation:** replace `must be outside` with `is not required to be outside`; short synonym lists covering only `need not`, `does not need to`, and `must not` are insufficient.
- **Qualified obligation:** append `where practicable`, `when convenient`, `when feasible`, or `to the extent possible` to a mandatory deadline, containment, terminal-state, or fail-closed clause.
- **Attempt-only weakening:** replace `verify that it is empty` with `attempt to verify that it is empty`; an unanchored `verify` substring still matches although successful verification is no longer required.
- **Deadline escape:** `verify that it is empty unless the cleanup deadline expires`.
- **Later contradiction:** retain the mandatory sentence, then add `The inactivity deadline may be omitted for trusted workers` or `The workload may instead remain inside the gateway boundary`.
- **Safety override:** `never terminate unrelated processes by name alone, except when containment is difficult`.

Select realistic weakening cases that address the claimed invariant; restore between probes. A green result can expose a limitation even when positive vocabulary remains. Do not expand synonym or exception coverage indefinitely: retain semantic judgment and state what the finite check proves. Independent review is required only when the governing task or repository requires it.

## Failure-stage attribution

A negative regression is not meaningful merely because it expects a generic failure. Helpers often perform several assertions in sequence, so a semantic-negation fixture may fail first because it deleted an exact required sentence and never exercise the new negation or owner-handoff guard.

For each guard added to a policy helper:

- retain every earlier prerequisite so execution reaches that guard;
- assert the specific failure reason or test the guard independently rather than using only `pytest.raises(AssertionError)`;
- pair the helper-level test with an actual governed-document mutation;
- keep the protected mandatory sentence intact when probing later contradictions.

If a fixture would also fail under the deletion-only implementation, it is not evidence that the semantic repair works.

## Permitted-handoff controls

Owner-handoff detection must distinguish forbidden routine-default questions from required explicit opt-ins. A section-wide regex banning modal verbs near `ask`, `confirm`, or `owner` can reject valid guidance such as confirming an explicit adult-mode, provider, publication, or image-replacement opt-in while still missing equivalent forbidden wording such as `has to consult`.

For every forbidden handoff probe, include a valid passing control in the same governed section:

- routine safe defaults proceed without interrupting the owner;
- a named consequential opt-in still requires owner confirmation;
- equivalent forbidden wording (`has to consult`, `is obliged to check with`, or similar) is rejected when applied to routine defaults.

Prefer clause-scoped assertions tied to the routine-default predicate over section-wide vocabulary blacklists.

### Owner-handoff synonym and ordering probe

When the protected contract is “do not ask before work begins,” test a retained canonical sentence plus a later contradiction in the **actual routed document**, not only a helper-built synthetic string. Include at least one mutation that changes all three lexical axes at once, for example:

> Before translation begins, the agent shall consult the human about whether the default or optional policy applies.

This catches common regex blind spots:

- `ask` is replaced by `consult`, `check with`, or `seek direction from`;
- `user|owner` omits `human`, `operator`, or another governed actor term;
- `must|required to|has to` omits `shall`, `is obliged to`, or imperative wording;
- a pattern assumes the temporal phrase appears before or after the action in only one order.

If a selected direct contradiction passes while canned mutations fail, report the guard as vocabulary-bound. Decide whether to narrow its claim or repair a demonstrated requirement. Do not introduce normalized owner-facing-line allowlists or semantic parsers merely to close hypothetical paraphrase gaps; explicit opt-in and ordinary reporting guidance must remain valid.

## Evidence standard

For every mutation record:

1. exact target OID and disposable checkout path;
2. exact byte replacement;
3. full gate command and exit status;
4. positive deletion-control result;
5. the assertion/guard that actually caused rejection;
6. a valid nearby policy control that remains accepted;
7. final checkout status.

A green direct-negation mutation is a concrete counterexample when the regression's stated rationale is to preserve that mandatory invariant.

## Correction shapes

Prefer the narrowest maintainable correction:

- assert a complete sentence or clause including mandatory modality;
- scope matching to the governed paragraph instead of the whole document;
- reject direct negation and weakening near the protected predicate;
- couple narrow exceptions with every required guard in one assertion;
- retain representative negative mutations as executable controls.

Do not claim general natural-language understanding from regexes. These checks are sentinels; semantic reading remains necessary, but a separate reviewer is not an automatic additional gate.

## Same-turn execution-obligation matrix

For policies that allow a freshly verified handle from an earlier turn but forbid claiming continuation without real execution, mutation-test **affirmative current-turn obligations** separately from benign clarification. Cover both word orders and sentence boundaries:

- modal: `A handle must be launched in the current turn`;
- conditional: `Work continues only if ... current turn`;
- equivalent conditional: `Work continues only when ... current turn`;
- reversed conditional: `Only when the current turn launches ... may continuation be claimed`;
- imperative: `Launch the handle in this turn before saying work continues`;
- multiline variants for each clause.

Pair those with passing controls that retain the same trigger nouns:

- `need not be launched in the current turn`;
- `launching in the same turn is not required`;
- `do not require launching in this turn when an earlier handle is freshly verified`;
- `is not always launched in the current turn`.

For an existing regex sentinel, sentence- or clause-bounded patterns can avoid unrelated matches. Broad proximity regexes over `launch`, `current turn`, and `always` can reject negated controls while missing `only when` and bare imperatives. Keep only representative controls within the declared contract and read the governed prose semantically; do not add an independent review round unless required.
