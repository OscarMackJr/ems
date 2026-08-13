[CmdletBinding()]
param([string]$EMSPath = "C:\temp\standars\ems")

$ErrorActionPreference = "Stop"

$workflow = Join-Path $EMSPath ".github\workflows\ems-validate.yml"
if(-not(Test-Path $workflow)){
    throw "Workflow not found: $workflow"
}

$text = Get-Content $workflow -Raw
$lines = Get-Content $workflow

$oldSelfMatchLines = @(
    $lines | Where-Object {
        $_ -match 'grep\s+-RInE' -and
        $_ -match 'AZURE_CLIENT_SECRET=' -and
        $_ -match 'AWS_SECRET_ACCESS_KEY='
    }
)

$newGrepLines = @(
    $lines | Where-Object {
        $_ -match 'grep\s+-RInE' -and
        $_ -match '\$secret_pattern'
    }
)

$checks = [ordered]@{
    WorkflowExists                  = Test-Path $workflow
    HasSecretPatternVariable        = $text -match "secret_pattern="
    ScansAzureClientSecret          = $text -match "AZURE_CLIENT_SECRET"
    ScansAwsSecretAccessKey         = $text -match "AWS_SECRET_ACCESS_KEY"
    ScansPrivateKeys                = $text -match "PRIVATE KEY"
    ScansGithubTokens               = $text -match "gh\[opsu\]"
    UsesVariableInGrep              = $newGrepLines.Count -eq 1
    OldSelfMatchingGrepRemoved      = $oldSelfMatchLines.Count -eq 0
    UsesWhitespaceAssignmentPattern = $text -match '\[\[:space:\]\]\*='
}

$rows = $checks.GetEnumerator() | ForEach-Object {
    [pscustomobject]@{Check=$_.Key;Pass=[bool]$_.Value}
}
$rows | Format-Table -AutoSize

if(@($rows | Where-Object {-not $_.Pass}).Count -gt 0){
    throw "EMS Validate secret-scan self-match v2 validation failed."
}

Write-Host ""
Write-Host "Relevant scanner lines:" -ForegroundColor Cyan
for($i=0; $i -lt $lines.Count; $i++){
    if(
        $lines[$i] -match 'secret_pattern=' -or
        $lines[$i] -match 'grep\s+-RInE.*\$secret_pattern'
    ){
        Write-Host ("{0,4}: {1}" -f ($i+1), $lines[$i])
    }
}

Write-Host ""
Write-Host "PASS: EMS Validate secret-scan self-match v2 validation succeeded." -ForegroundColor Green
