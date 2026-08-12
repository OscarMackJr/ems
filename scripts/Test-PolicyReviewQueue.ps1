[CmdletBinding()]
param([string]$Pass45 = "C:\temp\standars\Pass4_5")

$ErrorActionPreference = "Stop"
$queuePath = Join-Path $Pass45 "generated\policy-review\policy_review_queue.csv"

$q = Import-Csv $queuePath
$required = @(
    "EMS-CTRL-012","EMS-CTRL-014","EMS-CTRL-020",
    "EMS-CTRL-034","EMS-CTRL-036","EMS-CTRL-038","EMS-CTRL-039"
)

$errors = @()

foreach($id in $required){
    $row = $q | Where-Object control_id -eq $id
    if(-not $row){
        $errors += "$id missing from policy review queue"
        continue
    }
    foreach($field in @("policy_decision","policy_effective_date","policy_owner","approved_status_mapping")){
        if([string]::IsNullOrWhiteSpace($row.$field)){
            $errors += "$id missing $field"
        }
    }
}

Write-Host "Policy decision validation:" -ForegroundColor Cyan

if($errors.Count -gt 0){
    $errors | ForEach-Object { Write-Host "  ERROR: $_" -ForegroundColor Red }
    throw "Policy decision validation failed."
}

$q |
    Where-Object control_id -in $required |
    Select-Object control_id,control_name,policy_owner,approved_status_mapping |
    Format-Table -AutoSize

Write-Host "PASS: all seven policy decisions are populated." -ForegroundColor Green
