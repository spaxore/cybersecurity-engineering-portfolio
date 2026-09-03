# Cybersecurity Engineering Portfolio

A practical cybersecurity engineering portfolio focused on **cloud security architecture, identity, Kubernetes security, DevSecOps, governance, resilience, and defensive platform engineering**.

## About

I am a Cybersecurity Engineering student at ESPRIT, specializing in Network Infrastructure and Data Security, and building toward Cloud Security Architect and Security Engineer roles.

This repository contains hands-on projects developed in controlled local environments using free and open-source tools. The projects are designed to demonstrate how security architecture is defined, implemented, tested, documented, and validated through evidence.

The current portfolio direction emphasizes secure platform design rather than a single operational specialty. It covers privacy protection, Kubernetes security architecture, identity and access management, software supply-chain assurance, configuration governance, backup integrity, recovery testing, and continuity validation.

No production credentials, personal data, private keys, real cloud inventories, or sensitive organizational information are included in this repository.

## Completed portfolio projects

| Project | Focus | Main technologies |
| --- | --- | --- |
| [05 — Image Metadata and Privacy Toolkit](https://github.com/spaxore/cybersecurity-engineering-portfolio/tree/main/05-image-metadata-extractor) | Inspecting EXIF and GPS metadata, identifying privacy exposure, rendering location findings, and creating cleaned image copies. | Python, Pillow, EXIF, GPS privacy, Folium |
| [06 — Local Cloud Security Architecture Lab](https://github.com/spaxore/cybersecurity-engineering-portfolio/tree/main/06-local-cloud-security-architecture-lab) | Comparing insecure and hardened Kubernetes workloads through namespace isolation, Pod Security controls, NetworkPolicies, least-privilege RBAC, policy-as-code, and misconfiguration scanning. | Kubernetes, kind, Docker, NetworkPolicy, RBAC, OPA, Rego, Trivy |
| [07 — Identity and Access Architecture Lab](https://github.com/spaxore/cybersecurity-engineering-portfolio/tree/main/07-identity-and-access-architecture-lab) | Implementing and validating an OIDC identity architecture with authorization-code flow, PKCE, discovery, JWKS, JWT validation, issuer checks, and server-side RBAC. | Keycloak, Flask, OIDC, PKCE, JWT, JWKS, RBAC |
| [08 — Secure DevSecOps Supply-Chain Security Lab](https://github.com/spaxore/cybersecurity-engineering-portfolio/tree/main/08-secure-devsecops-supply-chain-lab) | Building a local software-supply-chain gate that checks secrets, source code, container configuration, vulnerabilities, software inventory, and policy compliance before delivery. | Gitleaks, Semgrep, Docker, Trivy, Syft, CycloneDX, OPA, GitHub Actions |
| [09 — Cloud Security Monitoring and Governance Lab](https://github.com/spaxore/cybersecurity-engineering-portfolio/tree/main/09-cloud-security-monitoring-governance-lab) | Collecting selected Kubernetes platform state, comparing it with an approved security baseline, identifying compliance gaps and configuration drift, and validating remediation. | Kubernetes, kind, PowerShell, Python, JSON baselines, configuration assurance |
| [10 — Resilient and Secure Platform Lab](https://github.com/spaxore/cybersecurity-engineering-portfolio/tree/main/10-resilient-secure-platform-lab) | Creating synthetic platform-state snapshots, verifying backup integrity with SHA-256 manifests, simulating controlled failure, restoring into an isolated workspace, validating the recovered state, and rejecting tampered backup input. | Python, PowerShell, SHA-256, backup and recovery testing, integrity validation |

## Architecture roadmap

The portfolio is being organized as a cloud-security architecture path. The first four areas are planned rework areas, while Projects 05–10 are completed and published.

| Roadmap area | Status | Architecture outcome |
| --- | --- | --- |
| 01 — Security Architecture and Threat Modeling | Planned rework | Define assets, trust boundaries, abuse cases, security requirements, and architecture decisions. |
| 02 — Network Segmentation and Firewall Architecture | Planned rework | Design zones, traffic flows, default-deny boundaries, and validated firewall policy. |
| 03 — Secrets Management and Key Protection | Planned rework | Model secret lifecycles, access boundaries, rotation, and protected local storage. |
| 04 — Infrastructure-as-Code Security and Policy | Planned rework | Validate infrastructure definitions with policy-as-code and secure configuration gates. |
| 05 — Privacy Engineering | Complete | Reduce metadata and location exposure from image artifacts. |
| 06 — Kubernetes Security Architecture | Complete | Harden workloads, namespaces, network boundaries, RBAC, and cluster policy. |
| 07 — Identity and Access Architecture | Complete | Validate modern identity flows, token handling, and authorization boundaries. |
| 08 — DevSecOps Supply-Chain Security | Complete | Prevent insecure source, dependency, image, and policy artifacts from delivery. |
| 09 — Cloud Security Governance | Complete | Detect configuration noncompliance and drift against an approved platform baseline. |
| 10 — Resilience and Secure Recovery | Complete | Verify backup integrity, controlled failure recovery, restoration, and continuity evidence. |

## Engineering principles

The projects follow several consistent principles:

- **Local-first:** Projects can be built and tested on a personal workstation without paid AWS, Azure, or GCP services.

- **Open-source tooling:** The portfolio prioritizes transparent tools such as Kubernetes, kind, Keycloak, Docker, Trivy, OPA, Python, and PowerShell.

- **Architecture before automation:** Each lab documents its objective, trust boundaries, controls, validation method, and limitations.

- **Evidence-based validation:** Security controls are demonstrated through passing and failing fixtures, sanitized summaries, or controlled test results.

- **Least privilege and secure defaults:** The projects prefer default-deny boundaries, explicit authorization, non-root workloads, controlled restoration, and approved baselines.

- **Safe public packaging:** Generated reports, credentials, private keys, local inventories, personal information, and environment-specific artifacts are excluded from Git.

## Tools and technologies

### Cloud and platform security

Kubernetes, kind, Docker, NetworkPolicies, Pod Security controls, RBAC, OPA, Rego, Trivy, PowerShell, Python, and JSON-based security baselines.

### Identity and access

Keycloak, OpenID Connect, PKCE, OAuth concepts, JWT, JWKS, issuer validation, Flask, RBAC, and access-control testing.

### DevSecOps and supply chain

Gitleaks, Semgrep, Trivy, Syft, CycloneDX SBOMs, Open Policy Agent, Dockerfiles, GitHub Actions, and CI/CD security gates.

### Privacy and evidence handling

Pillow, EXIF inspection, GPS privacy analysis, Folium, sanitized evidence, reproducible fixtures, and controlled local workspaces.

### Resilience and governance

Approved baselines, configuration-drift detection, SHA-256 integrity verification, backup archives, isolated restoration, failure simulation, recovery validation, and continuity controls.

## Validation and safety

All projects are conducted in controlled lab environments. Demonstration workloads, fixtures, and platform states are synthetic or intentionally isolated. The repository is not a source of production credentials or operational secrets, and no project should be connected to a system without reviewing its scope and safety assumptions first.

Generated outputs are generally ignored by Git because they can contain local paths, timestamps, package metadata, or other environment-specific information. Public evidence is captured only after review and sanitization.

## Author

**Mohammed Ikbal Messaoudi**

- GitHub: [@spaxore](https://github.com/spaxore)

- Portfolio website: [spaxore.github.io](https://spaxore.github.io/)

- Focus: Cloud Security Architecture, Kubernetes Security, IAM, DevSecOps, Governance, and Resilience
