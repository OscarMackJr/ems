[CmdletBinding()]
param([string]$EMSPath = "C:\temp\standars\ems")

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path

foreach($name in @(
    "Patch-EMSValidateSecretScanSelfMatch-v2.ps1",
    "Test-EMSValidateSecretScanSelfMatchFix-v2.ps1"
)){
    Copy-Item (Join-Path $here $name) (Join-Path $EMSPath "scripts\$name") -Force
}

foreach($name in @(
    "Patch-EMSValidateSecretScanSelfMatch-v2.ps1",
    "Test-EMSValidateSecretScanSelfMatchFix-v2.ps1"
)){
    $tokens=$null
    $errors=$null
    [System.Management.Automation.Language.Parser]::ParseFile(
        (Join-Path $EMSPath "scripts\$name"),
        [ref]$tokens,
        [ref]$errors
    ) | Out-Null

    if($errors.Count -gt 0){
        $errors | Format-List
        throw "PowerShell parser validation failed: $name"
    }
}

Write-Host "EMS Validate secret-scan self-match fix v2 tooling installed." -ForegroundColor Green
