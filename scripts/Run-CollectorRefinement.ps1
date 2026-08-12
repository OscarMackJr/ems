[CmdletBinding()]
param([string]$Pass45="C:\temp\standars\Pass4_5")
$ErrorActionPreference="Stop"
$py=Join-Path $Pass45 ".venv\Scripts\python.exe"
$out=Join-Path $Pass45 "generated\collector-refinement\refined_observations.json"
& $py (Join-Path $Pass45 "scripts\Collect-RefinedEvidence.py") `
 --repositories (Join-Path $Pass45 "registry\repository_registry.yaml") `
 --baseline-template (Join-Path $Pass45 "registry\repository_template_baseline.yaml") `
 --rollup (Join-Path $Pass45 "registry\repository_health_rollup.yaml") `
 --compliance (Join-Path $Pass45 "generated\wave1\repository_control_compliance_wave1.csv") `
 --out $out
if($LASTEXITCODE-ne 0){throw "Refined collector run failed."}
Write-Host "Refined collector output: $out" -ForegroundColor Green
