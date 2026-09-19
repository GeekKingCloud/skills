# Test-suite isolation from live application state

Use this when tests import a module whose path/config globals default to the user's real application home.

## Risk

A focused test can be logically correct yet still create durable runtime markers in the live home. Background production code may later consume or retry those markers, turning a test side effect into an operational alert loop. Targeted monkeypatches are easy to miss when new tests are added.

## Preferred fixture

Install a module-level `autouse=True` fixture that:

1. Captures the module's original application-home path before patching.
2. Snapshots the existence and bytes of the safety-critical live marker(s).
3. Monkeypatches the module-global home to `tmp_path` for every test in the module.
4. After the test, compares the original marker existence/bytes to the snapshot.

```python
@pytest.fixture(autouse=True)
def _isolate_app_home(tmp_path, monkeypatch):
    original_home = target_module._app_home
    original_marker = original_home / ".pending.json"
    before = original_marker.read_bytes() if original_marker.exists() else None

    monkeypatch.setattr(target_module, "_app_home", tmp_path)
    yield

    after = original_marker.read_bytes() if original_marker.exists() else None
    assert after == before, "tests mutated the original application marker"
```

## Why module-level autouse

- It protects current and future tests, including tests whose authors forget a targeted patch.
- Existing tests may still apply narrower overrides inside the isolated temp home.
- The byte sentinel proves absence of mutation rather than merely trusting fixture wiring.

## Boundaries and pitfalls

- Snapshot only safety-critical files; recursively hashing a busy live home creates race-prone assertions against legitimate runtime activity.
- If production may legitimately mutate the same marker concurrently, redirect the process environment before module import or assert only that the test path is under the temporary home. Do not mistake real concurrent runtime activity for test contamination.
- A parent-process monkeypatch does not affect subprocess imports. Subprocess tests that can write state must receive an isolated `HOME`/application-home environment explicitly.
- Keep bytecode caches outside the checkout during verification when cleanliness matters.
- This fixture prevents test writes; it does not authorize reading or deleting pre-existing live markers.
