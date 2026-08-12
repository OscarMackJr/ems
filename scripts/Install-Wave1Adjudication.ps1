[CmdletBinding()]
param(
    [string]$Pass45 = "C:\temp\standars\Pass4_5"
)
$ErrorActionPreference = "Stop"
$pkg = Split-Path -Parent $PSScriptRoot

Copy-Item (Join-Path $pkg "registry\adjudication_rules.json") `
          (Join-Path $Pass45 "registry\adjudication_rules.json") -Force

foreach ($name in @(
    "Build-Wave1AdjudicationQueue.py",
    "Validate-Wave1AdjudicationQueue.py",
    "Finalize-Wave1Adjudication.py",
    "Run-Wave1Adjudication.ps1",
    "Finalize-Wave1Adjudication.ps1"
)) {
    Copy-Item (Join-Path $PSScriptRoot $name) `
              (Join-Path $Pass45 "scripts\$name") -Force
}

Write-Host "Wave 1 adjudication tooling installed into $Pass45" -ForegroundColor Green
