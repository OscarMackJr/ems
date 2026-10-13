# Coding Conventions

**Analysis Date:** 2026-10-13

The repo is a governance/control-evidence repository (EMS). Code is mostly ~320 PowerShell scripts (`scripts/*.ps1`) and ~180 Python scripts (`scripts/*.py`) that read/write registries (`registry/*.json|yaml|csv`), registers (`registers/`), and generated output (`generated/`). No project-wide formatter config is committed (no `pyproject.toml`, `.prettierrc`, `.editorconfig`); `ruff` is listed in `requirements-dev.txt` and a `.ruff_cache/` exists, so ruff is run ad hoc with defaults.

## Naming Patterns

**Files (Python):**
- Two coexisting styles. Prefer `snake_case.py` verb-first for new work: `scripts/publish_archive_assessment_applicability_authority.py`, `scripts/certify_wave2d_batch_baseline.py`, `scripts/wave2d_applicability_authority.py` (library module).
- Legacy Wave scripts use `Verb-PascalCase.py` (`scripts/Adjudicate-Wave2DControls.py`, `scripts/Apply-PolicyApplicability.py`); do not add new ones in this style.
- Versioned fix iterations append `-v2`, `-v4a`, etc. (`scripts/Assess-Wave2DRepositoryContent-v2.py`).

**Files (PowerShell):** `Verb-Noun[-Qualifier].ps1` with approved-ish verbs; most frequent prefixes: `Run-`, `Install-`, `Show-`, `Validate-`, `Test-`, `Apply-`, `Promote-`, `Build-`, `Stage-`, `Qualify-`, `Add-...Record`. Wave identifiers embedded: `Wave2B1`, `Wave2D`.

**Python functions/variables:** `snake_case`; module constants `UPPER_SNAKE` (`ROOT`, `REGISTRY`, `FINAL_APPLICABILITY_STATES`, `CLASSIFICATION_FIELDS`). Path constants derived from `ROOT = Path(__file__).resolve().parents[1]`.

**Types/classes:** `PascalCase`; domain exceptions are `<Name>Error(ValueError)` (e.g. `AuthorityError` in `scripts/publish_archive_assessment_applicability_authority.py`).

**Control/ID identifiers:** `EMS-CTRL-NNN` (80 controls), governance decisions `AA1-GOV-NNN`, targets `REPO-NNN`, record IDs as strings. Status enums are UPPER_SNAKE strings: `PASS`, `FAIL`, `APPLICABLE`, `NOT_APPLICABLE`, `PENDING_APPLICABILITY`, `UNKNOWN`, `MISSING`, `NO_MATCH`.

**JSON keys / CSV columns:** `snake_case` (`control_id`, `target_id`, `applicability_state`).

## Code Style

**Python:**
- `from __future__ import annotations` at the top of newer scripts; stdlib imports, blank line, third-party (`jsonschema`, `yaml`).
- Type hints on function signatures (`def digest(p: Path) -> str`), built-in generics (`list[dict]`).
- Use `pathlib.Path` everywhere, `encoding='utf-8'` explicit (`utf-8-sig` when reading CSVs that may carry a BOM).
- Newer `publish_*` scripts use single quotes and compact one-line helpers (`def load(p): return json.loads(...)`); library modules (`scripts/wave2d_applicability_authority.py`) use double quotes, 4-space indent and multi-line formatting. Match the style of the file being edited.
- Deterministic JSON output: `json.dumps(value, indent=2, sort_keys=True) + '\n'`.
- Hashing: SHA-256 via `hashlib` (`digest()`/`sha256()` helpers) for lineage/manifests.
- Timestamps: `datetime.now(UTC)`, ISO-8601 with `Z` suffix.

**PowerShell:**
- Start with `[CmdletBinding()]` and a `param(...)` block; `[Parameter(Mandatory=$true)]` for required inputs.
- Root path parameters default to hard-coded Windows paths (`$EMSPath="C:\temp\standars\ems"`, `$Pass45="C:\temp\standars\Pass4_5"`); build paths with `Join-Path`.
- Guard with `Test-Path` + `throw "..."`.
- Output with `Write-Host "PASS: ..." -ForegroundColor Green`; failure via `throw`.
- Registers are CSV appended with `Export-Csv -Append -NoTypeInformation`; duplicate-ID check before append.

**Linting:** `ruff` (default rules) available; CI does not run it. CI (`.github/workflows/ems-validate.yml`) runs `py_compile` on every `scripts/*.py`, YAML/JSON parse validation of `registry`, `config`, `schemas`, and a regex secret scan (excludes `*.md`). Never embed token-like strings in scripts.

## Import Organization

1. `from __future__ import annotations`
2. stdlib (`argparse`, `hashlib`, `json`, `csv`, `datetime`, `pathlib`)
3. third-party (`jsonschema`, `yaml`, `jinja2`, `docx`)
4. Tests importing sibling scripts use `from scripts.<module> import ...` (package via `scripts/__init__.py`) or `importlib.util.spec_from_file_location` for scripts not meant as modules.

**Path Aliases:** None.

## Error Handling

- Fail closed. Validators raise a domain exception (`AuthorityError`) on any violated invariant (wrong control count, duplicate/unknown control, absolute path, unapproved decision ID, unknown treated as false, implicit N/A). Unknown/missing evidence resolves to `UNKNOWN`/pending, never to `NOT_APPLICABLE` or `PASS`.
- Resolver functions return status dicts instead of raising for expected data states (`resolve_applicability` returns `{"status","decision","source"}` and records each inspected source with `MISSING`/`NO_MATCH`).
- Schema validation with `jsonschema.Draft202012Validator(load(SCHEMA)).validate(obj)`.
- CLI scripts print a JSON result (`{'status':'PASS', ...sha256}`) or `PASS`; failure is an uncaught exception / non-zero exit. ~90 scripts use `sys.exit`/`SystemExit`; ~174 use `argparse`.
- Registry JSON must not contain absolute paths (enforced by `contains_absolute`); store repo-relative paths with forward slashes, normalize with `rel.replace("\\", "/")`.

## Logging

**Framework:** None (no `logging` module). Python uses `print`, PowerShell uses `Write-Host`. Machine-readable outcomes are written to `generated/**` JSON/CSV manifests rather than logs.

## Comments

- Sparse. Code is self-documenting through names; no docstrings or JSDoc/TSDoc in sampled scripts. Rationale lives in `docs/*.md` requirement documents and registry JSON, not in code comments.

## Function Design

- Small single-purpose helpers (`load`, `dump`, `digest`, `contains_absolute`), then `build_*` (pure construction) and `validate_*` (raises) pairs, then `main()` with `argparse` and `if __name__ == '__main__'`.
- Pass `Path` and plain dicts/lists; return dicts. Separate `build_x()` from `validate_x(x)` so tests can mutate a built object and assert validation fails.

## Module Design

**Exports:** Plain module-level functions; no `__all__`. `scripts/__init__.py` exists so `scripts` is importable.

**Barrel Files:** None.

## Data Artifact Conventions

- Authoritative data lives in `registry/` (JSON with matching `schemas/*.schema.json`, plus YAML such as `registry/control_catalog.yaml`, `registry/control_scope_registry.yaml`). Each new authority commonly comes with `docs/<NAME>.md`, `registry/<name>.json`, a schema, `scripts/publish_<name>.py`, and a test in `tests/`.
- Generated outputs go to `generated/` (gitignored); `.bak` files and pytest temp dirs (`.pytest-*`) are local and untracked.

---

*Convention analysis: 2026-10-13*
