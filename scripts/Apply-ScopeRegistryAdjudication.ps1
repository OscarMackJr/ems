[CmdletBinding()]
param([string]$EMSPath="C:\temp\standars\ems")
$ErrorActionPreference="Stop"
$py=Join-Path $EMSPath ".venv\Scripts\python.exe"
if(-not(Test-Path $py)){$py="python"}

& (Join-Path $EMSPath "scripts\Validate-ScopeRegistryAdjudication.ps1") -EMSPath $EMSPath -RequireComplete

$q=Join-Path $EMSPath "generated\wave2\scope-adjudication\scope_registry_adjudication_queue.csv"
$registry=Join-Path $EMSPath "registry\control_scope_registry.yaml"
$report=Join-Path $EMSPath "generated\wave2\scope-adjudication\scope_registry_adjudication_apply.json"

& $py (Join-Path $EMSPath "scripts\Apply-ScopeRegistryAdjudication.py") --queue $q --registry $registry --out-report $report
if($LASTEXITCODE-ne 0){throw "Applying scope adjudication failed."}

Write-Host ""
Write-Host "Re-running Wave 2A impact analysis with approved scopes..." -ForegroundColor Cyan
& (Join-Path $EMSPath "scripts\Run-Wave2A-ControlScope.ps1") -EMSPath $EMSPath
if($LASTEXITCODE-ne 0){throw "Post-adjudication Wave 2A rerun failed."}

Write-Host "Scope registry adjudication applied." -ForegroundColor Green
