$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$python = "python"
$resilience = Join-Path $projectRoot "src\resilience.py"
$backup = Join-Path $projectRoot "src\backup.py"
$recovery = Join-Path $projectRoot "src\recovery.py"
$tamper = Join-Path $projectRoot "src\tamper.py"

$workspace = Join-Path $projectRoot "workspace"
$backupDir = Join-Path $projectRoot "artifacts\backups"
$tamperedDir = Join-Path $projectRoot "artifacts\tampered"
$reports = Join-Path $projectRoot "reports"

New-Item -ItemType Directory -Force `
    $workspace, $backupDir, $tamperedDir, $reports | Out-Null

function Invoke-PythonStage {
    param(
        [string]$Name,
        [string]$Script,
        [string[]]$Arguments,
        [string]$OutputFile
    )

    Write-Host ""
    Write-Host "=== $Name ==="

    & $python $Script @Arguments 2>&1 |
        Tee-Object -FilePath $OutputFile

    if ($LASTEXITCODE -ne 0) {
        throw "Stage '$Name' failed with exit code ${LASTEXITCODE}."
    }
}

Write-Host "Project root: $projectRoot"

Write-Host ""
Write-Host "=== Clean generated test state ==="
Remove-Item (Join-Path $workspace "active-state.json") -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path $workspace "runtime") -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path $workspace "failure") -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path $workspace "recovery") -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path $backupDir "*.tar.gz") -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path $backupDir "*.manifest.json") -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path $tamperedDir "*") -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path $reports "*.txt") -Force -ErrorAction SilentlyContinue

Invoke-PythonStage `
    "Seed synthetic state" `
    $resilience `
    @("seed", "--workspace", $workspace) `
    (Join-Path $reports "01-seed.txt")

Invoke-PythonStage `
    "Validate healthy state" `
    $resilience `
    @("validate", "--state", (Join-Path $workspace "active-state.json")) `
    (Join-Path $reports "02-healthy-validation.txt")

New-Item -ItemType Directory -Force (Join-Path $workspace "runtime") | Out-Null
Copy-Item `
    (Join-Path $workspace "active-state.json") `
    (Join-Path $workspace "runtime\active-state.json") `
    -Force

Invoke-PythonStage `
    "Create verified backup" `
    $backup `
    @("create", "--state", (Join-Path $workspace "active-state.json"), "--backup-dir", $backupDir) `
    (Join-Path $reports "03-backup-create.txt")

$archive = Get-ChildItem -LiteralPath $backupDir -Filter "*.tar.gz" -File |
    Sort-Object LastWriteTime |
    Select-Object -Last 1

if ($null -eq $archive) {
    throw "No backup archive was created."
}

$manifest = Get-Item "$($archive.FullName).manifest.json"

Invoke-PythonStage `
    "Verify original backup" `
    $backup `
    @("verify", "--backup", $archive.FullName, "--manifest", $manifest.FullName) `
    (Join-Path $reports "04-backup-verification.txt")

Invoke-PythonStage `
    "Simulate controlled failure" `
    $recovery `
    @("simulate-failure", "--workspace", $workspace) `
    (Join-Path $reports "05-failure-simulation.txt")

$recoveryDestination = Join-Path $workspace "recovery"

Invoke-PythonStage `
    "Restore into isolated workspace" `
    $recovery `
    @("restore", "--backup", $archive.FullName, "--manifest", $manifest.FullName, "--destination", $recoveryDestination) `
    (Join-Path $reports "06-restore.txt")

Invoke-PythonStage `
    "Validate restored state" `
    $resilience `
    @("validate", "--state", (Join-Path $recoveryDestination "state.json")) `
    (Join-Path $reports "07-recovery-validation.txt")

$tamperedArchive = Join-Path $tamperedDir "tampered-backup.tar.gz"

Invoke-PythonStage `
    "Create tampered backup copy" `
    $tamper `
    @("--source", $archive.FullName, "--destination", $tamperedArchive) `
    (Join-Path $reports "08-tamper-create.txt")

Write-Host ""
Write-Host "=== Reject tampered backup ==="
& $python $backup verify `
    --backup $tamperedArchive `
    --manifest $manifest.FullName 2>&1 |
    Tee-Object -FilePath (Join-Path $reports "09-tamper-verification.txt")

$tamperExitCode = $LASTEXITCODE
if ($tamperExitCode -ne 1) {
    throw "Tampered backup returned exit code $tamperExitCode instead of expected exit code 1."
}

$summary = @"
Project 10 Resilience Lab Summary

Backup integrity verification: pass
Failure simulation: pass
Restore validation: pass
Tamper rejection: pass

Backup archive: $($archive.Name)
"@

$summary | Set-Content `
    -LiteralPath (Join-Path $reports "resilience-summary.txt") `
    -Encoding UTF8

Write-Host ""
Write-Host "Backup integrity verification: pass"
Write-Host "Failure simulation: pass"
Write-Host "Restore validation: pass"
Write-Host "Tamper rejection: pass"
Write-Host "Resilience lab completed successfully."
Write-Host "Reports written to: $reports"
