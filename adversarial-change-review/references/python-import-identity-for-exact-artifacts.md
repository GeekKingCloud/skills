# Python import-identity checks for exact-artifact reviews

Python review gates can silently exercise the wrong bytes through inherited `PYTHONPATH`, editable-install finders, user-site packages, runtime shims, or a source checkout on `sys.path`.

## Source/archive gate

- Run from the disposable exact-target root.
- Set `PYTHONPATH` explicitly to that root's source directory and use `PYTHONNOUSERSITE=1` when compatible.
- Before tests, print and assert every reviewed module's resolved `__file__` is beneath the disposable root.
- If a prior run imported elsewhere, discard its result and rerun after sanitizing routing.

## Installed wheel/sdist gate

Apply the inverse isolation rule:

- Install each artifact into its own clean environment.
- Run smoke checks from a neutral directory outside all checkouts, exports, and build trees.
- Remove source-routing environment entries; do not point `PYTHONPATH` at the reviewed source.
- Print and assert reviewed modules resolve beneath that environment's `site-packages`.
- A successful console command is contaminated evidence if imports came from a checkout, even when the intended artifact was installed in the virtual environment. Rerun after proving installed-artifact identity.
