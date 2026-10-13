# Technology Stack

**Analysis Date:** 2026-10-13

## Languages

**Primary:**
- Python 3.12 (CI-pinned in `.github/workflows/ems-validate.yml`) - authority/publication/adjudication scripts in `scripts/*.py`, tests in `tests/`
- PowerShell - ~320 operational scripts in `scripts/*.ps1` (Add-*, Apply-*, Run-*, Install-*, Patch-*, Prepare-* wrappers; resolve Python via `$env:VIRTUAL_ENV\Scripts\python.exe`)

**Secondary:**
- JSON / YAML - registries (`registry/*.json`), schemas (`schemas/*.schema.json`, `schemas/contracts`), config (`config/*.yaml|json`)
- Markdown, DOCX, PDF - controlled documents (`docs/`, `templates/`, `releases/`)

## Runtime

**Environment:**
- CPython 3.12; Windows 11 primary operator platform (PowerShell), ubuntu-latest in CI
- Optional LibreOffice (`soffice`, via `EMS_SOFFICE` env var) for document generation/conversion
- Node/npm referenced only by a few scripts (`npm test`, `npm run`) for scanned target repos

**Package Manager:**
- pip (virtualenv, `.venv`)
- Lockfile: missing (`requirements.txt` partly pinned only)

## Frameworks

**Core:**
- No application framework; script-driven governance pipeline over JSON/YAML registries
- Jinja2 3.1.6 - document/template rendering (`templates/`)
- PyYAML 6.0.3 - YAML registry/config parsing
- jsonschema - validation of registries against `schemas/`
- python-docx - DOCX generation/reading

**Testing:**
- pytest (`tests/`, `requirements-dev.txt`)

**Build/Dev:**
- ruff - linting (`requirements-dev.txt`)
- GitHub Actions workflow `.github/workflows/ems-validate.yml`

## Key Dependencies

**Critical:**
- `jsonschema` (unpinned) - schema validation of authority registries
- `PyYAML==6.0.3`, `Jinja2==3.1.6` (`requirements.txt`)
- `python-docx` (unpinned) - document output

**Infrastructure:**
- Python stdlib heavy: `hashlib`, `json`, `pathlib`, `argparse`, `subprocess`, `dataclasses`, `logging`, `csv`
- `hayes_verify` (imported in scripts; internal module)

## Configuration

**Environment:**
- `EMS_SOFFICE` (LibreOffice path), `VIRTUAL_ENV`, `TEMP`
- Governance config: `config/github_governance.yaml`, `config/branch_governance.json`, `config/license_compliance_policy.draft.yaml`, `config/repository_overrides.example.yaml`
- No `.env` files detected

**Build:**
- `.github/workflows/ems-validate.yml` (py_compile, YAML/JSON parse, secret-pattern grep)
- No pyproject.toml, no `.python-version`

## Platform Requirements

**Development:**
- Python 3.12, `pip install -r requirements.txt -r requirements-dev.txt`, PowerShell, git, GitHub CLI (`gh`), optional LibreOffice

**Production:**
- None; repository is itself the deliverable (controlled releases in `release/`, `releases/`, tagged e.g. `ems-v0.4.5-wave1`)

---

*Stack analysis: 2026-10-13*
