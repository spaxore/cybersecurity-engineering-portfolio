# Asset Inventory

| Asset ID | Asset | Classification | Security objectives | Related projects |
|---|---|---|---|---|
| A-001 | Identity-provider signing keys | Restricted | Confidentiality, integrity, availability | 07 |
| A-002 | OIDC discovery and JWKS metadata | Internal | Integrity, availability | 07 |
| A-003 | Administrative identities and roles | Restricted | Confidentiality, integrity, accountability | 06, 07 |
| A-004 | Access and identity tokens | Secret | Confidentiality, integrity, limited lifetime | 07 |
| A-005 | Source code and policy definitions | Internal | Integrity, confidentiality | 08 |
| A-006 | CI/CD credentials and service identities | Secret | Confidentiality, integrity, accountability | 08 |
| A-007 | Container images and SBOMs | Internal | Integrity, provenance, transparency | 08 |
| A-008 | Kubernetes workload configuration | Internal | Integrity, availability, least privilege | 06 |
| A-009 | Kubernetes RBAC and NetworkPolicies | Restricted | Integrity, isolation, least privilege | 06 |
| A-010 | Approved platform security baseline | Internal | Integrity, accountability | 09 |
| A-011 | Collected platform-state evidence | Internal | Confidentiality, integrity | 09 |
| A-012 | Backup archives and integrity manifests | Restricted | Integrity, availability | 10 |
| A-013 | Restored recovery workspace | Restricted | Integrity, isolation, availability | 10 |
| A-014 | Audit logs and security evidence | Internal | Integrity, availability, accountability | 06–10 |

## Crown-jewel assets

The most important assets are:

1. Identity-provider signing keys
2. Administrative identities and roles
3. CI/CD credentials
4. Kubernetes RBAC and workload configuration
5. Approved security baselines
6. Backup integrity manifests
7. Security evidence and audit records

## Asset-handling principles

- Never commit secrets, private keys, tokens, or real credentials.
- Keep restoration testing isolated from the source environment.
- Treat policy and baseline files as security-sensitive configuration.
- Minimize collected platform state to the fields required for governance decisions.
- Sanitize reports before public publication.
