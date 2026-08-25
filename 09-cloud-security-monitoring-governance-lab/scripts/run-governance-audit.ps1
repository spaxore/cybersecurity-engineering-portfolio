$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$python = (Get-Command python -ErrorAction Stop).Source
$auditor = Join-Path $root "src\audit.py"
$rules = Join-Path $root "rules\governance-rules.json"
$baseline = Join-Path $root "baseline\approved-baseline.json"
$reports = Join-Path $root "reports"
$fixtures = Join-Path $root "fixtures"

New-Item -ItemType Directory -Force $reports | Out-Null

function Invoke-GovernanceAudit {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$StateFile,
        [Parameter(Mandatory = $true)][bool]$ExpectFindings
    )

    $jsonReport = Join-Path $reports "$Name-audit.json"
    $markdownReport = Join-Path $reports "$Name-audit.md"

    Write-Host "`n=== $Name governance audit ===" -ForegroundColor Cyan

    $arguments = @(
        $auditor,
        "--baseline", $baseline,
        "--state", $StateFile,
        "--rules", $rules,
        "--output-json", $jsonReport,
        "--output-md", $markdownReport
    )

    if ($ExpectFindings) {
        $arguments += "--fail-on-findings"
    }

    & $python @arguments
    $exitCode = $LASTEXITCODE

    if ($ExpectFindings -and $exitCode -ne 1) {
        throw "$Name was expected to fail with findings, but returned exit code $exitCode."
    }

    if (-not $ExpectFindings -and $exitCode -ne 0) {
        throw "$Name was expected to pass, but returned exit code $exitCode."
    }

    Write-Host "$Name audit returned the expected exit code: $exitCode" -ForegroundColor Green
}

Set-Location $root

Invoke-GovernanceAudit `
    -Name "compliant" `
    -StateFile (Join-Path $fixtures "compliant-state.json") `
    -ExpectFindings $false

Invoke-GovernanceAudit `
    -Name "noncompliant" `
    -StateFile (Join-Path $fixtures "noncompliant-state.json") `
    -ExpectFindings $true

Invoke-GovernanceAudit `
    -Name "drifted" `
    -StateFile (Join-Path $fixtures "drifted-state.json") `
    -ExpectFindings $true

Write-Host "`nAll governance audit scenarios completed as expected." -ForegroundColor Green
Write-Host "Reports are available under: $reports"
