# Governance evidence

Project 09 produces sanitized evidence for configuration assurance and approved-state drift detection.

## Validated scenarios

| Scenario | Expected result | Demonstrated capability |
| --- | --- | --- |
| Compliant fixture | Pass with zero findings | A platform state that matches the approved baseline is accepted. |
| Noncompliant fixture | Fail with control findings | Missing security controls are detected. |
| Drifted fixture | Fail with drift findings | Changed, missing, and unexpected resources are detected. |
| Live kind cluster | Pass with zero findings after remediation | The running local Kubernetes platform matches the approved baseline. |

## Live validation summary

The live `kind-cloudsec-lab` snapshot was collected after the secure Project 06 baseline was redeployed and remediated. The collector recorded two target namespaces, one workload, and one RBAC role.

The final live audit returned:

```
compliance_findings: 0
drift_findings: 0
total_findings: 0
status: pass
```

## Evidence files

Generated JSON and Markdown reports are written under `reports/` during local execution. They are intentionally ignored by Git because they may contain host-specific metadata and should be reviewed before public sharing.

Recommended public evidence consists of sanitized screenshots or summaries showing:

1. The collector context and resource counts.

1. The live audit passing with zero findings.

1. The noncompliant fixture producing control findings.

1. The drifted fixture producing drift findings.

## Privacy and safety rules

Do not commit kubeconfig files, access tokens, service-account tokens, credentials, private keys, personal information, or raw host inventory. Do not expose the local kind cluster or audit service to the public internet.

The evidence demonstrates configuration governance, not SOC alerting or incident response.