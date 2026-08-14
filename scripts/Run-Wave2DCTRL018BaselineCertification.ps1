[CmdletBinding()]
param()
$ErrorActionPreference="Stop"
function Fail([string]$m){throw "EMS CTRL-018 BASELINE BLOCKED: $m"}

$ems=(Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$py=Join-Path $ems ".venv\Scripts\python.exe"
$spec=Join-Path $ems "registry\ctrl018_baseline_spec.json"
$schema=Join-Path $ems "schemas\ctrl018_baseline.schema.json"
$cert=Join-Path $ems "scripts\certify_ctrl018_baseline.py"
$val=Join-Path $ems "scripts\validate_ctrl018_baseline.py"

& $py -m ruff check $cert $val
if($LASTEXITCODE){Fail "Ruff failed"}
& $py $cert --ems-root $ems --spec $spec --schema $schema
if($LASTEXITCODE){Fail "certification failed"}
& $py $val --ems-root $ems --spec $spec
if($LASTEXITCODE){Fail "validation failed"}

Write-Host "PASS: CTRL-018 authoritative pilot baseline certified." -ForegroundColor Green
