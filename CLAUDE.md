<!-- GSD:project-start source:PROJECT.md -->
## Project

**EMS Not-Applicable Rule Publication (DEMO3-W1-REQ-001)**

EMS is a spec-driven governance repository: 80 controls (EMS-CTRL-001..080), declarative JSON/YAML registries, and Python/PowerShell scripts that collect evidence, adjudicate applicability, and publish hash-certified authorities. This project updates the EMS archive-assessment applicability authority so that it can answer a formal request from Hayes Verify: for each of 21 named controls, EMS either publishes a machine-readable `not_applicable_rule` with a named authority, or publishes an explicit decision that no rule will be published.

The consumer is Hayes Verify, an external assessor that reads EMS at a pinned commit, treats it as read-only, and will not make applicability decisions itself.

**Core Value:** For every one of the 21 requested controls, EMS publishes an explicit, machine-readable, authority-backed applicability decision that Hayes can cite — so that "EMS decided" is always distinguishable from "EMS has not decided yet".

### Constraints

- **Authority**: Oscar Mack is the approving EMS governance authority — no rule or no-rule decision is published on drafting judgment alone
- **Dual role**: The same person is the EMS approver and the Hayes developer — this must be written into each decision record, not left implicit
- **Drafting independence**: Drafts come from the control catalog definitions alone and are committed before any comparison with a target — prevents rules being shaped to a known result
- **Vocabulary**: Rule conditions use only the eight declared classification fields and the `KNOWN_TRUE` / `KNOWN_FALSE` states — Hayes's resolver requires this, and `UNKNOWN` must never resolve to not-applicable
- **Semantics**: Existing not-applicable semantics hold — explicit controlled rule required; unknown is not false; absence of evidence is not not-applicable
- **Boundary**: Nothing defined in Hayes is adopted into EMS — EMS chooses the shape
- **Publication pattern**: Follow the existing authority pattern (schema, publisher script, certification, traceability, pytest) — hash-based certification breaks on uncoordinated hand edits
- **Scope**: The 21 requested controls only — the other 59 stay undecided
- **Timeline**: Within days — keep the scope tight
- **Working tree**: Unrelated uncommitted work stays untouched and out of this project's commits — the commit Hayes re-pins to must contain only deliberate changes
- **Tech stack**: Python 3.12, `jsonschema`, PyYAML, pytest; Windows-primary with PowerShell wrappers — match the existing code
<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->
## Technology Stack

## Languages
- Python 3.12 (CI-pinned in `.github/workflows/ems-validate.yml`) - authority/publication/adjudication scripts in `scripts/*.py`, tests in `tests/`
- PowerShell - ~320 operational scripts in `scripts/*.ps1` (Add-*, Apply-*, Run-*, Install-*, Patch-*, Prepare-* wrappers; resolve Python via `$env:VIRTUAL_ENV\Scripts\python.exe`)
- JSON / YAML - registries (`registry/*.json`), schemas (`schemas/*.schema.json`, `schemas/contracts`), config (`config/*.yaml|json`)
- Markdown, DOCX, PDF - controlled documents (`docs/`, `templates/`, `releases/`)
## Runtime
- CPython 3.12; Windows 11 primary operator platform (PowerShell), ubuntu-latest in CI
- Optional LibreOffice (`soffice`, via `EMS_SOFFICE` env var) for document generation/conversion
- Node/npm referenced only by a few scripts (`npm test`, `npm run`) for scanned target repos
- pip (virtualenv, `.venv`)
- Lockfile: missing (`requirements.txt` partly pinned only)
## Frameworks
- No application framework; script-driven governance pipeline over JSON/YAML registries
- Jinja2 3.1.6 - document/template rendering (`templates/`)
- PyYAML 6.0.3 - YAML registry/config parsing
- jsonschema - validation of registries against `schemas/`
- python-docx - DOCX generation/reading
- pytest (`tests/`, `requirements-dev.txt`)
- ruff - linting (`requirements-dev.txt`)
- GitHub Actions workflow `.github/workflows/ems-validate.yml`
## Key Dependencies
- `jsonschema` (unpinned) - schema validation of authority registries
- `PyYAML==6.0.3`, `Jinja2==3.1.6` (`requirements.txt`)
- `python-docx` (unpinned) - document output
- Python stdlib heavy: `hashlib`, `json`, `pathlib`, `argparse`, `subprocess`, `dataclasses`, `logging`, `csv`
- `hayes_verify` (imported in scripts; internal module)
## Configuration
- `EMS_SOFFICE` (LibreOffice path), `VIRTUAL_ENV`, `TEMP`
- Governance config: `config/github_governance.yaml`, `config/branch_governance.json`, `config/license_compliance_policy.draft.yaml`, `config/repository_overrides.example.yaml`
- No `.env` files detected
- `.github/workflows/ems-validate.yml` (py_compile, YAML/JSON parse, secret-pattern grep)
- No pyproject.toml, no `.python-version`
## Platform Requirements
- Python 3.12, `pip install -r requirements.txt -r requirements-dev.txt`, PowerShell, git, GitHub CLI (`gh`), optional LibreOffice
- None; repository is itself the deliverable (controlled releases in `release/`, `releases/`, tagged e.g. `ems-v0.4.5-wave1`)
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

