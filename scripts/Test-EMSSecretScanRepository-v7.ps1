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
    SemanticCloudAssignment     = $workflowText.Contains("[[:space:]]*=")
}

$rows = $checks.GetEnumerator() | ForEach-Object {
    [pscustomobject]@{ Check=$_.Key; Pass=[bool]$_.Value }
}
$rows | Format-Table -AutoSize

if(@($rows | Where-Object { -not $_.Pass }).Count -gt 0){
    throw "Production workflow secret-scanner validation failed."
}

Write-Host ""
Write-Host "Running Windows-native repository preflight..." -ForegroundColor Cyan

$secretRegex = [regex]::new(
    '(gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY|(AZURE_CLIENT_SECRET|AWS_SECRET_ACCESS_KEY)\s*=)',
    [System.Text.RegularExpressions.RegexOptions]::Compiled
)

$hits = @()

$files = Get-ChildItem $EMSPath -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {
        $parts = $_.FullName -split '[\\/]'
        $_.Extension -ne ".md" -and
        $_.Extension -ne ".bak" -and
        -not ($parts -contains ".git") -and
        -not ($parts -contains ".venv") -and
        -not ($parts -contains "node_modules")
    }

foreach($file in $files){
    try{
        $lineNo = 0
        foreach($line in Get-Content $file.FullName -ErrorAction Stop){
            $lineNo++
            if($secretRegex.IsMatch($line)){
                $hits += [pscustomobject]@{
                    File = $file.FullName.Substring($EMSPath.Length).TrimStart('\','/')
                    Line = $lineNo
                    Text = $line.Trim()
                }
            }
        }
    }
    catch{
        # Ignore binary/unreadable files.
    }
}

if($hits.Count -gt 0){
    $hits | Format-Table -Wrap -AutoSize
    throw "Secret-pattern preflight found $($hits.Count) candidate match(es)."
}

Write-Host "PASS: repository preflight found no secret-pattern candidates." -ForegroundColor Green
