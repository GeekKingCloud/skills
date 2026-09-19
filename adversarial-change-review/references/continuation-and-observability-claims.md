# Continuation and observability claim review

Use this when an exact candidate changes assistant claims about future work, status output, lifecycle guards, or regression tests around detached execution.

## Claim semantics

- A final response ends foreground execution, but a durable executor may remain active.
- Do not require that the executor was launched in the current turn. A previously launched delegation, tracked process, service unit, or scheduled job can support a continuation claim when its exact handle has been freshly verified as active.
- Plans, task lists, handoffs, intentions, and remaining turn/autonomy budgets are not executors.
- Distinguish work completed before the current final response from work asserted to continue after it.

## Unknown is not inactive

Any status surface that catches an observation failure and substitutes `0`, `false`, or `No work active` makes an unsupported negative claim. Represent the affected field as unknown/unavailable. Derive an overall state conservatively rather than reporting inactivity when a material component could not be inspected.

For destructive lifecycle actions such as session finalization, reset, cleanup, or cancellation, inability to inspect an ownership-sensitive active-work source should normally fail closed by deferring the action. A retryable false deferral is safer than finalizing live work.

## Regression counterexamples

When records have a strong owner identifier plus a legacy fallback key, test all of these:

1. matching strong owner ID;
2. different strong owner ID with the same fallback key — must not match;
3. missing strong owner ID with matching fallback key — must match if compatibility requires it;
4. unrelated owner and key — must not match;
5. observation probe raises — status becomes unknown and destructive action is deferred.

A test where both the strong owner ID and fallback key differ does not prove precedence: an incorrect OR-based implementation still passes.

## Minimal adversarial probe

Patch the real inspector to raise a controlled exception and invoke the production status or lifecycle helper. Assert the rendered claim or guard result directly. This tests the failure policy rather than merely checking that an exception was logged.
