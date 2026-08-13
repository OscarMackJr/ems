[CmdletBinding()]
param([string]$EMSPath = "C:\temp\standars\ems")

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path

foreach($name in @(
    "Patch-EMSValidateSecretScanMaintenanceSource-v5.ps1",
    "Test-EMSValidateSecretScanRepository-v5.ps1"
)){
    Copy-Item (Join-Path $here $name) (Join-Path $EMSPath "scripts\$name") -Force
}

Write-Host "EMS Validate secret-scan maintenance-source fix v5 tooling installed." -ForegroundColor Green
