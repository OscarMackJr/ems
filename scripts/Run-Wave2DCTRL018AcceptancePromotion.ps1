[CmdletBinding()]
param(
    [string]$HayesVerifyPath="C:\temp\standars\hayes-verify",
    [ValidateSet("ACCEPT","REJECT")][string]$Decision,
    [string]$DecisionOwner,
    [string]$DecisionSource="HUMAN_EMS_CTRL018_PILOT_ACCEPTANCE",
    [string]$Rationale
)
$ErrorActionPreference="Stop"
function Fail([string]$m){throw "EMS CTRL-018 ACCEPTANCE BLOCKED: $m"}

$ems=(Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$py=Join-Path $ems ".venv\Scripts\python.exe"
$spec=Join-Path $ems "registry\ctrl018_acceptance_promotion_spec.json"
$acceptSchema=Join-Path $ems "schemas\ctrl018_acceptance_record.schema.json"
$promotionSchema=Join-Path $ems "schemas\ctrl018_promotion_record.schema.json"

& $py "$ems\scripts\prepare_ctrl018_acceptance.py" --ems-root $ems --hayes-root $HayesVerifyPath --spec $spec
if($LASTEXITCODE){Fail "preflight failed"}

if(-not $Decision){$Decision=(Read-Host "EMS decision [ACCEPT/REJECT]").Trim().ToUpperInvariant()}
if(-not $DecisionOwner){$DecisionOwner=Read-Host "Decision owner"}
if(-not $Rationale){$Rationale=Read-Host "Audit-quality decision rationale"}

& $py "$ems\scripts\record_ctrl018_acceptance.py" `
  --ems-root $ems --spec $spec --schema $acceptSchema `
  --decision $Decision --owner $DecisionOwner --source $DecisionSource --rationale $Rationale
if($LASTEXITCODE){Fail "decision recording failed"}

if($Decision -eq "REJECT"){
    Write-Host "PASS: CTRL-018 rejection recorded. Evidence was not promoted." -ForegroundColor Yellow
    exit 0
}

& $py "$ems\scripts\promote_ctrl018_evidence.py" `
  --ems-root $ems --hayes-root $HayesVerifyPath --spec $spec --schema $promotionSchema
if($LASTEXITCODE){Fail "promotion failed"}

& $py "$ems\scripts\validate_ctrl018_promotion.py" --ems-root $ems --spec $spec
if($LASTEXITCODE){Fail "promotion validation failed"}

Write-Host "PASS: CTRL-018 result accepted and evidence promoted under EMS authority." -ForegroundColor Green
