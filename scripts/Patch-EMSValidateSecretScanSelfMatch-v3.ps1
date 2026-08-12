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

$candidateIndexes = @()
for($i=0; $i -lt $lines.Count; $i++){
    $line = $lines[$i]
    $hasGrep  = [regex]::IsMatch($line, 'grep\s+-RInE')
    $hasAzure = $line.Contains("AZURE_CLIENT_SECRET")
    $hasAws   = $line.Contains("AWS_SECRET_ACCESS_KEY")

    if($hasGrep -and $hasAzure -and $hasAws){
        $candidateIndexes += $i
    }
}

if($candidateIndexes.Count -eq 0){
    Write-Host "No matching scanner command found." -ForegroundColor Yellow
    Write-Host "Relevant workflow lines:" -ForegroundColor Cyan

    for($i=0; $i -lt $lines.Count; $i++){
        $line = $lines[$i]
        if(
            $line.Contains("Secret-pattern sanity check") -or
            [regex]::IsMatch($line,'grep\s+-RInE') -or
            $line.Contains("AZURE_CLIENT_SECRET") -or
            $line.Contains("AWS_SECRET_ACCESS_KEY")
        ){
            Write-Host ("{0,4}: {1}" -f ($i+1), $line)
        }
    }

    throw "Secret-scan grep command containing both cloud-secret signals was not found."
}

if($candidateIndexes.Count -gt 1){
    Write-Host "Multiple candidate scanner commands found:" -ForegroundColor Yellow
    foreach($candidateIndex in $candidateIndexes){
        Write-Host ("{0,4}: {1}" -f ($candidateIndex+1), $lines[$candidateIndex])
    }
    throw "Refusing ambiguous secret-scan patch."
}

$index = $candidateIndexes[0]
$original = $lines[$index]

$indentMatch = [regex]::Match($original,'^(\s*)')
$indent = $indentMatch.Groups[1].Value

$hasContinuation = $original.TrimEnd().EndsWith('\')

$assignment = "${indent}secret_pattern='(gh[opsu]*[A-Za-z0-9_]{20,}|BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY|(AZURE_CLIENT_SECRET|AWS_SECRET_ACCESS_KEY)[[:space:]]*=)'"
$grepLine = "${indent}if grep -RInE `"`$secret_pattern`" ."
if($hasContinuation){
    $grepLine += " \"
}

$backup = "$workflow.pre-secret-scan-selfmatch-fix-v3.bak"
Copy-Item $workflow $backup -Force

try{
    $lines[$index] = $assignment
    $lines.Insert($index + 1, $grepLine)

    Set-Content $workflow $lines -Encoding UTF8

    $patchedLines = Get-Content $workflow
    $patchedText = $patchedLines -join [Environment]::NewLine

    $oldSelfMatchLines = @(
        $patchedLines | Where-Object {
            [regex]::IsMatch($_,'grep\s+-RInE') -and
            $_.Contains(("AZURE_CLIENT_SECRET" + "=")) -and
            $_.Contains(("AWS_SECRET_ACCESS_KEY" + "="))
        }
    )

    if($oldSelfMatchLines.Count -gt 0){
        throw "Old self-matching grep expression still exists."
    }

    $requiredSignals = @(
        "secret_pattern=",
        "AZURE_CLIENT_SECRET",
        "AWS_SECRET_ACCESS_KEY",
        "PRIVATE KEY",
        'grep -RInE "$secret_pattern"'
    )

    foreach($requiredSignal in $requiredSignals){
        if(-not $patchedText.Contains($requiredSignal)){
            throw "Required patched workflow signal missing: $requiredSignal"
        }
    }

    Write-Host "PASS: EMS Validate secret scan self-match patch v3 applied." -ForegroundColor Green
    Write-Host "Workflow: $workflow"
    Write-Host "Backup:   $backup"
    Write-Host ""
    Write-Host "Patched scanner block:" -ForegroundColor Cyan

    $start = [Math]::Max(0,$index-2)
    $end = [Math]::Min($lines.Count-1,$index+4)

    for($j=$start; $j -le $end; $j++){
        Write-Host ("{0,4}: {1}" -f ($j+1), $lines[$j])
    }
}
catch{
    Copy-Item $backup $workflow -Force
    throw
}

