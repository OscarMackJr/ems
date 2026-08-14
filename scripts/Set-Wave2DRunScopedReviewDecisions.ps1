[CmdletBinding()]
param(
    [string]$BatchId="BATCH-20260814T025624.670836Z",
    [string]$EMSPath="C:\temp\standars\ems",
    [string]$DecisionOwner="Oscar Mack"
)
$ErrorActionPreference="Stop"

$file=Join-Path $EMSPath "generated\wave2d\batch\runs\$BatchId\acceptance\human_review_completed.jsonl"
if(-not(Test-Path $file)){throw "Review file not found: $file"}

$rows=Get-Content $file | ForEach-Object {$_ | ConvertFrom-Json}

foreach($row in $rows){
    if($row.control_id -eq "EMS-CTRL-009" -and $row.target_id -eq "REPO-EMS"){
        $row.human_decision="HOLD"
        $row.decision_owner=$DecisionOwner
        $row.decision_rationale="Held because Hayes Verify returned INSUFFICIENT evidence; EMS will not accept or promote unsupported branch-policy evidence."
    }
    elseif($row.control_id -eq "EMS-CTRL-010" -and $row.target_id -eq "REPO-EMS"){
        $row.human_decision="HOLD"
        $row.decision_owner=$DecisionOwner
        $row.decision_rationale="Held because Hayes Verify returned INSUFFICIENT evidence; EMS will not accept or promote unsupported PR-review evidence."
    }
    elseif($row.control_id -eq "EMS-CTRL-018" -and $row.target_id -eq "REPO-EMS"){
        $row.human_decision="ACCEPT"
        $row.decision_owner=$DecisionOwner
        $row.decision_rationale="Accepted as an authoritative adverse finding because Hayes Verify returned SUFFICIENT evidence supporting the FAIL result for secret scanning on REPO-EMS."
    }
}

$rows | ForEach-Object { $_ | ConvertTo-Json -Depth 20 -Compress } | Set-Content $file -Encoding UTF8
Write-Host "PASS: run-scoped review decisions populated for $BatchId" -ForegroundColor Green
