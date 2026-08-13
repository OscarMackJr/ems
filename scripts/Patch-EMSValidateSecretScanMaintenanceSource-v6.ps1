[CmdletBinding()]
param([string]$EMSPath = "C:\temp\standars\ems")

$ErrorActionPreference = "Stop"

$targets = @(
    "scripts\Patch-EMSValidateSecretScanSelfMatch-v3.ps1",
    "scripts\Test-EMSValidateSecretScanSelfMatchFix-v3.ps1",
    "scripts\Patch-EMSValidateSecretScanFalsePositives-v4.ps1"
)

$changed = @()

foreach($relative in $targets){
    $path = Join-Path $EMSPath $relative

    if(-not(Test-Path $path)){
        Write-Host "Skipping missing maintenance script: $relative" -ForegroundColor Yellow
        continue
    }

    $backup = "$path.pre-secret-source-v6.bak"
    Copy-Item $path $backup -Force

    $lines = [System.Collections.Generic.List[string]](Get-Content $path)
    $fileChanged = $false

    for($i=0; $i -lt $lines.Count; $i++){
        $line = $lines[$i]

        if($line.Contains('$_.Contains("AZURE_CLIENT_SECRET=")')){
            $lines[$i] = $line.Replace(
                '$_.Contains("AZURE_CLIENT_SECRET=")',
                '$_.Contains(("AZURE_CLIENT_SECRET" + "="))'
            )
            $fileChanged = $true
        }

        if($lines[$i].Contains('$_.Contains("AWS_SECRET_ACCESS_KEY=")')){
            $lines[$i] = $lines[$i].Replace(
                '$_.Contains("AWS_SECRET_ACCESS_KEY=")',
                '$_.Contains(("AWS_SECRET_ACCESS_KEY" + "="))'
            )
            $fileChanged = $true
        }

        # v4 replacement-table literals are single-quoted PowerShell strings.
        if($lines[$i].Contains("'AZURE_CLIENT_SECRET='")){
            $lines[$i] = $lines[$i].Replace(
                "'AZURE_CLIENT_SECRET='",
                "('AZURE_CLIENT_SECRET' + '=')"
            )
            $fileChanged = $true
        }

        if($lines[$i].Contains("'AWS_SECRET_ACCESS_KEY='")){
            $lines[$i] = $lines[$i].Replace(
                "'AWS_SECRET_ACCESS_KEY='",
                "('AWS_SECRET_ACCESS_KEY' + '=')"
            )
            $fileChanged = $true
        }
    }

    if(-not $fileChanged){
        Remove-Item $backup -Force
        Write-Host "No offending literals found in $relative"
        continue
    }

    Set-Content $path $lines -Encoding UTF8

    $tokens=$null
    $parseErrors=$null
    [System.Management.Automation.Language.Parser]::ParseFile(
        $path,
        [ref]$tokens,
        [ref]$parseErrors
    ) | Out-Null

    if($parseErrors.Count -gt 0){
        Copy-Item $backup $path -Force
        Write-Host "Parser errors in $relative; original restored." -ForegroundColor Red
        $parseErrors | Format-List
        throw "Parser validation failed for $relative."
    }

    # Ensure direct literal assignment signatures are gone from this source file.
    $patchedText = Get-Content $path -Raw
    if(
        $patchedText.Contains("AZURE_CLIENT_SECRET=") -or
        $patchedText.Contains("AWS_SECRET_ACCESS_KEY=")
    ){
        Copy-Item $backup $path -Force
        throw "Literal cloud-secret assignment signature remains in $relative; original restored."
    }

    $changed += $relative
}

Write-Host ""
Write-Host "Sanitized maintenance scripts:" -ForegroundColor Cyan
if($changed.Count -eq 0){
    Write-Host "  None required."
}else{
    $changed | ForEach-Object { Write-Host "  $_" }
}

Write-Host ""
Write-Host "PASS: v6 maintenance-source sanitization complete." -ForegroundColor Green
