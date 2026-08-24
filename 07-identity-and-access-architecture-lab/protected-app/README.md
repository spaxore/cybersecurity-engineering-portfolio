# Identity and Access Architecture Lab

A free local identity lab that demonstrates how a protected application authenticates users with Keycloak and makes server-side authorization decisions from validated OIDC access tokens.

## Architecture

```
Browser
  |
  | Authorization Code + PKCE
  v
Keycloak: cloudsec realm :8080
  |
  | signed access token + realm roles
  v
Flask protected app :8000
  |
  +-- /observer  requires security-observer
  +-- /developer requires developer
  +-- /admin     requires security-admin
```

## Features

- Local Keycloak realm imported from version-controlled JSON.

- Authorization-code flow with PKCE S256.

- OIDC discovery instead of hard-coded endpoint assumptions.

- State validation to reduce callback forgery risk.

- JWT signature validation against Keycloak JWKS.

- Issuer and authorized-party checks.

- Server-side role authorization for protected routes.

- Explicit denied decisions for roles not present in the token.

- Local-only development binding on `127.0.0.1`.

## Project files

```
project-07/
|-- app.py
|-- requirements.txt
|-- run_project07.ps1
|-- docker-compose.yml
|-- .env
|-- keycloak/
|   `-- cloudsec-realm.json
`-- README.md
```

Do not commit `.env`, real credentials, access tokens, or private keys. The sample users and passwords are disposable local-lab values only.

## Run Keycloak

From the Keycloak project directory:

```
docker compose up -d
docker compose ps
curl.exe http://localhost:8080/realms/cloudsec/.well-known/openid-configuration
```

The discovery endpoint should return HTTP 200 and JSON metadata.

## Run the protected application

Create a Python virtual environment and install dependencies:

```
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Set local environment values and start the app:

```
$env:FLASK_SECRET_KEY = "local-development-secret-change-me"
$env:KEYCLOAK_BASE = "http://localhost:8080"
$env:KEYCLOAK_REALM = "cloudsec"
$env:KEYCLOAK_CLIENT_ID = "security-console"
$env:OIDC_REDIRECT_URI = "http://localhost:8000/callback"
.\.venv\Scripts\python.exe app.py
```

Alternatively, save `app.py`, `requirements.txt`, and `run_project07.ps1` in the same directory and run:

```
.\run_project07.ps1
```

Open:

```
http://localhost:8000
```

## Authorization test plan

| Test | Expected result |
| --- | --- |
| Sign in as `observer` | Dashboard shows `security-observer`. `/observer` is allowed. `/developer` is denied. |
| Sign in as `developer` | Dashboard shows `developer`. `/developer` is allowed. `/observer` is denied. |
| Sign in as either user and open `/admin` | Access is denied because neither test user has `security-admin`. |
| Modify the callback state | Callback is rejected. |
| Stop Keycloak and attempt login | Discovery or token exchange fails closed with an error. |

## Security decisions

The application uses authorization code with PKCE and disables direct password grants for the public client. It validates the token signature using the realm’s published JWKS keys, checks the expected issuer, and enforces roles on the server rather than trusting a client-side display value.

This is a localhost training application. Development mode, HTTP, sample credentials, and the Flask development server are not suitable for production. A production system would require HTTPS, a production WSGI server, secret management, secure cookies, key rotation, audit logging, rate limiting, and hardened Keycloak configuration.

## References

- [Keycloak container guide](https://www.keycloak.org/server/containers)

- [Keycloak realm import and export](https://www.keycloak.org/server/importExport)

- [Keycloak OpenID Connect endpoints](https://www.keycloak.org/securing-apps/oidc-layers)