$ErrorActionPreference = "Stop"

Set-Location (Split-Path -Parent $PSScriptRoot )

docker compose down --remove-orphans

Write-Host "Project 07 containers stopped and removed."
