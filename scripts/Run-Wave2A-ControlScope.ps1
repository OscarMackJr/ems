[CmdletBinding()]
param(
    [string]$EMSPath = "C:\temp\standars\ems"
)

$ErrorActionPreference="Stop"
$py = Join-Path $EMSPath ".venv\Scripts\python.exe"
if(-not(Test-Path $py)){ $py = "python" }

$registry = Join-Path $EMSPath "registry\control_scope_registry.yaml"
$taxonomy = Join-Path $EMSPath "registry\control_scope_taxonomy.yaml"
$report = Join-Path $EMSPath "generated\wave2\control_scope_validation.json"

# Prefer the final Wave 1 effective baseline if present in promoted releases.
$candidates = @(
    (Join-Path $EMSPath "generated\policy-review\effective_compliance_postpolicy.csv"),
    (Join-Path $EMSPath "releases\Pass4_5_Wave1_Baseline\generated\policy-review\effective_compliance_postpolicy.csv"),
    (Join-Path $EMSPath "releases\Pass4_5_Wave1_Baseline\generated\collector-acceptance\effective_compliance.csv"),
    (Join-Path $EMSPath "generated\collector-acceptance\effective_compliance.csv")
)
$compliance = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if(-not $compliance){
    throw "No Wave 1 effective compliance input found."
}

Write-Host "Validating Wave 2A scope registry..." -ForegroundColor Cyan
& $py (Join-Path $EMSPath "scripts\Validate-ControlScopeRegistry.py") `
    --registry $registry `
    --taxonomy $taxonomy `
    --report $report
if($LASTEXITCODE-ne 0){ throw "Control scope registry validation failed." }

Write-Host ""
Write-Host "Analyzing Wave 1 scope impact..." -ForegroundColor Cyan
& $py (Join-Path $EMSPath "scripts\Analyze-ControlScopeImpact.py") `
    --registry $registry `
    --compliance $compliance `
    --outdir (Join-Path $EMSPath "generated\wave2")
if($LASTEXITCODE-ne 0){ throw "Control scope impact analysis failed." }

Write-Host ""
Write-Host "Wave 2A complete." -ForegroundColor Green
Write-Host "Review:"
Write-Host "  generated\wave2\control_scope_matrix.csv"
Write-Host "  generated\wave2\scope_impact_analysis.csv"
Write-Host "  generated\wave2\scope_summary.json"
