# Exact-Commit Stateful Guardrail Review Patterns

## Immutable test checkout

Use when other agents may share the worktree:

```bash
target=<full-sha>
tmp="$(mktemp -d)"
git archive "$target" | tar -x -C "$tmp"
(
  cd "$tmp"
  # Run the repository's real test command here.
)
```

`git archive` exports tracked bytes from the named commit and prevents concurrent worktree edits from changing the evidence. Re-run syntax checks and targeted tests inside the archive. The archive has no `.git`, so run commit-diff checks in the source repository, not inside the export.

### Ad-hoc verification hygiene

When canonical tests do not exercise the counterexample, create a focused temporary script under `/tmp` with an OS-safe prefix such as `review-probe-`, run it against the immutable target bytes, record the concrete assertion/output, and delete it before finishing. Keep probes out of the source worktree unless the task explicitly requests a regression test change. After cleanup, verify both that temporary artifacts are absent and that the source worktree has not changed; if unrelated concurrent edits appeared, report them without resetting or cleaning them.

## Marker stability versus distinctness

A stateful boundary marker needs two properties that must be tested independently:

1. **Stability:** archive/reinsert or compaction changes physical row IDs but preserves the same logical event, so the marker must remain unchanged.
2. **Distinctness:** a later logical event must produce a different marker even when timestamps collide or round to the same displayed precision.

A timestamp-only marker, especially one formatted to fixed decimal precision, usually proves stability but not distinctness. A timestamp-plus-content-hash marker still collides for two distinct repeated prompts with identical bytes and timestamp; test that case explicitly, not only same-time messages with different content. A row-ID-only marker usually proves distinctness but not stability. Prefer immutable logical provenance such as a preserved platform/event identifier, potentially compounded with canonical content/time. Test all three cases separately: duplicate physical rows for one logical event, distinct same-time/different-content events, and distinct same-time/same-content events.

For timestamp+digest+duplicate-ordinal fallbacks, also combine compaction and distinctness in one sampling interval. Start with two active identical same-time rows (marker ordinal 2), compact away the older duplicate and reinsert the prior latest logical event, then append a genuinely new identical same-time event before the next watchdog read. The newest row again has ordinal 2, so the complete fallback marker can remain byte-identical even though a real owner boundary occurred. Carry a high pre-compaction lineage baseline into evaluation and require the new event to reset it; otherwise the watchdog can falsely stop owner-directed work. An ordinal-decrease test alone does not cover this collision.

When immutable provenance is absent, perfect logical reconstruction is impossible in this sequence. Use the narrowest conservative fallback:

- Keep unique timestamp/content equivalence classes compaction-stable; their archive/reinsert copy can retain the logical marker.
- When more than one active event has identical normalized content and timestamp, add a physical event token (such as the selected insertion ID) only to that ambiguous duplicate marker.
- Accept that ambiguous duplicate reinsertion will reset the baseline. This false-negative tradeoff is safer for a false-stop-sensitive guardrail than allowing a genuinely new owner event to collide and inherit mature unattended usage.
- Keep an independent host-burst circuit breaker so one conservative lineage reset does not erase all containment.

The regression must cover both sides: ordinary unique archive/reinsert keeps its marker, while duplicate compaction plus a new identical event before the next sample changes the marker and yields `lineage_calls == 0` / `stop == False`. Do not generalize a row ID into every fallback marker; that recreates compaction churn for ordinary boundaries.

Minimal evaluation shape:

```python
first_sample = read_usage(now)[0][0]
_, state = evaluate([first_sample], total, {}, now)

# Insert a distinct logical boundary with the same timestamp and grow usage.
second_sample = read_usage(later)[0][0]
result, _ = evaluate([second_sample], new_total, state, later)

assert second_sample.marker != first_sample.marker
assert result.lineage_calls == 0
assert not result.stop
```

## Synthetic events stored as user-role rows

Do not assume a storage role maps one-to-one to a human actor. Agent runtimes may persist these as `role='user'` so they can be injected into the next model turn:

- async delegation completion notices;
- compaction/task-list restoration messages;
- scheduled-job prompts;
- recovery or handoff injections;
- out-of-band control messages.

For owner-boundary logic:

