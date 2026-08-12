[CmdletBinding()]
param(
    [string]$Pass45 = "C:\temp\standars\Pass4_5",
    [switch]$SkipFreeze
)

$ErrorActionPreference = "Stop"

function Run-Step([string]$Name, [scriptblock]$Action) {
    Write-Host ""
    Write-Host "=== $Name ===" -ForegroundColor Cyan
    & $Action
    if ($LASTEXITCODE -ne 0) {
        throw "$Name failed."
    }
}

Run-Step "Validate populated policy queue" {
    & (Join-Path $Pass45 "scripts\Test-PolicyReviewQueue.ps1") -Pass45 $Pass45
}

Run-Step "Apply policy adjudication decisions" {
    & (Join-Path $Pass45 "scripts\Apply-PolicyDecisions.ps1") -Pass45 $Pass45
}

Run-Step "Resolve policy-pending compliance and recompute repository health" {
    & (Join-Path $Pass45 "scripts\Resolve-PolicyPendingCompliance.ps1") -Pass45 $Pass45
}

Run-Step "Finalize Wave 1 adjudication" {
    & (Join-Path $Pass45 "scripts\Finalize-Wave1Adjudication.ps1") -Pass45 $Pass45
}

if (-not $SkipFreeze) {
    Run-Step "Freeze Wave 1 baseline" {
        & (Join-Path $Pass45 "scripts\Freeze-Wave1Baseline.ps1") -Pass45 $Pass45
    }
}

Write-Host ""
Write-Host "Pass 4.5 Wave 1 policy closeout sequence complete." -ForegroundColor Green
