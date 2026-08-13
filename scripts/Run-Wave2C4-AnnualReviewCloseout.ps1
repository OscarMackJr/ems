[CmdletBinding()]
param(
    [string]$EMSPath="C:\temp\standars\ems",
    [string]$BaselinePath="C:\temp\standars\ems-local-archive\wave1-input\effective_compliance_postpolicy.csv",
    [switch]$PromoteAndCloseout
)

$ErrorActionPreference="Stop"
function Fail([string]$m){throw "WAVE 2C.4 BLOCKED: $m"}

$root=(Resolve-Path $EMSPath).Path
$branch=(git -C $root branch --show-current).Trim()
if($branch-ne"feature/wave2c-remediation"){Fail "Expected feature/wave2c-remediation; current=$branch"}

$py=$null
if($env:VIRTUAL_ENV){
    $candidate=Join-Path $env:VIRTUAL_ENV "Scripts\python.exe"
    if(Test-Path $candidate){$py=$candidate}
}
if(-not $py){
    $cmd=Get-Command python -ErrorAction SilentlyContinue
    if($cmd){$py=$cmd.Source}
}
if(-not $py){Fail "No usable Python interpreter found."}

$out=Join-Path $root "generated\wave2c\annual-review"
$close=Join-Path $root "generated\wave2c\annual-review-closeout"
New-Item -ItemType Directory -Force -Path $out,$close|Out-Null


# === Already-promoted closeout resume path ===
$promotionRecordPath=Join-Path $root "generated\wave2c\annual-review-closeout\promotion_record.json"
$authoritativeEvidencePath=Join-Path $root "evidence\ems\EMS-CTRL-080.yaml"
$queuePath=Join-Path $root "generated\wave2c\remediation_queue.csv"

if((Test-Path $promotionRecordPath) -and (Test-Path $authoritativeEvidencePath) -and (Test-Path $queuePath)){
    $resumePromotion=Get-Content $promotionRecordPath -Raw | ConvertFrom-Json
    $resumeRows=@(Import-Csv $queuePath)
    $resumeCtrl=@($resumeRows | Where-Object {$_.control_id -eq "EMS-CTRL-080"})
    $resumeOpen=@($resumeRows | Where-Object {$_.remediation_state -eq "OPEN"})

    $alreadyPromoted=(
        $resumePromotion.wave -eq "2C.4" -and
        $resumePromotion.control_id -eq "EMS-CTRL-080" -and
        $resumePromotion.promotion_performed -eq $true -and
        $resumePromotion.pre_open_count -eq 1 -and
        $resumePromotion.post_open_count -eq 0 -and
        $resumeCtrl.Count -eq 1 -and
        $resumeCtrl[0].current_status -eq "PASS" -and
        $resumeCtrl[0].evidence_sufficiency -eq "SUFFICIENT" -and
        $resumeCtrl[0].promotion_status -eq "PROMOTED" -and
        $resumeCtrl[0].remediation_state -eq "CLOSED" -and
        $resumeOpen.Count -eq 0
    )

    if($alreadyPromoted){
        $actualHash=(Get-FileHash -Algorithm SHA256 $authoritativeEvidencePath).Hash.ToLowerInvariant()
        $expectedHash=([string]$resumePromotion.authoritative_evidence_sha256).ToLowerInvariant()
        if($actualHash -ne $expectedHash){
            Fail "Already-promoted CTRL-080 evidence hash mismatch."
        }

        Write-Host "=== Wave 2C.4 already-promoted closeout resume ===" -ForegroundColor Cyan
        Write-Host "CTRL-080 promotion already verified; skipping qualification/review/promotion." -ForegroundColor Green

        Write-Host "`n=== Rerun higher-scope / inheritance evaluation ===" -ForegroundColor Cyan
        $inheritance=Join-Path $root "scripts\Run-Wave2B1-Inheritance.ps1"
        if(-not(Test-Path $inheritance)){Fail "Inheritance runner not found."}
        if(-not(Test-Path $BaselinePath)){Fail "Wave 1 baseline not found: $BaselinePath"}
        & $inheritance -BaselinePath $BaselinePath
        if($LASTEXITCODE){Fail "Inheritance rerun failed."}

        Write-Host "`n=== Certify Wave 2C closeout ===" -ForegroundColor Cyan
        & $py (Join-Path $root "scripts\Closeout-Wave2C4.py") `
            --root $root `
            --out (Join-Path $close "wave2c_closeout_certification.json")
        if($LASTEXITCODE){Fail "Wave 2C closeout certification failed."}

        Write-Host "`nPASS: Wave 2C closeout resumed from existing CTRL-080 promotion." -ForegroundColor Green
        exit 0
    }
}

