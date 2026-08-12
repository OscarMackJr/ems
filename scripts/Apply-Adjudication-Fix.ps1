[CmdletBinding()]
param(
    [string]$Pass45 = "C:\temp\standars\Pass4_5"
)

$ErrorActionPreference = "Stop"

$rules = Join-Path $Pass45 "registry\adjudication_rules.json"
$builder = Join-Path $Pass45 "scripts\Build-Wave1AdjudicationQueue.py"

if (-not (Test-Path $rules)) {
    throw "Rules file not found: $rules"
}
if (-not (Test-Path $builder)) {
    throw "Builder script not found: $builder"
}

Write-Host "Patching adjudication rules..." -ForegroundColor Cyan

$r = Get-Content $rules -Raw | ConvertFrom-Json

# Generic WARNING outcomes should be reviewed as collector/evidence interpretation
# rather than introducing an undefined generic REVIEW state.
$r.default_dispositions.WARNING = "COLLECTOR_REVIEW"

$r | ConvertTo-Json -Depth 20 | Set-Content $rules -Encoding UTF8

Write-Host "Patching builder fallback..." -ForegroundColor Cyan

$text = Get-Content $builder -Raw

$text = $text.Replace(
    'default_disp.get(status, "REVIEW")',
    'default_disp.get(status, "COLLECTOR_REVIEW")'
)

Set-Content $builder $text -Encoding UTF8

Write-Host "Removing stale adjudication queue outputs..." -ForegroundColor Cyan

$adjudicationDir = Join-Path $Pass45 "generated\adjudication"
if (Test-Path $adjudicationDir) {
    Get-ChildItem $adjudicationDir -Filter "wave1_adjudication_*" -ErrorAction SilentlyContinue |
        Remove-Item -Force
}

Write-Host ""
Write-Host "Adjudication fix applied." -ForegroundColor Green
Write-Host "Rerun:"
Write-Host "  .\scripts\Run-Wave1Adjudication.ps1"
