[CmdletBinding()]param([string]$Org="OscarMackJr",[string]$Repository="nono")
$full="$Org/$Repository"
$tags=gh api "repos/$full/tags?per_page=100"|ConvertFrom-Json
$rules=gh api "repos/$full/rulesets?targets=tag" 2>$null|ConvertFrom-Json
$active=@($rules|Where-Object{$_.target-eq"tag"-and$_.enforcement-eq"active"})
[pscustomobject]@{Repository=$full;TagCount=@($tags).Count;ActiveTagRulesets=$active.Count;EMS_CTRL_013=if($active.Count-gt0){"PASS"}else{"WARNING"}}|Format-List
