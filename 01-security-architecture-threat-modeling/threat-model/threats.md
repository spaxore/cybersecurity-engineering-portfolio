# STRIDE Threat Analysis

This analysis applies STRIDE to the composite platform's major trust boundaries.

## Threat catalog

| Threat ID | STRIDE category | Trust boundary | Threat | Affected assets | Existing control | Residual risk |
|---|---|---|---|---|---|---|
| T-001 | Spoofing | B-004 | An attacker obtains or abuses an administrative identity. | A-003, A-004 | OIDC authentication, Keycloak, RBAC | Phishing or endpoint compromise may still expose a valid session. |
| T-002 | Spoofing | B-005 | A forged, expired, or incorrectly issued token is accepted. | A-001, A-002, A-004 | Signature, issuer, audience, and expiration validation | Identity-provider compromise remains high impact. |
| T-003 | Tampering | B-001 | An unauthorized source or policy change is introduced. | A-005, A-008, A-009 | Protected branches, review, secret scanning, CI checks | A reviewer may approve a malicious or misunderstood change. |
| T-004 | Tampering | B-003 | An insecure workload bypasses delivery or deployment controls. | A-007, A-008, A-009 | Policy gates, image scanning, RBAC | Emergency or local-only deployment paths may bypass CI controls. |
| T-005 | Repudiation | B-010 | A security-relevant change or administrative action cannot be attributed. | A-014 | Git history, audit events, pipeline records | Local logs may be incomplete or altered by a privileged operator. |
| T-006 | Information disclosure | B-002 | CI/CD output exposes a secret, token, or sensitive build value. | A-006, A-014 | Gitleaks, secret isolation, sanitized evidence | New secret formats or verbose tooling may evade detection. |
| T-007 | Information disclosure | B-007 | A workload accesses data or service information beyond its need. | A-003, A-008, A-009 | RBAC, service accounts, NetworkPolicies | A compromised workload may exploit an undiscovered permission path. |
| T-008 | Denial of service | B-006 | Excessive or malicious traffic exhausts workload or cluster resources. | A-008, A-014 | Network boundaries, resource controls, monitoring | The local lab does not model full production-scale resilience. |
| T-009 | Elevation of privilege | B-003 | A deployment identity receives broader cluster permissions than required. | A-003, A-006, A-009 | Least-privilege RBAC and reviewed deployment configuration | Configuration drift can reintroduce excessive permissions. |
| T-010 | Elevation of privilege | B-007 | A workload escapes its intended security boundary through excessive privileges. | A-008, A-009 | Non-root execution, dropped capabilities, seccomp, RBAC | Kernel or runtime vulnerabilities remain outside this lab's scope. |
| T-011 | Tampering | B-009 | A backup is modified before restoration. | A-012, A-013 | SHA-256 manifest validation and isolated restore | Integrity depends on protection of the trusted manifest. |
| T-012 | Information disclosure | B-010 | Public evidence contains private paths, credentials, or host information. | A-011, A-014 | Sanitization guidance and secret scanning | Manual review can miss sensitive content. |

## Highest-priority threats

The highest-priority threats for this platform are:

1. T-002 — Invalid identity tokens accepted by protected services.
2. T-004 — Insecure workloads bypassing delivery controls.
3. T-009 — Excessive deployment or cluster permissions.
4. T-010 — Workload privilege escalation.
5. T-011 — Tampered backup restored as trusted input.
6. T-012 — Sensitive information published as portfolio evidence.

## Analysis limitations

This is an architecture-level STRIDE analysis. It does not claim that every threat is exploitable in the local lab. The purpose is to identify security requirements, existing controls, validation opportunities, and residual risks.
