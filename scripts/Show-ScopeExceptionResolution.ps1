[CmdletBinding()]
param([string]$EMSPath="C:\temp\standars\ems")
$dir=Join-Path $EMSPath "generated\wave2\scope-adjudication"
$q=Import-Csv (Join-Path $dir "scope_registry_adjudication_queue.resolved.csv")
Write-Host "Resolution summary:" -ForegroundColor Cyan
$q|Group-Object reviewer_decision|Select-Object Name,Count|Format-Table -AutoSize
Write-Host ""
Write-Host "Reclassifications:" -ForegroundColor Cyan
$q|Where-Object reviewer_decision -eq "RECLASSIFY"|
  Select-Object control_id,control_name,current_scope,proposed_scope,reviewer_rationale|
  Format-Table -Wrap -AutoSize
Write-Host ""
Write-Host "Remaining deferred:" -ForegroundColor Cyan
$q|Where-Object reviewer_decision -eq "DEFER"|
  Select-Object control_id,control_name,current_scope,proposed_scope,reviewer_rationale|
  Format-Table -Wrap -AutoSize
