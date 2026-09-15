# Security Architecture and Threat Modeling

Project 01 in the cybersecurity engineering portfolio.

> Define the system, understand the threats, and select controls before implementation.

## Objective

This project documents the security architecture and threat model for the portfolio's local cloud-security platform.

The model treats Projects 06–10 as a connected logical platform containing:

- A local Kubernetes workload environment
- An OIDC identity provider
- A secure software supply-chain pipeline
- Configuration governance and drift monitoring
- Backup integrity and controlled recovery

The purpose is not to model a production system. The purpose is to demonstrate how assets, trust boundaries, threats, risks, security requirements, and architectural decisions are identified before controls are implemented.

## Related portfolio projects

| Project | Contribution to the composite platform |
| --- | --- |
| 06 — Local Cloud Security Architecture Lab | Kubernetes namespaces, workload hardening, NetworkPolicies, RBAC, OPA, and Trivy |
| 07 — Identity and Access Architecture Lab | Keycloak, OIDC, PKCE, JWT validation, JWKS, issuer validation, and RBAC |
| 08 — Secure DevSecOps Supply-Chain Security Lab | Secret scanning, source analysis, image scanning, SBOM generation, and policy gates |
| 09 — Cloud Security Monitoring and Governance Lab | Approved baselines, platform-state collection, compliance checks, and drift detection |
| 10 — Resilient and Secure Platform Lab | Backup integrity, controlled failure, isolated restoration, and recovery validation |

## Threat-modeling method

The project uses:

1. System and data-flow modeling
2. Asset identification
3. Trust-boundary analysis
4. STRIDE threat analysis
5. Abuse-case development
6. Risk scoring
7. Security-requirement definition
8. Threat-to-control mapping
9. Architecture decision records
10. Residual-risk documentation

## Primary trust boundaries

- User or operator to identity provider
- Identity provider to application or platform
- CI/CD pipeline to deployment target
- Kubernetes ingress to workloads
- Workloads to data and platform services
- Backup source to restoration workspace
- Monitoring collector to governance evidence store

## Scope limitations

This project uses local, synthetic, and sanitized evidence. It does not include:

- Production credentials
- Real cloud inventories
- Real customer data
- Public infrastructure testing
- Exploitation of third-party systems
- Production deployment
- Unreviewed secrets or private keys

## Project structure

```text
01-security-architecture-threat-modeling/
|-- architecture/
|   |-- system-context.md
|   |-- logical-architecture.mmd
|   |-- trust-boundaries.md
|   |-- security-requirements.md
|   `-- architecture-decisions.md
|-- controls/
|   `-- control-mapping.md
|-- evidence/
|   `-- README.md
|-- reports/
|   `-- .gitkeep
|-- threat-model/
|   |-- assets.md
|   |-- threats.md
|   |-- abuse-cases.md
|   `-- risk-register.csv
`-- README.md
```

## Expected outcome

The final result should show how the existing portfolio controls relate to identified threats and architectural risks.

The important outcome is not the number of threats documented. It is the traceability between:

Asset -> Trust boundary -> Threat -> Risk -> Requirement -> Existing control -> Residual risk

