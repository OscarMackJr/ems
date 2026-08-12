[CmdletBinding()]
param([string]$Pass45="C:\temp\standars\Pass4_5")

$ErrorActionPreference="Stop"
$py=Join-Path $Pass45 ".venv\Scripts\python.exe"
$v1=Join-Path $Pass45 "generated\collector-refinement\refined_observations.json"
$v2=Join-Path $Pass45 "generated\collector-refinement-v2\refined_observations_v2.json"
$out=Join-Path $Pass45 "generated\collector-refinement-v2\collector_refinement_v1_vs_v2.csv"

if(-not(Test-Path $v1)){throw "v1 refined observations not found: $v1"}
if(-not(Test-Path $v2)){throw "v2 refined observations not found: $v2"}

& $py (Join-Path $Pass45 "scripts\Compare-CollectorRefinement.py") `
 --v1 $v1 `
 --v2 $v2 `
 --out $out

if($LASTEXITCODE-ne 0){throw "Collector comparison failed."}
