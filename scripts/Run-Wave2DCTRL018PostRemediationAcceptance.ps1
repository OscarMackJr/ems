[CmdletBinding()]
param(
    [string]$HayesVerifyPath="C:\temp\standars\hayes-verify",
    [string]$DecisionOwner,
    [string]$DecisionSource="HUMAN_EMS_CTRL018_POST_REMEDIATION_ACCEPTANCE",
    [string]$Rationale
)
$ErrorActionPreference="Stop"
function Fail([string]$m){throw "EMS CTRL-018 POST-REMEDIATION BLOCKED: $m"}

$ems=(Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$py=Join-Path $ems ".venv\Scripts\python.exe"
$spec=Join-Path $ems "registry\ctrl018_post_remediation_spec.json"
$script=Join-Path $ems "scripts\process_ctrl018_post_remediation.py"

if(-not $DecisionOwner){$DecisionOwner=Read-Host "Decision owner"}
if(-not $Rationale){
    $Rationale=Read-Host "Audit-quality post-remediation rationale"
}

& $py -m ruff check $script
if($LASTEXITCODE){Fail "Ruff failed"}

& $py $script `
  --ems-root $ems `
  --hayes-root $HayesVerifyPath `
  --spec $spec `
  --owner $DecisionOwner `
  --source $DecisionSource `
  --rationale $Rationale
if($LASTEXITCODE){Fail "post-remediation acceptance/promotion failed"}

Write-Host "PASS: CTRL-018 post-remediation evidence accepted, promoted, and baselined." -ForegroundColor Green
