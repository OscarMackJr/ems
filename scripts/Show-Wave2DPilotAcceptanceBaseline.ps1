[CmdletBinding()]
param()
$ems=(Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$base=Join-Path $ems "generated\wave2d\pilot-acceptance-baseline\EMS-CTRL-009\REPO-001"
Write-Host "=== Baseline registration ===" -ForegroundColor Cyan
Get-Content "$ems\registry\release_baselines\wave2d_pilot_ctrl009_repo001_baseline.json"
Write-Host "`n=== Baseline certification ===" -ForegroundColor Cyan
Get-Content "$base\baseline_certification.json"
Write-Host "`n=== Baseline manifest ===" -ForegroundColor Cyan
Get-Content "$base\baseline_manifest.json"
