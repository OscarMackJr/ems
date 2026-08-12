[CmdletBinding()]
param([string]$Pass45="C:\temp\standars\Pass4_5")
$ErrorActionPreference="Stop"
$py=Join-Path $Pass45 ".venv\Scripts\python.exe"
$base=Join-Path $Pass45 "generated\wave1\repository_control_compliance_wave1.csv"
$v2=Join-Path $Pass45 "generated\collector-refinement-v2\refined_observations_v2.json"
$roll=Join-Path $Pass45 "registry\repository_health_rollup.yaml"
$stage=Join-Path $Pass45 "generated\collector-acceptance\effective_compliance_stage1.csv"
$health=Join-Path $Pass45 "generated\collector-acceptance\repository_health_v2.json"
$final=Join-Path $Pass45 "generated\collector-acceptance\effective_compliance.csv"

& $py (Join-Path $Pass45 "scripts\Merge-AcceptedCollectors.py") --baseline $base --refined-v2 $v2 --out $stage
if($LASTEXITCODE-ne 0){throw "Collector merge failed."}

& $py (Join-Path $Pass45 "scripts\Recompute-RepositoryHealth.py") --compliance $stage --rollup $roll --out $health
if($LASTEXITCODE-ne 0){throw "Repository health recompute failed."}

& $py (Join-Path $Pass45 "scripts\Apply-RepositoryHealth.py") --compliance $stage --health $health --out $final
if($LASTEXITCODE-ne 0){throw "Repository health merge failed."}

Write-Host "Collector acceptance merge complete." -ForegroundColor Green
Write-Host "Effective compliance: $final"
