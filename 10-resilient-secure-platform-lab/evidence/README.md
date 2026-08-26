# Evidence Guidance

Project 10 produces sanitized evidence for backup integrity, controlled failure simulation, recovery validation, and tamper rejection.

## Recommended evidence

The safest public evidence is a screenshot or sanitized text summary containing these four results:

| Evidence item | Expected result |
|---|---|
| Backup integrity verification | `pass` |
| Controlled failure simulation | `pass` |
| Isolated restore validation | `pass` |
| Tampered backup rejection | `pass` with expected exit code `1` |

The final runner output is sufficient to demonstrate the control flow. Generated reports under `reports/` are useful for local review but are ignored by Git because they contain environment-specific paths and filenames.

## Safety rules

Use only the synthetic state created by this lab. Do not replace it with real cloud inventory, production backups, database exports, credentials, tokens, private keys, personal data, or confidential incident material.

Before publishing a screenshot, hide Windows usernames, absolute paths, machine names, timestamps that reveal sensitive work, and unrelated terminal history. Do not publish backup archives from real systems.

## Evidence interpretation

A successful archive extraction is not enough to demonstrate secure recovery. The evidence should show that the archive was verified before restoration, that the restored state passed security validation, and that a modified archive was rejected by the integrity gate.