## Naming Patterns
- Two coexisting styles. Prefer `snake_case.py` verb-first for new work: `scripts/publish_archive_assessment_applicability_authority.py`, `scripts/certify_wave2d_batch_baseline.py`, `scripts/wave2d_applicability_authority.py` (library module).
- Legacy Wave scripts use `Verb-PascalCase.py` (`scripts/Adjudicate-Wave2DControls.py`, `scripts/Apply-PolicyApplicability.py`); do not add new ones in this style.
- Versioned fix iterations append `-v2`, `-v4a`, etc. (`scripts/Assess-Wave2DRepositoryContent-v2.py`).
## Code Style
- `from __future__ import annotations` at the top of newer scripts; stdlib imports, blank line, third-party (`jsonschema`, `yaml`).
- Type hints on function signatures (`def digest(p: Path) -> str`), built-in generics (`list[dict]`).
- Use `pathlib.Path` everywhere, `encoding='utf-8'` explicit (`utf-8-sig` when reading CSVs that may carry a BOM).
- Newer `publish_*` scripts use single quotes and compact one-line helpers (`def load(p): return json.loads(...)`); library modules (`scripts/wave2d_applicability_authority.py`) use double quotes, 4-space indent and multi-line formatting. Match the style of the file being edited.
- Deterministic JSON output: `json.dumps(value, indent=2, sort_keys=True) + '\n'`.
- Hashing: SHA-256 via `hashlib` (`digest()`/`sha256()` helpers) for lineage/manifests.
- Timestamps: `datetime.now(UTC)`, ISO-8601 with `Z` suffix.
- Start with `[CmdletBinding()]` and a `param(...)` block; `[Parameter(Mandatory=$true)]` for required inputs.
- Root path parameters default to hard-coded Windows paths (`$EMSPath="C:\temp\standars\ems"`, `$Pass45="C:\temp\standars\Pass4_5"`); build paths with `Join-Path`.
- Guard with `Test-Path` + `throw "..."`.
- Output with `Write-Host "PASS: ..." -ForegroundColor Green`; failure via `throw`.
- Registers are CSV appended with `Export-Csv -Append -NoTypeInformation`; duplicate-ID check before append.
## Import Organization
## Error Handling
- Fail closed. Validators raise a domain exception (`AuthorityError`) on any violated invariant (wrong control count, duplicate/unknown control, absolute path, unapproved decision ID, unknown treated as false, implicit N/A). Unknown/missing evidence resolves to `UNKNOWN`/pending, never to `NOT_APPLICABLE` or `PASS`.
- Resolver functions return status dicts instead of raising for expected data states (`resolve_applicability` returns `{"status","decision","source"}` and records each inspected source with `MISSING`/`NO_MATCH`).
- Schema validation with `jsonschema.Draft202012Validator(load(SCHEMA)).validate(obj)`.
- CLI scripts print a JSON result (`{'status':'PASS', ...sha256}`) or `PASS`; failure is an uncaught exception / non-zero exit. ~90 scripts use `sys.exit`/`SystemExit`; ~174 use `argparse`.
- Registry JSON must not contain absolute paths (enforced by `contains_absolute`); store repo-relative paths with forward slashes, normalize with `rel.replace("\\", "/")`.
## Logging
## Comments
- Sparse. Code is self-documenting through names; no docstrings or JSDoc/TSDoc in sampled scripts. Rationale lives in `docs/*.md` requirement documents and registry JSON, not in code comments.
## Function Design
- Small single-purpose helpers (`load`, `dump`, `digest`, `contains_absolute`), then `build_*` (pure construction) and `validate_*` (raises) pairs, then `main()` with `argparse` and `if __name__ == '__main__'`.
- Pass `Path` and plain dicts/lists; return dicts. Separate `build_x()` from `validate_x(x)` so tests can mutate a built object and assert validation fails.
## Module Design
## Data Artifact Conventions
- Authoritative data lives in `registry/` (JSON with matching `schemas/*.schema.json`, plus YAML such as `registry/control_catalog.yaml`, `registry/control_scope_registry.yaml`). Each new authority commonly comes with `docs/<NAME>.md`, `registry/<name>.json`, a schema, `scripts/publish_<name>.py`, and a test in `tests/`.
- Generated outputs go to `generated/` (gitignored); `.bak` files and pytest temp dirs (`.pytest-*`) are local and untracked.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

