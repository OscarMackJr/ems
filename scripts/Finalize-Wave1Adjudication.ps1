[CmdletBinding()]
param(
    [string]$Pass45 = "C:\temp\standars\Pass4_5"
)

$ErrorActionPreference = "Stop"
$py = Join-Path $Pass45 ".venv\Scripts\python.exe"
$queue = Join-Path $Pass45 "generated\adjudication\wave1_adjudication_queue.csv"
$outdir = Join-Path $Pass45 "generated\adjudication"

if (-not (Test-Path $queue)) {
    throw "Adjudication queue not found: $queue"
}

& $py `
    (Join-Path $Pass45 "scripts\Finalize-Wave1Adjudication.py") `
    --queue $queue `
    --outdir $outdir

if ($LASTEXITCODE -ne 0) {
    throw "Wave 1 adjudication finalization failed."
}
