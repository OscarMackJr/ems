[CmdletBinding()]
param([string]$Pass45="C:\temp\standars\Pass4_5")
$ErrorActionPreference="Stop"

Write-Host "1. Building grouped policy review queue..." -ForegroundColor Cyan
& (Join-Path $Pass45 "scripts\Build-PolicyReviewQueue.ps1") -Pass45 $Pass45
if($LASTEXITCODE-ne 0){throw "Policy queue build failed."}

Write-Host ""
Write-Host "Wave 1 closeout paused for policy decisions." -ForegroundColor Yellow
Write-Host "Edit:"
Write-Host "  generated\policy-review\policy_review_queue.csv"
Write-Host ""
Write-Host "Populate policy_decision and approved_status_mapping for each control."
Write-Host "Then run, in order:"
Write-Host "  .\scripts\Apply-PolicyDecisions.ps1"
Write-Host "  .\scripts\Resolve-PolicyPendingCompliance.ps1"
Write-Host "  .\scripts\Finalize-Wave1Adjudication.ps1"
Write-Host "  .\scripts\Freeze-Wave1Baseline.ps1"
