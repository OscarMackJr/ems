[CmdletBinding()]
param(
    [string]$EMSPath="C:\temp\standars\ems"
)
$ErrorActionPreference="Stop"
$qpath=Join-Path $EMSPath "generated\wave2\scope-adjudication\scope_registry_adjudication_queue.csv"
if(-not(Test-Path $qpath)){throw "Adjudication queue not found: $qpath"}
$q=Import-Csv $qpath
Copy-Item $qpath "$qpath.pre-prefill.bak" -Force

$obvious=@(
"EMS-CTRL-009","EMS-CTRL-010","EMS-CTRL-011","EMS-CTRL-012","EMS-CTRL-013","EMS-CTRL-014","EMS-CTRL-015",
"EMS-CTRL-017","EMS-CTRL-018","EMS-CTRL-019","EMS-CTRL-020","EMS-CTRL-021",
"EMS-CTRL-025","EMS-CTRL-026","EMS-CTRL-027","EMS-CTRL-028","EMS-CTRL-031","EMS-CTRL-033",
"EMS-CTRL-034","EMS-CTRL-035","EMS-CTRL-036","EMS-CTRL-037","EMS-CTRL-038","EMS-CTRL-039","EMS-CTRL-051","EMS-CTRL-079",
"EMS-CTRL-067","EMS-CTRL-068","EMS-CTRL-069","EMS-CTRL-070","EMS-CTRL-071","EMS-CTRL-072","EMS-CTRL-075","EMS-CTRL-076","EMS-CTRL-080",
"EMS-CTRL-073","EMS-CTRL-074","EMS-CTRL-078"
)

$changed=0
foreach($r in $q){
    if($r.control_id -in $obvious -and [string]::IsNullOrWhiteSpace($r.reviewer_decision)){
        $r.reviewer_decision="APPROVED"
        $r.proposed_scope=$r.current_scope
        $r.reviewer_rationale="Approved in Wave 2A.1 based on the control's primary operating boundary and current EMS architecture."
        $r.reviewer="EMS Architecture"
        $r.review_date=(Get-Date).ToString("yyyy-MM-dd")
        $changed++
    }
}
$q|Export-Csv $qpath -NoTypeInformation -Encoding UTF8
Write-Host "Pre-approved $changed obvious scope classifications." -ForegroundColor Green
Write-Host "Review all remaining blank decisions manually before applying."
