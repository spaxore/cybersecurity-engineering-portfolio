# Architecture Decision Records

## ADR-001 — Use a composite platform model

### Status

Accepted

### Context

Projects 06–10 already implement related security capabilities across Kubernetes, identity, supply-chain security, governance, and recovery. Modeling them as unrelated systems would hide important dependencies and trust relationships.

### Decision

Represent Projects 06–10 as one logical composite platform for threat-modeling purposes.

### Rationale

This approach:

- Reuses existing architecture and evidence.
- Shows how controls interact across project boundaries.
- Avoids inventing an unrelated fictional business system.
- Creates a foundation for the first four architecture projects.
- Makes residual risks and control dependencies easier to explain.

### Consequences

The model is logical rather than a claim that all components are deployed as one production system. Relationships must be described as architectural dependencies and integration assumptions.

---

## ADR-002 — Use default-deny network boundaries

### Status

Accepted

### Context

Implicit network trust allows workloads or services to communicate without an explicit business or platform requirement.

### Decision

Use default-deny ingress and egress principles, adding only explicitly approved communication paths.

### Rationale

Default-deny boundaries:

- Reduce accidental exposure.
- Limit lateral movement.
- Make allowed flows reviewable.
- Produce clearer validation evidence.
- Align with least-privilege architecture.

### Consequences

The design requires explicit flow documentation and may require additional configuration when a legitimate service-to-service path is introduced.

---

## ADR-003 — Validate identity tokens at the service boundary

### Status

Accepted

### Context

A service cannot safely trust a token merely because it was received from a browser, proxy, or another application component.

### Decision

Each protected service must validate token signature, issuer, audience, expiration, and required scopes or roles.

### Rationale

Validation at the service boundary prevents incorrect trust assumptions and ensures authorization is enforced where the protected action occurs.

### Consequences

Services must have access to trusted identity-provider metadata and must define behavior for expired, invalid, or unavailable key information.

---

## ADR-004 — Treat policy checks as delivery gates

### Status

Accepted

### Context

Security review performed only after deployment can allow insecure source, images, or configurations to reach the runtime environment.

### Decision

Run secret, source, image, SBOM, and policy checks before a delivery decision is approved.

### Rationale

Preventive checks:

- Provide earlier feedback.
- Reduce the cost of remediation.
- Create repeatable evidence.
- Make security requirements executable.
- Support consistent review across changes.

### Consequences

The pipeline must define failure behavior, maintain its own dependencies securely, and avoid allowing emergency bypasses to become normal practice.

---

## ADR-005 — Restore backups only into an isolated workspace

### Status

Accepted

### Context

A backup may be corrupted, tampered with, incomplete, or incompatible with the intended destination.

### Decision

Verify backup integrity before restoration and restore into an isolated workspace before recovery validation.

### Rationale

Isolation reduces the risk that untrusted recovery input alters the source environment. Integrity verification provides a clear rejection decision for tampered artifacts.

### Consequences

Recovery testing requires additional storage and validation steps. Successful restoration into an isolated workspace does not automatically prove production recovery readiness.
