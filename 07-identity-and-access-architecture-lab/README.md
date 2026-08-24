# Identity and Access Architecture Lab

A free local identity and access management lab demonstrating how a protected application authenticates users with Keycloak and makes server-side authorization decisions based on validated OpenID Connect roles.

## Purpose

This project models a cloud security architecture capability locally. It focuses on identity as a security boundary: users authenticate through a central identity provider, applications validate signed tokens, and authorization is enforced according to least-privilege roles.

The lab does not require AWS or Azure. It runs locally with Docker Desktop, Keycloak, Flask, Python, and OpenID Connect.

## Architecture objective

The application demonstrates:

- Authorization Code flow with PKCE using S256.
- OIDC discovery through Keycloak metadata.
- Callback state validation.
- JWT signature validation using Keycloak JWKS keys.
- Issuer and authorized-party validation.
- Server-side role-based authorization.
- Explicit access-denied decisions.
- Local-only development boundaries.

## Local architecture

Browser -> Keycloak cloudsec realm -> Flask protected application

Keycloak runs at `http://localhost:8080`.
The protected application runs at `http://localhost:8000`.

## Identity model

| Identity | Role | Intended access |
|---|---|---|
| `observer` | `security-observer` | Read-only security observer workspace. |
| `developer` | `developer` | Developer workspace. |
| `lab-admin` | `security-admin` | Administrative workspace for controlled testing. |

The test passwords are disposable local-lab credentials. Never reuse them outside this exercise.

## Project structure

    07-identity-and-access-architecture-lab/
    |-- README.md
    |-- docker-compose.yml
    |-- .gitignore
    |-- keycloak/
    |   |-- README.md
    |   `-- cloudsec-realm.example.json
    |-- protected-app/
    |   |-- app.py
    |   |-- requirements.txt
    |   |-- run_project07.ps1
    |   `-- README.md
    |-- architecture/
    |   |-- logical-architecture.mmd
    |   |-- threat-model.md
    |   `-- access-control-matrix.md
    `-- reports/
        `-- README.md

## Run locally

Start Keycloak from this project directory:

`docker compose up -d`

Verify that Keycloak is available:

`curl.exe -i http://localhost:8080/realms/cloudsec/.well-known/openid-configuration`

Start the protected application:

`Set-Location .\protected-app`

`.\.venv\Scripts\python.exe app.py`

Open `http://localhost:8000` and select **Sign in with Keycloak**.

## Authorization test plan

| Test | Expected result |
|---|---|
| Sign in as `observer` and open `/observer` | Allowed. |
| Sign in as `observer` and open `/developer` | Denied with HTTP 403. |
| Sign in as `developer` and open `/developer` | Allowed. |
| Sign in as `developer` and open `/observer` | Denied with HTTP 403. |
| Sign in as `lab-admin` and open `/admin` | Allowed. |
| Modify the callback state | Callback rejected. |
| Stop Keycloak and attempt login | Authentication fails closed. |

## Security decisions

The application uses authorization code with PKCE and does not use the password grant. Tokens are validated using Keycloak's published signing keys. Authorization is enforced on the server, not by hiding or showing client-side buttons.

The local Keycloak service binds to localhost only. Development credentials and HTTP are used solely for this training lab.

## Limitations

This project is a local identity architecture simulation. It does not replace a production identity platform. A production deployment would require HTTPS, secure cookie settings, external secret management, MFA enforcement, audit logging, rate limiting, key rotation, high availability, and hardened Keycloak configuration.

Do not expose this development service to the internet. Do not commit `.env` files, live realm files with passwords, access tokens, private keys, or personal data.

## References

- https://www.keycloak.org/server/containers
- https://www.keycloak.org/server/importExport
- https://www.keycloak.org/securing-apps/oidc-layers
