# Resilience Threat Model

## Scope

This threat model covers the local backup and recovery workflow used by Project 10. It focuses on integrity, availability, and preservation of security controls during recovery testing.

## Assets

| Asset | Required property |
|---|---|
| Synthetic platform-state snapshot | Integrity and correctness. |
| Backup archive | Integrity and availability. |
| External manifest | Accurate expected digest values. |
| Recovery workspace | Isolation and controlled write access. |
| Recovery evidence | Accuracy without sensitive disclosure. |

## Threats and mitigations

| Threat | Example | Demonstrated mitigation |
|---|---|---|
| Backup tampering | An archive byte changes after creation. | SHA-256 mismatch blocks verification. |
| Incomplete state | A required service or security property is missing. | State validation blocks backup or recovery acceptance. |
| Unsafe extraction | An archive member uses an absolute or parent-traversal path. | Archive-member validation rejects the path. |
| Source overwrite | Recovery testing writes over the known-good state. | Restoration uses a separate recovery workspace. |
| False recovery confidence | Files extract but security requirements are missing. | Post-restore validation checks the recovered state. |
| Evidence leakage | Reports expose local or confidential information. | Synthetic state, ignored outputs, and evidence rules reduce disclosure risk. |

## Trust assumptions

The lab assumes that the external manifest is stored separately from the archive and is available for verification. In a production design, the manifest would need stronger authenticity protection, such as signing, protected storage, or an independently trusted key.

The lab also assumes that the synthetic state is small enough to package as a single archive. Production systems would require data-store consistency controls, encryption-key recovery, retention policy, and tested restoration ordering.

## Out of scope

The lab does not model ransomware encryption, compromised key management, database transaction consistency, multi-site failover, legal retention, or a production disaster-recovery facility. Those topics require system-specific data-flow and trust-boundary analysis.
