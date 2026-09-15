# Security Requirements

These requirements convert the threat model into testable architecture expectations.

## Identity and access requirements

| ID | Requirement | Priority | Related project |
|---|---|---|---|
| SR-001 | Protected services must validate token signature, issuer, audience, and expiration. | High | 07 |
| SR-002 | Privileged roles must be separate from ordinary user roles. | High | 06, 07 |
| SR-003 | Service accounts must receive only the permissions required for their function. | High | 06 |
| SR-004 | Administrative access must require stronger authentication and produce audit events. | High | 07 |
| SR-005 | Invalid, expired, or incorrectly scoped tokens must be rejected. | High | 07 |

## Workload and network requirements

| ID | Requirement | Priority | Related project |
|---|---|---|---|
| SR-006 | Workloads must not run as root unless a documented exception exists. | High | 06 |
| SR-007 | Privilege escalation must be disabled for ordinary workloads. | High | 06 |
| SR-008 | Workload capabilities must be minimized. | Medium | 06 |
| SR-009 | Network communication must be explicitly allowed through policy. | High | 06 |
| SR-010 | Workloads must not have unrestricted access to platform or data services. | High | 06 |
| SR-011 | Sensitive service endpoints must not be publicly exposed by default. | High | 06 |

## Software supply-chain requirements

| ID | Requirement | Priority | Related project |
|---|---|---|---|
| SR-012 | Source changes must be checked for secrets before delivery. | High | 08 |
| SR-013 | Source code must be checked for project-defined insecure patterns. | Medium | 08 |
| SR-014 | Container images must be scanned for vulnerabilities and misconfigurations. | High | 08 |
| SR-015 | A software bill of materials must be generated for reviewed artifacts. | Medium | 08 |
| SR-016 | Policy violations must block the delivery decision. | High | 08 |

## Governance and monitoring requirements

| ID | Requirement | Priority | Related project |
|---|---|---|---|
| SR-017 | Approved platform configuration must be represented in a versioned baseline. | High | 09 |
| SR-018 | Collected platform state must be limited to approved fields. | Medium | 09 |
| SR-019 | Compliance checks must produce explainable findings. | High | 09 |
| SR-020 | Configuration drift must be distinguishable from an approved change. | High | 09 |
| SR-021 | Governance evidence must include baseline and collection context. | Medium | 09 |

## Backup and recovery requirements

| ID | Requirement | Priority | Related project |
|---|---|---|---|
| SR-022 | Backup integrity must be checked before restoration. | High | 10 |
| SR-023 | Tampered or mismatched backup input must be rejected. | High | 10 |
| SR-024 | Restoration must occur in an isolated workspace. | High | 10 |
| SR-025 | Recovery output must be validated after restoration. | High | 10 |
| SR-026 | Recovery operations must generate reviewable evidence. | Medium | 10 |

## Evidence and public-release requirements

| ID | Requirement | Priority | Related project |
|---|---|---|---|
| SR-027 | Public evidence must not contain credentials, private keys, tokens, or personal data. | High | 06–10 |
| SR-028 | Generated reports must be reviewed before publication. | High | 06–10 |
| SR-029 | Security findings must identify the affected control or requirement. | Medium | 06–10 |
| SR-030 | Demonstrations must use synthetic or intentionally isolated environments. | High | 06–10 |

## Requirement acceptance principles

A requirement is considered adequately addressed when:

1. The architecture identifies the relevant control.
2. The related project implements or demonstrates the control.
3. A validation method exists.
4. Evidence can be reviewed without exposing sensitive information.
5. Any residual risk is documented.
