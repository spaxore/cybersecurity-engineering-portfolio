$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$workspace = Join-Path $projectRoot "workspace"
$artifacts = Join-Path $projectRoot "artifacts"
$backupDirectory = Join-Path $artifacts "backups"
$reports = Join-Path $projectRoot "reports"

New-Item -ItemType Directory -Force `
    $workspace, `
    $artifacts, `
    $backupDirectory, `
    $reports | Out-Null

Get-ChildItem -LiteralPath $workspace -Force |
    Where-Object { $_.Name -ne ".gitkeep" } |
    Remove-Item -Recurse -Force

Get-ChildItem -LiteralPath $artifacts -Force |
    Where-Object { $_.Name -ne "backups" } |
    Remove-Item -Recurse -Force

Get-ChildItem -LiteralPath $backupDirectory -Force |
    Where-Object { $_.Name -ne ".gitkeep" } |
    Remove-Item -Recurse -Force

Get-ChildItem -LiteralPath $reports -Force |
    Where-Object { $_.Name -ne ".gitkeep" } |
    Remove-Item -Recurse -Force

New-Item -ItemType File -Force `
    "$workspace\.gitkeep", `
    "$backupDirectory\.gitkeep", `
    "$reports\.gitkeep" | Out-Null

Get-ChildItem -LiteralPath (Join-Path $projectRoot "src") `
    -Directory `
    -Filter "__pycache__" `
    -Force `
    -ErrorAction SilentlyContinue |
    Remove-Item -Recurse -Force

Write-Host "Generated Project 10 artifacts, workspaces, reports, and Python cache were removed."
Write-Host "workspace, artifacts\backups, and reports .gitkeep placeholders were preserved."
