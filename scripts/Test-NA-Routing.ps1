[CmdletBinding()]
param([string]$Pass45 = "C:\temp\standars\Pass4_5")

$queuePath = Join-Path $Pass45 "generated\adjudication\wave1_adjudication_queue.csv"
if(-not(Test-Path $queuePath)){ throw "Queue not found. Re-run adjudication first." }

$q = Import-Csv $queuePath
$bad = $q | Where-Object {
    $_.proposed_disposition -eq "CONFIRM_NA" -and $_.wave1_status -ne "NOT_APPLICABLE"
}

Write-Host "CONFIRM_NA total: $(($q | Where-Object proposed_disposition -eq 'CONFIRM_NA').Count)"
Write-Host "Invalid CONFIRM_NA rows: $($bad.Count)"

if($bad.Count -gt 0){
    $bad | Select-Object repository_name,control_id,control_name,wave1_status,proposed_disposition | Format-Table -AutoSize
    throw "Invalid CONFIRM_NA routing remains."
}

Write-Host "PASS: all CONFIRM_NA rows are NOT_APPLICABLE." -ForegroundColor Green

Write-Host ""
Write-Host "nono release-control routing:" -ForegroundColor Cyan
$q | Where-Object {
    $_.repository_name -eq "nono" -and $_.control_id -in @("EMS-CTRL-013","EMS-CTRL-035","EMS-CTRL-036","EMS-CTRL-038")
} | Select-Object repository_name,control_id,control_name,wave1_status,proposed_disposition | Format-Table -AutoSize
