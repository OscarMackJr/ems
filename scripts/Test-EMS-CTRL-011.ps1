[CmdletBinding()]
param([string]$Org="OscarMackJr")
$repos=gh repo list $Org --limit 1000 --json nameWithOwner,defaultBranchRef|ConvertFrom-Json
$results=@()
foreach($r in $repos){
 $repo=$r.nameWithOwner;$branch=$r.defaultBranchRef.name
 $present=$false;$loc=$null
 foreach($c in @(".github/CODEOWNERS","CODEOWNERS","docs/CODEOWNERS")){
  gh api "repos/$repo/contents/$c" 2>$null|Out-Null
  if($LASTEXITCODE -eq 0){$present=$true;$loc=$c;break}
 }
 $pr=$false;$co=$false;$status="NOT_EVALUATED"
 if(-not $present){$status="FAIL"}
 elseif($branch){
  $raw=gh api "repos/$repo/branches/$branch/protection" 2>$null
  if($LASTEXITCODE -eq 0 -and $raw){
   $p=$raw|ConvertFrom-Json
   $pr=($null -ne $p.required_pull_request_reviews)
   if($pr){$co=[bool]$p.required_pull_request_reviews.require_code_owner_reviews}
   $status=if($pr -and $co){"PASS"}else{"WARNING"}
  } else {$status="WARNING"}
 }
 $results += [pscustomobject]@{Repository=$repo;CodeownersLocation=$loc;CODEOWNERSPresent=$present;PullRequestRequired=$pr;CodeOwnerReviewRequired=$co;EMS_CTRL_011=$status}
}
$results|Format-Table -AutoSize
