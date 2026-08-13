[CmdletBinding()]
param(
    [string]$EMSPath = "C:\temp\standars\ems"
)

$ErrorActionPreference = "Stop"

$workflow = Join-Path $EMSPath ".github\workflows\ems-validate.yml"
if(-not(Test-Path $workflow)){
    throw "Workflow not found: $workflow"
}

$lines = [System.Collections.Generic.List[string]](Get-Content $workflow)

$matches = @()
for($i=0; $i -lt $lines.Count; $i++){
    $line = $lines[$i]
    if(
        $line -match 'grep\s+-RInE' -and
        $line -match 'AZURE_CLIENT_SECRET' -and
        $line -match 'AWS_SECRET_ACCESS_KEY'
    ){
        $matches += $i
    }
}

if($matches.Count -eq 0){
    Write-Host "No matching scanner command found." -ForegroundColor Yellow
    Write-Host "Relevant workflow lines:" -ForegroundColor Cyan
    for($i=0; $i -lt $lines.Count; $i++){
        if(
            $lines[$i] -match 'Secret-pattern sanity check' -or
            $lines[$i] -match 'grep\s+-RInE' -or
            $lines[$i] -match 'AZURE_CLIENT_SECRET' -or
            $lines[$i] -match 'AWS_SECRET_ACCESS_KEY'
        ){
            Write-Host ("{0,4}: {1}" -f ($i+1), $lines[$i])
        }
    }
    throw "Secret-scan grep command containing both cloud-secret signals was not found."
}

if($matches.Count -gt 1){
    Write-Host "Multiple candidate scanner commands found:" -ForegroundColor Yellow
    foreach($idx in $matches){
        Write-Host ("{0,4}: {1}" -f ($idx+1), $lines[$idx])
    }
    throw "Refusing ambiguous secret-scan patch."
}

$idx = $matches[0]
$original = $lines[$idx]

# Capture indentation.
$indent = ""
if($original -match '^(\s*)'){
    $indent = $Matches[1]
}

# Preserve whether the original grep line had a shell continuation.
$hasContinuation = $original.TrimEnd().EndsWith('\')

$assignment = "${indent}secret_pattern='(gh[opsu]*[A-Za-z0-9_]{20,}|BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY|(AZURE_CLIENT_SECRET|AWS_SECRET_ACCESS_KEY)[[:space:]]*=)'"
$grepLine = "${indent}if grep -RInE `"`$secret_pattern`" ."
if($hasContinuation){
    $grepLine += " \"
}

$backup = "$workflow.pre-secret-scan-selfmatch-fix-v2.bak"
Copy-Item $workflow $backup -Force

try {
    $lines[$idx] = $assignment
    $lines.Insert($idx + 1, $grepLine)

    Set-Content $workflow $lines -Encoding UTF8

    $patched = Get-Content $workflow -Raw

    # Fail if the old literal self-matching alternation is still present in a grep command.
    $oldSelfMatch = Get-Content $workflow | Where-Object {
        $_ -match 'grep\s+-RInE' -and
        $_ -match 'AZURE_CLIENT_SECRET=' -and
        $_ -match 'AWS_SECRET_ACCESS_KEY='
    }
    if($oldSelfMatch){
        throw "Old self-matching grep expression still exists."
    }

    foreach($required in @(
        "secret_pattern=",
        "AZURE_CLIENT_SECRET",
        "AWS_SECRET_ACCESS_KEY",
        "PRIVATE KEY",
        'grep -RInE "$secret_pattern"'
    )){
        if(-not $patched.Contains($required)){
            throw "Required patched workflow signal missing: $required"
        }
    }

    Write-Host "PASS: EMS Validate secret scan self-match patch v2 applied." -ForegroundColor Green
    Write-Host "Workflow: $workflow"
    Write-Host "Backup:   $backup"
    Write-Host ""
    Write-Host "Patched scanner block:" -ForegroundColor Cyan
    $start = [Math]::Max(0,$idx-2)
    $end = [Math]::Min($lines.Count-1,$idx+4)
    for($j=$start; $j -le $end; $j++){
        Write-Host ("{0,4}: {1}" -f ($j+1), $lines[$j])
    }
}
catch {
    Copy-Item $backup $workflow -Force
    throw
}
