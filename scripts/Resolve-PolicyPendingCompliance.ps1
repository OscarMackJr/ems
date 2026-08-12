[CmdletBinding()]
param([string]$Pass45="C:\temp\standars\Pass4_5")
$ErrorActionPreference="Stop"
$py=Join-Path $Pass45 ".venv\Scripts\python.exe"
$eff=Join-Path $Pass45 "generated\collector-acceptance\effective_compliance.csv"
$pq=Join-Path $Pass45 "generated\policy-review\policy_review_queue.csv"
$stage=Join-Path $Pass45 "generated\policy-review\effective_compliance_postpolicy_stage1.csv"
$health=Join-Path $Pass45 "generated\policy-review\repository_health_postpolicy.json"
$final=Join-Path $Pass45 "generated\policy-review\effective_compliance_postpolicy.csv"
$roll=Join-Path $Pass45 "registry\repository_health_rollup.yaml"

& $py (Join-Path $Pass45 "scripts\Apply-PolicyStatusMappings.py") --effective-compliance $eff --policy-queue $pq --out $stage
if($LASTEXITCODE-ne 0){throw "Policy status mapping failed."}

& $py (Join-Path $Pass45 "scripts\Recompute-Health-PostPolicy.py") --compliance $stage --rollup $roll --out $health
if($LASTEXITCODE-ne 0){throw "Post-policy health recompute failed."}

& $py (Join-Path $Pass45 "scripts\Apply-Health-PostPolicy.py") --compliance $stage --health $health --out $final
if($LASTEXITCODE-ne 0){throw "Post-policy health merge failed."}

Write-Host "Post-policy effective compliance: $final" -ForegroundColor Green
