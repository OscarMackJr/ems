[CmdletBinding()]
param([string]$Pass45="C:\temp\standars\Pass4_5")
$ErrorActionPreference="Stop"
$qpath=Join-Path $Pass45 "generated\adjudication\wave1_adjudication_queue.csv"
$q=Import-Csv $qpath
Copy-Item $qpath "$qpath.pre-collector-acceptance.bak" -Force
$targets=@("EMS-CTRL-015","EMS-CTRL-025","EMS-CTRL-031","EMS-CTRL-033","EMS-CTRL-037","EMS-CTRL-079")
$closed=0
foreach($r in $q){
 if($r.control_id -in $targets -and $r.proposed_disposition -eq "COLLECTOR_REVIEW"){
  $r.reviewer_disposition="ACCEPT"
  $r.reviewer_decision="ACCEPT_V2_COLLECTOR"
  $r.reviewer_notes="Collector Refinement v2 accepted as authoritative for Pass 4.5. Prior Wave 1 heuristic result superseded."
  $closed++
 }
}
$q|Export-Csv $qpath -NoTypeInformation -Encoding UTF8
Write-Host "Closed $closed collector-review adjudications." -ForegroundColor Green
