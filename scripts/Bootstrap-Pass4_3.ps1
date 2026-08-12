[CmdletBinding()]
param()
$ErrorActionPreference="Stop"
$root=Split-Path -Parent $PSScriptRoot
$venv=Join-Path $root ".venv"
if (-not (Test-Path $venv)) { python -m venv $venv }
$py=Join-Path $venv "Scripts\python.exe"
& $py -m pip install --upgrade pip
& $py -m pip install -r (Join-Path $root "requirements.txt")
if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed." }
Write-Host "Pass4_3 environment ready." -ForegroundColor Green