## System Overview
```text
```
## Component Responsibilities
| Component | Responsibility | File |
|-----------|----------------|------|
| Control catalog | 80 controls (EMS-CTRL-001..080) definitions | `registry/control_catalog.yaml` |
| Scope registry | Scope per control (REPOSITORY/EMS/ORGANIZATION) | `registry/control_scope_registry.yaml` |
| Waves plan | Wave/control rollout | `registry/evaluation_waves.yaml` |
| Applicability | Policy applicability, overrides, profiles | `registry/policy_applicability.yaml`, `registry/applicability_profiles.yaml`, `registry/repository_applicability_overrides.yaml` |
| Adjudication | Rules and decisions routing (PASS/FAIL/NA) | `registry/adjudication_rules.json`, `registry/policy_decisions.json` |
| Repository registry | Target repos (e.g. REPO-001) | `registry/repository_registry.yaml` |
| Evidence collectors | Gather GitHub / repo / higher-scope evidence | `scripts/Collect-*.py`, `scripts/collectors/higher-scope/` |
| Evaluators | Sufficiency, coverage, applicability | `scripts/Evaluate-*.py` |
| Wave 2D pipeline | Batch qualify/certify/promote/apply | `scripts/Run-Wave2DBatchPipeline.ps1`, `scripts/*wave2d_batch*.py` |
| Per-control lifecycle | prepare/capture/validate/promote/certify (CTRL-010, CTRL-018) | `scripts/*_ctrl010_*.py`, `scripts/*ctrl018*.py` |
| Control-requirement authorities | Dependency supply chain, release integrity, test quality, onboarding | `registry/<domain>_*.json`, `docs/*_REQUIREMENTS.md` |
| Archive assessment (AA1-AA3) | Applicability authority publish | `scripts/publish_archive_assessment_applicability_authority.py`, `registry/archive_assessment_applicability_authority.json` |
| Tests | Registry and authority validation | `tests/` |
## Pattern Overview
- Scripts are single-purpose stages in a waved program (Wave1, 2B, 2C, 2D, then domain authorities); each stage reads a JSON `*_spec.json` in `registry/` and writes artifacts.
- State is files: registry JSON/YAML is authoritative; outputs carry SHA-256 hashes and certification records (status `PASS`/`FAIL`, `baseline_state: AUTHORITATIVE|BLOCKED`).
- Pipeline phases: collect -> qualify -> adjudicate (human review where needed) -> freeze -> promote -> certify -> publish baseline.
- Self-governing: changes to controls/policy/schemas are control-plane changes.
- Mixed languages: PowerShell for orchestration/git/PR steps, Python for logic.
## Layers
- Purpose: Declarative authority and per-stage specs
- Location: `registry/`, `config/`, `schemas/`
- Contains: YAML catalogs, JSON authorities, `*_spec.json`, publication history/certification/traceability files
- Depends on: nothing
- Used by: all scripts
- Purpose: Transform registry + evidence into outputs
- Location: `scripts/`
- Contains: ~520 scripts (verbs: Run, Install, Show, Validate, Test, Apply, Promote, Build, Stage, Qualify, Patch, Freeze, Collect, Publish)
- Depends on: registry, schemas (`jsonschema`, `yaml`)
- Used by: operators, wrapper scripts
- Location: `evidence/{ems,organization,wave2d}/`, `generated/`, `registers/`, `release/`, `releases/`
- Contains: per-control evidence YAML (`EMS-CTRL-NNN.yaml`), frozen release manifests
## Data Flow
### Primary Evidence Path
### Authority publication flow (newer domain work)
## Key Abstractions
## Entry Points
## Architectural Constraints
- **Threading:** Single-process, synchronous scripts.
- **Global state:** Module-level argparse execution in older scripts (not importable); registry files are shared mutable state.
- **Circular imports:** Not applicable (scripts are standalone; no shared package beyond `scripts/__init__.py`).
- **Windows-centric:** PowerShell wrappers; paths normalized via `rel.replace("\\","/")`.
- **Encoding:** read JSON with `utf-8-sig` (older) / `utf-8` (newer).
## Anti-Patterns
### Versioned hotfix script proliferation
### Duplicated helper code
## Error Handling
## Cross-Cutting Concerns
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
