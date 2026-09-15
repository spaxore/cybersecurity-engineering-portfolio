# Trust-Boundary Analysis

A trust boundary is a point where data, identities, privileges, or administrative control move between components with different trust levels.

## Boundary inventory

| Boundary ID | Boundary | Risk focus | Related projects |
|---|---|---|---|
| B-001 | Developer workstation to source repository | Unauthorized or malicious source changes | 08 |
| B-002 | Source repository to CI/CD pipeline | Untrusted code or workflow execution | 08 |
| B-003 | CI/CD pipeline to Kubernetes cluster | Unauthorized deployment or excessive deployment privilege | 06, 08 |
| B-004 | User or operator to identity provider | Authentication abuse or identity impersonation | 07 |
| B-005 | Identity provider to protected services | Invalid token or incorrect authorization decision | 07 |
| B-006 | Kubernetes ingress to workloads | Unauthorized network access or lateral movement | 06 |
| B-007 | Workloads to platform and data services | Excessive service permissions or data exposure | 06, 07 |
| B-008 | Platform state collector to governance evidence | Excessive collection or manipulated evidence | 09 |
| B-009 | Backup source to restoration workspace | Tampered backup or unsafe restoration | 10 |
| B-010 | Evidence workspace to public repository | Disclosure of secrets or private system details | 06–10 |

## B-001 — Developer workstation to source repository

The developer workstation is where source code, policy, configuration, and workflow changes are created. The repository is the controlled record of proposed changes.

### Main threats

- Compromised developer workstation
- Unauthorized repository access
- Malicious or accidental configuration change
- Secret committed to source control
- Unreviewed direct modification of a protected branch

### Required controls

- Strong account authentication
- Protected branches
- Pull-request review
- Secret scanning
- Local and CI validation
- Audit history for repository changes
- No credentials or private keys in source files

## B-002 — Source repository to CI/CD pipeline

The CI/CD pipeline executes code and security tooling based on repository content. Repository files must therefore be treated as potentially untrusted input.

### Main threats

- Malicious workflow modification
- Dependency compromise
- Script injection
- Poisoned build input
- Exposure of CI/CD secrets

### Required controls

- Workflow review
- Minimal runner permissions
- Pinned or controlled action versions
- Secret isolation
- Gitleaks and Semgrep checks
- Container and dependency scanning
- SBOM generation
- Policy gate before delivery

## B-003 — CI/CD pipeline to Kubernetes cluster

The pipeline may deploy workloads or configuration to the cluster. This is a high-impact privilege boundary.

### Main threats

- Overprivileged deployment identity
- Unauthorized deployment
- Deployment of insecure workloads
- Bypass of policy checks
- Compromise of deployment credentials

### Required controls

- Dedicated deployment identity
- Least-privilege RBAC
- Protected deployment branch
- Policy checks before deployment
- Immutable artifact references
- Deployment audit records
- Short-lived or rotatable credentials

## B-004 — User or operator to identity provider

Users and operators depend on the identity provider for authentication.

### Main threats

- Credential theft
- Phishing
- Brute-force authentication
- Unauthorized administrative login
- Misconfigured redirect or client settings

### Required controls

- Strong authentication
- MFA for privileged users
- Secure redirect URI configuration
- Rate limiting and account protection
- Short-lived authorization codes
- PKCE for public clients
- Login and administrative audit events

## B-005 — Identity provider to protected services

Protected services trust identity claims issued by the identity provider.

### Main threats

- Forged token
- Wrong issuer accepted
- Wrong audience accepted
- Expired token accepted
- Excessive role or scope
- Unavailable key-discovery endpoint

### Required controls

- Signature validation
- Issuer validation
- Audience validation
- Expiration validation
- Scope and role validation
- JWKS key rotation handling
- Fail-closed behavior when validation fails

## B-006 — Kubernetes ingress to workloads

Ingress traffic crosses from an external or less-trusted network into workload namespaces.

### Main threats

- Unauthorized service access
- Lateral movement
- Insecure exposed endpoint
- Network-policy bypass
- Denial of service

### Required controls

- Default-deny ingress
- Explicit allow rules
- Namespace separation
- TLS where applicable
- Request validation
- Service exposure review
- Network-policy testing

## B-007 — Workloads to platform and data services

Workloads access other services using identities, network paths, and configuration.

### Main threats

- Excessive RBAC permission
- Unauthorized data access
- Service-account token misuse
- Unrestricted egress
- Compromised workload movement

### Required controls

- Dedicated service accounts
- Least-privilege RBAC
- Default-deny egress where practical
- Restricted service-to-service access
- Non-root execution
- Dropped capabilities
- Read-only filesystems where practical
- Runtime and audit monitoring

## B-008 — Platform state collector to governance evidence

The collector gathers selected platform state and compares it with an approved baseline.

### Main threats

- Excessive collection
- Collection of secrets
- Manipulated state data
- Unauthorized collector access
- False compliance result

### Required controls

- Explicit collection scope
- Secret-field exclusion
- Read-only access
- Integrity-protected evidence
- Baseline version tracking
- Collection timestamp
- Review of compliance logic

## B-009 — Backup source to restoration workspace

Backup artifacts are verified and restored into an isolated workspace.

### Main threats

- Tampered archive
- Mismatched integrity manifest
- Malicious restoration input
- Restoration into the wrong environment
- Backup confidentiality exposure

### Required controls

- SHA-256 or stronger integrity verification
- Isolated restoration workspace
- Explicit restore target
- Reject-on-integrity-failure behavior
- Backup access control
- Recovery validation
- Restore audit trail

## B-010 — Evidence workspace to public repository

Local reports may be published as portfolio evidence.

### Main threats

- Credential disclosure
- Private path disclosure
- Personal data exposure
- Cloud or cluster identifier disclosure
- Unreviewed scan output

### Required controls

- Evidence sanitization checklist
- Secret scanning before commit
- Review of generated reports
- Synthetic fixtures
- Exclusion of private keys and tokens
- Public repository review before push
