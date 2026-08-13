[CmdletBinding()]
param([string]$EMSPath = "C:\temp\standars\ems")

$ErrorActionPreference = "Stop"

$workflow = Join-Path $EMSPath ".github\workflows\ems-validate.yml"
if(-not(Test-Path $workflow)){
    throw "Workflow not found: $workflow"
}

$text = Get-Content $workflow -Raw

$checks = [ordered]@{
    HasExplicitClassicTokenPrefixes = $text.Contains("gh[pousr]_")
    HasFineGrainedTokenPrefix       = $text.Contains("github_pat_")
    NoBroadGhWildcardPattern        = -not $text.Contains("gh[opsu]*")
    ScansAzureClientSecret          = $text.Contains("AZURE_CLIENT_SECRET")
    ScansAwsSecretAccessKey         = $text.Contains("AWS_SECRET_ACCESS_KEY")
    ScansPrivateKeys                = $text.Contains("PRIVATE KEY")
    UsesSemanticAssignmentPattern   = $text.Contains("[[:space:]]*=")
}

$rows = $checks.GetEnumerator() | ForEach-Object {
    [pscustomobject]@{ Check=$_.Key; Pass=[bool]$_.Value }
}
$rows | Format-Table -AutoSize

if(@($rows | Where-Object { -not $_.Pass }).Count -gt 0){
    throw "EMS secret scanner v4 structural validation failed."
}

# Reproduce the GitHub Actions grep locally against the repository.
Push-Location $EMSPath
try{
    $bash = Get-Command bash -ErrorAction SilentlyContinue
    if($bash){
        Write-Host ""
        Write-Host "Running local secret-pattern sanity scan through bash..." -ForegroundColor Cyan

        $cmd = @'
secret_pattern='(gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY|(AZURE_CLIENT_SECRET|AWS_SECRET_ACCESS_KEY)[[:space:]]*=)'
if grep -RInE "$secret_pattern" . --exclude-dir=.git --exclude-dir=.venv --exclude='*.md'; then
  exit 7
fi
exit 0
'@

        & bash -lc $cmd
        if($LASTEXITCODE -eq 7){
            throw "Local secret scan still found candidate patterns."
        }
        elseif($LASTEXITCODE -ne 0){
            throw "Local bash secret scan failed unexpectedly with exit code $LASTEXITCODE."
        }
    }
    else{
        Write-Host ""
        Write-Host "bash not available locally; structural validation only." -ForegroundColor Yellow
    }
}
finally{
    Pop-Location
}

Write-Host ""
Write-Host "PASS: EMS secret scanner v4 validation succeeded." -ForegroundColor Green
