$ErrorActionPreference = "Stop"

Set-Location (Split-Path -Parent $PSScriptRoot)

if (-not (Test-Path ".\keycloak\cloudsec-realm.json")) {
    Copy-Item ".\keycloak\cloudsec-realm.example.json" ".\keycloak\cloudsec-realm.json"
    Write-Warning "A local realm file was created from the example. Replace placeholder passwords before using the lab."
}

if (-not (Test-Path ".\.env")) {
    Copy-Item ".\.env.example" ".\.env"
    Write-Warning "A local .env file was created from the example. Replace the placeholder bootstrap password before using the lab."
}

docker compose up -d
docker compose ps

$ready = $false

for ($i = 0; $i -lt 30; $i++) {
    try {
        $response = Invoke-WebRequest `
            -Uri "http://localhost:8080/realms/cloudsec/.well-known/openid-configuration" `
            -UseBasicParsing `
            -TimeoutSec 5

        if ($response.StatusCode -eq 200 ) {
            $ready = $true
            break
        }
    }
    catch {
        Start-Sleep -Seconds 2
    }
}

if (-not $ready) {
    docker compose logs --tail=100 keycloak
    throw "Keycloak did not become ready within the expected time."
}

Write-Host "Keycloak is ready at http://localhost:8080"
