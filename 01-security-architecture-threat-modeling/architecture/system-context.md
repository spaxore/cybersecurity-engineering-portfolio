# Composite Platform — System Context

## Purpose

The composite platform is a logical security architecture assembled from Projects 06–10 of this portfolio.

It represents a local-first platform where workloads are deployed to a Kubernetes environment, users and services authenticate through an OIDC identity provider, changes pass through a secure software-supply-chain gate, platform state is checked against approved governance baselines, and backup artifacts are validated before restoration.

The composite model is used to identify threats and architecture requirements that span multiple projects.

## System components

| Component | Source project | Responsibility | Security significance |
|---|---|---|---|
| Developer workstation | 08, 09, 10 | Creates changes, runs validation, and reviews evidence. | Potential source of malicious or accidental changes. |
| Source repository | 08 | Stores application, policy, infrastructure, and workflow definitions. | Requires integrity and secret protection. |
| CI/CD security pipeline | 08 | Performs source, secret, image, SBOM, and policy checks. | Acts as a preventive delivery gate. |
| Local Kubernetes cluster | 06, 09 | Runs controlled workloads and platform services. | Requires isolation, least privilege, and secure defaults. |
| Identity provider | 07 | Authenticates users and issues OIDC tokens. | Token and authorization trust anchor. |
| Application workloads | 06 | Provide controlled platform functionality. | Must be non-root, restricted, and observable. |
| Platform state collector | 09 | Collects selected platform configuration. | Must avoid unauthorized or excessive data collection. |
| Approved baseline | 09 | Defines expected secure configuration. | Reference for compliance and drift detection. |
| Backup workspace | 10 | Stores synthetic backup artifacts and integrity manifests. | Must reject tampered or untrusted input. |
| Restoration workspace | 10 | Receives controlled recovery output. | Must remain isolated from the source environment. |
| Evidence and reports | 06–10 | Store sanitized validation results. | Must not disclose secrets or private host data. |

## Actors

| Actor | Description | Trust level |
|---|---|---|
| Developer | Proposes source, policy, or configuration changes. | Partially trusted |
| Platform administrator | Operates the local platform and reviews changes. | Privileged |
| Security reviewer | Reviews threat findings, policy results, and residual risk. | Trusted reviewer |
| CI/CD runner | Executes automated security checks. | Controlled automation |
| Identity provider | Issues authentication and authorization claims. | Trusted dependency |
| Backup operator | Initiates controlled backup and recovery tests. | Privileged |
| Unauthorized user | Attempts to access or alter platform resources. | Untrusted |

## Protected assets

The highest-value assets in the composite system are:

1. Identity-provider signing keys and token-validation metadata
2. Administrative identities and authorization mappings
3. Source code, policy files, and workflow definitions
4. Kubernetes workload and RBAC configuration
5. Approved security baselines
6. Backup archives and integrity manifests
7. Recovery outputs
8. Security evidence and audit records
9. CI/CD credentials and service identities
10. Secrets that must never enter source control

## Security objectives

1. Only authenticated and authorized identities may access protected platform functions.
2. Workloads must run with least privilege and secure runtime defaults.
3. Changes must be reviewed and validated before deployment.
4. Identity tokens must be validated for issuer, audience, signature, and expiration.
5. Network communication must be explicitly allowed rather than implicitly trusted.
6. Approved platform state must be distinguishable from drifted or unauthorized state.
7. Backup artifacts must be verified before restoration.
8. Restored data must enter an isolated workspace before validation.
9. Audit evidence must preserve integrity while minimizing sensitive information.
10. Security controls must produce repeatable and reviewable evidence.

## Out of scope

The model does not represent:

- A production cloud account
- Real customer information
- Real payment processing
- Public-facing infrastructure
- Production disaster recovery
- Real organizational credentials
- Testing against systems outside the controlled lab
