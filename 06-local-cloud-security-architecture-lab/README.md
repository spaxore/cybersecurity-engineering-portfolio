# Local Cloud Security Architecture Lab

A free, local Kubernetes security lab that demonstrates cloud-security-architecture principles without requiring an AWS or Azure account.

> Design secure boundaries. Enforce least privilege. Validate controls with evidence.

## Overview

This project simulates a small secure cloud platform on a local computer using Docker Desktop, Kubernetes, kind, Open Policy Agent, and Trivy. It starts with an intentionally insecure workload, captures security findings, applies security controls, and validates a hardened workload with before-and-after evidence.

## Architecture outcomes

- Namespace-based environment separation.
- Default-deny ingress and egress NetworkPolicies.
- Least-privilege Kubernetes RBAC.
- Non-root workload execution.
- Disabled privilege escalation.
- Dropped Linux capabilities.
- Read-only container filesystem with dedicated writable volumes.
- Runtime-default seccomp profile.
- Policy-as-code validation with OPA.
- Vulnerability, misconfiguration, and secret scanning with Trivy.
- Before-and-after JSON evidence reports.

## Technology stack

| Technology | Purpose |
|---|---|
| Docker Desktop | Local container runtime. |
| kind | Local Kubernetes cluster running in Docker. |
| kubectl | Kubernetes administration and validation. |
| Open Policy Agent | Policy-as-code security checks. |
| Trivy | Kubernetes vulnerability and configuration scanning. |
| PowerShell | Repeatable local deployment and cleanup commands. |

## Project structure

    06-local-cloud-security-architecture-lab/
    |-- README.md
    |-- architecture/
    |-- kubernetes/
    |-- policies/
    |-- reports/
    `-- scripts/
## Prerequisites

Verify that Docker Desktop is running its Linux engine:

```powershell
docker info
kubectl version --client
kind version
trivy --version
docker run --rm openpolicyagent/opa:latest version
```

## Create the cluster

```powershell
kind create cluster --name cloudsec-lab --wait 60s
kubectl cluster-info --context kind-cloudsec-lab
kubectl get nodes
```

## Deploy the lab

```powershell
kubectl apply -f kubernetes/00-namespaces.yaml
kubectl apply -f kubernetes/10-insecure-workload.yaml
kubectl -n workload-dev rollout status deployment/demo-api-insecure
```

The insecure deployment is intentionally included as a controlled test fixture. It should produce security warnings and policy violations.

Apply the hardened configuration:

```powershell
kubectl delete -f kubernetes/10-insecure-workload.yaml
kubectl apply -f kubernetes/20-secure-workload.yaml
kubectl apply -f kubernetes/30-network-policies.yaml
kubectl apply -f kubernetes/40-rbac.yaml
kubectl -n workload-dev rollout status deployment/demo-api-secure
```

## Validate security controls

Test RBAC:

```powershell
kubectl auth can-i list pods --as=system:serviceaccount:security-lab:security-observer -n workload-dev
kubectl auth can-i delete deployments --as=system:serviceaccount:security-lab:security-observer -n workload-dev
```

Expected results are `yes` for listing pods and `no` for deleting deployments.

Evaluate the OPA policy:

```powershell
docker run --rm `
  -v "${PWD}:/project" `
  openpolicyagent/opa:latest eval `
  --format pretty `
  --data /project/policies/kubernetes_security.rego `
  --input /project/policies/insecure-deployment.json `
  "data.kubernetes.security.deny"
```

The intentionally insecure input should produce violations for non-root execution, privilege escalation, and read-only filesystem requirements.

## Capture scan evidence

```powershell
trivy k8s `
  --include-namespaces workload-dev `
  --report all `
  --scanners vuln,misconfig,secret `
  --format json `
  --output reports/after-hardening.json
```

The vulnerability counts may remain because vulnerabilities can originate from the base image. The architecture improvement is demonstrated through the hardened manifest, OPA decisions, RBAC results, NetworkPolicies, and before/after reports.

## Cleanup

```powershell
kind delete cluster --name cloudsec-lab
```

## Limitations

This is a local architecture simulation, not a replacement for a public-cloud deployment. It does not model provider-specific services such as AWS Organizations, Azure Management Groups, managed IAM, or cloud-native key management. Its purpose is to demonstrate transferable security architecture principles: isolation, least privilege, policy enforcement, secure workload configuration, and evidence-driven validation.

Only analyze and administer systems you own or are authorized to use. Do not commit kubeconfig files, Docker credentials, private keys, personal data, or unreviewed scan output to a public repository.

## References

- https://kind.sigs.k8s.io/docs/user/quick-start/
- https://openpolicyagent.org/docs/deploy/docker
- https://trivy.dev/docs/latest/target/kubernetes/
