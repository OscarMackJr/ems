[CmdletBinding()]
param(
    [string]$EMSPath = "C:\temp\standars\ems",
    [string]$SearchRoot = "C:\temp\standars",
    [switch]$Commit
)

$ErrorActionPreference = "Stop"

if(-not(Test-Path $EMSPath)){ throw "EMS repository not found: $EMSPath" }
if(-not(Test-Path $SearchRoot)){ throw "Search root not found: $SearchRoot" }

$py = Join-Path $EMSPath ".venv\Scripts\python.exe"
if(-not(Test-Path $py)){ $py = "python" }

$outDir = Join-Path $EMSPath "generated\wave2\control-source-recovery"
New-Item -ItemType Directory -Path $outDir -Force | Out-Null

Write-Host "Searching EMS development lineage for authoritative control sources..." -ForegroundColor Cyan
Write-Host "Search root: $SearchRoot"

# Find plausible YAML sources while excluding Python environments and generated evidence.
$candidates = Get-ChildItem -Path $SearchRoot -Recurse -File -Include *.yaml,*.yml -ErrorAction SilentlyContinue |
    Where-Object {
        $_.FullName -notmatch '\\.venv\\' -and
        $_.FullName -notmatch '\\site-packages\\' -and
        $_.FullName -notmatch '\\generated\\' -and
        (
            $_.Name -match 'control.*(catalog|registry).*\.ya?ml$' -or
            $_.FullName -match '\\registry\\.*control.*\.ya?ml$'
        ) -and
        $_.Name -notmatch 'scope|taxonomy|mapping'
    }

if(-not $candidates){
    throw "No candidate YAML control sources found under $SearchRoot"
}

$validator = @'
import sys, re, json, yaml
from pathlib import Path

def walk(x, ids, named):
    if isinstance(x, dict):
        cid=x.get("control_id") or x.get("id")
        if isinstance(cid,str) and re.fullmatch(r"EMS-CTRL-\d{3}",cid):
            ids.add(cid)
            name=x.get("control_name") or x.get("name") or x.get("title")
            if isinstance(name,str) and name.strip():
                named.add(cid)
        for v in x.values():
            walk(v,ids,named)
    elif isinstance(x,list):
        for v in x:
            walk(v,ids,named)

results=[]
for raw in sys.argv[1:]:
    p=Path(raw)
    ids=set(); named=set()
    try:
        d=yaml.safe_load(p.read_text(encoding="utf-8"))
        walk(d,ids,named)
        results.append({
            "path":str(p),
            "control_id_count":len(ids),
            "named_control_count":len(named),
            "has_all_80":len(ids)==80,
            "missing":[f"EMS-CTRL-{i:03d}" for i in range(1,81) if f"EMS-CTRL-{i:03d}" not in ids]
        })
    except Exception as e:
        results.append({"path":str(p),"error":str(e),"control_id_count":0,"named_control_count":0,"has_all_80":False})

print(json.dumps(results,indent=2))
'@

$validatorPath = Join-Path $outDir "Validate-ControlSourceCandidates.py"
Set-Content $validatorPath $validator -Encoding UTF8

$jsonPath = Join-Path $outDir "control_source_candidates.json"
$args = @($validatorPath) + @($candidates.FullName)
$resultText = & $py @args
if($LASTEXITCODE-ne 0){ throw "Candidate validation failed." }

$resultText | Set-Content $jsonPath -Encoding UTF8
$results = $resultText | ConvertFrom-Json

$ranked = $results |
    Sort-Object `
        @{Expression={ if($_.has_all_80){0}else{1} }}, `
        @{Expression={ -[int]$_.named_control_count }}, `
        @{Expression={ -[int]$_.control_id_count }}, `
        path

Write-Host ""
Write-Host "Candidate control sources:" -ForegroundColor Cyan
$ranked |
    Select-Object path,control_id_count,named_control_count,has_all_80 |
    Format-Table -AutoSize

$winner = $ranked | Where-Object has_all_80 -eq $true | Select-Object -First 1

if(-not $winner){
    Write-Host ""
    Write-Host "No single candidate contains all 80 controls." -ForegroundColor Yellow
    Write-Host "Best candidates were written to:"
    Write-Host "  $jsonPath"
    throw "No authoritative 80-control source could be validated."
}

Write-Host ""
Write-Host "Validated authoritative control source:" -ForegroundColor Green
Write-Host "  $($winner.path)"
Write-Host "  Control IDs: $($winner.control_id_count)"
Write-Host "  Named controls: $($winner.named_control_count)"

$destDir = Join-Path $EMSPath "registry"
New-Item -ItemType Directory -Path $destDir -Force | Out-Null
$dest = Join-Path $destDir "control_catalog.yaml"

$sourcePath = [System.IO.Path]::GetFullPath([string]$winner.path)
$destPath   = [System.IO.Path]::GetFullPath($dest)

if($sourcePath -ieq $destPath){
    Write-Host ""
    Write-Host "Authoritative catalog is already present in the EMS repository." -ForegroundColor Green
    Write-Host "  $destPath"
    Write-Host "Skipping copy; continuing with final validation."
}
else {
    if(Test-Path $destPath){
        Copy-Item $destPath "$destPath.pre-lineage-recovery.bak" -Force
    }

    Copy-Item $sourcePath $destPath -Force

    Write-Host ""
    Write-Host "Restored authoritative catalog:" -ForegroundColor Green
    Write-Host "  $destPath"
}

# Final validation of restored destination.
$checkText = & $py $validatorPath $dest
$check = $checkText | ConvertFrom-Json
if(-not $check[0].has_all_80){
    throw "Restored catalog failed final 80-control validation."
}

Write-Host ""
Write-Host "Restored authoritative catalog:" -ForegroundColor Green
Write-Host "  $dest"

if($Commit){
    Push-Location $EMSPath
    try {
        git add registry/control_catalog.yaml
        git commit -m "Wave 2A.1: restore authoritative 80-control catalog"
        if($LASTEXITCODE -eq 0){
            git push
            if($LASTEXITCODE-ne 0){ throw "Git push failed." }
        } else {
            Write-Host "No changes committed." -ForegroundColor Yellow
        }
    }
    finally { Pop-Location }
}

Write-Host ""
Write-Host "Next:" -ForegroundColor Cyan
Write-Host "  .\scripts\Find-EMSControlSources.ps1"
Write-Host "  .\scripts\Run-ScopeExceptionResolver.ps1"
Write-Host "  .\scripts\Show-ScopeExceptionResolution.ps1"

