[CmdletBinding()]
param(
    [string]$EMSPath = "C:\temp\standars\ems",
    [string]$Pass45 = "C:\temp\standars\Pass4_5",
    [switch]$Commit
)

$ErrorActionPreference = "Stop"

if(-not(Test-Path $EMSPath)){
    throw "EMS repository not found: $EMSPath"
}
if(-not(Test-Path $Pass45)){
    throw "Pass 4.5 source not found: $Pass45"
}

$py = Join-Path $EMSPath ".venv\Scripts\python.exe"
if(-not(Test-Path $py)){ $py = "python" }

Write-Host "Searching Pass 4.5 for authoritative control sources..." -ForegroundColor Cyan

# Search the working Pass 4.5 tree and frozen Wave 1 baseline.
$searchRoots = @(
    $Pass45,
    (Join-Path $Pass45 "release\Pass4_5_Wave1_Baseline")
) | Where-Object { Test-Path $_ }

$catalogCandidates = @()
$controlDirs = @()

foreach($sr in $searchRoots){
    $catalogCandidates += Get-ChildItem -Path $sr -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object {
            $_.Name -in @(
                "control_catalog.yaml","control_catalog.yml",
                "control_registry.yaml","control_registry.yml"
            )
        }

    $controlDirs += Get-ChildItem -Path $sr -Recurse -Directory -ErrorAction SilentlyContinue |
        Where-Object {
            $_.Name -eq "controls" -or
            $_.FullName -match '\\registry\\controls$'
        }
}

# Prefer registry catalog in live Pass4_5, then any consolidated catalog.
$catalog = $catalogCandidates |
    Sort-Object @{
        Expression = {
            if($_.FullName -like "$Pass45\registry\*"){0}
            elseif($_.FullName -notmatch '\\release\\'){1}
            else{2}
        }
    }, FullName |
    Select-Object -First 1

$restored = $false

if($catalog){
    Write-Host "Found consolidated authoritative source:" -ForegroundColor Green
    Write-Host "  $($catalog.FullName)"

    $destRegistry = Join-Path $EMSPath "registry"
    New-Item -ItemType Directory -Path $destRegistry -Force | Out-Null

    $destName = if($catalog.Name -match 'catalog'){"control_catalog.yaml"}else{"control_registry.yaml"}
    $dest = Join-Path $destRegistry $destName

    Copy-Item $catalog.FullName $dest -Force
    Write-Host "Restored to:" -ForegroundColor Green
    Write-Host "  $dest"
    $restored = $true
}
else {
    # Prefer the control directory with the most YAML files.
    $ranked = foreach($d in $controlDirs){
        $count = @(Get-ChildItem $d.FullName -Recurse -File -Include *.yaml,*.yml -ErrorAction SilentlyContinue).Count
        [pscustomobject]@{Path=$d.FullName;Count=$count}
    }

    $sourceDir = $ranked | Sort-Object Count -Descending | Select-Object -First 1

    if($sourceDir -and $sourceDir.Count -gt 0){
        Write-Host "Found one-file-per-control library:" -ForegroundColor Green
        Write-Host "  $($sourceDir.Path)"
        Write-Host "  YAML files: $($sourceDir.Count)"

        $dest = Join-Path $EMSPath "controls"
        if(Test-Path $dest){
            Copy-Item $dest "$dest.pre-wave2a1-control-library.bak" -Recurse -Force
            Remove-Item $dest -Recurse -Force
        }
        New-Item -ItemType Directory -Path $dest -Force | Out-Null
        Copy-Item "$($sourceDir.Path)\*" $dest -Recurse -Force
        $restored = $true
    }
}

if(-not $restored){
    Write-Host ""
    Write-Host "No authoritative control source found in Pass 4.5." -ForegroundColor Red
    Write-Host "Potential control-related files found:" -ForegroundColor Yellow
    Get-ChildItem -Path $Pass45 -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match 'control' } |
        Select-Object -First 100 FullName |
        Format-Table -AutoSize
    throw "Unable to restore authoritative EMS control library."
}

# Validate 80 control IDs from whatever was restored.
$validator = @'
import sys, re, yaml
from pathlib import Path

root=Path(sys.argv[1])
ids=set()

def walk(x):
    if isinstance(x,dict):
        cid=x.get("control_id") or x.get("id")
        if isinstance(cid,str) and re.fullmatch(r"EMS-CTRL-\d{3}",cid):
            ids.add(cid)
        for v in x.values():
            walk(v)
    elif isinstance(x,list):
        for v in x:
            walk(v)

for p in root.rglob("*.yaml"):
    try:
        walk(yaml.safe_load(p.read_text(encoding="utf-8")))
    except Exception:
        pass
for p in root.rglob("*.yml"):
    try:
        walk(yaml.safe_load(p.read_text(encoding="utf-8")))
    except Exception:
        pass

expected={f"EMS-CTRL-{i:03d}" for i in range(1,81)}
missing=sorted(expected-ids)
print(f"Discovered control IDs: {len(ids)}")
if missing:
    print("Missing:", ", ".join(missing))
    raise SystemExit(1)
print("PASS: all 80 authoritative EMS control IDs are present.")
'@

$validatorPath = Join-Path $env:TEMP "validate_ems_control_library.py"
Set-Content $validatorPath $validator -Encoding UTF8

& $py $validatorPath $EMSPath
if($LASTEXITCODE-ne 0){
    throw "Restored control library does not contain all 80 EMS controls."
}

if($Commit){
    Push-Location $EMSPath
    try {
        git add registry controls 2>$null
        git commit -m "Wave 2A.1: restore authoritative EMS control library"
        if($LASTEXITCODE-ne 0){
            Write-Host "No new control-library changes to commit, or commit failed." -ForegroundColor Yellow
        } else {
            git push
            if($LASTEXITCODE-ne 0){ throw "Git push failed." }
        }
    }
    finally { Pop-Location }
}

Write-Host ""
Write-Host "Authoritative EMS control library restored and validated." -ForegroundColor Green
Write-Host ""
Write-Host "Next:"
Write-Host "  .\scripts\Find-EMSControlSources.ps1"
Write-Host "  .\scripts\Run-ScopeExceptionResolver.ps1"
Write-Host "  .\scripts\Show-ScopeExceptionResolution.ps1"
