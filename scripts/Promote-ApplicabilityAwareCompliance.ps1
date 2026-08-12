[CmdletBinding()]
param([string]$Pass45 = "C:\temp\standars\Pass4_5")

$ErrorActionPreference = "Stop"

$source = Join-Path $Pass45 "generated\policy-applicability\effective_compliance_with_applicability.csv"
$target = Join-Path $Pass45 "generated\collector-acceptance\effective_compliance.csv"

if(-not(Test-Path $source)){
    throw "Applicability-aware compliance file not found: $source"
}
if(Test-Path $target){
    Copy-Item $target "$target.pre-policy-applicability.bak" -Force
}

Copy-Item $source $target -Force

Write-Host "Applicability-aware compliance promoted to effective compliance input." -ForegroundColor Green
Write-Host "Source: $source"
Write-Host "Target: $target"
