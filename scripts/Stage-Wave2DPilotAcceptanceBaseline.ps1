[CmdletBinding()]
param()
$ErrorActionPreference="Stop"
$ems=(Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $ems

$paths=@(
 "registry/wave2d_pilot_acceptance_baseline_spec.json",
 "registry/release_baselines/wave2d_pilot_ctrl009_repo001_baseline.json",
 "schemas/wave2d_pilot_acceptance_baseline.schema.json",
 "scripts/Certify-Wave2DPilotAcceptanceBaseline.py",
 "scripts/Validate-Wave2DPilotAcceptanceBaseline.py",
 "scripts/Run-Wave2DPilotAcceptanceBaselineCertification.ps1",
 "scripts/Show-Wave2DPilotAcceptanceBaseline.ps1",
 "scripts/Stage-Wave2DPilotAcceptanceBaseline.ps1",
 "generated/wave2d/pilot-acceptance/EMS-CTRL-009/REPO-001/acceptance_record.json",
 "generated/wave2d/pilot-acceptance/EMS-CTRL-009/REPO-001/promotion_record.json",
 "evidence/wave2d/EMS-CTRL-009/REPO-001/evidence.json"
)

foreach($p in $paths){
    if(Test-Path $p){git add -- $p}
}

git diff --cached --name-status
Write-Host "PASS: pilot acceptance baseline persistence artifacts staged." -ForegroundColor Green
Write-Host "Generated certification/manifest output remains unstaged unless separately governed." -ForegroundColor DarkGray
