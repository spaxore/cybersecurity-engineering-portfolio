# Cloud Security Governance Model

## Purpose

Project 09 measures the security state of a local Kubernetes platform against an approved baseline. It demonstrates configuration assurance, compliance evaluation, and drift detection for a cloud-security architecture.

The project is intentionally not a SOC workflow. It does not implement alert triage, incident queues, or security-operations case management. Its purpose is to answer this architecture question:

> Does the running platform still match the security controls that were approved for it?

## Governance flow

The collector reads selected Kubernetes resources and converts them into a normalized snapshot. The auditor evaluates that snapshot against explicit governance rules and compares it with the approved baseline.

```text
Kubernetes state
      |
      v
Normalized snapshot
      |
      +--> Compliance rules
      +--> Approved baseline
      |
      v
Governance audit
      |
      +--> Compliance findings
      +--> Configuration drift findings
      |
      v
JSON and Markdown evidence
```

## Control catalog

| Control ID | Control | Severity | Validation |
|---|---|---|---|
| NS-001 | Workload namespaces declare restricted Pod Security enforcement. | High | Namespace labels are checked for `restricted`. |
| NS-002 | Namespaces identify an owner and environment. | Medium | `security-owner` and `environment` labels are required. |
| WL-001 | Workloads run as non-root users. | High | Deployment security context is normalized and evaluated. |
| WL-002 | Privilege escalation is disabled. | High | Container security context must set the value to false. |
| WL-003 | Linux capabilities are reduced. | High | The container must drop `ALL` capabilities. |
| WL-004 | Workloads define resource requests and limits. | Medium | CPU and memory requests and limits must be present. |
| NP-001 | Workload namespaces use default-deny network isolation. | High | Each target namespace must contain `default-deny-ingress-egress`. |
| RB-001 | Read-only identities do not receive write or secret access. | High | Verbs and sensitive resource access are evaluated. |

## Approved RBAC design

The Project 06 RBAC design separates the service-account namespace from the Role namespace:

| Resource | Namespace | Purpose |
|---|---|---|
| ServiceAccount `security-observer` | `security-lab` | Identity used by the observer workload or operator. |
| Role `security-observer-readonly` | `workload-dev` | Read-only permissions within the protected workload namespace. |
| RoleBinding `security-observer-readonly` | `workload-dev` | Binds the role to the observer service account. |

The RoleBinding subject may reference a service account from another namespace. Project 09 records the Role scope as `workload-dev` because that is where the permissions apply.

## Baseline lifecycle

The approved baseline is a versioned security decision. It should be changed only after a deliberate architecture review. A normal audit compares current state with the existing baseline; it should not silently rewrite the baseline to make findings disappear.

A baseline change should identify the affected control, explain the security reason, record the reviewer, and include a validation run. The current lab keeps the baseline in `baseline/approved-baseline.json` so that it can be reviewed as source-controlled policy data.

## Drift categories

| Drift category | Meaning | Example |
|---|---|---|
| Missing resource | An approved object is no longer present. | The approved deployment disappears. |
| Unexpected resource | A new object exists outside the approved state. | An unapproved namespace appears. |
| Changed configuration | An approved field has changed. | A workload replica count or security setting changes. |
| Removed control | A required security control is absent. | A default-deny NetworkPolicy is removed. |
| Unexpected control | A control exists that was not in the baseline. | An unreviewed network policy is added. |

## Decision model

A snapshot passes when it has zero compliance findings and zero drift findings. A snapshot fails when either category contains one or more findings.

The intentionally noncompliant and drifted fixtures demonstrate that the auditor detects failure conditions. The live `kind-cloudsec-lab` snapshot demonstrates that the remediated platform matches the approved baseline.

## Evidence requirements

Public evidence should contain sanitized counts, control IDs, and pass/fail decisions. It should not contain access tokens, credentials, private keys, kubeconfig contents, personal information, or unnecessary host details.

The most useful evidence for this lab is:

1. A compliant live audit with zero compliance and drift findings.
2. A noncompliant fixture showing control violations.
3. A drifted fixture showing changed, missing, or unexpected resources.
4. A snapshot summary showing the active local Kubernetes context and collected resource counts.

## Limitations

The lab audits selected normalized resources rather than every Kubernetes object. It uses a local kind cluster and a manually approved baseline. A production governance platform would require broader resource coverage, identity-aware ownership, signed evidence, scheduled execution, centralized retention, exception workflows, and authenticated access to audit results.
