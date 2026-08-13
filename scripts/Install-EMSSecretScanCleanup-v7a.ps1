[CmdletBinding()]
param([string]$EMSPath = "C:\temp\standars\ems")

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path

Copy-Item `
    (Join-Path $here "Patch-StageEMSSecretScanCleanup-v7a.ps1") `
    (Join-Path $EMSPath "scripts\Patch-StageEMSSecretScanCleanup-v7a.ps1") `
    -Force

$tokens=$null
$errors=$null
[System.Management.Automation.Language.Parser]::ParseFile(
    (Join-Path $EMSPath "scripts\Patch-StageEMSSecretScanCleanup-v7a.ps1"),
    [ref]$tokens,
    [ref]$errors
) | Out-Null

if($errors.Count -gt 0){
    $errors | Format-List
    throw "v7a installer parser validation failed."
}

Write-Host "EMS Secret Scan Cleanup v7a staging-guard hotfix installed." -ForegroundColor Green
