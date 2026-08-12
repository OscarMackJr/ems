[CmdletBinding()]
param([string]$EMSPath="C:\temp\standars\ems")

Write-Host "Potential EMS control sources:" -ForegroundColor Cyan

Get-ChildItem -Path $EMSPath -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Name -match 'control.*\.(yaml|yml|json)$' -or
        $_.FullName -match '\\controls\\'
    } |
    Select-Object FullName |
    Sort-Object FullName |
    Format-Table -AutoSize
