# Evidence

This directory is reserved for sanitized screenshots or exported summaries from the Project 08 pipeline.

Recommended evidence:

| Evidence | Demonstrated control |
|---|---|
| Local pipeline pass | All deterministic security checks complete successfully. |
| Local policy denial | OPA rejects the failing policy fixture. |
| GitHub Actions run | The same checks execute on push or pull request. |
| SBOM artifact | The application dependency inventory is generated. |
| Container scan result | High and critical image findings are gated. |

Do not commit access tokens, repository secrets, credentials, private keys, personal data, or raw logs containing sensitive values. Keep generated reports in the ignored `reports` directory unless they have been reviewed and sanitized.
