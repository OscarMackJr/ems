[CmdletBinding()]
param(
    [string]$BatchId="BATCH-20260814T025624.670836Z",
    [string]$EMSPath="C:\temp\standars\ems",
    [string]$BatchOwner="Oscar Mack",
    [switch]$AcceptQualified
)
$ErrorActionPreference="Stop"
function Fail([string]$m){throw "EMS RUN-SCOPED BATCH BLOCKED: $m"}

$ems=(Resolve-Path $EMSPath).Path
$py=Join-Path $ems ".venv\Scripts\python.exe"
$runRoot=Join-Path $ems "generated\wave2d\batch\runs\$BatchId"
$qualified=Join-Path $runRoot "acceptance\qualification_queue.jsonl"
$review=Join-Path $runRoot "acceptance\human_review_queue.jsonl"
$reviewed=Join-Path $runRoot "acceptance\human_review_completed.jsonl"
$decisions=Join-Path $runRoot "acceptance\acceptance_decisions.jsonl"
$promotionRoot=Join-Path $runRoot "promotion"
$evidenceRoot=Join-Path $ems "evidence\wave2d\batch\$BatchId"
$manifest=Join-Path $runRoot "baseline\manifest.json"
$certification=Join-Path $runRoot "baseline\certification.json"
$registration=Join-Path $ems "registry\release_baselines\wave2d_batch_$BatchId.json"

if(-not(Test-Path $qualified)){Fail "qualification queue missing"}
if(-not(Test-Path $review)){Fail "human review queue missing"}

if(-not(Test-Path $reviewed)){
    & $py "$ems\scripts\prepare_run_scoped_review.py" --input $review --output $reviewed
    if($LASTEXITCODE){Fail "review preparation failed"}
    Write-Host "Human review file created: $reviewed" -ForegroundColor Yellow
    Write-Host "Populate human_decision, decision_owner, decision_rationale and rerun."
    exit 2
}

$argsList=@(
 "$ems\scripts\apply_run_scoped_acceptance.py",
 "--batch-id",$BatchId,
 "--qualified",$qualified,
 "--reviewed",$reviewed,
 "--output",$decisions,
 "--batch-owner",$BatchOwner
)
if($AcceptQualified){$argsList += "--accept-qualified"}

& $py @argsList
if($LASTEXITCODE){Fail "acceptance decisions failed"}

& $py "$ems\scripts\promote_run_scoped_evidence.py" `
  --ems-root $ems `
  --batch-id $BatchId `
  --decisions $decisions `
  --promotion-root $promotionRoot `
  --evidence-root $evidenceRoot
if($LASTEXITCODE){Fail "promotion failed"}

& $py "$ems\scripts\certify_run_scoped_batch_baseline.py" `
  --ems-root $ems `
  --batch-id $BatchId `
  --promotion-root $promotionRoot `
  --manifest $manifest `
  --registration $registration `
  --certification $certification
if($LASTEXITCODE){Fail "baseline certification failed"}

Write-Host "PASS: run-scoped acceptance, promotion, and baseline certification complete." -ForegroundColor Green
