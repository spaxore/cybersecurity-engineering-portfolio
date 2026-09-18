# Network Zone Model

## Zone definitions

### Z-001 — Untrusted

This zone represents the Internet and other networks that are not controlled by the organization.

**Allowed destination:** Approved DMZ services only.

**Default policy:** Deny.

### Z-002 — DMZ

The DMZ contains public-facing services that must accept limited external traffic.

**Examples:**

- Reverse proxy
- Public web gateway
- Public API gateway

**Allowed communication:**

- HTTPS from the untrusted zone
- Approved application requests to the application zone
- Approved logging to the management zone

**Default policy:** Deny.

### Z-003 — Application

The application zone contains internal services that process requests and business logic.

**Allowed communication:**

- Requests from approved DMZ services
- Database connections to approved data services
- Monitoring from the management zone
- Administrative access from the management zone

**Default policy:** Deny.

### Z-004 — Data

The data zone contains databases and sensitive internal services.

**Allowed communication:**

- Database connections from approved application services
- Administrative access from the management zone
- Backup traffic from approved recovery services

**Default policy:** Deny.

### Z-005 — Management

The management zone contains administrative and security-monitoring systems.

**Examples:**

- Administrative workstation
- Logging collector
- Monitoring service
- Backup controller

**Allowed communication:**

- Administrative access to approved systems
- Log collection from approved zones
- Health checks
- Backup and recovery operations

**Default policy:** Deny.

## Boundary principles

| Boundary | Security principle |
|---|---|
| Untrusted to DMZ | Expose only approved public services |
| DMZ to Application | Permit only required application endpoints |
| Application to Data | Permit only required database protocols |
| Management to all zones | Restrict to named administrators and approved tools |
| Data to Internet | Deny by default |
| Zone to same zone | Deny unless explicitly required |