1. Query representative live rows read-only and inspect content/provenance fields.
2. Search the installed/runtime source for every producer of model-facing `role='user'` injections; do not infer the inventory solely from repository fixtures or observed rows.
3. Compare related producer variants independently (for example, singular versus batch completion notices, old versus current compaction headers, and wrapped versus unwrapped recovery notes). A shared phrase does not imply one exact prefix covers every variant.
4. Insert each synthetic class after a real owner boundary.
5. Confirm the selected marker does not change and the baseline does not reset.
6. Prefer durable provenance metadata over an expanding prefix blacklist. If metadata is unavailable, enumerate known synthetic prefixes and add regression fixtures for each.
7. Add paired acceptance controls for legitimate bracketed inputs—voice-message wrappers, reply context, mid-turn owner steering, and scheduled task prompts—so filtering internal notices does not suppress real boundaries.
8. Parameterize fallback prefix predicates rather than interpolating stored content into SQL, and benchmark the complete predicate set against production-shaped no-index data.

When provenance is unavailable, derive the initial prefix inventory from representative read-only state rather than memory. Separate internal lifecycle notices from user-originated transport wrappers: both may use `role='user'` and leading brackets, but only the latter should reset an owner-scoped budget. Also test **nested composition**: an interruption/recovery wrapper can prepend model-facing guidance to either a genuine owner message or a synthetic async/process completion. Filtering the wrapper wholesale creates false exclusions, while ignoring it can let a wrapped synthetic event reset the baseline; strip/parse the wrapper and classify the enclosed payload. A content digest can disambiguate distinct same-timestamp owner events only when their canonical bytes differ; verify both byte stability across compaction and repeated-identical-content behavior.

### Empty user-placeholder counterexample

Some compaction and recovery transcripts preserve model/API sequencing with an empty `role='user'` row, often in a shape like:

```text
assistant: [CONTEXT COMPACTION — REFERENCE ONLY] ...
user:     ""
assistant: ""
tool:      <retained continuation>
```

A newest-by-insertion-ID boundary query that excludes only known content prefixes will select the empty user placeholder. Its timestamp/digest marker then differs from the genuine owner marker and resets the lineage baseline exactly when accumulated unattended work is already high.

Required probe:

1. Establish state from a genuine owner row with durable transport provenance.
2. Increase cumulative usage beyond the stop threshold.
3. Insert the synthetic compaction summary followed by a provenance-free empty user placeholder and continuation rows.
4. Read and evaluate again; assert the genuine owner marker remains selected and the accumulated delta still stops.

Validated nonempty transport/event provenance remains authoritative even when text is empty—attachment-only owner events can be legitimate—but a NULL/empty-content user row without such provenance is not an owner boundary. Normalize provenance consistently in both SQL filtering and marker construction.

### Provenance-precedence validation

Content classification and durable provenance need a paired acceptance matrix:

| Row kind                           | Durable platform/event ID | Content begins synthetic prefix | Expected boundary    |
| ---------------------------------- | ------------------------: | ------------------------------: | -------------------- |
| Runtime-generated notice           | absent                    | yes                             | exclude              |
| Genuine owner paste                | present                   | yes                             | include              |
| Genuine ordinary input             | present                   | no                              | include              |
| Provenance-free legacy owner input | absent                    | no                              | include via fallback |

Use this fuller branch matrix when the storage role is overloaded:

| Provenance           | Stored content / shape                                                                     | Expected result                  |
| -------------------- | ------------------------------------------------------------------------------------------ | -------------------------------- |
| validated durable ID | empty, ordinary, or synthetic-looking pasted text                                          | include; durable provenance wins |
| absent               | NULL, empty, or whitespace-only user placeholder                                           | exclude                          |
| absent               | known interruption/recovery wrapper whose extracted payload starts with a synthetic prefix | exclude                          |
| absent               | known wrapper whose payload is genuine but quotes a synthetic prefix later                 | include                          |
| absent               | direct known synthetic prefix                                                              | exclude                          |
| absent               | nonempty ordinary or bracket-prefixed legacy input not proven synthetic                    | include through fallback         |

Implement and test that order literally. In schema-versioned SQLite code, feature-detect the provenance column before building the query, use the same normalized nonempty test in candidate filtering and marker construction, and parameterize every prefix branch. Pair each rejection fixture with a nearby acceptance control so tightening one branch cannot silently suppress legitimate owner boundaries.

