[CmdletBinding()]
param(
    [string]$EMSPath="C:\temp\standars\ems"
)

$ErrorActionPreference="Stop"
$dir=Join-Path $EMSPath "generated\wave2\scope-adjudication"
$src=Join-Path $dir "scope_registry_adjudication_queue.reviewed.csv"
$dst=Join-Path $dir "scope_registry_adjudication_queue.csv"
$exceptions=Join-Path $dir "scope_registry_review_exceptions.csv"

if(-not(Test-Path $src)){throw "Reviewed queue not found: $src"}

$ex=@()
if(Test-Path $exceptions){$ex=Import-Csv $exceptions}
if($ex.Count -gt 0){
    Write-Host "Cannot promote reviewed queue yet; $($ex.Count) controls remain DEFERRED." -ForegroundColor Yellow
    $ex | Select-Object control_id,control_name,current_scope,not_evaluated_row_count,reason | Format-Table -AutoSize
    throw "Resolve scope-review exceptions before promotion."
}

Copy-Item $dst "$dst.pre-automated-review.bak" -Force
Copy-Item $src $dst -Force

Write-Host "Reviewed scope queue promoted to authoritative adjudication queue." -ForegroundColor Green
