# Codebase Concerns

**Analysis Date:** 2026-10-13

Repository is an EMS governance/controls repo: JSON registries (`registry/`, 111 files), schemas, controlled documents (`docs/`), and ~520 one-off PowerShell/Python scripts (`scripts/`, ~321 `.ps1`, ~181 `.py`). Little conventional application code.

## Tech Debt

**Script sprawl of one-off patch/hotfix installers:**
- Issue: `scripts/` holds ~520 wave-specific scripts, many are sequential fixes (`Install-EMSValidateSecretScan*-v2..v6.ps1`, `Apply-Wave2B23a-CTRL075-*Hotfix*.ps1`, `Install-Wave2B*Hotfix*.ps1`, `Assess-Wave2DRepositoryContent-v2.py`, `Collect-RefinedEvidence-v2.py`). Superseded versions are never removed; no index says which is current.
- Files: `scripts/Install-EMSValidateSecretScan*.ps1`, `scripts/Apply-Wave2B23a-CTRL075-*.ps1`, `scripts/Assess-Wave2DRepositoryContent*.py`
- Impact: Executors cannot tell the canonical script; re-running an old one may regress state.
- Fix approach: Add `scripts/README` index, move superseded scripts to `scripts/archive/`, fold fixes into the base script.

**Backup files committed:**
- Issue: 17 `*.bak` files in `scripts/` (e.g. `Certify-Wave2B.py.pre-authoritative-population-hotfix.bak`) and `.github/workflows/ems-validate.yml.pre-secret-scan-v4.bak`.
- Fix approach: Delete; git history preserves them. Add `*.bak` to `.gitignore`.

**Hardcoded Windows absolute path defaults:**
- Issue: Many PowerShell scripts default `$EMSPath="C:\temp\standars\ems"` (e.g. `scripts/Add-AIPlatformRecord.ps1`).
- Impact: Breaks on other machines/CI; not portable to Linux runners.
- Fix approach: Default to `$PSScriptRoot/..` or git toplevel.

**Dense, unformatted Python:**
- Issue: Scripts such as `scripts/Certify-Wave2CPostCloseoutBranch.py` use compressed one-line imports and tight style; `ruff` is in `requirements-dev.txt` but no ruff config detected.
- Fix approach: Add `pyproject.toml` with ruff config and run it across `scripts/`.

**Duplicated logic across scripts:**
- Issue: Subprocess/`gh` wrappers repeated in `scripts/Collect-GitHubEvidence.py`, `scripts/Collect-PolicyApplicability.py`, `scripts/Collect-RefinedEvidence-v2.py`, `scripts/Certify-Wave2CPostCloseoutBranch.py`. No shared module.
- Fix approach: Extract `scripts/lib/` shared helpers.

## Known Bugs

None explicitly tracked (no TODO/FIXME in repo code). Repeated "false positive"/"self-match" fix chains for the secret scan (`scripts/Install-EMSValidateSecretScanSelfMatchFix-v3.ps1`, `...MaintenanceSourceFix-v6.ps1`) indicate the secret scan in `.github/workflows/ems-validate.yml` has been unstable.

## Security Considerations

**Secret scan via regex in workflow:**
- Risk: Iteratively patched regex scanning can miss secrets or be bypassed by maintenance-source exclusions.
- Files: `.github/workflows/ems-validate.yml`, `scripts/Test-EMSValidateSecretScan*.ps1`
- Recommendations: Replace with a maintained scanner (gitleaks/trufflehog); review exclusions.

**Subprocess calls to `gh` / git:**
- Risk: Lists-of-args used (no `shell=True` detected), so injection risk is low; relies on ambient `gh` auth.
- Files: `scripts/Collect-GitHubEvidence.py`, `scripts/Collect-PolicyApplicability.py`

**Unpinned dev dependencies:**
- Risk: `requirements-dev.txt` lists `ruff`, `pytest`, `jsonschema`, `python-docx` without versions (runtime `requirements.txt` is pinned: PyYAML 6.0.3, Jinja2 3.1.6). Supply-chain control docs exist (`docs/DEPENDENCY_SUPPLY_CHAIN_CONTROL_REQUIREMENTS.md`) yet dev deps are not pinned or locked.

## Performance Bottlenecks

**Large generated artifacts:**
- `generated/` is ~18M (gitignored but present locally), `release/` 3.7M, `registry/` 1.2M. Evidence and registry JSON are rewritten wholesale by scripts; diffs are large and review is hard.

## Fragile Areas

**Registry JSON files edited by many scripts:**
- Files: `registry/adjudication_rules.json`, `registry/policy_decisions.json` (currently modified, uncommitted), `registry/*_publication_history.json`, `registry/*_publication_certification.json`
- Why fragile: Cross-referenced authority, traceability, and certification files must stay consistent; hash-based certification breaks on any uncoordinated edit.
- Safe modification: Use the publishing/certification scripts (e.g. `scripts/publish_test_quality_controlled_requirements.py`, `scripts/Certify-Wave2B.py`) rather than hand edits; re-run tests afterward.

**Working tree clutter:**
- Many untracked `.pytest-*` directories (`.pytest-temp`, `.pytest-realpilot-*`, `.pytest-tq-*`, `.pytest-hometown-*`, `.pytest-dsc023-publication`) and ~60 untracked new registry/docs files from in-progress onboarding/supply-chain work. Not in `.gitignore`; risk of accidental commit.
- Fix approach: Add `.pytest-*/` and `.pytest_cache/` to `.gitignore`; commit or stage the new registry authority files deliberately.

**Local `.venv/` inside repo root:** ignored, but tooling that globs the repo (grep, secret scan) must exclude it.

## Scaling Limits

Governance state is flat JSON files in git; growth of wave history (`registry/*_publication_history.json`, `releases/`, `release/`) increases script load time and merge conflicts. No database or index.

## Dependencies at Risk

Not detected beyond unpinned dev deps (above). `python-docx` and `PyYAML` imported ad hoc by scripts; not all imports are declared in `requirements.txt`.

## Missing Critical Features

**Single CI workflow:** only `.github/workflows/ems-validate.yml`; no evidence it runs the pytest suite or ruff, nor schema validation across all `registry/*.json`.

## Test Coverage Gaps

**Scripts almost entirely untested:**
- What's not tested: Only 3 test files exist: `tests/test_archive_assessment_applicability_authority.py`, `tests/test_control_scope_registry.py`, `tests/test_wave2d_applicability_authority.py`. ~500 scripts (collectors, certifiers, adjudicators such as `scripts/Certify-Wave2B.py`, `scripts/Collect-Wave1Evidence.py`) have no unit tests.
- Notably, pytest temp directories named for onboarding/test-quality/supply-chain work (`.pytest-realpilot-*`, `.pytest-tq-*`) suggest tests existed or are being run but corresponding test files are not in `tests/` (untracked or missing).
- Risk: Regressions in certification/adjudication logic go unnoticed.
- Priority: High for certifiers and adjudicators; Medium for collectors.

---

*Concerns audit: 2026-10-13*
