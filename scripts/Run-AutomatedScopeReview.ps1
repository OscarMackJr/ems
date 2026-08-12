[CmdletBinding()]
param(
    [string]$EMSPath="C:\temp\standars\ems"
)

$ErrorActionPreference="Stop"
$py=Join-Path $EMSPath ".venv\Scripts\python.exe"
if(-not(Test-Path $py)){$py="python"}

$q=Join-Path $EMSPath "generated\wave2\scope-adjudication\scope_registry_adjudication_queue.csv"
$model=Join-Path $EMSPath "registry\automated_scope_review_model.json"
$out=Join-Path $EMSPath "generated\wave2\scope-adjudication\scope_registry_adjudication_queue.reviewed.csv"
$exceptions=Join-Path $EMSPath "generated\wave2\scope-adjudication\scope_registry_review_exceptions.csv"

if(-not(Test-Path $q)){
    throw "Scope adjudication queue not found. Run Build-ScopeRegistryAdjudication.ps1 first."
}

& $py (Join-Path $EMSPath "scripts\Review-ScopeRegistry.py") `
    --queue $q `
    --model $model `
    --out $out `
    --exceptions $exceptions

if($LASTEXITCODE-ne 0){throw "Automated scope review failed."}

Write-Host ""
Write-Host "Automated scope review complete." -ForegroundColor Green
Write-Host "Reviewed queue:"
Write-Host "  $out"
Write-Host "Exceptions requiring human review:"
Write-Host "  $exceptions"
