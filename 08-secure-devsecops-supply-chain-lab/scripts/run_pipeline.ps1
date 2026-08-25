$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$reports = Join-Path $root "reports"
New-Item -ItemType Directory -Force $reports | Out-Null

$image = "project08-demo:local"

function Invoke-DockerCheck {
    param(
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [Parameter(Mandatory = $true)][string]$Name
    )

    Write-Host "`n=== $Name ===" -ForegroundColor Cyan
    & docker @Arguments

    if ($LASTEXITCODE -ne 0) {
        throw "$Name failed with exit code $LASTEXITCODE"
    }
}

Write-Host "Project root: $root"

Invoke-DockerCheck `
    -Name "Build demo container" `
    -Arguments @("build", "--tag", $image, ".\app")

$volume = "${root}:/repo"

Invoke-DockerCheck `
    -Name "Gitleaks directory scan" `
    -Arguments @(
        "run", "--rm",
        "-v", $volume,
        "zricethezav/gitleaks:latest",
        "dir",
        "/repo",
        "--config=/repo/.gitleaks.toml",
        "--no-banner"
    )

Invoke-DockerCheck `
    -Name "Semgrep source scan" `
    -Arguments @(
        "run", "--rm",
        "-v", $volume,
        "semgrep/semgrep:latest",
        "semgrep",
        "--config=/repo/.semgrep/rules.yml",
        "/repo/app/src"
    )

Write-Host "`n=== Trivy container scan ===" -ForegroundColor Cyan
& docker run --rm `
    -v /var/run/docker.sock:/var/run/docker.sock `
    -v $volume `
    aquasec/trivy:latest image `
    --format json `
    --output /repo/reports/trivy-image.json `
    --severity HIGH,CRITICAL `
    --ignore-unfixed `
    --exit-code 0 `
    $image

if ($LASTEXITCODE -ne 0) {
    throw "Trivy container scan could not complete."
}

Write-Host "Trivy report written to reports/trivy-image.json"

Write-Host "`n=== Syft SBOM generation ===" -ForegroundColor Cyan
& docker run --rm `
    -v $volume `
    anchore/syft:latest `
    dir:/repo/app `
    -o cyclonedx-json=/repo/reports/sbom.cdx.json

if ($LASTEXITCODE -ne 0) {
    throw "SBOM generation failed."
}

Write-Host "SBOM written to reports/sbom.cdx.json"

Write-Host "`n=== OPA policy evaluation ===" -ForegroundColor Cyan
$opaResult = & docker run --rm `
    -v $volume `
    openpolicyagent/opa:latest eval `
    --format raw `
    --data /repo/policies/supply-chain.rego `
    --input /repo/policies/policy-input.json `
    "count(data.supplychain.deny) > 0"

$opaExitCode = $LASTEXITCODE
$opaText = (($opaResult | ForEach-Object { $_.ToString() }) -join "`n").Trim()

if ($opaExitCode -ne 0) {
    throw "OPA policy evaluation could not complete. Exit code: $opaExitCode"
}

Write-Host "Policy violations present: $opaText"

if ($opaText -eq "true") {
    throw "OPA policy gate failed because policy violations were detected."
}

if ($opaText -ne "false") {
    throw "OPA returned an unexpected result: $opaText"
}

Write-Host "OPA policy gate passed with zero violations." -ForegroundColor Green
Write-Host "`nPipeline completed successfully." -ForegroundColor Green
Write-Host "Reports are available under: $reports"
