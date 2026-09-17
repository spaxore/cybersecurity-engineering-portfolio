# Evidence Guidance

## Purpose

This directory documents how to prepare safe, reproducible, and reviewable evidence for Project 01.

The evidence should demonstrate traceability between:

```text
Asset -> Trust boundary -> Threat -> Risk -> Requirement -> Control -> Residual risk
```

## Recommended evidence

| Evidence | Purpose |
|---|---|
| Logical architecture diagram | Shows components, data flows, and trust boundaries. |
| Asset inventory | Identifies protected assets and their classifications. |
| Trust-boundary analysis | Explains where identities, data, or privileges cross boundaries. |
| STRIDE threat catalog | Records threats and existing controls. |
| Abuse-case document | Describes undesirable actions and their mitigations. |
| Risk register | Prioritizes threats by likelihood, impact, owner, and status. |
| Control mapping | Connects Project 01 findings to Projects 06–10. |
| Architecture decisions | Explains important design choices and consequences. |
| Portfolio project references | Shows where the implemented controls are demonstrated. |

## Sanitization checklist

Before committing evidence, confirm that it contains no:

- Passwords
- Access tokens
- API keys
- Private keys
- Certificates containing private material
- Real customer or employee information
- Personal home-directory paths
- Internal hostnames or IP addresses
- Cloud account identifiers
- Kubernetes credentials or kubeconfig files
- Docker registry credentials
- Unsanitized terminal history
- Unreviewed generated reports

## Evidence naming

Use descriptive names such as:

```text
threat-control-traceability.md
risk-register-review.md
architecture-review-summary.md
```

Avoid names that disclose local usernames, private hostnames, timestamps of personal activity, or credentials.

## Validation principles

Evidence should be:

1. Reproducible from the documented project files.
2. Traceable to a threat, risk, requirement, or control.
3. Sanitized before public publication.
4. Clear about whether a result is passing, failing, accepted, or residual risk.
5. Explicit about the limitations of the local lab.

## Project boundary

This project is an architecture and threat-modeling exercise. It does not authorize testing against systems outside the controlled portfolio environment.
