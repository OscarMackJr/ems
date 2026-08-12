[CmdletBinding()]
param(
    [string]$Pass45 = "C:\temp\standars\Pass4_5",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$queuePath = Join-Path $Pass45 "generated\policy-review\policy_review_queue.csv"
$decisionPath = Join-Path $Pass45 "registry\policy_decisions.json"

if (-not (Test-Path $queuePath)) {
    throw "Policy review queue not found: $queuePath"
}
if (-not (Test-Path $decisionPath)) {
    throw "Policy decisions registry not found: $decisionPath"
}

$backup = "$queuePath.pre-policy-population.bak"
Copy-Item $queuePath $backup -Force

$queue = Import-Csv $queuePath
$registry = Get-Content $decisionPath -Raw | ConvertFrom-Json
$effectiveDate = $registry.effective_date
$changed = 0
$skipped = 0

foreach ($row in $queue) {
    $decision = $registry.decisions.PSObject.Properties |
        Where-Object { $_.Name -eq $row.control_id } |
        Select-Object -ExpandProperty Value -ErrorAction SilentlyContinue

    if (-not $decision) {
        continue
    }

    $alreadyPopulated =
        -not [string]::IsNullOrWhiteSpace($row.policy_decision) -or
        -not [string]::IsNullOrWhiteSpace($row.approved_status_mapping)

    if ($alreadyPopulated -and -not $Force) {
        $skipped++
        continue
    }

    $row.policy_decision = $decision.policy_decision
    $row.policy_effective_date = $effectiveDate
    $row.policy_owner = $decision.policy_owner
    $row.policy_notes = $decision.policy_notes
    $row.approved_status_mapping = $decision.approved_status_mapping
    $changed++
}

$queue | Export-Csv $queuePath -NoTypeInformation -Encoding UTF8

Write-Host ""
Write-Host "Policy queue population complete." -ForegroundColor Green
Write-Host "  Updated rows: $changed"
Write-Host "  Preserved existing rows: $skipped"
Write-Host "  Backup: $backup"

Write-Host ""
Write-Host "Populated decisions:" -ForegroundColor Cyan
Import-Csv $queuePath |
    Select-Object control_id, control_name, policy_owner, approved_status_mapping |
    Format-Table -AutoSize
