[CmdletBinding(SupportsShouldProcess)]
param(
 [Parameter(Mandatory=$true)][string]$TeamSlug,
 [string]$Org="OscarMackJr",
 [string[]]$Repositories=@("bluto","fiskroad","hometown","nono","olive","popeye")
)
$ErrorActionPreference="Stop"
$template=Join-Path (Split-Path -Parent $PSScriptRoot) ".github\CODEOWNERS"
$content=(Get-Content $template -Raw).Replace("TEAM_SLUG",$TeamSlug)
$encoded=[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($content))
foreach($name in $Repositories){
 $repo="$Org/$name"
 $meta=gh api "repos/$repo"|ConvertFrom-Json
 $base=$meta.default_branch
 $ref=gh api "repos/$repo/git/ref/heads/$base"|ConvertFrom-Json
 $branch="ems/codeowners-baseline"
 gh api "repos/$repo/git/ref/heads/$branch" 2>$null | Out-Null
 if($LASTEXITCODE -ne 0 -and $PSCmdlet.ShouldProcess($repo,"Create $branch")){
   gh api --method POST "repos/$repo/git/refs" -f ref="refs/heads/$branch" -f sha="$($ref.object.sha)"|Out-Null
 }
 if($PSCmdlet.ShouldProcess($repo,"Add .github/CODEOWNERS")){
   gh api --method PUT "repos/$repo/contents/.github/CODEOWNERS" -f message="EMS: establish CODEOWNERS baseline" -f content="$encoded" -f branch="$branch"|Out-Null
   $existing=gh pr list --repo $repo --head $branch --state open --json number --limit 1|ConvertFrom-Json
   if(-not $existing){ gh pr create --repo $repo --base $base --head $branch --title "EMS: establish CODEOWNERS baseline" --body "Adds CODEOWNERS for EMS-CTRL-011. After merge, require PR and Code Owner review on the protected default branch."|Out-Null }
 }
}
Write-Host "Prepared CODEOWNERS PRs." -ForegroundColor Green
