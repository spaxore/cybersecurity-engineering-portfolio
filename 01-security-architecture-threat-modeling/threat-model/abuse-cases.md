# Abuse Cases

These abuse cases describe undesirable actions that the architecture must prevent, detect, or limit.

## AC-001 — Deploy an insecure workload

### Scenario

An attacker or careless contributor modifies a workload definition to run as root, enable privilege escalation, or remove network restrictions.

### Preconditions

- The attacker can modify source or submit a change.
- The delivery process accepts the modified definition.

### Potential impact

- Workload compromise
- Lateral movement
- Unauthorized access to platform services
- Increased blast radius

### Preventive controls

- Protected branch review
- Policy-as-code validation
- Non-root workload requirements
- Disabled privilege escalation
- NetworkPolicies
- Restricted RBAC

### Detection and evidence

- Failed policy result
- Changed-file review
- Kubernetes configuration scan
- Deployment audit record

### Residual risk

A privileged administrator may bypass the normal delivery path. Emergency changes require separate review and audit.

---

## AC-002 — Abuse an administrative identity

### Scenario

An attacker obtains a valid administrative session or convinces an operator to approve an unauthorized action.

### Preconditions

- Administrative identity exists.
- Authentication or session protection is weakened.

### Potential impact

- Unauthorized configuration changes
- Access to sensitive platform data
- Destruction or alteration of evidence
- Deployment of malicious workloads

### Preventive controls

- MFA for privileged access
- Separate administrator roles
- Least-privilege RBAC
- Short-lived tokens
- Approval for high-impact changes

### Detection and evidence

- Identity-provider audit events
- Repository history
- Kubernetes audit records
- Governance drift report

### Residual risk

Endpoint compromise and social engineering remain outside the primary control boundary.

---

## AC-003 — Bypass software-supply-chain checks

### Scenario

A contributor modifies a workflow, disables a security check, or uses an alternate delivery path to avoid secret, image, or policy validation.

### Preconditions

- Workflow or pipeline configuration can be changed.
- A bypass path exists.

### Potential impact

- Secret exposure
- Vulnerable image delivery
- Unreviewed artifact deployment
- Loss of confidence in build evidence

### Preventive controls

- Protected workflow files
- Required pipeline checks
- Minimal runner permissions
- Review of workflow changes
- Policy gate failure on violations

### Detection and evidence

- Pipeline status
- Workflow diff
- Security tool output
- Delivery decision record

### Residual risk

A compromised CI/CD platform or administrator may still alter the execution environment.

---

## AC-004 — Restore a tampered backup

### Scenario

A backup artifact is modified while its integrity is not properly verified, then restored into a trusted environment.

### Preconditions

- Backup artifact is available to the restoration process.
- Integrity validation is skipped or incorrectly trusted.

### Potential impact

- Corrupted recovery
- Malicious configuration restored
- Loss of data integrity
- Contamination of the recovery environment

### Preventive controls

- SHA-256 integrity manifest
- Reject-on-mismatch behavior
- Isolated restoration workspace
- Post-restore validation

### Detection and evidence

- Integrity comparison result
- Restore decision
- Recovery validation report
- Tamper-test fixture

### Residual risk

If the trusted manifest is compromised, the integrity process cannot identify all modifications.

---

## AC-005 — Publish sensitive evidence

### Scenario

A generated report or terminal screenshot containing a token, local path, hostname, or private configuration is committed to the public repository.

### Preconditions

- Generated output is copied without review.
- Evidence sanitization is skipped.

### Potential impact

- Credential compromise
- Privacy exposure
- Disclosure of local environment details
- Loss of professional credibility

### Preventive controls

- Evidence review checklist
- Secret scanning
- Synthetic fixtures
- Repository ignore rules
- Removal of host-specific data

### Detection and evidence

- Pre-commit scan
- Pull-request review
- Repository history review
- Evidence checklist

### Residual risk

Manual review can miss unusual encodings or sensitive information hidden in large generated files.
