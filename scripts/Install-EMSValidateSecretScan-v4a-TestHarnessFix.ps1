[CmdletBinding()]
param([string]$EMSPath = "C:\temp\standars\ems")

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path

Copy-Item `
    (Join-Path $here "Test-EMSValidateSecretScanFalsePositives-v4a.ps1") `
    (Join-Path $EMSPath "scripts\Test-EMSValidateSecretScanFalsePositives-v4a.ps1") `
    -Force

$tokens=$null
$parseErrors=$null

[System.Management.Automation.Language.Parser]::ParseFile(
    (Join-Path $EMSPath "scripts\Test-EMSValidateSecretScanFalsePositives-v4a.ps1"),
    [ref]$tokens,
    [ref]$parseErrors
) | Out-Null

if($parseErrors.Count -gt 0){
    $parseErrors | Format-List
    throw "PowerShell parser validation failed."
}

Write-Host "PASS: EMS Validate v4a test-harness fix installed." -ForegroundColor Green
