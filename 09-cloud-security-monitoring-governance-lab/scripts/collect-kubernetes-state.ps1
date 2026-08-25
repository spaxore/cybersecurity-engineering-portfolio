$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$reports = Join-Path $root "reports"
$output = Join-Path $reports "current-snapshot.json"

New-Item -ItemType Directory -Force $reports | Out-Null

if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
    throw "kubectl was not found in PATH."
}

$context = (& kubectl config current-context).Trim()
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($context)) {
    throw "kubectl has no active context."
}

function Get-KubectlJson {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    $raw = & kubectl @Arguments

    if ($LASTEXITCODE -ne 0) {
        throw "kubectl command failed: kubectl $($Arguments -join ' ')"
    }

    $text = ($raw -join "`n").Trim()
    if ([string]::IsNullOrWhiteSpace($text)) {
        return $null
    }

    return $text | ConvertFrom-Json
}

function Test-DropAllCapabilities {
    param([object]$SecurityContext)

    if ($null -eq $SecurityContext) {
        return $false
    }

    if ($null -eq $SecurityContext.capabilities) {
        return $false
    }

    return @($SecurityContext.capabilities.drop) -contains "ALL"
}

function Get-WorkloadSnapshot {
    param([object]$Deployment)

    $podSpec = $Deployment.spec.template.spec
    $container = @($podSpec.containers)[0]
    $containerSecurity = $container.securityContext
    $podSecurity = $podSpec.securityContext

    $runAsNonRoot = $false
    if ($null -ne $containerSecurity -and $null -ne $containerSecurity.runAsNonRoot) {
        $runAsNonRoot = [bool]$containerSecurity.runAsNonRoot
    }
    elseif ($null -ne $podSecurity -and $null -ne $podSecurity.runAsNonRoot) {
        $runAsNonRoot = [bool]$podSecurity.runAsNonRoot
    }

    $allowPrivilegeEscalation = $true
    if ($null -ne $containerSecurity -and $null -ne $containerSecurity.allowPrivilegeEscalation) {
        $allowPrivilegeEscalation = [bool]$containerSecurity.allowPrivilegeEscalation
    }

    $readOnlyRootFilesystem = $false
    if ($null -ne $containerSecurity -and $null -ne $containerSecurity.readOnlyRootFilesystem) {
        $readOnlyRootFilesystem = [bool]$containerSecurity.readOnlyRootFilesystem
    }

    $seccompProfile = "Unconfined"
    if ($null -ne $podSecurity -and $null -ne $podSecurity.seccompProfile) {
        $seccompProfile = [string]$podSecurity.seccompProfile.type
    }

    $requestsDefined = $false
    $limitsDefined = $false
    if ($null -ne $container.resources) {
        $requestsDefined = $null -ne $container.resources.requests
        $limitsDefined = $null -ne $container.resources.limits
    }

    return [ordered]@{
        namespace = [string]$Deployment.metadata.namespace
        kind = "Deployment"
        name = [string]$Deployment.metadata.name
        replicas = [int]$Deployment.spec.replicas
        security = [ordered]@{
            run_as_non_root = $runAsNonRoot
            allow_privilege_escalation = $allowPrivilegeEscalation
            capabilities_drop_all = Test-DropAllCapabilities $containerSecurity
            read_only_root_filesystem = $readOnlyRootFilesystem
            seccomp_profile = $seccompProfile
        }
        resources = [ordered]@{
            requests_defined = $requestsDefined
            limits_defined = $limitsDefined
        }
    }
}

$targetNamespaces = @("security-lab", "workload-dev")

$namespaceResponse = Get-KubectlJson @("get", "namespaces", "-o", "json")
$networkPolicyResponse = Get-KubectlJson @("get", "networkpolicies", "--all-namespaces", "-o", "json")
$deploymentResponse = Get-KubectlJson @("get", "deployments", "--all-namespaces", "-o", "json")
$roleResponse = Get-KubectlJson @("get", "roles", "--all-namespaces", "-o", "json")

$namespaces = foreach ($name in $targetNamespaces) {
    $namespaceObject = @(
        $namespaceResponse.items |
            Where-Object { $_.metadata.name -eq $name }
    ) | Select-Object -First 1

    if ($null -eq $namespaceObject) {
        continue
    }

    $labels = $namespaceObject.metadata.labels
    $policies = @(
        $networkPolicyResponse.items |
            Where-Object { $_.metadata.namespace -eq $name } |
            ForEach-Object { [string]$_.metadata.name } |
            Sort-Object
    )

    [ordered]@{
        name = $name
        labels = [ordered]@{
            "pod-security.kubernetes.io/enforce" = [string]$labels.'pod-security.kubernetes.io/enforce'
            "security-owner" = [string]$labels.'security-owner'
            "environment" = [string]$labels.environment
        }
        network_policies = @($policies)
    }
}

$workloads = foreach ($deployment in $deploymentResponse.items) {
    if ($targetNamespaces -contains [string]$deployment.metadata.namespace) {
        Get-WorkloadSnapshot $deployment
    }
}

# The Project 06 Role is intentionally in workload-dev.
# Its subject service account is security-observer from security-lab.
$observerRole = @(
    $roleResponse.items |
        Where-Object {
            $_.metadata.namespace -eq "workload-dev" -and
            $_.metadata.name -eq "security-observer-readonly"
        }
) | Select-Object -First 1

$rbac = @()

if ($null -ne $observerRole) {
    $rules = @($observerRole.rules)
    $verbs = @(
        $rules |
            ForEach-Object { $_.verbs } |
            ForEach-Object { $_ } |
            Sort-Object -Unique
    )
    $resources = @(
        $rules |
            ForEach-Object { $_.resources } |
            ForEach-Object { $_ } |
            Sort-Object -Unique
    )
    $writeVerbs = @("create", "update", "patch", "delete", "deletecollection")

    $rbac = @(
        [ordered]@{
            namespace = "workload-dev"
            identity = "security-observer"
            verbs = @($verbs)
            can_read_secrets = $resources -contains "secrets"
            can_write_workloads = (@($verbs | Where-Object { $writeVerbs -contains $_ }).Count -gt 0)
        }
    )
}

$snapshot = [ordered]@{
    snapshot_version = "1.0"
    captured_at = [DateTime]::UtcNow.ToString("o")
    platform = $context
    environment = "local-training"
    namespaces = @($namespaces)
    workloads = @($workloads)
    rbac = @($rbac)
}

$snapshot | ConvertTo-Json -Depth 20 |
    Set-Content -LiteralPath $output -Encoding UTF8

Write-Host "Kubernetes snapshot written to: $output"
Write-Host "Context: $context"
Write-Host "Namespaces collected: $(@($snapshot.namespaces).Count)"
Write-Host "Workloads collected: $(@($snapshot.workloads).Count)"
Write-Host "RBAC roles collected: $(@($snapshot.rbac).Count)"
