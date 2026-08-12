# Pass 4.3 Runbook

1. Unzip as `C:\temp\standars\Pass4_3`.
2. Run `scripts\Bootstrap-Pass4_3.ps1`.
3. Confirm `gh auth status`.
4. Run `Run-Pass4_3.ps1`.
5. Review discovered repositories.
6. Add governance classifications to `registry\repository_overrides.yaml`.
7. Rerun Pass4_3.
8. Review `generated\observations\github_observations.json`.
9. Review `generated\compliance\repository_control_compliance.csv`.

Do not put PATs or secrets in YAML. GitHub API checks that are unavailable or lack permission remain `NOT_EVALUATED`.
