param([string]$ClusterName = "cloudsec-lab")
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
kubectl config use-context "kind-$ClusterName" | Out-Null
kubectl apply -f (Join-Path $root "kubernetes\00-namespaces.yaml")
kubectl apply -f (Join-Path $root "kubernetes\20-secure-workload.yaml")
kubectl apply -f (Join-Path $root "kubernetes\30-network-policies.yaml")
kubectl apply -f (Join-Path $root "kubernetes\40-rbac.yaml")
kubectl -n workload-dev rollout status deployment/demo-api-secure --timeout=120s
kubectl -n workload-dev get pods,services,networkpolicies
kubectl auth can-i list pods --as=system:serviceaccount:security-lab:security-observer -n workload-dev
kubectl auth can-i delete deployments --as=system:serviceaccount:security-lab:security-observer -n workload-dev
