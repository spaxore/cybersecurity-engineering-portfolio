# Reports and evidence

This directory is reserved for local validation evidence. Generated reports are ignored by Git so that credentials, host details, tokens, and noisy local output are not accidentally published.

Recommended evidence includes:

| Evidence | Purpose |
|---|---|
| OIDC discovery response status | Confirms that the realm publishes usable OIDC metadata. |
| Successful role test | Demonstrates that an assigned role reaches its intended workspace. |
| Denied role test | Demonstrates least-privilege route enforcement with HTTP 403. |
| Invalid-state test | Demonstrates callback protection against login CSRF. |
| Client redirect review | Demonstrates that local redirect URIs are explicitly configured. |
| Account-switching test | Demonstrates that the application does not silently reuse the previous account. |

Do not commit access tokens, cookies, `.env` files, live realm exports, passwords, private keys, or personal data. Keep only sanitized screenshots or summaries in a public repository.
