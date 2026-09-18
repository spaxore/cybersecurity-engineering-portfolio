# System Context

## Objective

The system is a segmented local network architecture designed to protect applications, data, and administrative services from unauthorized access and lateral movement.

## External actors

| Actor | Trust level | Interaction |
|---|---|---|
| Internet user | Untrusted | Requests approved public services |
| External administrator | Restricted | Uses approved remote administration path only |
| Internal user | Controlled | Accesses approved application services |
| Security administrator | Privileged | Performs administration from the management zone |
| Monitoring system | Trusted service | Collects approved logs and health data |

## Network zones

| Zone ID | Zone | Purpose | Trust level |
|---|---|---|---|
| Z-001 | Untrusted | Internet and external networks | Very low |
| Z-002 | DMZ | Public-facing reverse proxy or web gateway | Low |
| Z-003 | Application | Internal application workloads | Medium |
| Z-004 | Data | Databases and sensitive services | High |
| Z-005 | Management | Administration, monitoring, and security tooling | Very high |

## High-level traffic policy

- Internet traffic may reach only approved DMZ services.
- DMZ services may reach only explicitly approved application endpoints.
- Application services may reach only required data services.
- Data services may not initiate connections to the Internet.
- Administrative access must originate from the management zone.
- Management systems may collect logs from approved zones.
- All undocumented traffic is denied.

## Out of scope

- Real enterprise firewall deployment
- Production IP addresses
- Real customer or employee data
- Internet-wide scanning
- Unauthorized access to third-party systems
- High-availability firewall clustering
- Full production-scale DDoS protection

## Security assumptions

1. Firewall configuration changes are reviewed before deployment.
2. Zone membership is documented and maintained.
3. Administrative credentials are protected separately.
4. Logs are collected from approved systems.
5. The lab uses synthetic hosts and test flows.
6. Default-deny behavior remains enabled at each enforcement point.
