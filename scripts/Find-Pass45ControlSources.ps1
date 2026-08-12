[CmdletBinding()]
param([string]$Pass45="C:\temp\standars\Pass4_5")

Write-Host "Control-related sources under Pass 4.5:" -ForegroundColor Cyan
Get-ChildItem -Path $Pass45 -Recurse -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Name -match 'control' -or
        $_.FullName -match '\\controls\\'
    } |
    Select-Object FullName,PSIsContainer |
    Sort-Object FullName |
    Format-Table -AutoSize
