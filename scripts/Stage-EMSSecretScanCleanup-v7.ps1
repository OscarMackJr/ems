[CmdletBinding()]
param([string]$EMSPath = "C:\temp\standars\ems")

$ErrorActionPreference = "Stop"

Push-Location $EMSPath
try{
    Write-Host "=== Validate before staging ===" -ForegroundColor Cyan
    & (Join-Path $EMSPath "scripts\Test-EMSSecretScanRepository-v7.ps1") -EMSPath $EMSPath
    if($LASTEXITCODE -ne 0){
        throw "Secret-scan preflight failed."
    }

    Write-Host ""
    Write-Host "=== Stage durable secret-scan state ===" -ForegroundColor Cyan

    git add .github/workflows/ems-validate.yml
    if($LASTEXITCODE -ne 0){ throw "Unable to stage workflow." }

    # Stage deletions of transient maintenance scripts.
    git add -u scripts
    if($LASTEXITCODE -ne 0){ throw "Unable to stage maintenance-script deletions." }

    # Stage only the durable v7 preflight and cleanup scripts.
    git add scripts/Cleanup-EMSSecretScanTransientScripts-v7.ps1
    git add scripts/Test-EMSSecretScanRepository-v7.ps1
    git add scripts/Stage-EMSSecretScanCleanup-v7.ps1

    Write-Host ""
    git status --short

    $stagedStatus = @(git diff --cached --name-status)

    $badTransient = @()

    foreach($entry in $stagedStatus){
        if([string]::IsNullOrWhiteSpace($entry)){ continue }

        $parts = $entry -split "`t"
        $status = $parts[0]
        $path = $parts[-1]

        if($path -match '^scripts/(Patch|Test|Install)-EMSValidateSecretScan'){
            # Deletion is the desired cleanup outcome. Any add/modify/rename/copy
            # means transient maintenance tooling would remain in the baseline.
            if($status -notmatch '^D'){
                $badTransient += "$status`t$path"
            }
        }
    }

    if($badTransient.Count -gt 0){
        throw "Transient secret-scan maintenance scripts remain staged as non-deletions: $($badTransient -join ', ')"
    }

    Write-Host ""
    Write-Host "PASS: durable secret-scan cleanup staged." -ForegroundColor Green
}
finally{
    Pop-Location
}

