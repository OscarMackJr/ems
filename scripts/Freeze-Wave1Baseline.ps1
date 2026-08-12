[CmdletBinding()]
param([string]$Pass45="C:\temp\standars\Pass4_5")
$ErrorActionPreference="Stop"
$py=Join-Path $Pass45 ".venv\Scripts\python.exe"
$config=Join-Path $Pass45 "registry\wave1_closeout_config.json"
$out=Join-Path $Pass45 "release\Pass4_5_Wave1_Baseline"
& $py (Join-Path $Pass45 "scripts\Freeze-Wave1Baseline.py") --pass45 $Pass45 --config $config --outdir $out
if($LASTEXITCODE-ne 0){throw "Wave 1 freeze failed."}
