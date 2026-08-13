[CmdletBinding()]
param([string]$EMSPath = "C:\temp\standars\ems")

$ErrorActionPreference = "Stop"

$workflow = Join-Path $EMSPath ".github\workflows\ems-validate.yml"
if(-not(Test-Path $workflow)){
    throw "Workflow not found: $workflow"
}

$workflowText = Get-Content $workflow -Raw

$checks = [ordered]@{
    ExplicitGithubTokenPrefixes = $workflowText.Contains("gh[pousr]_")
    FineGrainedTokenPrefix      = $workflowText.Contains("github_pat_")
    NoBroadGithubWildcard       = -not $workflowText.Contains("gh[opsu]*")
    AzureAssignmentDetection    = $workflowText.Contains("AZURE_CLIENT_SECRET")
    AwsAssignmentDetection      = $workflowText.Contains("AWS_SECRET_ACCESS_KEY")
    PrivateKeyDetection         = $workflowText.Contains("PRIVATE KEY")
}

$checkRows = $checks.GetEnumerator() | ForEach-Object {
    [pscustomobject]@{ Check=$_.Key; Pass=[bool]$_.Value }
}
$checkRows | Format-Table -AutoSize

if(@($checkRows | Where-Object { -not $_.Pass }).Count -gt 0){
    throw "Workflow secret-scanner structural validation failed."
}

Write-Host ""
Write-Host "Running Windows-native repository secret-pattern preflight..." -ForegroundColor Cyan

# Equivalent .NET regex for the GitHub Actions grep expression.
$secretRegex = [regex]::new(
    '(gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY|(AZURE_CLIENT_SECRET|AWS_SECRET_ACCESS_KEY)\s*=)',
    [System.Text.RegularExpressions.RegexOptions]::Compiled
)

$excludedDirs = @(".git",".venv")
$hits = @()

$files = Get-ChildItem $EMSPath -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Extension -ne ".md" -and
        -not ($_.FullName -split '[\\/]' | Where-Object { $_ -in $excludedDirs })
    }

foreach($file in $files){
    try{
        $lineNumber = 0
        foreach($line in Get-Content $file.FullName -ErrorAction Stop){
            $lineNumber++
            if($secretRegex.IsMatch($line)){
                $hits += [pscustomobject]@{
                    File = $file.FullName.Substring($EMSPath.Length).TrimStart('\','/')
                    Line = $lineNumber
                    Text = $line.Trim()
                }
            }
        }
    }
    catch{
        # Ignore binary/unreadable files; GitHub grep similarly focuses on textual matches.
    }
}

if($hits.Count -gt 0){
    $hits | Format-Table -Wrap -AutoSize
    throw "Secret-pattern preflight found $($hits.Count) candidate match(es)."
}

Write-Host "PASS: Windows-native secret-pattern preflight found no candidates." -ForegroundColor Green
