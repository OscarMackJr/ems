[CmdletBinding()]
param([string]$Pass45="C:\temp\standars\Pass4_5")
$ErrorActionPreference="Stop"
$py=Join-Path $Pass45 ".venv\Scripts\python.exe"
$repos=Join-Path $Pass45 "registry\repository_registry.yaml"
$policy=Join-Path $Pass45 "registry\policy_applicability.yaml"
$overrides=Join-Path $Pass45 "registry\repository_applicability_overrides.yaml"
$outdir=Join-Path $Pass45 "generated\policy-applicability"
$json=Join-Path $outdir "policy_applicability.json"
$matrix=Join-Path $outdir "policy_applicability_matrix.csv"

New-Item -ItemType Directory -Path $outdir -Force | Out-Null
gh auth status | Out-Null
if($LASTEXITCODE-ne 0){throw "GitHub CLI authentication required."}

& $py (Join-Path $Pass45 "scripts\Collect-PolicyApplicability.py") --repositories $repos --policy $policy --overrides $overrides --out $json
if($LASTEXITCODE-ne 0){throw "Policy applicability collection failed."}

& $py (Join-Path $Pass45 "scripts\Validate-PolicyApplicability.py") --input $json
if($LASTEXITCODE-ne 0){throw "Policy applicability validation failed."}

& $py (Join-Path $Pass45 "scripts\Export-PolicyApplicabilityMatrix.py") --applicability $json --out $matrix
if($LASTEXITCODE-ne 0){throw "Applicability matrix export failed."}

Write-Host "Policy applicability evaluation complete." -ForegroundColor Green
Write-Host "Review: $matrix"
