# Evidence Guidance

## Required evidence

Project 2 evidence should demonstrate:

1. The defined network zones.
2. The documented allowed and denied flows.
3. The default-deny firewall posture.
4. Successful allowed-flow tests.
5. Successful denied-flow tests.
6. The absence of undocumented permits.
7. The limitations of the local model.

## Recommended evidence files

| Evidence | Description |
|---|---|
| `zone-model-review.md` | Review of zone purpose and trust levels |
| `traffic-matrix-review.md` | Review of allowed and denied flows |
| `policy-validation.txt` | Sanitized validator output |
| `control-coverage.md` | Mapping between controls and test cases |
| `architecture-review.md` | Final design review and residual risks |

## Sanitization checklist

Before committing evidence, remove:

- Real IP addresses
- Real hostnames
- VPN details
- Firewall credentials
- API tokens
- Private keys
- Customer or employee information
- Internal network diagrams
- Unreviewed command history
- Personal Windows usernames and paths

Use synthetic zone names such as:

```text
Z-001 Untrusted
Z-002 DMZ
Z-003 Application
Z-004 Data
Z-005 Management
```

## Evidence interpretation

A passing test demonstrates that the local policy model produced the expected decision. It does not prove that a production firewall is secure.

Evidence should distinguish between:

- `PASS` — expected policy decision was produced.
- `FAIL` — policy decision did not match the expected result.
- `NOT TESTED` — no validation was performed.
- `RESIDUAL RISK` — risk remains after the control.

## Scope limitation

This project is a defensive, authorized network-architecture lab. It uses synthetic traffic definitions and local policy validation. It does not authorize scanning, probing, or accessing networks that are not part of the controlled lab.
