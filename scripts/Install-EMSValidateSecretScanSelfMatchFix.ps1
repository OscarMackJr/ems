[CmdletBinding()]
param([string]$EMSPath = "C:\temp\standars\ems")

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path

foreach($name in @(
    "Patch-EMSValidateSecretScanSelfMatch.ps1",
    "Test-EMSValidateSecretScanSelfMatchFix.ps1"
)){
    Copy-Item (Join-Path $here $name) (Join-Path $EMSPath "scripts\$name") -Force
}

Write-Host "EMS Validate secret-scan self-match fix tooling installed." -ForegroundColor Green
