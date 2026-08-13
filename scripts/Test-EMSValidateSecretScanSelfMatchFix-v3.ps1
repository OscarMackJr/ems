[CmdletBinding()]
param([string]$EMSPath = "C:\temp\standars\ems")

$ErrorActionPreference = "Stop"

$workflow = Join-Path $EMSPath ".github\workflows\ems-validate.yml"
if(-not(Test-Path $workflow)){
    throw "Workflow not found: $workflow"
}

$lines = Get-Content $workflow
$text = $lines -join [Environment]::NewLine

$oldSelfMatchLines = @(
    $lines | Where-Object {
        [regex]::IsMatch($_,'grep\s+-RInE') -and
        $_.Contains("AZURE_CLIENT_SECRET=") -and
        $_.Contains("AWS_SECRET_ACCESS_KEY=")
    }
)

$newGrepLines = @(
    $lines | Where-Object {
        [regex]::IsMatch($_,'grep\s+-RInE') -and
        $_.Contains('$secret_pattern')
    }
)

$checks = [ordered]@{
    WorkflowExists                   = Test-Path $workflow
    HasSecretPatternVariable         = $text.Contains("secret_pattern=")
    ScansAzureClientSecret           = $text.Contains("AZURE_CLIENT_SECRET")
    ScansAwsSecretAccessKey          = $text.Contains("AWS_SECRET_ACCESS_KEY")
    ScansPrivateKeys                 = $text.Contains("PRIVATE KEY")
    ScansGithubTokens                = $text.Contains("gh[opsu]")
    UsesVariableInGrep               = $newGrepLines.Count -eq 1
    OldSelfMatchingGrepRemoved       = $oldSelfMatchLines.Count -eq 0
    UsesWhitespaceAssignmentPattern = $text.Contains("[[:space:]]*=")
}

$rows = $checks.GetEnumerator() | ForEach-Object {
    [pscustomobject]@{
        Check = $_.Key
        Pass  = [bool]$_.Value
    }
}

$rows | Format-Table -AutoSize

if(@($rows | Where-Object {-not $_.Pass}).Count -gt 0){
    throw "EMS Validate secret-scan self-match v3 validation failed."
}

Write-Host ""
Write-Host "Relevant scanner lines:" -ForegroundColor Cyan
for($i=0; $i -lt $lines.Count; $i++){
    if(
        $lines[$i].Contains("secret_pattern=") -or
        ([regex]::IsMatch($lines[$i],'grep\s+-RInE') -and $lines[$i].Contains('$secret_pattern'))
    ){
        Write-Host ("{0,4}: {1}" -f ($i+1), $lines[$i])
    }
}

Write-Host ""
Write-Host "PASS: EMS Validate secret-scan self-match v3 validation succeeded." -ForegroundColor Green
