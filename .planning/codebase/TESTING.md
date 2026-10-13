# Testing Patterns

**Analysis Date:** 2026-10-13

## Test Framework

**Runner:**
- pytest (unpinned, from `requirements-dev.txt`: `ruff`, `pytest`, `jsonschema`, `PyYAML`, `Jinja2`, `python-docx`)
- Config: none (no `pytest.ini`, `pyproject.toml`, `conftest.py`); defaults apply, run from repo root.
- One file uses stdlib `unittest` (`tests/test_control_scope_registry.py`), which pytest also collects.

**Assertion Library:** plain `assert` (pytest), `self.assertEqual` (unittest), `pytest.raises`.

**Run Commands:**
```bash
python -m pytest tests                       # Run all tests
python -m pytest tests/test_wave2d_applicability_authority.py -k pending   # Single test
python -m pytest tests --basetemp=.pytest-temp   # Matches the untracked .pytest-* dirs used locally
python -m ruff check scripts tests           # Lint (not enforced in CI)
```
Coverage tooling: not configured.

## Test File Organization

**Location:** Separate top-level `tests/` directory (not co-located).

**Naming:** `tests/test_<subject>.py`; functions `test_<behavior>` (long, behavior-describing, e.g. `test_adjudicated_applicable_wins_over_pending_matrix`).

**Structure:**
```
tests/
├── test_archive_assessment_applicability_authority.py   # fail-closed validation of AA3 authority
├── test_control_scope_registry.py                       # registry shape (80 controls, unique IDs, scopes)
└── test_wave2d_applicability_authority.py               # resolver behavior using tmp_path CSVs
```
Only 3 test files (~164 lines). The ~500 scripts in `scripts/` are otherwise validated by PowerShell `Test-*.ps1`/`Validate-*.ps1` scripts and CI parse checks.

## Test Structure

**Suite Organization (mutation / fail-closed pattern, `tests/test_archive_assessment_applicability_authority.py`):**
```python
SPEC = importlib.util.spec_from_file_location('aa3_authority', Path(__file__).parents[1] / 'scripts' / 'publish_archive_assessment_applicability_authority.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

def invalid(mutator):
    value = copy.deepcopy(build_authority())
    mutator(value)
    with pytest.raises(AuthorityError):
        validate_authority(value)

def test_remove_control_fails_closed(): invalid(lambda a: a['controls'].pop())
```
Pattern: build a valid object, mutate one invariant via a lambda, assert the validator raises. Name tests `test_<violation>_fails_closed`. One-line test bodies are accepted here.

**Function-style with tmp_path (`tests/test_wave2d_applicability_authority.py`):**
```python
def _write_csv(path: Path, rows: list[dict]): ...

def test_pending_does_not_terminate_search(tmp_path):
    first = tmp_path / "first.csv"
    ...
    result = resolve_applicability(tmp_path, "EMS-CTRL-009", "REPO-001", [...])
    assert result["status"] == "PASS"
```
Private `_helper` functions write fixtures; assertions check `status`, `decision`, `source`.

**Data-contract unittest (`tests/test_control_scope_registry.py`):** `setUpClass` loads `registry/control_scope_registry.yaml` relative to `Path(__file__).resolve().parents[1]`, then tests assert counts, uniqueness, and key scope examples.

## Mocking

**Framework:** None (no `unittest.mock`/`monkeypatch` in use).

**Patterns:** Isolate via real temp files (`tmp_path`) and deep-copied real data instead of mocks. Import scripts by `from scripts.<module> import ...` (package) or `importlib.util.spec_from_file_location` when the module reads real repo registries at import time.

**What to Mock:** Prefer not to; inject paths (`ems_root`, candidates list) into functions so tests can pass `tmp_path`.

**What NOT to Mock:** Registries, schemas, catalog (`registry/control_catalog.yaml`) — tests build against the real controlled data so drift is detected.

## Fixtures and Factories

**Test Data:** Generated inline in tests (CSV rows via `_write_csv`); real repo data for authority/registry tests. Built-in `tmp_path` is the only fixture used. Pytest base temp output appears as untracked `.pytest-*` and `.pytest_cache` directories (not committed; should stay untracked).

**Location:** No shared `conftest.py` or fixtures directory.

## Coverage

**Requirements:** None enforced.

## Test Types

**Unit Tests:** Pure functions and validators (`resolve_applicability`, `validate_authority`).

**Integration/Contract Tests:** Registry-shape tests against real `registry/*.yaml|json`; `build_authority()` reads real catalog and `generated/archive-assessment/ems-aa2/approval` closure files, so it requires those artifacts present.

**Script-level checks:** PowerShell `scripts/Test-*.ps1` (e.g. `scripts/Test-NA-Routing.ps1`) throw on failure and print `PASS: ...`; these are run manually, not in CI.

**CI (`.github/workflows/ems-validate.yml`):** Python 3.12; installs `requirements.txt` only (pytest is NOT run in CI); steps: `py_compile` of `scripts/*.py`, YAML parse, JSON parse, secret-pattern grep.

**E2E Tests:** Not used.

## Common Patterns

**Async Testing:** Not applicable.

**Error Testing:**
```python
with pytest.raises(AuthorityError):
    validate_authority(value)
```

**Adding a new test:** Create `tests/test_<subject>.py`; for a new `publish_*` authority, add `build_x`/`validate_x` in the script and write one `_fails_closed` test per invariant (missing/duplicate/unknown ID, absolute path, unapproved provenance, unknown-treated-as-false). Use `tmp_path` for any file output.

---

*Testing analysis: 2026-10-13*
