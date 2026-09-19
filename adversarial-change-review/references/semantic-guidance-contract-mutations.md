# Semantic guidance-contract mutation testing

Use this only when evaluating an existing machine-enforced guidance contract or a specifically requested evaluator change. Ordinary prose review does not require an evaluator, parser, or mutation matrix. The task's scope, threat model, and verification budget govern the selection below; do not broaden a finite sentinel into arbitrary natural-language recognition.

## Mutation matrix

For a demonstrated evaluator failure, select a few realistic counterexamples and passing controls from the relevant grammar axes:

- **Obligation:** `must`, `required`, `requires`, `mandatory`, `has to`, `should`, `always`.
- **Condition/sequencing:** `only if`, `only when`, `unless`, `provided that`, `once`, `after`, `without`, `absent`, `conditional upon`, `contingent on`, `prerequisite`.
- **Execution action:** launch/start/spawn/create/schedule/initiate, including passive and nominal forms (`is to be started`, `the initiation ... is mandatory`).
- **Turn binding:** same/current/this turn, in either word order and across line breaks within one sentence.
- **Voice:** direct, imperative, negative-imperative, passive, conditional, and nominal.

Do not generate the cross-product by default. Compare observed behavior with the evaluator's declared coverage. A passing contradiction disproves semantic completeness, but is not automatically a release blocker when the agreed gate is only a wording sentinel with semantic review.

## False-positive controls

For every broadened obligation/action class, add controls for:

- `need not`, `not required`, `not mandatory`, `no prerequisite`;
- `does not need to` and `does not have to`;
- an earlier handle freshly verified active;
- unrelated current-turn examples in a later sentence.

Keep matching sentence-bounded. A connector or obligation in one sentence must not combine with an action/turn phrase in a later sentence.

## Review loop

1. Freeze and identify the exact candidate SHA.
2. Run the unmodified canonical evaluator.
3. Apply hostile and benign mutations in a disposable object-addressed checkout.
4. Require hostile mutations to fail and benign controls to pass.
5. Remove the mutation, re-attest exact bytes, and rerun canonical gates.
6. Keep approval bound to the tested candidate. After an amendment, rerun affected checks required by the contract; do not automatically repeat independent review or unaffected gates.

## Reporting

Separate runtime defects from evaluator gaps. Record each mutation sentence, observed exit/result, expected classification, and the exact pattern or parser branch responsible. Do not claim semantic completeness from a finite synonym list; state the supported grammar classes and probe their boundaries explicitly.
