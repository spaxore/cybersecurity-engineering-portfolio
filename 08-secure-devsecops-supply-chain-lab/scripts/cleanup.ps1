$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Remove-Item ".\reports\trivy-image.json" -Force -ErrorAction SilentlyContinue
Remove-Item ".\reports\sbom.cdx.json" -Force -ErrorAction SilentlyContinue
Remove-Item ".\reports\gitleaks.json" -Force -ErrorAction SilentlyContinue
Remove-Item ".\app\src\__pycache__" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "Generated reports and Python cache removed."
