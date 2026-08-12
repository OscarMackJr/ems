[CmdletBinding()]
param([string]$Pass45="C:\temp\standars\Pass4_5")
$ErrorActionPreference="Stop"
$qpath=Join-Path $Pass45 "generated\adjudication\wave1_adjudication_queue.csv"
$rpath=Join-Path $Pass45 "registry\adjudication_rules.json"
$q=Import-Csv $qpath
Copy-Item $qpath "$qpath.pre-license-routing.bak" -Force
Copy-Item $rpath "$rpath.pre-license-routing.bak" -Force
$changed=0
foreach($row in $q){
 if($row.control_id -eq "EMS-CTRL-020"){
  $row.proposed_disposition="POLICY_REVIEW"
  $row.adjudication_rationale="License compliance must be based on an approved dependency-license policy plus scan evidence; LICENSE-file presence alone is insufficient."
  $changed++
 }
}
$q|Export-Csv $qpath -NoTypeInformation -Encoding UTF8
$r=Get-Content $rpath -Raw|ConvertFrom-Json
if(-not $r.control_rules.'EMS-CTRL-020'){
 $r.control_rules|Add-Member -NotePropertyName 'EMS-CTRL-020' -NotePropertyValue ([pscustomobject]@{})
}
$r.control_rules.'EMS-CTRL-020'|Add-Member -Force NoteProperty default_disposition "POLICY_REVIEW"
$r.control_rules.'EMS-CTRL-020'|Add-Member -Force NoteProperty warning_disposition "POLICY_REVIEW"
$r.control_rules.'EMS-CTRL-020'|Add-Member -Force NoteProperty fail_disposition "POLICY_REVIEW"
$r|ConvertTo-Json -Depth 30|Set-Content $rpath -Encoding UTF8
Write-Host "Re-routed $changed EMS-CTRL-020 rows to POLICY_REVIEW." -ForegroundColor Green
