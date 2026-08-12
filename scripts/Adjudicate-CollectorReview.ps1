[CmdletBinding()]
param([string]$Pass45="C:\temp\standars\Pass4_5")
$ErrorActionPreference="Stop"
$qpath=Join-Path $Pass45 "generated\adjudication\wave1_adjudication_queue.csv"
$q=Import-Csv $qpath
Copy-Item $qpath "$qpath.pre-collector-refinement.bak" -Force
$targets=@("EMS-CTRL-015","EMS-CTRL-025","EMS-CTRL-031","EMS-CTRL-033","EMS-CTRL-037","EMS-CTRL-079")
$changed=0
foreach($row in $q){
 if($row.proposed_disposition -ne "COLLECTOR_REVIEW" -or $row.control_id -notin $targets){continue}
 $row.reviewer_disposition="COLLECTOR_REVIEW"
 switch($row.control_id){
  "EMS-CTRL-033" {$row.reviewer_decision="REJECT_REGRESSION";$row.reviewer_notes="Wave 1 reproducible-build heuristic was too weak; preserve prior status pending technology-aware reevaluation."}
  "EMS-CTRL-025" {$row.reviewer_decision="REJECT_WAVE1_RESULT";$row.reviewer_notes="Workflow-name detection is insufficient. Reevaluate workflow content and repository test structure."}
  "EMS-CTRL-031" {$row.reviewer_decision="REJECT_WAVE1_RESULT";$row.reviewer_notes="Zero artifacts does not prove test-evidence retention failure. Reevaluate workflow execution and artifact retention."}
  "EMS-CTRL-037" {$row.reviewer_decision="REJECT_WAVE1_RESULT";$row.reviewer_notes="Zero artifacts does not prove build-artifact retention failure. Reevaluate build/release artifact production and retention."}
  "EMS-CTRL-015" {$row.reviewer_decision="REJECT_WAVE1_RESULT";$row.reviewer_notes="No assertions were produced. Reevaluate against the formal repository-template baseline."}
  "EMS-CTRL-079" {$row.reviewer_decision="REJECT_WAVE1_RESULT";$row.reviewer_notes="GitHub community health is not EMS repository health. Reevaluate as a control roll-up."}
 }
 $changed++
}
$q|Export-Csv $qpath -NoTypeInformation -Encoding UTF8
Write-Host "Adjudicated $changed collector-review rows." -ForegroundColor Green
