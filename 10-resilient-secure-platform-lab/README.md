# Resilient and Secure Platform Lab

Project 10 in the cybersecurity engineering portfolio.

## Objective

This project demonstrates a local, reproducible resilience workflow for a small cloud-security platform. It will create a sanitized platform-state snapshot, package it into a checksum-verified backup, simulate loss of the active state, restore the backup into an isolated recovery workspace, validate security requirements, and reject a deliberately tampered backup.

The lab is intentionally free, local, and open-source. It will not require a cloud account, paid service, external monitoring platform, or real infrastructure data. Its purpose is to prove that a secure platform is not only protected during normal operation but also recoverable after controlled failure.

## Architecture boundaries

```
Synthetic platform state
          |
          v
Snapshot and security validation
          |
          v
Backup archive + SHA-256 manifest
          |
          v
Controlled active-state failure
          |
          v
Isolated recovery workspace
          |
          v
Post-restore validation
          |
          +---- pass: recovery accepted
          +---- fail: recovery blocked

Tampered archive ----> digest mismatch ----> rejected
```

The source state, backup artifact, recovery workspace, and generated evidence are separate boundaries. Recovery testing must not overwrite the known-good source state.

## Planned controls

| Control | Planned implementation | Why it matters |
| --- | --- | --- |
| State snapshot | Synthetic JSON platform state | Creates a repeatable recovery input without exposing real data. |
| Security validation | Required encryption, least privilege, backup, and restore-test fields | Prevents an insecure state from being treated as recoverable. |
| Backup integrity | SHA-256 digest for the archive and state content | Detects modified or incomplete backup artifacts. |
| Recovery isolation | Separate recovery directory | Reduces accidental source overwrite risk. |
| Failure simulation | Controlled removal of active state | Proves the recovery path starts from an unavailable state. |
| Restore validation | Re-check controls after extraction | Prevents successful file extraction from being mistaken for secure recovery. |
| Tamper rejection | Deliberately modified backup copy | Demonstrates that integrity failure blocks recovery. |
| Sanitized evidence | JSON and Markdown summaries | Makes the result reviewable without publishing sensitive data. |

## Planned project structure

```
10-resilient-secure-platform-lab/
|-- architecture/
|-- artifacts/
|   `-- backups/
|-- evidence/
|-- reports/
|-- scripts/
|-- src/
|-- workspace/
|-- .gitignore
`-- README.md
```

Generated workspaces, backup archives, tampered copies, reports, Python cache, and secrets must remain ignored by Git.

## Acceptance criteria

The project will be considered complete only when all four conditions pass:

| Acceptance criterion | Required result |
| --- | --- |
| Healthy state validation | Zero security findings. |
| Original backup verification | Archive and state digests match the manifest. |
| Recovery validation | Restored state passes all security requirements. |
| Tamper test | Modified backup is rejected with a non-zero result. |

## Safety boundary

The implementation will operate only inside this Project 10 directory and will use synthetic state. It will not connect to cloud accounts, delete live services, alter the Kubernetes cluster used by Project 09, access personal files, or process real backups.

## Learning sequence

1. Define and validate the synthetic platform state.

1. Create a backup archive and integrity manifest.

1. Verify the original backup.

1. Simulate active-state loss in the lab workspace.

1. Restore into a separate recovery workspace.

1. Validate the restored state.

1. Modify a copied archive and confirm that verification rejects it.

1. Add evidence guidance, cleanup, and final documentation.

## Limitations

This is a compact local architecture demonstration. It does not provide production key management, immutable storage, cross-region replication, database-native consistency, workload orchestration, or a real disaster-recovery site. Those capabilities would require a system-specific design after defining data stores, recovery objectives, trust boundaries, and regulatory requirements.