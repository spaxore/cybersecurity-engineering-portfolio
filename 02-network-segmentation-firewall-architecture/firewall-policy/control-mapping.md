# Network Segmentation Control Mapping

| Control ID | Security objective | Implementation | Validation |
|---|---|---|---|
| NS-001 | Deny undocumented traffic | `FW-999` final default-deny rule | TC-010 |
| NS-002 | Protect public services | Allow only HTTPS from Z-001 to Z-002 | TC-001 |
| NS-003 | Prevent direct application exposure | Deny Z-001 to Z-003 | TC-002 |
| NS-004 | Prevent direct data exposure | Deny Z-001 to Z-004 | TC-003 |
| NS-005 | Restrict DMZ-to-application access | Allow only TCP 8443 from Z-002 to Z-003 | TC-004 |
| NS-006 | Prevent DMZ-to-data access | Deny Z-002 to Z-004 | TC-005 |
| NS-007 | Restrict application database access | Allow only TCP 5432 from Z-003 to Z-004 | TC-006 |
| NS-008 | Block unapproved database protocols | Deny TCP 3306 from Z-003 to Z-004 | TC-007 |
| NS-009 | Prevent data-zone Internet egress | Deny Z-004 to Z-001 | TC-008 |
| NS-010 | Restrict administration | Permit management traffic from Z-005 only | TC-009 |
| NS-011 | Log security-relevant traffic | Log denied traffic and sensitive allowed traffic | Policy review |
| NS-012 | Support repeatable validation | JSON policy fixture and Python validator | All test cases |

## Threat relationship

| Threat | Network control |
|---|---|
| Unauthorized external access | Z-001 restrictions and default deny |
| Lateral movement | Zone separation and explicit inter-zone rules |
| Direct database exposure | Z-004 isolation |
| Unauthorized administration | Z-005 management boundary |
| Data exfiltration | Restricted data-zone egress |
| Policy bypass | Final default-deny rule and automated tests |
| Unreviewed firewall change | Rule ownership and review requirements |

## Residual risks

The lab does not model:

- Firewall high availability
- Large-scale denial-of-service attacks
- Compromise of the firewall administrator
- Encrypted malicious traffic inspection
- Host-level compromise inside a trusted zone
- Production-scale routing complexity
