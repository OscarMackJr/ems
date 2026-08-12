[CmdletBinding(SupportsShouldProcess)]
param([string]$Org="OscarMackJr",[string]$Repository="nono",[string]$EvidenceDir="C:\temp\standars\Pass4_5\generated\remediation\EMS-CTRL-013")
$ErrorActionPreference="Stop"
New-Item -ItemType Directory -Force -Path $EvidenceDir|Out-Null
$full="$Org/$Repository";$name="EMS Release Tag Immutability"
gh auth status|Out-Null
if($LASTEXITCODE-ne 0){throw "gh auth required"}
$existingRaw=gh api "repos/$full/rulesets?targets=tag" 2>&1;$code=$LASTEXITCODE
if($code-ne 0){
 $msg=$existingRaw -join "`n"
 @{repository=$full;status=if($msg-match "403|Upgrade|plan"){"EXCEPTION"}else{"FAIL"};reason=$msg}|ConvertTo-Json -Depth 10|Set-Content "$EvidenceDir\result.json"
 if($msg-match "403|Upgrade|plan"){Write-Host "Rulesets unavailable on current plan." -ForegroundColor Yellow;return}
 throw $msg
}
$existing=$existingRaw|ConvertFrom-Json
if($existing|Where-Object{$_.name-eq$name -and $_.target-eq"tag"}){Write-Host "Ruleset already exists." -ForegroundColor Green;return}
$payload=@{
 name=$name;target="tag";enforcement="active";
 bypass_actors=@(@{actor_id=1;actor_type="OrganizationAdmin";bypass_mode="always"});
 conditions=@{ref_name=@{include=@("refs/tags/v*","refs/tags/[0-9]*");exclude=@()}};
 rules=@(@{type="update";parameters=@{update_allows_fetch_and_merge=$false}},@{type="deletion"})
}
$path="$EvidenceDir\create-ruleset-payload.json";$payload|ConvertTo-Json -Depth 20|Set-Content $path
if($PSCmdlet.ShouldProcess($full,"Create active release-tag immutability ruleset")){
 $result=gh api --method POST "repos/$full/rulesets" --input $path 2>&1;$code=$LASTEXITCODE
 if($code-ne 0){
  $msg=$result -join "`n"
  @{repository=$full;status=if($msg-match "403|Upgrade|plan"){"EXCEPTION"}else{"FAIL"};reason=$msg}|ConvertTo-Json -Depth 10|Set-Content "$EvidenceDir\result.json"
  if($msg-match "403|Upgrade|plan"){Write-Host "Ruleset creation unavailable on current plan." -ForegroundColor Yellow;return}
  throw $msg
 }
 ($result -join "`n")|Set-Content "$EvidenceDir\ruleset-created.json"
 Write-Host "Created $name for $full." -ForegroundColor Green
}
