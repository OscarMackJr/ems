[CmdletBinding()]
param([string]$Pass45 = "C:\temp\standars\Pass4_5")

$ErrorActionPreference = "Stop"

$builder = Join-Path $Pass45 "scripts\Build-Wave1AdjudicationQueue.py"
$rules   = Join-Path $Pass45 "registry\adjudication_rules.json"
$py      = Join-Path $Pass45 ".venv\Scripts\python.exe"

foreach($p in @($builder,$rules,$py)){
    if(-not(Test-Path $p)){ throw "Required file missing: $p" }
}

Copy-Item $builder "$builder.pre-na-routing-fix.bak" -Force
Copy-Item $rules   "$rules.pre-na-routing-fix.bak" -Force

# Patch JSON rules.
$r = Get-Content $rules -Raw | ConvertFrom-Json
$r.default_dispositions.WARNING = "COLLECTOR_REVIEW"
$r.default_dispositions.FAIL = "REMEDIATE"
$r.default_dispositions.NOT_APPLICABLE = "CONFIRM_NA"

# Add status-specific overrides for release controls.
foreach($id in @("EMS-CTRL-013","EMS-CTRL-035","EMS-CTRL-036","EMS-CTRL-038")){
    if(-not $r.control_rules.$id){
        $r.control_rules | Add-Member -NotePropertyName $id -NotePropertyValue ([pscustomobject]@{})
    }
}
$r.control_rules.'EMS-CTRL-013' | Add-Member -Force NoteProperty warning_disposition "REMEDIATE"
$r.control_rules.'EMS-CTRL-013' | Add-Member -Force NoteProperty not_applicable_disposition "CONFIRM_NA"

$r.control_rules.'EMS-CTRL-035' | Add-Member -Force NoteProperty warning_disposition "POLICY_REVIEW"
$r.control_rules.'EMS-CTRL-035' | Add-Member -Force NoteProperty not_applicable_disposition "CONFIRM_NA"

$r.control_rules.'EMS-CTRL-036' | Add-Member -Force NoteProperty warning_disposition "POLICY_REVIEW"
$r.control_rules.'EMS-CTRL-036' | Add-Member -Force NoteProperty not_applicable_disposition "CONFIRM_NA"

$r.control_rules.'EMS-CTRL-038' | Add-Member -Force NoteProperty warning_disposition "POLICY_REVIEW"
$r.control_rules.'EMS-CTRL-038' | Add-Member -Force NoteProperty not_applicable_disposition "CONFIRM_NA"

$r | ConvertTo-Json -Depth 30 | Set-Content $rules -Encoding UTF8

# Patch builder safely by replacing the single assignment line.
$text = Get-Content $builder -Raw

$old = '        disposition = c_rule.get("default_disposition", default_disp.get(status, "COLLECTOR_REVIEW"))'

$new = @'
        if status == "NOT_APPLICABLE":
            disposition = c_rule.get("not_applicable_disposition", default_disp.get("NOT_APPLICABLE", "CONFIRM_NA"))
        elif status == "WARNING":
            disposition = c_rule.get("warning_disposition", c_rule.get("default_disposition", default_disp.get("WARNING", "COLLECTOR_REVIEW")))
            if disposition == "CONFIRM_NA":
                disposition = "COLLECTOR_REVIEW"
        elif status == "FAIL":
            disposition = c_rule.get("fail_disposition", c_rule.get("default_disposition", default_disp.get("FAIL", "REMEDIATE")))
            if disposition == "CONFIRM_NA":
                disposition = "REMEDIATE"
        else:
            disposition = default_disp.get(status, "COLLECTOR_REVIEW")
'@

if(-not $text.Contains($old)){
    Copy-Item "$builder.pre-na-routing-fix.bak" $builder -Force
    Copy-Item "$rules.pre-na-routing-fix.bak" $rules -Force
    throw "Expected disposition assignment was not found; originals restored."
}

$text = $text.Replace($old,$new.TrimEnd())
Set-Content $builder $text -Encoding UTF8

& $py -m py_compile $builder
if($LASTEXITCODE -ne 0){
    Copy-Item "$builder.pre-na-routing-fix.bak" $builder -Force
    Copy-Item "$rules.pre-na-routing-fix.bak" $rules -Force
    throw "Patched builder failed syntax validation; originals restored."
}

Write-Host "N/A routing patch applied successfully." -ForegroundColor Green
Write-Host "Rerun: .\scripts\Run-Wave1Adjudication.ps1"