Before implementing this precedence, inspect every known synthetic producer and representative live rows read-only. Confirm synthetic injections do not copy or invent the platform/event ID. If they do, field presence is not authoritative and the design needs stronger origin metadata. Then parameterize one genuine platform fixture per configured synthetic prefix; testing only one prefix can hide a precedence bug in generated SQL.

### Canonical Unicode normalization inside SQLite

Do not duplicate “nonblank” semantics with SQLite `trim()` and application-language `strip()`: SQLite's one-argument `trim()` removes only ASCII space, while Python's `str.strip()` covers tabs, newlines, and Unicode whitespace. For a read-only Python/SQLite guardrail, define one normalizer and register it on every connection before running selection queries:

```python
def normalize_boundary_text(value: object) -> str:
    return str(value or "").strip()

con.create_function(
    "boundary_normalize",
    1,
    normalize_boundary_text,
    deterministic=True,
)
```

Use `boundary_normalize(column) <> ''` for SQL eligibility and call the same function during marker construction. The regression matrix must independently cover both content and provenance with `NULL`, empty string, ASCII space, tab, CR/LF, vertical tab/form feed, NEL (`U+0085`), NBSP (`U+00A0`), representative `U+2000` whitespace, line/paragraph separators, and ideographic space. Assert the operational result at the stop threshold—not merely which row was selected—so any normalization mismatch is proven unable to reset a mature safety baseline. Benchmark the exact UDF-backed query against production-shaped data because Python callbacks can change query cost.

A minimal read-only inventory shape is:

```sql
SELECT
  CASE
    WHEN content LIKE '[ASYNC DELEGATION%' THEN 'async'
    WHEN content LIKE '[CONTEXT COMPACTION%' THEN 'compaction'
    WHEN content LIKE '[System note:%' THEN 'system-note'
    ELSE 'other'
  END AS class,
  COUNT(*) AS rows,
  SUM(
    CASE WHEN length(trim(COALESCE(platform_message_id, ''))) > 0
         THEN 1 ELSE 0 END
  ) AS with_provenance
  FROM messages
  WHERE role = 'user'
  GROUP BY class;
  ```

  Adapt column names after `PRAGMA table_info(messages)`; never assume current and legacy schemas match. Use this same canonical normalization everywhere provenance is interpreted: candidate selection, empty-placeholder rejection, content-filter bypass, marker construction, fixtures, and diagnostic inventory. Include the cross-product of NULL/empty/whitespace content with NULL/empty/whitespace provenance; otherwise SQL may admit a placeholder that application code later strips back to “no provenance.”

### Wrapper wildcard counterexample

Do not use a predicate shaped like `wrapper_prefix%\n\nsynthetic_prefix%` to mean “the enclosed payload begins with this prefix.” SQL `%` can cross newlines and consume genuine payload text. This owner message is therefore a required acceptance control:

```text
<wrapper header>

Please debug this notice I received:

[Recent channel messages] quoted evidence
```

The payload begins with `Please debug`, so it is genuine even though a later paragraph quotes a synthetic prefix. Build the probe with an older owner marker and a newer durable platform/event ID, then assert that the newer marker is selected and the lineage baseline resets. Also compare evaluation at the stop threshold: misclassification should reproduce a stop with the old marker, while correct extraction should yield zero lineage delta with the new marker. The implementation should identify the wrapper's actual closing boundary, extract the immediately enclosed payload, and apply `startswith` classification to that payload only.

A synthetic reset is especially dangerous when a rolling-window guard has no eligible historical baseline yet: repeated internal events can suppress the lineage guard during the startup portion of the window.

## SQL query review

For large SQLite state databases:

- inspect `PRAGMA table_info` and `PRAGMA index_list`;
- use `EXPLAIN QUERY PLAN` on the exact query;
- bound candidate sessions before message aggregation;
- verify correlated message lookup uses a session/activity index;
- cap returned parent sessions before per-parent child aggregation;
- time the query read-only against representative current and legacy fixtures.

A bounded legacy fallback may intentionally miss old long-lived sessions when the schema lacks activity metadata. Document this as a conservative false-negative tradeoff rather than silently returning to an unbounded message-table scan.

## Review output

For PASS-or-findings-only requests, use:

```text
- **SEVERITY — path:line** — Concrete invariant violation, exact reproduction outcome, operational consequence, and correction/test required.
```

Do not add a process summary, “looks good” section, or speculative concern. Report only issues reproduced against the named target.
