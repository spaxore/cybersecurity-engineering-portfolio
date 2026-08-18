# Threat Model

## Scope

This model covers the local Kubernetes workload in `workload-dev`, the `security-lab` observer identity, NetworkPolicies, OPA validation, and Trivy scanning. It is a local training simulation and does not claim to model every provider-specific cloud control.

## Assets and boundaries

| Asset | Security concern |
|---|---|
| Application workload | Unauthorized execution, privilege escalation, and compromise. |
| Kubernetes API access | Excessive permissions could modify workloads or secrets. |
| Service-account token | A stolen token could access Kubernetes resources. |
| Namespace network paths | Unrestricted traffic could enable lateral movement. |
| Container image | Vulnerable dependencies or exposed secrets. |
| Security reports | Reports may contain host or environment details requiring review. |

The lab separates the Windows host, Docker/kind cluster, Kubernetes namespaces, and workload containers. The `security-lab` identity is separate from `workload-dev` and receives only selected read permissions.

## Threat scenarios and controls

| Threat | Initial condition | Control | Evidence |
|---|---|---|---|
| Privilege escalation | `allowPrivilegeEscalation: true` | Set it to `false` and validate with OPA. | OPA denial. |
| Root execution | Container runs as UID 0. | Use `runAsNonRoot: true` and a non-root UID. | Secure manifest and pod status. |
| Writable root filesystem | Container can modify its image filesystem. | Use `readOnlyRootFilesystem: true` with explicit volumes. | Secure manifest. |
| Excessive capabilities | Default Linux capabilities remain. | Drop `ALL` capabilities. | Secure manifest and Trivy review. |
| Lateral movement | Namespace accepts and emits all traffic. | Default-deny ingress and egress policies. | NetworkPolicy output. |
| Excessive permissions | Observer can alter workloads or read secrets. | Namespace-scoped read-only Role. | `kubectl auth can-i`. |
| Vulnerable image | Base image has known vulnerabilities. | Scan with Trivy. | Before/after JSON reports. |
| Policy bypass | Manifest omits security settings. | Evaluate with OPA before deployment. | OPA policy result. |

## Residual risk

The cluster is single-node and does not model high availability, provider-managed control planes, cloud IAM, managed key management, production ingress, or external identity federation. Base-image vulnerabilities can remain after workload hardening. A production implementation would also require image pinning by digest, signed artifacts, a private registry, centralized audit logs, stronger admission enforcement, and operational monitoring.
