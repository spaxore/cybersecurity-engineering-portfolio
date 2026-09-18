# Network Segmentation and Firewall Architecture

## Purpose

This project designs and validates a segmented defensive network architecture using security zones, explicit traffic flows, default-deny firewall policy, and repeatable validation evidence.

The project demonstrates how network boundaries reduce lateral movement, restrict unnecessary exposure, and enforce least-privilege communication between services.

## Scope

The lab models a local enterprise-style network containing:

- Internet or untrusted external networks
- An edge firewall
- A public-facing DMZ
- An internal application zone
- A protected data zone
- A management and monitoring zone

No real production systems, credentials, customer data, or external networks are used.

## Security objectives

1. Separate systems according to trust and sensitivity.
2. Permit only documented business-required traffic.
3. Deny unspecified traffic by default.
4. Restrict administrative access to the management zone.
5. Prevent direct Internet access to the data zone.
6. Limit lateral movement between workloads.
7. Produce evidence for both allowed and denied traffic.
8. Document assumptions, limitations, and residual risks.

## Project stages

| Stage | Outcome |
|---|---|
| 1 | System context and security zones |
| 2 | Logical network architecture |
| 3 | Traffic-flow matrix |
| 4 | Default-deny firewall policy |
| 5 | Allowed and denied traffic fixtures |
| 6 | Repeatable policy validation |
| 7 | Threat and control mapping |
| 8 | Evidence guidance and final review |

## Relationship to Project 01

Project 01 defined abstract trust boundaries. Project 02 converts those boundaries into concrete network zones, permitted flows, firewall rules, and validation tests.

## Safety boundary

This is a defensive architecture lab. Validation is limited to synthetic network flows, local fixtures, and authorized lab systems.
