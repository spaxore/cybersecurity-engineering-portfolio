# Default-Deny Firewall Policy

## Policy statement

The firewall uses a **default-deny** posture. Traffic is permitted only when a rule explicitly identifies the source zone, destination zone, protocol, port, purpose, and owner.

Unmatched traffic is denied and should be logged.

## Rule format

| Field | Requirement |
|---|---|
| Rule ID | Unique identifier |
| Source zone | Specific source zone or approved object |
| Destination zone | Specific destination zone or approved object |
| Protocol | Explicit protocol |
| Destination port | Explicit port or narrowly defined service |
| Action | Allow or Deny |
| Logging | Required for denied traffic and sensitive allowed traffic |
| Owner | Responsible service or team |
| Review | Periodic or change-triggered review |

## Firewall rules

| Rule ID | Source | Destination | Protocol | Port | Action | Logging | Purpose |
|---|---|---|---|---:|---|---|---|
| FW-001 | Z-001 | Z-002 | TCP | 443 | Allow | Yes | Public HTTPS access |
| FW-002 | Z-001 | Z-002 | TCP | 80 | Allow | Yes | Redirect HTTP to HTTPS |
| FW-003 | Z-001 | Z-003 | Any | Any | Deny | Yes | Block direct application exposure |
| FW-004 | Z-001 | Z-004 | Any | Any | Deny | Yes | Block direct data exposure |
| FW-005 | Z-002 | Z-003 | TCP | 8443 | Allow | Yes | Gateway-to-application traffic |
| FW-006 | Z-002 | Z-004 | Any | Any | Deny | Yes | Block DMZ-to-data access |
| FW-007 | Z-003 | Z-004 | TCP | 5432 | Allow | Yes | Approved database access |
| FW-008 | Z-003 | Z-004 | TCP | 3306 | Deny | Yes | Block unapproved database protocol |
| FW-009 | Z-004 | Z-001 | Any | Any | Deny | Yes | Block data-zone Internet egress |
| FW-010 | Z-005 | Z-002 | TCP | 22 | Allow | Yes | Restricted administration |
| FW-011 | Z-005 | Z-003 | TCP | 22 | Allow | Yes | Restricted administration |
| FW-012 | Z-005 | Z-004 | TCP | 22 | Allow | Yes | Restricted data administration |
| FW-013 | Z-005 | Z-002 | TCP | 443 | Allow | Yes | Management and health checks |
| FW-014 | Z-005 | Z-003 | TCP | 443 | Allow | Yes | Application management |
| FW-015 | Z-002 | Z-005 | UDP | 514 | Allow | Yes | DMZ log forwarding |
| FW-016 | Z-003 | Z-005 | UDP | 514 | Allow | Yes | Application log forwarding |
| FW-017 | Z-004 | Z-005 | TCP | 443 | Allow | Yes | Backup export |
| FW-018 | Z-002 | Z-004 | TCP | 5432 | Deny | Yes | Prevent DMZ database access |
| FW-019 | Z-004 | Z-003 | Any | Any | Deny | Yes | Block unsolicited data connections |
| FW-999 | Any | Any | Any | Any | Deny | Yes | Final default-deny rule |

## Rule-order requirements

1. Stateful return traffic is evaluated before new-connection rules.
2. Specific rules are evaluated before broad rules.
3. Explicit deny rules are retained for sensitive prohibited paths.
4. `FW-999` remains the final rule.
5. Any rule change requires review and validation.
6. Unmatched traffic must never be silently allowed.

## Logging requirements

Log at least:

- Rule ID
- Timestamp
- Source zone and address
- Destination zone and address
- Protocol and port
- Action
- Connection state
- Reason for denial where available

Do not place credentials, tokens, or sensitive payloads in firewall evidence.
