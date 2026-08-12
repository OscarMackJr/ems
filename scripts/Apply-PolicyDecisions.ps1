[CmdletBinding()]
param([string]$Pass45="C:\temp\standars\Pass4_5")
$ErrorActionPreference="Stop"
$py=Join-Path $Pass45 ".venv\Scripts\python.exe"
$pq=Join-Path $Pass45 "generated\policy-review\policy_review_queue.csv"
$aq=Join-Path $Pass45 "generated\adjudication\wave1_adjudication_queue.csv"
$tmp=Join-Path $Pass45 "generated\adjudication\wave1_adjudication_queue.policy.tmp.csv"
& $py (Join-Path $Pass45 "scripts\Apply-PolicyReviewDecisions.py") --policy-queue $pq --adjudication-queue $aq --out $tmp
if($LASTEXITCODE-ne 0){throw "Applying policy adjudication decisions failed."}
Copy-Item $aq "$aq.pre-policy-decisions.bak" -Force
Move-Item $tmp $aq -Force
Write-Host "Policy adjudication decisions applied." -ForegroundColor Green
