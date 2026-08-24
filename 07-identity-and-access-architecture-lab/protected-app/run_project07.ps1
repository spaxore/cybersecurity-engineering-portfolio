$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    py -m venv .venv
}

.\.venv\Scripts\python.exe -m pip install -r requirements.txt

$env:FLASK_SECRET_KEY = "local-development-secret-change-me"
$env:KEYCLOAK_BASE = "http://localhost:8080"
$env:KEYCLOAK_REALM = "cloudsec"
$env:KEYCLOAK_CLIENT_ID = "security-console"
$env:OIDC_REDIRECT_URI = "http://localhost:8000/callback"

.\.venv\Scripts\python.exe app.py
