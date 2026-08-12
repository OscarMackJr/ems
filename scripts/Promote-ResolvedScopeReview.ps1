[CmdletBinding()]
param([string]$EMSPath="C:\temp\standars\ems")
$ErrorActionPreference="Stop"
$dir=Join-Path $EMSPath "generated\wave2\scope-adjudication"
$src=Join-Path $dir "scope_registry_adjudication_queue.resolved.csv"
$dst=Join-Path $dir "scope_registry_adjudication_queue.csv"
if(-not(Test-Path $src)){throw "Resolved queue not found."}
$q=Import-Csv $src
$deferred=@($q|Where-Object reviewer_decision -eq "DEFER")
if($deferred.Count -gt 0){
    $deferred|Select-Object control_id,control_name,current_scope,proposed_scope|Format-Table -AutoSize
    throw "$($deferred.Count) deferred control(s) remain. Do not promote yet."
}
Copy-Item $dst "$dst.pre-exception-resolution.bak" -Force
Copy-Item $src $dst -Force
Write-Host "Resolved scope review promoted." -ForegroundColor Green
