[CmdletBinding()]
param([string]$Pass45="C:\temp\standars\Pass4_5")

$ErrorActionPreference="Stop"
$py=Join-Path $Pass45 ".venv\Scripts\python.exe"
$out=Join-Path $Pass45 "generated\collector-refinement-v2\refined_observations_v2.json"

& $py (Join-Path $Pass45 "scripts\Collect-RefinedEvidence-v2.py") `
 --repositories (Join-Path $Pass45 "registry\repository_registry.yaml") `
 --baseline-template (Join-Path $Pass45 "registry\repository_template_baseline.yaml") `
 --rollup (Join-Path $Pass45 "registry\repository_health_rollup.yaml") `
 --compliance (Join-Path $Pass45 "generated\wave1\repository_control_compliance_wave1.csv") `
 --out $out

if($LASTEXITCODE-ne 0){throw "Collector Refinement v2 failed."}

Write-Host ""
Write-Host "Collector Refinement v2 complete." -ForegroundColor Green
Write-Host "Output: $out"
