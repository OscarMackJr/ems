# Codebase Structure

**Analysis Date:** 2026-10-13

## Directory Layout

```
ems/
├── README.md             # Project overview, baseline tag ems-v0.4.5-wave1
├── requirements.txt      # Runtime deps
├── requirements-dev.txt  # Test deps
├── config/               # Governance config (branch_governance.json, github_governance.yaml)
├── docs/                 # Runbooks and control-requirement docs
├── registry/             # Authoritative catalogs, specs, authorities (~111 files)
│   ├── wave2d/           # Wave 2D sub-specs
│   └── release_baselines/# Baseline registrations
├── schemas/              # JSON Schemas (~43), schemas/contracts/ for Wave 2D contracts
├── scripts/              # ~520 PowerShell/Python stages; collectors/higher-scope/
├── tests/                # unittest/pytest tests (3 files)
├── templates/            # CODEOWNERS.j2
├── evidence/             # Promoted per-control evidence: ems/, organization/, wave2d/
├── generated/            # Generated outputs (gitignored by default): archive-assessment/ems-aa1..aa3, wave2*, governance-proposals
├── registers/            # ai-governance, security-data-governance, wave2c
├── release/              # wave2b-closeout, wave2c (controlled docs, post-closeout)
└── releases/             # Pass4_5_Wave1_Baseline, self-assessment
```

## Directory Purposes

**`registry/`:** Source of truth. Control catalog (`control_catalog.yaml`), scope (`control_scope_registry.yaml`), waves (`evaluation_waves.yaml`), applicability, adjudication (`adjudication_rules.json`, `policy_decisions.json`), repository registry, per-stage specs (`wave2c*_spec.json`, `wave2d_*_spec.json`, `ctrl010_*`, `ctrl018_*`, `hs_*_spec.json`), domain authority sets (`dependency_supply_chain_*`, `release_integrity_*`, `test_quality_*`, `new_repository_onboarding_*`, `real_repository_onboarding_pilot_*`).

**`scripts/`:** Operational code. Key groups: `Run-Wave2D*.ps1` (runners), `Collect-*`, `Evaluate-*`, `Adjudicate-*`, `Apply-*`, `Build-*`, `Promote-*`, `Certify-*`, `Freeze-*`, `Publish-*`, `Install-*` (installer/hotfix), `Show-*`/`Inspect-*` (read-only reporting), `Validate-*`/`validate_*`, `Test-*`.

**`schemas/`:** `<name>.schema.json` matching a registry file name.

**`evidence/`:** `EMS-CTRL-NNN.yaml` per control; `.pre-<change>.bak` snapshots alongside.

**`tests/`:** `test_<subject>.py`.

## Key File Locations

**Entry Points:**
- `scripts/Run-Wave2DBatchPipeline.ps1`: Wave 2D batch orchestrator
- `scripts/publish_archive_assessment_applicability_authority.py`: latest authority publisher

**Configuration:**
- `config/branch_governance.json`, `config/github_governance.yaml`
- `registry/repository_overrides.yaml`

**Core Logic:**
- `scripts/Evaluate-EvidenceSufficiency.py`, `scripts/Adjudicate-Wave2DApplicability.py`, `scripts/Collect-Wave1Evidence.py`

**Testing:**
- `tests/test_control_scope_registry.py`, `tests/test_wave2d_applicability_authority.py`, `tests/test_archive_assessment_applicability_authority.py`

## Naming Conventions

**Files:**
- Older PowerShell/Python scripts: `Verb-Noun.ext` PascalCase with wave tags (`Apply-Wave2B23a-CTRL075Refinement.ps1`, `Run-Wave2DCTRL010Closeout.ps1`)
- Newer Python: `snake_case` `verb_noun.py` (`publish_archive_assessment_applicability_authority.py`, `validate_ctrl010_baseline.py`)
- Registry: `snake_case.json|yaml`; stage specs end `_spec.json`; authority sets end `_authority`, `_traceability`, `_publication_history`, `_publication_certification`
- Schemas: `<registry_name>.schema.json`
- Evidence: `EMS-CTRL-NNN.yaml`
- Backups: `<file>.pre-<reason>.bak` (gitignored via `*.bak`)

**Directories:** lowercase, hyphen or underscore; wave names `wave2d`, `ems-aa3`.

## Where to Add New Code

**New feature/stage:** `scripts/<verb>_<noun>.py` (snake_case, `ROOT = Path(__file__).resolve().parents[1]`); spec in `registry/<name>_spec.json`; schema in `schemas/`; tests in `tests/test_<name>.py`.

**New control-domain authority:** five-file set in `registry/` (requirements/authority, evidence_authority, traceability, publication_history, publication_certification), doc in `docs/<DOMAIN>_REQUIREMENTS.md`, schema in `schemas/`.

**New orchestration:** `scripts/Run-<Name>.ps1` calling Python with `--root`/`--spec`.

**Utilities:** no shared module exists; add under `scripts/` rather than duplicating helpers.

## Special Directories

**`generated/`:** transient outputs; gitignored (publishers still write authority outputs here).
**`.pytest-*/`:** pytest temp dirs, untracked; do not commit.
**`scripts/__pycache__`, `tests/__pycache__`:** generated, ignored.
**`release/`, `releases/`:** committed controlled release artifacts and manifests.
**`.planning/`:** GSD planning docs.

---

*Structure analysis: 2026-10-13*
