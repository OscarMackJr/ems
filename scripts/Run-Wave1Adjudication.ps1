[CmdletBinding()]
param(
    [string]$Pass45 = "C:\temp\standars\Pass4_5"
)

$ErrorActionPreference = "Stop"

$py = Join-Path $Pass45 ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
    throw "Pass4_5 Python environment not found: $py"
}

$compliance = Join-Path $Pass45 "generated\wave1\repository_control_compliance_wave1.csv"
$observations = Join-Path $Pass45 "generated\wave1\wave1_observations.json"
$rules = Join-Path $Pass45 "registry\adjudication_rules.json"
$outdir = Join-Path $Pass45 "generated\adjudication"
$report = Join-Path $Pass45 "generated\reports\wave1_adjudication_validation.json"

foreach ($required in @($compliance,$observations,$rules)) {
    if (-not (Test-Path $required)) {
        throw "Required adjudication input missing: $required"
    }
}

Write-Host "Building Wave 1 adjudication queue..." -ForegroundColor Cyan

& $py `
    (Join-Path $Pass45 "scripts\Build-Wave1AdjudicationQueue.py") `
    --compliance $compliance `
    --observations $observations `
    --rules $rules `
    --outdir $outdir

if ($LASTEXITCODE -ne 0) {
    throw "Failed to build adjudication queue."
}

Write-Host ""
Write-Host "Validating adjudication queue..." -ForegroundColor Cyan

& $py `
    (Join-Path $Pass45 "scripts\Validate-Wave1AdjudicationQueue.py") `
    --queue (Join-Path $outdir "wave1_adjudication_queue.csv") `
    --report $report

if ($LASTEXITCODE -ne 0) {
    throw "Adjudication queue validation failed."
}

Write-Host ""
Write-Host "Wave 1 adjudication queue ready." -ForegroundColor Green
Write-Host "Review/edit:"
Write-Host "  $(Join-Path $outdir 'wave1_adjudication_queue.csv')"
Write-Host ""
Write-Host "After review, populate reviewer_disposition and reviewer_decision, then run:"
Write-Host "  .\scripts\Finalize-Wave1Adjudication.ps1"
