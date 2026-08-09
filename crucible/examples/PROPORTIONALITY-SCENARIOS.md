# Proportionality Scenarios

Use these scenarios to forward-test changes to Crucible or Roast gate behavior. They are decision fixtures, not mandatory checks for every run.

## Recoverable Development Structure

An empty development database has no users, production data, producers, or consumers. A completion race can certify contradictory facts. A reviewer also proposes exact patch-version pinning, immutable manifests, alerts, and automatic cleanup.

Expected decision: block the credible completion-integrity defect. Defer or reject assurance machinery that does not protect the current milestone. Prefer observable manual recovery over a cleanup subsystem unless automatic recovery is required.

## Live Financial Write Path

A live payment path can issue duplicate irreversible charges under a credible race.

Expected decision: use a live-critical posture and block the race even if its isolated likelihood would otherwise be Medium.

## Mutable Review Subject

Files change while an exact-artifact reviewer is inspecting them.

Expected decision: mark the review process invalidated and rerun against a frozen candidate. Do not classify path drift as a product architecture defect.

## Safeguard Ratchet

Automatic cleanup is added for partial deployment. Review then shows that cleanup could delete concurrent external work.

Expected decision: compare removal, manual recovery, staging, and further ownership machinery. Do not automatically add another control.

## Overstated Evidence

Runtime compilation passes, but a static inspection skipped one large file while the report claims complete static coverage.

Expected decision: correct or narrow the evidence claim. Do not revise product architecture unless the skipped file reveals a target defect.

## Eventual Production Ambition

A disposable development proof may later become a production component.

Expected decision: gate the current development milestone from present exposure. Record production-only requirements as deferred lifecycle gates rather than importing them immediately.
