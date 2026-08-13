[CmdletBinding()]
param(
    [string]$EMSPath = "C:\temp\standars\ems"
)

$ErrorActionPreference = "Stop"

$workflow = Join-Path $EMSPath ".github\workflows\ems-validate.yml"
if(-not(Test-Path $workflow)){
    throw "Workflow not found: $workflow"
}

$backup = "$workflow.pre-secret-scan-selfmatch-fix.bak"
Copy-Item $workflow $backup -Force

$text = Get-Content $workflow -Raw

$old = @"
if grep -RInE '(gh[opsu]*[A-Za-z0-9_]{20,}|BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY|AZURE_CLIENT_SECRET=|AWS_SECRET_ACCESS_KEY=)' .
"@

# Also support the exact variant seen in the current workflow/log where the token class
# may not contain an underscore.
$old2 = @"
if grep -RInE '(gh[opsu]*[A-Za-z0-9]{20,}|BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY|AZURE_CLIENT_SECRET=|AWS_SECRET_ACCESS_KEY=)' .
"@

$new = @"
secret_pattern='(gh[opsu]*[A-Za-z0-9_]{20,}|BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY|(AZURE_CLIENT_SECRET|AWS_SECRET_ACCESS_KEY)[[:space:]]*=)'
if grep -RInE "`$secret_pattern" .
"@

if($text.Contains($old)){
    $text = $text.Replace($old,$new)
}
elseif($text.Contains($old2)){
    $text = $text.Replace($old2,$new)
}
else{
    # Regex fallback tolerant of whitespace differences.
    $pattern = "if grep -RInE '\(gh\[opsu\]\*\[A-Za-z0-9_?\]\{20,\}\|BEGIN \(RSA \|EC \|OPENSSH \)\?PRIVATE KEY\|AZURE_CLIENT_SECRET=\|AWS_SECRET_ACCESS_KEY=\)' \."
    $replacement = @"
secret_pattern='(gh[opsu]*[A-Za-z0-9_]{20,}|BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY|(AZURE_CLIENT_SECRET|AWS_SECRET_ACCESS_KEY)[[:space:]]*=)'
if grep -RInE "`$secret_pattern" .
"@
    $changed = [regex]::Replace($text,$pattern,$replacement)
    if($changed -eq $text){
        Copy-Item $backup $workflow -Force
        throw "Expected secret-scan grep line not found; workflow restored."
    }
    $text = $changed
}

Set-Content $workflow $text -Encoding UTF8

# Ensure the literal assignment signatures that triggered the false positive no longer
# appear in the scanner command itself.
$patched = Get-Content $workflow -Raw
if($patched -match "AZURE_CLIENT_SECRET=\|AWS_SECRET_ACCESS_KEY="){
    Copy-Item $backup $workflow -Force
    throw "Self-matching literal secret assignment signatures remain; workflow restored."
}

# The scanner must still include both secret variable names and PRIVATE KEY/token checks.
foreach($required in @(
    "AZURE_CLIENT_SECRET",
    "AWS_SECRET_ACCESS_KEY",
    "PRIVATE KEY",
    "gh[opsu]"
)){
    if(-not $patched.Contains($required)){
        Copy-Item $backup $workflow -Force
        throw "Required secret scan signal missing after patch: $required"
    }
}

Write-Host "PASS: EMS Validate secret scan patched to avoid self-matching." -ForegroundColor Green
Write-Host "Backup: $backup"
Write-Host ""
Write-Host "Next:"
Write-Host "  git add .github/workflows/ems-validate.yml"
Write-Host "  git commit -m `"fix EMS secret scan self-match`""
Write-Host "  git push"
