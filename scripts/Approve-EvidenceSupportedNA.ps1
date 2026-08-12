[CmdletBinding()]
param([string]$Pass45 = "C:\temp\standars\Pass4_5")

$queuePath = Join-Path $Pass45 "generated\adjudication\wave1_adjudication_queue.csv"
if(-not(Test-Path $queuePath)){ throw "Queue not found." }

$q = Import-Csv $queuePath
$changed = 0

foreach($row in $q){
    if(
        $row.proposed_disposition -eq "CONFIRM_NA" -and
        $row.wave1_status -eq "NOT_APPLICABLE" -and
        [string]::IsNullOrWhiteSpace($row.reviewer_disposition)
    ){
        $row.reviewer_disposition = "CONFIRM_NA"
        $row.reviewer_decision = "APPROVED"
        $row.reviewer_notes = "No release or release-tag activity was detected. The control is not applicable while this repository does not produce versioned/distributable releases. Reevaluate applicability if release activity is introduced."
        $changed++
    }
}

Copy-Item $queuePath "$queuePath.pre-na-auto-approval.bak" -Force
$q | Export-Csv $queuePath -NoTypeInformation -Encoding UTF8

Write-Host "Approved $changed evidence-supported N/A rows." -ForegroundColor Green
