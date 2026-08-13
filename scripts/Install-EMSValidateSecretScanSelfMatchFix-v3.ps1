[CmdletBinding()]
param([string]$EMSPath = "C:\temp\standars\ems")

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path

foreach($name in @(
    "Patch-EMSValidateSecretScanSelfMatch-v3.ps1",
    "Test-EMSValidateSecretScanSelfMatchFix-v3.ps1"
)){
    Copy-Item (Join-Path $here $name) (Join-Path $EMSPath "scripts\$name") -Force
}

foreach($name in @(
    "Patch-EMSValidateSecretScanSelfMatch-v3.ps1",
    "Test-EMSValidateSecretScanSelfMatchFix-v3.ps1"
)){
    $tokens=$null
    $parseErrors=$null

    [System.Management.Automation.Language.Parser]::ParseFile(
        (Join-Path $EMSPath "scripts\$name"),
        [ref]$tokens,
        [ref]$parseErrors
    ) | Out-Null

    if($parseErrors.Count -gt 0){
        $parseErrors | Format-List
        throw "PowerShell parser validation failed: $name"
    }
}

Write-Host "EMS Validate secret-scan self-match fix v3 tooling installed." -ForegroundColor Green
