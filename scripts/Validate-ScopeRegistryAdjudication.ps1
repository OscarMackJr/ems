[CmdletBinding()]
param([string]$EMSPath="C:\temp\standars\ems",[switch]$RequireComplete)
$ErrorActionPreference="Stop"
$py=Join-Path $EMSPath ".venv\Scripts\python.exe"
if(-not(Test-Path $py)){$py="python"}
$q=Join-Path $EMSPath "generated\wave2\scope-adjudication\scope_registry_adjudication_queue.csv"
$r=Join-Path $EMSPath "generated\wave2\scope-adjudication\scope_registry_adjudication_validation.json"
$args=@((Join-Path $EMSPath "scripts\Validate-ScopeRegistryAdjudication.py"),"--queue",$q,"--report",$r)
if($RequireComplete){$args+="--require-complete"}
& $py @args
if($LASTEXITCODE-ne 0){throw "Scope adjudication validation failed."}
