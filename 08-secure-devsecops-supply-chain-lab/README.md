# Secure DevSecOps Supply-Chain Security Lab

Project 08 in the cybersecurity engineering portfolio.

## Objective

This project demonstrates a local-first software supply-chain security pipeline for a small Flask application and its container image. The same security controls are mirrored in GitHub Actions for push and pull-request validation.

The project focuses on prevention and engineering controls. It checks source code, dependencies, container configuration, secrets, software inventories, and policy compliance before a workload is considered ready for delivery.

## Security controls

| Control | Tool or mechanism | Result |
| --- | --- | --- |
| Secret detection | Gitleaks | Detects credentials and high-risk secret patterns in project files. |
| Source analysis | Semgrep | Applies project-specific Python rules for unsafe debug mode, shell execution, and hardcoded credentials. |
| Container build | Docker | Builds a demo image with a dedicated non-root runtime user. |
| Container scanning | Trivy | Scans the demo image for high and critical vulnerabilities. |
| Software inventory | Syft | Generates a CycloneDX SBOM for the application directory. |
| Policy as code | Open Policy Agent | Evaluates supply-chain requirements and blocks non-compliant inputs. |
| Automated delivery gate | GitHub Actions | Runs the same core checks on pushes and pull requests. |

## Architecture

```
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
```

The local pipeline is the primary demonstration environment. GitHub Actions provides a reproducible hosted mirror of the same preventive checks, but no paid cloud service is required to understand or run the lab.

## Project structure

```
08-secure-devsecops-supply-chain-lab/
|-- .github/
|   `-- workflows/
|       `-- security-pipeline.yml
|-- .semgrep/
|   `-- rules.yml
|-- app/
|   |-- Dockerfile
|   |-- requirements.txt
|   `-- src/
|       `-- app.py
|-- evidence/
|   `-- README.md
|-- policies/
|   |-- policy-input-failing.json
|   |-- policy-input.json
|   `-- supply-chain.rego
|-- reports/
|   `-- .gitkeep
|-- scripts/
|   |-- cleanup.ps1
|   `-- run_pipeline.ps1
|-- .gitignore
|-- .gitleaks.toml
`-- README.md
```

Generated reports are deliberately kept out of version control by default. The `reports/.gitkeep` file preserves the output directory in the repository.

## Prerequisites

The lab is designed for Windows PowerShell, Docker Desktop using the Linux engine, and locally installed command-line tools. The required tools are Docker, Python 3, Gitleaks, Semgrep, Trivy, Syft, and Git. OPA can be executed locally through its official Docker image, so a separate host installation is not required.

Verify the important tools before running the pipeline:

```
docker version
python --version
gitleaks version
semgrep --version
trivy --version
syft version
git --version
```

The Docker daemon must be running before the image-build and container-scan stages are started.

## Local validation

From the Project 08 directory, run the complete local pipeline:

```
Set-Location "C:\Users\ikbal\cybersecurity-engineering-portfolio\08-secure-devsecops-supply-chain-lab"
powershell -ExecutionPolicy Bypass -File ".\scripts\run_pipeline.ps1"
```

The pipeline performs the following sequence:

1. Scans the repository for secrets with Gitleaks.

1. Scans the Python source with the project-specific Semgrep rules.

1. Builds the demo Docker image.

1. Scans the image with Trivy.

1. Generates a CycloneDX software bill of materials with Syft.

1. Evaluates the compliant policy input with OPA.

1. Reports the final delivery decision and output locations.

A successful run ends with a message similar to:

```
Policy violations present: false
OPA policy gate passed with zero violations.
Pipeline completed successfully.
```

## Policy demonstrations

The Rego policy requires a container definition to use a pinned base-image tag, run as a non-root user, and define a health check. The compliant input demonstrates a passing policy decision:

```
$project08 = "C:\Users\ikbal\cybersecurity-engineering-portfolio\08-secure-devsecops-supply-chain-lab"
$volume = "${project08}:/repo"

docker run --rm `
    -v $volume `
    openpolicyagent/opa:latest eval `
    --format pretty `
    --data /repo/policies/supply-chain.rego `
    --input /repo/policies/policy-input.json `
    "data.supplychain.deny"
```

The compliant input returns an empty result. The intentionally failing fixture demonstrates the gate detecting three violations:

```
docker run --rm `
    -v $volume `
    openpolicyagent/opa:latest eval `
    --fail-defined `
    --format pretty `
    --data /repo/policies/supply-chain.rego `
    --input /repo/policies/policy-input-failing.json `
    "data.supplychain.deny"
```

The expected failing findings are:

```
container must define a health check
container must run as a non-root user
container must use a pinned base image tag
```

This pair of fixtures shows both sides of a policy gate: an approved input passes, while a deliberately non-compliant input produces a non-zero result and explains why delivery should be blocked.

## Reports

The local pipeline writes generated output under `reports/`:

| Report | Purpose |
| --- | --- |
| `trivy-image.json` | Machine-readable container vulnerability and package-scan result. |
| `sbom.cdx.json` | CycloneDX software bill of materials generated by Syft. |
| Other local outputs | Tool-specific logs or intermediate results created during execution. |

Reports can contain environment-specific paths, package metadata, or other details that should be reviewed before public sharing. They are ignored by Git unless explicitly sanitized and approved.

To remove generated reports and Python cache files after testing:

```
powershell -ExecutionPolicy Bypass -File ".\scripts\cleanup.ps1"
```

## GitHub Actions

The workflow at `.github/workflows/security-pipeline.yml` mirrors the main preventive controls on pushes and pull requests. It is intended to make the security gate visible as part of the repository change process.

The workflow does not replace local validation. Local execution remains useful for debugging, reviewing reports, and testing policy fixtures before creating a commit. The workflow also does not deploy the application or connect to a production environment.

## Evidence and safety

The `evidence/README.md` file describes how to produce sanitized evidence for the project. Suitable public evidence includes a successful pipeline summary, a zero-violation OPA result, a failing policy-fixture result, and a report-directory listing that does not disclose personal or host-specific information.

Do not commit `.env` files, credentials, access tokens, private keys, personal data, local virtual environments, Docker credentials, or unsanitized host information. Do not publish generated reports without reviewing them. The demo container and pipeline are intended for local development and validation only.

## What this project demonstrates

This lab demonstrates that supply-chain security can be implemented as an engineering control before deployment. It connects source analysis, secret prevention, container hardening, vulnerability assessment, software inventory, and policy-as-code enforcement into one repeatable delivery decision.

The primary architectural lesson is that security controls should be automated at the point where changes are built and reviewed. A developer receives actionable feedback before an insecure image or dependency set becomes a deployment artifact.

The project also demonstrates separation of concerns. Gitleaks and Semgrep protect source and change quality, Trivy examines the built image, Syft provides transparency into included software, and OPA expresses organization-specific requirements independently from the build script.

## Limitations

This is a deliberately small local lab rather than a production software factory. It does not provide signed artifact promotion, a private registry, admission control, long-term vulnerability tracking, dependency-update automation, or a production secrets manager. Those capabilities are appropriate future extensions, but they are outside the scope of this free, local-first portfolio project.

The vulnerability result from Trivy is time-dependent because vulnerability databases and package versions change. The important repeatable outcome is that the image is scanned and the result is made visible before delivery; a current scan should always be interpreted using the tool output generated at that time.

This project is a DevSecOps supply-chain assurance lab. It is not a SOC, SIEM, detection-engineering, incident-response, or threat-hunting project.
