[CmdletBinding()]
param(
    [string]$Config = (Join-Path (Split-Path -Parent $PSScriptRoot) "config\github_governance.yaml"),
    [string]$Output = (Join-Path (Split-Path -Parent $PSScriptRoot) "generated\CODEOWNERS")
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$py = Join-Path $root ".venv\Scripts\python.exe"

if (-not (Test-Path $py)) {
    throw "Virtual environment not found. Run .\scripts\Bootstrap.ps1 first."
}

& $py (Join-Path $PSScriptRoot "Generate-Codeowners.py") `
    --config $Config `
    --template (Join-Path $root "templates\CODEOWNERS.j2") `
    --out $Output

if ($LASTEXITCODE -ne 0) {
    throw "CODEOWNERS generation failed."
}
