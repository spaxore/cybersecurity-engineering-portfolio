[CmdletBinding()]
param(
    [string]$NmapPath = "C:\Program Files (x86)\Nmap\nmap.exe",
    [switch]$CreateBaseline
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ScopeFile = Join-Path $ProjectRoot "workspace\scope.json"
$DiscoveryFile = Join-Path $ProjectRoot "workspace\live-inventory.json"
$ServiceFile = Join-Path $ProjectRoot "workspace\service-inventory.json"
$BaselineFile = Join-Path $ProjectRoot "workspace\approved-services.json"
$RiskReportFile = Join-Path $ProjectRoot "workspace\risk-report.json"

$ScopeScript = Join-Path $ProjectRoot "src\scope.py"
$DiscoveryScript = Join-Path $ProjectRoot "src\discovery.py"
$ServiceScript = Join-Path $ProjectRoot "src\service_scan.py"
$RiskScript = Join-Path $ProjectRoot "src\risk_report.py"

function Invoke-PythonStep {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    Write-Host ""
    Write-Host "=== $Name ===" -ForegroundColor Cyan
    & python @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$Name failed with exit code $LASTEXITCODE"
    }
}

if (-not (Test-Path -LiteralPath $NmapPath -PathType Leaf)) {
    throw "Nmap executable not found: $NmapPath"
}

foreach ($requiredFile in @(
    $ScopeFile,
    $ScopeScript,
    $DiscoveryScript,
    $ServiceScript,
    $RiskScript
)) {
    if (-not (Test-Path -LiteralPath $requiredFile -PathType Leaf)) {
        throw "Required file not found: $requiredFile"
    }
}

Write-Host "NetMap authorized workflow" -ForegroundColor Green
Write-Host "Nmap:  $NmapPath"
Write-Host "Scope: $ScopeFile"
Write-Host "Only targets declared in scope.json will be scanned."

Invoke-PythonStep "Validate authorized scope" @(
    $ScopeScript,
    "validate",
    "--scope",
    $ScopeFile
)

Invoke-PythonStep "Discover authorized hosts" @(
    $DiscoveryScript,
    "--nmap",
    $NmapPath,
    "--scope",
    $ScopeFile,
    "--output",
    $DiscoveryFile
)

Invoke-PythonStep "Identify services on discovered hosts" @(
    $ServiceScript,
    "--nmap",
    $NmapPath,
    "--scope",
    $ScopeFile,
    "--discovery",
    $DiscoveryFile,
    "--output",
    $ServiceFile,
    "--top-ports",
    "100"
)

if ($CreateBaseline -or -not (Test-Path -LiteralPath $BaselineFile -PathType Leaf)) {
    Invoke-PythonStep "Create or refresh approved service baseline" @(
        $RiskScript,
        "baseline",
        "--inventory",
        $ServiceFile,
        "--baseline",
        $BaselineFile,
        "--output",
        $BaselineFile
    )
}
else {
    Write-Host "Using existing approved baseline: $BaselineFile" -ForegroundColor Yellow
}

Invoke-PythonStep "Classify risks and compare with baseline" @(
    $RiskScript,
    "compare",
    "--inventory",
    $ServiceFile,
    "--baseline",
    $BaselineFile,
    "--output",
    $RiskReportFile
)

Write-Host ""
Write-Host "NetMap workflow completed successfully." -ForegroundColor Green
Write-Host "Discovery inventory: $DiscoveryFile"
Write-Host "Service inventory:   $ServiceFile"
Write-Host "Approved baseline:   $BaselineFile"
Write-Host "Risk report:         $RiskReportFile"
