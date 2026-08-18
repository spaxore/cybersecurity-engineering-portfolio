# Security Controls Matrix

| Control objective | Implementation | Validation evidence |
|---|---|---|
| Separate workload boundaries | `workload-dev`, `security-lab`, and `monitoring` namespaces. | `kubectl get namespaces --show-labels`. |
| Enforce baseline policy | Pod Security labels on namespaces. | Pod Security warnings during insecure deployment. |
| Prevent privilege escalation | `allowPrivilegeEscalation: false`. | OPA and secure manifest. |
| Prevent root execution | `runAsNonRoot: true`, UID 101. | OPA and running secure pod. |
| Reduce filesystem tampering | Read-only root filesystem and dedicated writable volumes. | OPA and secure manifest. |
| Reduce kernel attack surface | Drop all default capabilities. | Secure manifest and Trivy review. |
| Apply syscall restrictions | RuntimeDefault seccomp profile. | Secure manifest. |
| Reduce lateral movement | Default-deny ingress and egress policies. | `kubectl describe networkpolicy`. |
| Limit observer permissions | Namespace-scoped read-only Role and RoleBinding. | `kubectl auth can-i` results. |
| Avoid unnecessary token exposure | Disable token automount on the application workload. | Secure manifest. |
| Detect image and manifest risk | Trivy vulnerability, misconfiguration, and secret scans. | JSON reports. |
| Enforce policy before deployment | OPA Rego checks. | OPA denial output. |
