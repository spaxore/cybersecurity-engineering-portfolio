# Threat Model

## Scope

This lab models a local protected application using Keycloak as the identity provider. The purpose is to demonstrate identity boundaries, token validation, least-privilege authorization, and explicit access-denied decisions.

## Assets

| Asset | Security concern |
|---|---|
| Keycloak realm | Incorrect realm configuration or excessive administrator access. |
| User identities | Credential theft, account misuse, and unauthorized role assignment. |
| OIDC tokens | Forgery, replay, issuer confusion, or signature-validation failure. |
| Protected routes | Unauthorized access to observer, developer, or administrator functions. |
| Realm configuration | Accidental publication of passwords or unsafe redirect URIs. |

## Trust boundaries

| Boundary | Description |
|---|---|
| Browser boundary | The browser is an untrusted user-agent that carries the authorization response. |
| Identity boundary | Keycloak issues tokens for the `cloudsec` realm. |
| Application boundary | Flask validates tokens and enforces route authorization. |
| Filesystem boundary | Local configuration may contain disposable credentials and must remain uncommitted. |

## Threat scenarios and controls

| Threat | Potential impact | Control or mitigation | Validation evidence |
|---|---|---|---|
| Callback state tampering | A login response from an unrelated request is accepted. | A random state value is stored in the session and compared during callback. | Invalid-state callback test is rejected. |
| Authorization-code interception | An attacker attempts to redeem a captured authorization code. | PKCE S256 verifier and challenge are used during token exchange. | Code exchange includes the verifier. |
| Forged token | An unauthorized user receives a fabricated role. | JWT signature is checked against Keycloak JWKS keys. | Invalid signature fails validation. |
| Wrong issuer | A token from another realm is accepted. | The expected issuer is validated. | Token with the wrong issuer is rejected. |
| Unauthorized route access | A user reaches a workspace without its role. | Server-side role checks return HTTP 403. | Observer and developer denial tests. |
| Unsafe redirect | Authorization or logout responses are sent to an unsafe URL. | Exact local redirect values are registered in Keycloak. | Keycloak client settings review. |
| Credential publication | Test passwords become public repository content. | Live realm exports and `.env` are ignored; only a sanitized example is committed. | Secret search returns no live password matches. |
| Keycloak exposure | The development identity service is reachable from other hosts. | The container port is bound to `127.0.0.1`. | Compose configuration review. |
| SSO session misuse | A browser silently reuses the previous account. | Login requests use `prompt=login`, and logout redirects through Keycloak. | Account-switching test. |

## Residual risk

The lab uses HTTP, development mode, sample credentials, and Flask's development server. These choices are appropriate only for localhost training. Production use would require HTTPS, secure cookie settings, external secret management, MFA, audit logging, rate limiting, key rotation, hardened Keycloak settings, and a production WSGI server.

## Responsible use

Use this lab only on systems and identities you own or are authorized to administer. Do not expose it to the public internet and do not reuse the test credentials.
