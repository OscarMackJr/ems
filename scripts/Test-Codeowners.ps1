[CmdletBinding()]
param([string]$Org="OscarMackJr")
$repos=gh repo list $Org --limit 1000 --json nameWithOwner,defaultBranchRef|ConvertFrom-Json
$result=@()
foreach($r in $repos){
 $repo=$r.nameWithOwner;$branch=$r.defaultBranchRef.name
 gh api "repos/$repo/contents/.github/CODEOWNERS" 2>$null|Out-Null
 $present=$LASTEXITCODE -eq 0
 $raw=gh api "repos/$repo/branches/$branch/protection" 2>$null
 $protected=$LASTEXITCODE -eq 0
 $pr=$false;$ownerReview=$false
 if($protected){
  $p=$raw|ConvertFrom-Json
  if($p.required_pull_request_reviews){
   $pr=$true
   $ownerReview=[bool]$p.required_pull_request_reviews.require_code_owner_reviews
  }
 }
 $status=if($present -and $pr -and $ownerReview){"PASS"}elseif($present){"WARNING"}else{"FAIL"}
 $result += [pscustomobject]@{Repository=$repo;CODEOWNERS=$present;PullRequestRequired=$pr;CodeOwnerReviewRequired=$ownerReview;EMS_CTRL_011=$status}
}
$result|Format-Table -AutoSize
