# Threat-to-Control Mapping

This document maps identified threats to security requirements and controls implemented or demonstrated by Projects 06–10.

| Threat ID | Risk ID | Security requirement | Existing control | Source project | Validation evidence | Residual risk |
|---|---|---|---|---|---|---|
| T-001 | R-001 | SR-002, SR-004 | OIDC authentication, privileged-role separation, RBAC, and administrative audit events | 07, 06 | Authorization allow/deny results and identity-validation evidence | Phishing or endpoint compromise may expose a valid session. |
| T-002 | R-001 | SR-001, SR-005 | JWT signature, issuer, audience, expiration, scope, and role validation | 07 | Valid-token and invalid-token validation results | Identity-provider compromise remains high impact. |
| T-003 | R-010 | SR-012, SR-016 | Protected repository changes, secret scanning, source analysis, and required checks | 08 | Pipeline results and reviewed change history | A reviewer may approve a malicious or misunderstood change. |
| T-004 | R-002 | SR-006, SR-007, SR-009, SR-016 | Policy gates, image scanning, non-root workloads, restricted capabilities, and RBAC | 06, 08 | Insecure-versus-hardened manifests and failing policy output | Emergency or local-only deployment paths may bypass CI controls. |
| T-005 | R-008 | SR-021, SR-026, SR-029 | Git history, pipeline records, platform evidence, and recovery reports | 08–10 | Timestamped sanitized evidence and review history | Privileged local operators may alter local evidence. |
| T-006 | R-005 | SR-012, SR-027, SR-028 | Gitleaks, secret isolation, output review, and sanitized reports | 08 | Secret-scan result and reviewed report directory | New secret formats or verbose tooling may evade detection. |
| T-007 | R-004 | SR-003, SR-009, SR-010 | Least-privilege RBAC, service accounts, NetworkPolicies, and restricted egress | 06, 07 | `kubectl auth can-i` results and network-policy tests | A compromised workload may exploit an undiscovered permission path. |
| T-008 | R-007 | SR-009, SR-010, SR-019 | Network boundaries, resource controls, configuration monitoring, and compliance checks | 06, 09 | Allowed/denied flow tests and governance findings | The local lab does not model full production-scale resilience. |
| T-009 | R-003 | SR-002, SR-003, SR-016 | Dedicated identities, least-privilege RBAC, policy review, and delivery controls | 06, 08 | RBAC allow/deny tests and policy-gate results | Configuration drift can reintroduce excessive permissions. |
| T-010 | R-004 | SR-006, SR-007, SR-008, SR-010 | Non-root execution, disabled privilege escalation, dropped capabilities, seccomp, and RBAC | 06 | Hardened workload manifest and scan results | Kernel or runtime vulnerabilities remain outside this lab's scope. |
| T-011 | R-006 | SR-022, SR-023, SR-024, SR-025 | SHA-256 manifest verification, reject-on-mismatch behavior, isolated restore, and recovery validation | 10 | Valid-backup and tampered-backup test results | A compromised trusted manifest may undermine integrity validation. |
| T-012 | R-009 | SR-027, SR-028, SR-030 | Sanitization checklist, secret scanning, synthetic fixtures, and review before publication | 06–10 | Sanitized evidence review and repository scan | Manual review can miss unusual encodings or hidden sensitive content. |

## Control coverage summary

| Control area | Covered by | Coverage status |
|---|---|---|
| Identity validation | Project 07 | Demonstrated |
| Privileged authorization | Projects 06 and 07 | Demonstrated |
| Workload hardening | Project 06 | Demonstrated |
| Network isolation | Project 06 | Demonstrated locally |
| Secret detection | Project 08 | Demonstrated |
| Supply-chain policy enforcement | Project 08 | Demonstrated |
| Configuration governance | Project 09 | Demonstrated |
| Backup integrity | Project 10 | Demonstrated |
| Isolated recovery | Project 10 | Demonstrated |
| Composite threat model | Project 01 | In progress |

## Coverage gaps

The current portfolio still has planned work in:

- Formal network-zone and firewall architecture
- Dedicated secrets-management and key-rotation workflows
- Infrastructure-as-Code security and policy
- Production-scale monitoring and recovery
- Independent tamper-resistant evidence storage

These gaps are addressed by the planned Projects 02–04 and are not claimed as complete by this project.
