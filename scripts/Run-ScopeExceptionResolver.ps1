[CmdletBinding()]
param(
    [string]$EMSPath="C:\temp\standars\ems"
)

$ErrorActionPreference="Stop"

$py=Join-Path $EMSPath ".venv\Scripts\python.exe"
if(-not(Test-Path $py)){$py="python"}

$dir=Join-Path $EMSPath "generated\wave2\scope-adjudication"
$reviewed=Join-Path $dir "scope_registry_adjudication_queue.reviewed.csv"
$out=Join-Path $dir "scope_registry_adjudication_queue.resolved.csv"
$exceptions=Join-Path $dir "scope_registry_review_exceptions_resolved.csv"

if(-not(Test-Path $reviewed)){
    throw "Reviewed queue not found: $reviewed"
}

Write-Host "Discovering authoritative EMS control source..." -ForegroundColor Cyan

# Prefer explicit catalog / registry files wherever they exist.
$candidates = Get-ChildItem -Path $EMSPath -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Name -in @(
            "control_catalog.yaml",
            "control_catalog.yml",
            "control_registry.yaml",
            "control_registry.yml"
        )
    } |
    Sort-Object @{
        Expression = {
            if($_.FullName -match "\\registry\\"){0}
            elseif($_.FullName -match "\\releases\\"){1}
            else{2}
        }
    }, FullName

$catalog = $candidates | Select-Object -First 1

if($catalog){
    Write-Host "Using authoritative control source:" -ForegroundColor Green
    Write-Host "  $($catalog.FullName)"

    & $py (Join-Path $EMSPath "scripts\Resolve-ScopeReviewExceptions.py") `
        --catalog $catalog.FullName `
        --reviewed-queue $reviewed `
        --out $out `
        --exceptions $exceptions

    if($LASTEXITCODE-ne 0){
        throw "Scope exception resolution failed."
    }
}
else {
    # Fallback: synthesize a temporary catalog from one-YAML-per-control files.
    $controlDirCandidates=@(
        (Join-Path $EMSPath "controls"),
        (Join-Path $EMSPath "registry\controls")
    ) | Where-Object { Test-Path $_ }

    $controlDir=$controlDirCandidates | Select-Object -First 1

    if(-not $controlDir){
        Write-Host ""
        Write-Host "No control catalog/registry file or controls directory was found." -ForegroundColor Red
        Write-Host ""
        Write-Host "Searched for:"
        Write-Host "  control_catalog.yaml / .yml"
        Write-Host "  control_registry.yaml / .yml"
        Write-Host "  controls\"
        Write-Host "  registry\controls\"
        throw "Authoritative EMS control source not found."
    }

    Write-Host "No consolidated catalog found." -ForegroundColor Yellow
    Write-Host "Building temporary catalog from:"
    Write-Host "  $controlDir"

    $tempCatalog=Join-Path $dir "discovered_control_catalog.yaml"

    $builder=@'
import sys
from pathlib import Path
import yaml

src=Path(sys.argv[1])
out=Path(sys.argv[2])

controls=[]

for p in sorted(list(src.rglob("*.yaml")) + list(src.rglob("*.yml"))):
    try:
        d=yaml.safe_load(p.read_text(encoding="utf-8"))
    except Exception:
        continue

    def walk(x):
        if isinstance(x,dict):
            cid=x.get("control_id") or x.get("id")
            if isinstance(cid,str) and cid.startswith("EMS-CTRL-"):
                controls.append(x)
            for v in x.values():
                walk(v)
        elif isinstance(x,list):
            for v in x:
                walk(v)

    walk(d)

# De-duplicate by control id.
by={}
for c in controls:
    cid=c.get("control_id") or c.get("id")
    by[cid]=c

payload={"controls":[by[k] for k in sorted(by)]}
out.write_text(yaml.safe_dump(payload,sort_keys=False),encoding="utf-8")
print(f"Discovered {len(by)} authoritative control records.")
'@

    $builderPath=Join-Path $dir "Build-DiscoveredControlCatalog.py"
    Set-Content $builderPath $builder -Encoding UTF8

    & $py $builderPath $controlDir $tempCatalog
    if($LASTEXITCODE-ne 0){
        throw "Could not synthesize control catalog."
    }

    if(-not(Test-Path $tempCatalog)){
        throw "Temporary control catalog was not created."
    }

    Write-Host "Using synthesized catalog:" -ForegroundColor Green
    Write-Host "  $tempCatalog"

    & $py (Join-Path $EMSPath "scripts\Resolve-ScopeReviewExceptions.py") `
        --catalog $tempCatalog `
        --reviewed-queue $reviewed `
        --out $out `
        --exceptions $exceptions

    if($LASTEXITCODE-ne 0){
        throw "Scope exception resolution failed."
    }
}

Write-Host ""
Write-Host "Scope exception resolution complete." -ForegroundColor Green
Write-Host "Resolved queue:"
Write-Host "  $out"
Write-Host "Remaining exceptions:"
Write-Host "  $exceptions"
