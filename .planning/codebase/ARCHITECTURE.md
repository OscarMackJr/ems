<!-- refreshed: 2026-10-13 -->
# Architecture

**Analysis Date:** 2026-10-13

## System Overview

```text
┌─────────────────────────────────────────────────────────────┐
│             Orchestration (PowerShell wrappers)              │
│  `scripts/Run-*.ps1` `Install-*.ps1` `Apply-*.ps1`           │
│  `Publish-*.ps1` `Prepare-*.ps1` `Stage-*.ps1`               │
└────────┬──────────────────┬──────────────────┬──────────────┘
         │ --spec / --root   │                  │
         ▼                  ▼                  ▼
┌──────────────────┬──────────────────┬───────────────────────┐
│ Collect / Discover│ Evaluate / Adjudicate │ Promote / Certify / Freeze │
│ `scripts/Collect-*.py` │ `scripts/Evaluate-*.py` │ `scripts/Promote-*.py` │
│ `scripts/collectors/higher-scope/` │ `scripts/Adjudicate-*.py` │ `scripts/Certify-*.py` `Freeze-*.py` │
└────────┬─────────┴────────┬─────────┴──────────┬────────────┘
         ▼                  ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│   Registry / spec layer (declarative JSON+YAML)              │
│   `registry/*.yaml|json`, `schemas/*.schema.json`            │
└─────────────────────────────────────────────────────────────┘
         ▼
┌─────────────────────────────────────────────────────────────┐
│ Evidence + outputs: `evidence/`, `generated/`, `registers/`, │
│ `release/`, `releases/` (hash-certified manifests)           │
└─────────────────────────────────────────────────────────────┘
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

**Overall:** Spec-driven, file-based governance pipeline ("governed evidence ledger"); no server or application runtime.

**Key Characteristics:**
- Scripts are single-purpose stages in a waved program (Wave1, 2B, 2C, 2D, then domain authorities); each stage reads a JSON `*_spec.json` in `registry/` and writes artifacts.
- State is files: registry JSON/YAML is authoritative; outputs carry SHA-256 hashes and certification records (status `PASS`/`FAIL`, `baseline_state: AUTHORITATIVE|BLOCKED`).
- Pipeline phases: collect -> qualify -> adjudicate (human review where needed) -> freeze -> promote -> certify -> publish baseline.
- Self-governing: changes to controls/policy/schemas are control-plane changes.
- Mixed languages: PowerShell for orchestration/git/PR steps, Python for logic.

## Layers

**Registry/Spec layer:**
- Purpose: Declarative authority and per-stage specs
- Location: `registry/`, `config/`, `schemas/`
- Contains: YAML catalogs, JSON authorities, `*_spec.json`, publication history/certification/traceability files
- Depends on: nothing
- Used by: all scripts

**Stage scripts layer:**
- Purpose: Transform registry + evidence into outputs
- Location: `scripts/`
- Contains: ~520 scripts (verbs: Run, Install, Show, Validate, Test, Apply, Promote, Build, Stage, Qualify, Patch, Freeze, Collect, Publish)
- Depends on: registry, schemas (`jsonschema`, `yaml`)
- Used by: operators, wrapper scripts

**Output/evidence layer:**
- Location: `evidence/{ems,organization,wave2d}/`, `generated/`, `registers/`, `release/`, `releases/`
- Contains: per-control evidence YAML (`EMS-CTRL-NNN.yaml`), frozen release manifests

## Data Flow

### Primary Evidence Path

1. Collect evidence (`scripts/Collect-Wave1Evidence.py`, `scripts/Collect-GitHubEvidence.py`, higher-scope `scripts/collectors/higher-scope/Collect-HS-*.ps1`)
2. Evaluate sufficiency/applicability (`scripts/Evaluate-EvidenceSufficiency.py`, `scripts/Evaluate-RepositoryApplicability.py`)
3. Adjudicate (`scripts/Adjudicate-Wave2DApplicability.py` reads CSV matrix + rules per spec; human review via `Prepare-Wave2DAssistedHumanReview.py`)
4. Promote evidence into `evidence/` (`scripts/Promote-*.py`), certify and freeze (`Certify-*.py`, `Freeze-*.py`), publish baseline (`Publish-*.ps1`)

### Authority publication flow (newer domain work)

1. Build authority JSON in `registry/` validated against `schemas/<name>.schema.json`
2. Publisher script (`scripts/publish_*.py`) computes SHA-256 digests, rejects absolute paths, dumps sorted JSON, writes to `generated/<area>/`
3. Tests in `tests/` assert authority invariants

**State Management:** git-tracked files; `.bak` snapshots (`*.pre-<fix>.bak`) before mutating hotfixes.

## Key Abstractions

**Spec file:** `registry/wave2d_*_spec.json`, `registry/ctrl010_*_spec.json` - parametrizes a script's inputs/outputs (e.g. `matrix_file`, `rules_output`, `decisions_output`).
**Authority:** `registry/*_authority.json` / `*_requirements.json` + `*_traceability.json` + `*_publication_history.json` + `*_publication_certification.json` - five-file set per control domain.
**Evidence envelope/contracts:** `schemas/contracts/wave2d_*.schema.json`, `schemas/hs_*_envelope.schema.json`.
**Wave:** `registry/evaluation_waves.yaml`.

## Entry Points

**PowerShell runners:** `scripts/Run-Wave2DBatchPipeline.ps1`, `Run-Wave2D*.ps1`, `Run-Pass*` - operator-invoked; call Python with `--root`/`--ems-root` and `--spec`.
**Python stages:** each script is `argparse` main-at-module-level (older) or `ROOT = Path(__file__).resolve().parents[1]` (newer `publish_*.py`).
**Tests:** `python -m pytest tests/` (`requirements-dev.txt`).

## Architectural Constraints

- **Threading:** Single-process, synchronous scripts.
- **Global state:** Module-level argparse execution in older scripts (not importable); registry files are shared mutable state.
- **Circular imports:** Not applicable (scripts are standalone; no shared package beyond `scripts/__init__.py`).
- **Windows-centric:** PowerShell wrappers; paths normalized via `rel.replace("\\","/")`.
- **Encoding:** read JSON with `utf-8-sig` (older) / `utf-8` (newer).

## Anti-Patterns

### Versioned hotfix script proliferation

**What happens:** Fixes ship as new scripts (`Install-EMSValidateSecretScan...-v4/v5/v6/v7`, `Apply-Wave2B23a-CTRL075-Hotfix*.ps1`) plus `.bak` copies rather than editing the original.
**Why it's wrong:** Hard to know which script is current; `scripts/` has 500+ files.
**Do this instead:** Edit the canonical script and add a test in `tests/`; follow the newer `publish_*.py` pattern.

### Duplicated helper code

**What happens:** `sha`, `load`, `rp` helpers redefined in every script (`scripts/validate_ctrl010_baseline.py`).
**Do this instead:** Share helpers in a module under `scripts/`.

## Error Handling

**Strategy:** Fail-closed validation. Validators accumulate `errors`, print JSON `{"status": "PASS"|"FAIL", ...}` and exit 0/1. Newer code raises custom `AuthorityError(ValueError)`.

## Cross-Cutting Concerns

**Logging:** stdout JSON/text; no logging framework.
**Validation:** `jsonschema` against `schemas/`; SHA-256 hash chains.
**Authentication:** GitHub access in collectors (token via environment; not stored in repo).

---

*Architecture analysis: 2026-10-13*
