# External Integrations

**Analysis Date:** 2026-10-13

## APIs & External Services

**Source control / governance:**
- GitHub (organization `OscarMackJr`, team `twg-global-appdev`) - repo discovery, branch protection, CODEOWNERS, PRs, releases
  - Client: `gh` CLI (`gh api`, `gh pr`, `gh release`, `gh repo`, `gh auth`) and `git` invoked from `scripts/*.ps1`
  - Auth: `gh auth` interactive login (no token env var in repo)
  - Config: `config/github_governance.yaml`, `config/branch_governance.json`

**Document tooling:**
- LibreOffice (`soffice`) - local DOCX/PDF conversion, path via `EMS_SOFFICE`

**Target-repo scanning:**
- Scripts run `npm test` / `npm run` in assessed repositories (onboarding pilot, test-quality, dependency supply chain registries in `registry/`)

## Data Storage

**Databases:**
- None

**File Storage:**
- Local filesystem only: `registry/` (JSON authority records), `registers/`, `evidence/`, `generated/` (transient, mostly untracked), `release/`, `releases/` (zip/pdf/docx artifacts)

**Caching:**
- None

## Authentication & Identity

**Auth Provider:**
- None in-app; relies on GitHub CLI credentials and GitHub code-owner review

## Monitoring & Observability

**Error Tracking:**
- None

**Logs:**
- Script stdout, JSONL evidence logs (`*.jsonl`), Python `logging`

## CI/CD & Deployment

**Hosting:**
- GitHub repository (branches `feature/*`, PR merges into `main`)

**CI Pipeline:**
- GitHub Actions `.github/workflows/ems-validate.yml` on pull_request and push to main: py_compile of `scripts/*.py`, YAML/JSON parse validation, secret-pattern scan (`ghp_`, `github_pat_`, private keys, `AZURE_CLIENT_SECRET`, `AWS_SECRET_ACCESS_KEY`). pytest is not run in CI.

## Environment Configuration

**Required env vars:**
- `EMS_SOFFICE` (optional), `VIRTUAL_ENV` (optional)

**Secrets location:**
- None stored in repo; `.env*` not present

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

---

*Integration audit: 2026-10-13*
