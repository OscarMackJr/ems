[CmdletBinding()]
param()
$ErrorActionPreference="Stop"
function Fail([string]$m){throw "EMS PILOT BASELINE CERTIFICATION BLOCKED: $m"}

$ems=(Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$py=Join-Path $ems ".venv\Scripts\python.exe"
$spec=Join-Path $ems "registry\wave2d_pilot_acceptance_baseline_spec.json"
$schema=Join-Path $ems "schemas\wave2d_pilot_acceptance_baseline.schema.json"
$pytestTemp=Join-Path $ems ".pytest-temp"

$certifier=Join-Path $ems "scripts\certify_wave2d_pilot_acceptance_baseline.py"
$validator=Join-Path $ems "scripts\validate_wave2d_pilot_acceptance_baseline.py"

if(-not(Test-Path $py)){Fail "EMS venv Python missing: $py"}
if(-not(Test-Path $certifier)){Fail "certifier missing: $certifier"}
if(-not(Test-Path $validator)){Fail "validator missing: $validator"}

Write-Host "=== Scoped Ruff preflight ===" -ForegroundColor Cyan
& $py -m ruff check $certifier $validator
if($LASTEXITCODE){Fail "Scoped Ruff preflight failed"}

if(Test-Path $pytestTemp){
    Remove-Item $pytestTemp -Recurse -Force -ErrorAction SilentlyContinue
}
New-Item -ItemType Directory -Force -Path $pytestTemp | Out-Null

Write-Host "`n=== Targeted EMS pytest preflight ===" -ForegroundColor Cyan
$targetTest=Join-Path $ems "tests\test_wave2d_applicability_authority.py"
if(Test-Path $targetTest){
    & $py -m pytest --basetemp="$pytestTemp" -q $targetTest
    if($LASTEXITCODE){Fail "targeted pytest preflight failed"}
}
else{
    Write-Host "No targeted baseline prerequisite test found; continuing." -ForegroundColor DarkGray
}

Write-Host "`n=== Register and certify pilot acceptance baseline ===" -ForegroundColor Cyan
& $py $certifier `
    --ems-root $ems `
    --spec $spec `
    --schema $schema
if($LASTEXITCODE){Fail "baseline certification failed"}

Write-Host "`n=== Validate persisted baseline ===" -ForegroundColor Cyan
& $py $validator `
    --ems-root $ems `
    --spec $spec
if($LASTEXITCODE){Fail "persisted baseline validation failed"}

Write-Host "PASS: EMS pilot acceptance baseline persisted and certified." -ForegroundColor Green
Write-Host "baseline_state = AUTHORITATIVE"