Write-Host "=== Wave 2C.4 initialize Annual EMS Review register ===" -ForegroundColor Cyan
& $py (Join-Path $root "scripts\Initialize-Wave2C4AnnualReview.py") --root $root
if($LASTEXITCODE){Fail "Annual review register initialization failed."}

Write-Host "`n=== Validate Annual EMS Review register ===" -ForegroundColor Cyan
& $py (Join-Path $root "scripts\Validate-Wave2C4AnnualReview.py") `
    --root $root `
    --report (Join-Path $out "register_validation.json")
if($LASTEXITCODE){Fail "Annual review register validation failed."}

Write-Host "`n=== Qualify EMS-CTRL-080 ===" -ForegroundColor Cyan
& $py (Join-Path $root "scripts\Qualify-Wave2C4AnnualReview.py") --root $root
if($LASTEXITCODE){Fail "CTRL-080 qualification failed."}


$qualificationPath=Join-Path $out "qualification.json"
if(-not(Test-Path $qualificationPath)){
    Fail "CTRL-080 qualification artifact not found: $qualificationPath"
}
$qualification=Get-Content $qualificationPath -Raw | ConvertFrom-Json
$ctrl=$qualification.control

$qualified=(
    $ctrl.status -eq "PASS" -and
    $ctrl.sufficiency -eq "SUFFICIENT" -and
    $ctrl.promotion_eligible -eq $true -and
    $ctrl.promotion_status -eq "QUALIFIED_NOT_PROMOTED" -and
    $ctrl.remediation_state -eq "OPEN"
)

if(-not $qualified){
    Write-Host ""
    Write-Host "CTRL-080 not yet qualified; review/promotion skipped." -ForegroundColor Yellow
    Write-Host "Status: $($ctrl.status)"
    Write-Host "Sufficiency: $($ctrl.sufficiency)"
    Write-Host "Promotion eligible: $($ctrl.promotion_eligible)"
    Write-Host "Missing assertions: $($ctrl.missing_assertions)"
    Write-Host ""
    Write-Host "PASS: Wave 2C.4 remains fail-closed with no promotion performed." -ForegroundColor Green
    exit 0
}

Write-Host "`n=== Review CTRL-080 evidence ===" -ForegroundColor Cyan
$args=@(
    (Join-Path $root "scripts\ReviewPromote-Wave2C4AnnualReview.py"),
    "--root",$root,
    "--outdir",$close
)
if($PromoteAndCloseout){$args += "--promote"}
& $py @args
if($LASTEXITCODE){Fail "CTRL-080 review/promotion failed."}

if(-not $PromoteAndCloseout){
    Write-Host "`nPASS: CTRL-080 review complete. No promotion performed." -ForegroundColor Green
    Write-Host "After reviewing evidence, rerun with -PromoteAndCloseout."
    exit 0
}

Write-Host "`n=== Rerun higher-scope / inheritance evaluation ===" -ForegroundColor Cyan
$inheritance=Join-Path $root "scripts\Run-Wave2B1-Inheritance.ps1"
if(Test-Path $inheritance){
    if(-not(Test-Path $BaselinePath)){Fail "Wave 1 baseline not found: $BaselinePath"}
    & $inheritance -BaselinePath $BaselinePath
    if($LASTEXITCODE){Fail "Inheritance rerun failed."}
}else{
    Fail "Inheritance runner not found."
}

Write-Host "`n=== Certify Wave 2C closeout ===" -ForegroundColor Cyan
& $py (Join-Path $root "scripts\Closeout-Wave2C4.py") `
    --root $root `
    --out (Join-Path $close "wave2c_closeout_certification.json")
if($LASTEXITCODE){Fail "Wave 2C closeout certification failed."}

Write-Host "`nPASS: Wave 2C closed with zero open remediation controls." -ForegroundColor Green
