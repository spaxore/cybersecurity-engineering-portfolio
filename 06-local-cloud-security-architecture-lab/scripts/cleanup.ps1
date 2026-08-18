param([string]$ClusterName = "cloudsec-lab", [switch]$DeleteCluster)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
kubectl config use-context "kind-$ClusterName" | Out-Null
kubectl delete -f (Join-Path $root "kubernetes\40-rbac.yaml") --ignore-not-found
kubectl delete -f (Join-Path $root "kubernetes\30-network-policies.yaml") --ignore-not-found
kubectl delete -f (Join-Path $root "kubernetes\20-secure-workload.yaml") --ignore-not-found
kubectl delete -f (Join-Path $root "kubernetes\00-namespaces.yaml") --ignore-not-found
if ($DeleteCluster) { kind delete cluster --name $ClusterName }
