$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
    throw "kubectl was not found in PATH."
}

$context = (& kubectl config current-context).Trim()
if ($LASTEXITCODE -ne 0 -or $context -ne "kind-cloudsec-lab") {
    throw "Expected active kubectl context kind-cloudsec-lab, found: $context"
}

Write-Host "Applying namespace governance labels..." -ForegroundColor Cyan

kubectl label namespace security-lab `
    pod-security.kubernetes.io/enforce=restricted `
    security-owner=platform-security `
    environment=local-training `
    --overwrite

kubectl label namespace workload-dev `
    pod-security.kubernetes.io/enforce=restricted `
    security-owner=application-platform `
    environment=development `
    --overwrite

Write-Host "Applying default-deny and DNS network policies..." -ForegroundColor Cyan

$policyFile = Join-Path $root "reports\governance-remediation-network-policies.yaml"
$policyText = @'
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress-egress
  namespace: security-lab
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress-egress
  namespace: workload-dev
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns-egress
  namespace: workload-dev
spec:
  podSelector: {}
  policyTypes:
    - Egress
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
      ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53
'@

$policyText | Set-Content -LiteralPath $policyFile -Encoding UTF8
kubectl apply -f $policyFile
Remove-Item $policyFile -Force -ErrorAction SilentlyContinue

Write-Host "Applying workload resource requests and limits..." -ForegroundColor Cyan

$patchFile = Join-Path $root "reports\workload-resources-patch.json"
$patchText = @'
{
  "spec": {
    "template": {
      "spec": {
        "containers": [
          {
            "name": "nginx",
            "resources": {
              "requests": {
                "cpu": "10m",
                "memory": "16Mi"
              },
              "limits": {
                "cpu": "100m",
                "memory": "128Mi"
              }
            }
          }
        ]
      }
    }
  }
}
'@

$patchText | Set-Content -LiteralPath $patchFile -Encoding UTF8
kubectl -n workload-dev patch deployment demo-api-secure `
    --type strategic `
    --patch-file $patchFile
Remove-Item $patchFile -Force -ErrorAction SilentlyContinue

kubectl -n workload-dev rollout status deployment/demo-api-secure --timeout=120s

Write-Host "Governance remediation completed." -ForegroundColor Green
