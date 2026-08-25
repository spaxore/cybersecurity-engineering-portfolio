# Secure DevSecOps Supply-Chain Security Lab

Project 08 in the cybersecurity engineering portfolio.

## Objective

This project demonstrates a local-first software supply-chain security pipeline for a small Flask application and its container image. The same security controls are mirrored in GitHub Actions for push and pull-request validation.

The project focuses on prevention and engineering controls rather than SOC operations. It checks source code, dependencies, container configuration, secrets, software inventories, and policy compliance before a workload is considered ready for delivery.

## Security controls

| Control | Tool or mechanism | Result |
|---|---|---|
| Secret detection | Gitleaks | Detects credentials and high-risk secret patterns in project files. |
| Source analysis | Semgrep | Applies project-specific Python rules for unsafe debug mode, shell execution, and hardcoded credentials. |
| Container build | Docker | Builds a demo image with a dedicated non-root runtime user. |
| Container scanning | Trivy | Scans the demo image for high and critical vulnerabilities. |
| Software inventory | Syft | Generates a CycloneDX SBOM for the application directory. |
| Policy as code | Open Policy Agent | Evaluates supply-chain requirements and blocks non-compliant inputs. |
| Automated delivery gate | GitHub Actions | Runs the same core checks on pushes and pull requests. |

## Architecture

```text
Developer change
      |
      v
Source and dependency checks
      |
      +--> Gitleaks secret scan
      +--> Semgrep source scan
      +--> Docker image build
      +--> Trivy image scan
      +--> Syft CycloneDX SBOM
      +--> OPA policy gate
      |
      v
Delivery decision: pass or fail
      |
      v
GitHub Actions mirror on push and pull request
