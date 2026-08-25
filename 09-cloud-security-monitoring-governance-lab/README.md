Cloud Security Monitoring and Governance Lab
Project 09 in the cybersecurity engineering portfolio.

Objective
This project provides a local snapshot auditor for a Kubernetes security architecture. It collects selected platform resources, normalizes them into a portable snapshot, evaluates explicit governance controls, compares the current state with an approved baseline, and reports configuration drift.


Architecture
Local Kubernetes platform
          |
          v
Normalized security snapshot
          |
          +--> Compliance rules
          +--> Approved baseline
          |
          v
Governance auditor
          |
          +--> Compliance findings
          +--> Drift findings
          |
          v
JSON and Markdown audit evidence

Project 09 builds on Project 06. Project 06 establishes a secure Kubernetes baseline; Project 09 measures whether the running platform still matches that approved state.

Governance controls
Control	Requirement	Severity
NS-001	Workload namespaces declare restricted Pod Security enforcement.	High
NS-002	Namespaces identify their security owner and environment.	Medium
WL-001	Workloads run as non-root users.	High
WL-002	Privilege escalation is disabled.	High
WL-003	Linux capabilities are reduced.	High
WL-004	CPU and memory requests and limits are defined.	Medium
NP-001	Workload namespaces use default-deny network isolation.	High
RB-001	Read-only identities do not receive write or secret access.	High
Project structure
09-cloud-security-monitoring-governance-lab/
|-- README.md
|-- .gitignore
|-- architecture/
|   |-- logical-architecture.mmd
|   `-- governance-model.md
|-- baseline/
|   `-- approved-baseline.json
|-- fixtures/
|   |-- compliant-state.json
|   |-- noncompliant-state.json
|   `-- drifted-state.json
|-- reports/
|   `-- .gitkeep
|-- rules/
|   `-- governance-rules.json
|-- scripts/
|   |-- apply-governance-remediation.ps1
|   |-- cleanup.ps1
|   |-- collect-kubernetes-state.ps1
|   `-- run-governance-audit.ps1
|-- evidence/
|   `-- README.md
`-- src/
    `-- audit.py

Generated reports under reports/ are intentionally ignored by Git because they may contain local platform metadata and timestamps.

Run the fixture audits
From the Project 09 directory, run:

$project09 = "C:\Users\ikbal\cybersecurity-engineering-portfolio\09-cloud-security-monitoring-governance-lab"
Set-Location $project09
powershell -ExecutionPolicy Bypass -File ".\scripts\run-governance-audit.ps1"

Expected results:

compliant audit returned the expected exit code: 0
noncompliant audit returned the expected exit code: 1
drifted audit returned the expected exit code: 1
All governance audit scenarios completed as expected.

The compliant fixture matches the approved baseline. The noncompliant fixture demonstrates missing controls. The drifted fixture demonstrates changed, missing, and unexpected resources.

Collect live Kubernetes state
The live collection path requires the kind-cloudsec-lab context and the secure Project 06 workload.

Set-Location $project09
powershell -ExecutionPolicy Bypass -File ".\scripts\collect-kubernetes-state.ps1"

The collector writes reports/current-snapshot.json and records selected namespaces, workloads, network policies, and the read-only observer RBAC Role.

The Project 06 RBAC design places the security-observer service account in security-lab, while the security-observer-readonly Role and RoleBinding are scoped to workload-dev. Project 09 models the Role scope accurately.

Run the live audit
python ".\src\audit.py" `
    --baseline ".\baseline\approved-baseline.json" `
    --state ".\reports\current-snapshot.json" `
    --rules ".\rules\governance-rules.json" `
    --output-json ".\reports\current-audit.json" `
    --output-md ".\reports\current-audit.md"

The final validated live result was:

compliance_findings: 0
drift_findings: 0
total_findings: 0
Status: pass

This result was reached after restoring the disposable kind cluster, applying the secure workload baseline, adding governance labels and network policies, defining workload resource requests and limits, and aligning the approved RBAC model with the actual Kubernetes Role scope.

Governance decisions
The approved baseline is versioned source data. It should be changed only after an architecture review. A baseline must not be rewritten simply to hide an unexpected finding.

A compliant state passes with zero compliance findings and zero drift findings. Any nonzero finding count requires review.

Evidence and safety
Public evidence should contain control IDs, resource counts, and pass/fail decisions, but no kubeconfig contents, service-account tokens, credentials, private keys, personal information, or unnecessary host inventory.

The evidence demonstrates configuration governance.

Limitations
This lab audits selected normalized resources rather than every Kubernetes object. It uses a local kind cluster and a manually approved baseline. A production governance platform would require broader resource coverage, authenticated access, scheduled execution, signed evidence, centralized retention, exception workflows, ownership integration, and stronger change control.

Use this project only on local systems and clusters that you own or are authorized to administer. Do not expose the kind cluster or audit data to the public internet.
