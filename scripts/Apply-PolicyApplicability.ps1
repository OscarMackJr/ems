[CmdletBinding()]
param([string]$Pass45="C:\temp\standars\Pass4_5")
$ErrorActionPreference="Stop"
$py=Join-Path $Pass45 ".venv\Scripts\python.exe"
$src=Join-Path $Pass45 "generated\collector-acceptance\effective_compliance.csv"
$app=Join-Path $Pass45 "generated\policy-applicability\policy_applicability.json"
$out=Join-Path $Pass45 "generated\policy-applicability\effective_compliance_with_applicability.csv"
if(-not(Test-Path $src)){throw "Missing effective compliance input: $src"}
if(-not(Test-Path $app)){throw "Run Run-PolicyApplicability.ps1 first."}
& $py (Join-Path $Pass45 "scripts\Apply-PolicyApplicability.py") --compliance $src --applicability $app --out $out
if($LASTEXITCODE-ne 0){throw "Applying policy applicability failed."}
Write-Host "Applicability-aware compliance created: $out" -ForegroundColor Green
