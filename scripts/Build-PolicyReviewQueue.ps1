[CmdletBinding()]
param([string]$Pass45="C:\temp\standars\Pass4_5")
$ErrorActionPreference="Stop"
$py=Join-Path $Pass45 ".venv\Scripts\python.exe"
$q=Join-Path $Pass45 "generated\adjudication\wave1_adjudication_queue.csv"
$out=Join-Path $Pass45 "generated\policy-review"
& $py (Join-Path $Pass45 "scripts\Build-PolicyReviewQueue.py") --queue $q --outdir $out
if($LASTEXITCODE-ne 0){throw "Policy review queue build failed."}
Write-Host "Review: $out\policy_review_queue.csv" -ForegroundColor Green
