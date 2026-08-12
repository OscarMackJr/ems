[CmdletBinding()]
param([string]$EMSPath="C:\temp\standars\ems")
$ErrorActionPreference="Stop"
$py=Join-Path $EMSPath ".venv\Scripts\python.exe"
if(-not(Test-Path $py)){$py="python"}
$registry=Join-Path $EMSPath "registry\control_scope_registry.yaml"
$matrix=Join-Path $EMSPath "generated\wave2\control_scope_matrix.csv"
$outdir=Join-Path $EMSPath "generated\wave2\scope-adjudication"
& $py (Join-Path $EMSPath "scripts\Build-ScopeRegistryAdjudication.py") --registry $registry --impact-matrix $matrix --outdir $outdir
if($LASTEXITCODE-ne 0){throw "Scope adjudication queue build failed."}
Write-Host "Review: $outdir\scope_registry_adjudication_queue.csv" -ForegroundColor Green
