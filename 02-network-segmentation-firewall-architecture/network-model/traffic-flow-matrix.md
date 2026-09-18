# Traffic-Flow Matrix

All traffic is denied by default. A flow is allowed only when it has a documented source, destination, protocol, port, purpose, and owner.

| Flow ID | Source zone | Destination zone | Protocol | Port | Purpose | Decision | Owner |
|---|---|---|---|---:|---|---|---|
| F-001 | Z-001 Untrusted | Z-002 DMZ | TCP | 443 | Public HTTPS access to approved gateway | Allow | Web owner |
| F-002 | Z-001 Untrusted | Z-002 DMZ | TCP | 80 | Optional HTTP redirect to HTTPS | Allow with restriction | Web owner |
| F-003 | Z-001 Untrusted | Z-003 Application | TCP | Any | Direct access to internal application | Deny | Platform owner |
| F-004 | Z-001 Untrusted | Z-004 Data | TCP | Any | Direct access to protected data | Deny | Data owner |
| F-005 | Z-002 DMZ | Z-003 Application | TCP | 8443 | Gateway-to-application request | Allow | Application owner |
| F-006 | Z-002 DMZ | Z-004 Data | TCP | 5432 | Direct DMZ-to-database access | Deny | Data owner |
| F-007 | Z-003 Application | Z-004 Data | TCP | 5432 | Approved application database access | Allow | Application owner |
| F-008 | Z-003 Application | Z-004 Data | TCP | 3306 | Unapproved alternate database access | Deny | Data owner |
| F-009 | Z-004 Data | Z-001 Untrusted | TCP | 443 | Direct Internet egress from data zone | Deny | Data owner |
| F-010 | Z-005 Management | Z-002 DMZ | TCP | 22 | Administrative maintenance | Allow | Security administrator |
| F-011 | Z-005 Management | Z-003 Application | TCP | 22 | Administrative maintenance | Allow | Security administrator |
| F-012 | Z-005 Management | Z-004 Data | TCP | 22 | Restricted data-service administration | Allow with restriction | Data administrator |
| F-013 | Z-005 Management | Z-002 DMZ | TCP | 443 | Management interface or health check | Allow | Security administrator |
| F-014 | Z-005 Management | Z-003 Application | TCP | 443 | Application administration or monitoring | Allow | Security administrator |
| F-015 | Z-002 DMZ | Z-005 Management | UDP | 514 | Approved log forwarding | Allow | SOC owner |
| F-016 | Z-003 Application | Z-005 Management | UDP | 514 | Approved log forwarding | Allow | SOC owner |
| F-017 | Z-004 Data | Z-005 Management | TCP | 443 | Backup export to recovery controller | Allow with restriction | Recovery owner |
| F-018 | Z-003 Application | Z-002 DMZ | TCP | Any | Unnecessary reverse-direction access | Deny | Platform owner |
| F-019 | Z-004 Data | Z-003 Application | TCP | Any | Unsolicited database-to-application connection | Deny | Data owner |
| F-020 | Any zone | Any zone | Any | Any | Undocumented traffic | Deny | Network owner |

## Policy interpretation

- `Allow` means the flow is required and may be implemented.
- `Allow with restriction` means the flow requires source restrictions, authentication, logging, or other compensating controls.
- `Deny` means the flow must be blocked.
- `Any` is used only to document a deny rule or a deliberately broad prohibited category.
- Return traffic for an approved stateful connection is assumed to be handled by the firewall state table.
- No rule should be created solely because traffic is technically convenient.

## Review requirements

Each allowed flow must have:

1. A documented business or security purpose.
2. A named owner.
3. A defined source and destination.
4. A limited protocol and port.
5. Logging or monitoring where appropriate.
6. A review date or change reference.
