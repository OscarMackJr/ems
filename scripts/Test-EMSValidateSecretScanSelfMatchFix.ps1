[CmdletBinding()]
param([string]$EMSPath = "C:\temp\standars\ems")

$ErrorActionPreference = "Stop"
$workflow = Join-Path $EMSPath ".github\workflows\ems-validate.yml"
$text = Get-Content $workflow -Raw

$checks = [ordered]@{
    WorkflowExists                = Test-Path $workflow
    HasSecretPatternVariable      = $text -match "secret_pattern="
    ScansAzureClientSecret        = $text -match "AZURE_CLIENT_SECRET"
    ScansAwsSecretAccessKey       = $text -match "AWS_SECRET_ACCESS_KEY"
    ScansPrivateKeys              = $text -match "PRIVATE KEY"
    ScansGithubTokens             = $text -match "gh\[opsu\]"
    NoLiteralAzureAssignmentAlt   = -not ($text -match "AZURE_CLIENT_SECRET=\|AWS_SECRET_ACCESS_KEY=")
}

$rows = $checks.GetEnumerator() | ForEach-Object {
    [pscustomobject]@{Check=$_.Key;Pass=[bool]$_.Value}
}
$rows | Format-Table -AutoSize

if(@($rows | Where-Object {-not $_.Pass}).Count -gt 0){
    throw "EMS Validate secret-scan self-match patch validation failed."
}

Write-Host "PASS: secret-scan patch validation succeeded." -ForegroundColor Green
