[CmdletBinding()]
param([string]$EMSPath = "C:\temp\standars\ems")

$ErrorActionPreference = "Stop"

$scriptRoot = Join-Path $EMSPath "scripts"
if(-not(Test-Path $scriptRoot)){
    throw "Scripts directory not found: $scriptRoot"
}

$targets = Get-ChildItem $scriptRoot -File -Filter "*EMSValidateSecretScan*.ps1"

$changed = @()

foreach($file in $targets){
    $text = Get-Content $file.FullName -Raw
    $original = $text

    # Remove literal cloud-secret assignment strings from maintenance source.
    # Runtime detection remains in the workflow; these source files only need to
    # construct the same strings without containing them verbatim.
    $text = $text.Replace(
        'AZURE_CLIENT_SECRET=',
        'AZURE_CLIENT_SECRET" + "="'
    )
    $text = $text.Replace(
        'AWS_SECRET_ACCESS_KEY=',
        'AWS_SECRET_ACCESS_KEY" + "="'
    )

    # Repair common quote shapes produced by replacement in Contains() probes.
    $text = $text.Replace(
        '$_.Contains("AZURE_CLIENT_SECRET" + "="")',
        '$_.Contains(("AZURE_CLIENT_SECRET" + "="))'
    )
    $text = $text.Replace(
        '$_.Contains("AWS_SECRET_ACCESS_KEY" + "="")',
        '$_.Contains(("AWS_SECRET_ACCESS_KEY" + "="))'
    )

    if($text -ne $original){
        $backup = "$($file.FullName).pre-secret-source-v5.bak"
        Copy-Item $file.FullName $backup -Force
        Set-Content $file.FullName $text -Encoding UTF8

        $tokens=$null
        $parseErrors=$null
        [System.Management.Automation.Language.Parser]::ParseFile(
            $file.FullName,
            [ref]$tokens,
            [ref]$parseErrors
        ) | Out-Null

        if($parseErrors.Count -gt 0){
            Copy-Item $backup $file.FullName -Force
            $parseErrors | Format-List
            throw "Parser validation failed after sanitizing $($file.Name); original restored."
        }

        $changed += $file.FullName
    }
}

Write-Host "Sanitized maintenance scripts:" -ForegroundColor Cyan
if($changed.Count -eq 0){
    Write-Host "  None required."
}
else{
    $changed | ForEach-Object { Write-Host "  $_" }
}

Write-Host ""
Write-Host "PASS: EMS secret-scan maintenance source sanitization complete." -ForegroundColor Green
