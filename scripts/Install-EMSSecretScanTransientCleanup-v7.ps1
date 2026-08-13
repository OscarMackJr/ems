[CmdletBinding()]
param([string]$EMSPath = "C:\temp\standars\ems")

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path

foreach($name in @(
    "Cleanup-EMSSecretScanTransientScripts-v7.ps1",
    "Test-EMSSecretScanRepository-v7.ps1",
    "Stage-EMSSecretScanCleanup-v7.ps1"
)){
    Copy-Item (Join-Path $here $name) (Join-Path $EMSPath "scripts\$name") -Force
}

foreach($name in @(
    "Cleanup-EMSSecretScanTransientScripts-v7.ps1",
    "Test-EMSSecretScanRepository-v7.ps1",
    "Stage-EMSSecretScanCleanup-v7.ps1"
)){
    $tokens=$null
    $errs=$null
    [System.Management.Automation.Language.Parser]::ParseFile(
        (Join-Path $EMSPath "scripts\$name"),
        [ref]$tokens,
        [ref]$errs
    ) | Out-Null

    if($errs.Count -gt 0){
        $errs | Format-List
        throw "Parser validation failed: $name"
    }
}

Write-Host "EMS secret-scan transient cleanup v7 tooling installed." -ForegroundColor Green
