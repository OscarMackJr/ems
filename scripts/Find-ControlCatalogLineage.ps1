[CmdletBinding()]
param([string]$SearchRoot="C:\temp\standars")

Get-ChildItem -Path $SearchRoot -Recurse -File -Include *.yaml,*.yml -ErrorAction SilentlyContinue |
    Where-Object {
        $_.FullName -notmatch '\\.venv\\' -and
        $_.FullName -notmatch '\\site-packages\\' -and
        $_.FullName -notmatch '\\generated\\' -and
        (
            $_.Name -match 'control.*(catalog|registry).*\.ya?ml$' -or
            $_.FullName -match '\\registry\\.*control.*\.ya?ml$'
        )
    } |
    Select-Object FullName |
    Sort-Object FullName |
    Format-Table -AutoSize
