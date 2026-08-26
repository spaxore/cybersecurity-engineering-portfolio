#!/usr/bin/env python3
"""Project 10: create and verify an integrity-protected state backup."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from resilience import load_json, validate_platform_state


UTC = timezone.utc


class BackupError(Exception):
    """Expected backup-integrity error."""


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(value, indent=2, sort_keys=True) + "\n"
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def manifest_path_for(archive: Path) -> Path:
    return archive.parent / (archive.name + ".manifest.json")


def create_backup(state_path: Path, backup_dir: Path) -> Dict[str, Any]:
    state = load_json(state_path)
    findings = validate_platform_state(state)
    if findings:
        raise BackupError(
            "refusing to back up a state with security findings: "
            + "; ".join(findings)
        )

    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    archive = backup_dir / f"platform-state-{timestamp}.tar.gz"

    with tempfile.TemporaryDirectory(prefix="project10-backup-") as temporary:
        staging = Path(temporary)
        staged_state = staging / "state.json"
        state_bytes = (json.dumps(state, indent=2, sort_keys=True) + "\n").encode(
            "utf-8"
        )
        staged_state.write_bytes(state_bytes)
        state_hash = sha256_bytes(state_bytes)

        internal_manifest = {
            "manifest_version": 1,
            "artifact_type": "synthetic-platform-state-backup",
            "state_file": "state.json",
            "state_sha256": state_hash,
            "created_at_utc": utc_now(),
        }
        write_json(staging / "backup-manifest.json", internal_manifest)

        with tarfile.open(archive, "w:gz") as handle:
            handle.add(staged_state, arcname="state.json")
            handle.add(
                staging / "backup-manifest.json",
                arcname="backup-manifest.json",
            )

    external_manifest = {
        "manifest_version": 1,
        "archive": archive.name,
        "archive_sha256": sha256_file(archive),
        "state_sha256": state_hash,
        "created_at_utc": utc_now(),
        "integrity_algorithm": "SHA-256",
    }
    manifest_path = manifest_path_for(archive)
    write_json(manifest_path, external_manifest)

    return {
        "stage": "backup",
        "status": "pass",
        "archive": str(archive),
        "manifest": str(manifest_path),
        "archive_sha256": external_manifest["archive_sha256"],
        "state_sha256": state_hash,
    }


def validate_archive_member(name: str) -> None:
    member_path = Path(name)
    if member_path.is_absolute() or ".." in member_path.parts:
        raise BackupError(f"unsafe archive member path: {name}")


def verify_backup(archive: Path, manifest_path: Path) -> Dict[str, Any]:
    if not archive.exists():
        raise BackupError(f"backup archive not found: {archive}")
    if not manifest_path.exists():
        raise BackupError(f"backup manifest not found: {manifest_path}")

    manifest = load_json(manifest_path)
    expected_archive_hash = manifest.get("archive_sha256")
    expected_state_hash = manifest.get("state_sha256")
    actual_archive_hash = sha256_file(archive)

    if actual_archive_hash != expected_archive_hash:
        raise BackupError(
            "archive SHA-256 mismatch: "
            f"expected {expected_archive_hash}, got {actual_archive_hash}"
        )

    with tempfile.TemporaryDirectory(prefix="project10-verify-") as temporary:
        extraction = Path(temporary)
        with tarfile.open(archive, "r:gz") as handle:
            members = handle.getmembers()
            for member in members:
                validate_archive_member(member.name)
                if member.issym() or member.islnk():
                    raise BackupError(
                        f"symbolic or hard link is not allowed: {member.name}"
                    )
                if not (member.isfile() or member.isdir()):
                    raise BackupError(
                        f"unsupported archive entry type: {member.name}"
                    )
            handle.extractall(extraction, members=members)

        state_path = extraction / "state.json"
        internal_manifest_path = extraction / "backup-manifest.json"
        if not state_path.exists():
            raise BackupError("archive does not contain state.json")
        if not internal_manifest_path.exists():
            raise BackupError("archive does not contain backup-manifest.json")

        actual_state_hash = sha256_file(state_path)
        if actual_state_hash != expected_state_hash:
            raise BackupError(
                "state SHA-256 mismatch: "
                f"expected {expected_state_hash}, got {actual_state_hash}"
            )

        state = load_json(state_path)
        findings = validate_platform_state(state)
        if findings:
            raise BackupError(
                "backup state failed validation: " + "; ".join(findings)
            )

        internal_manifest = load_json(internal_manifest_path)
        if internal_manifest.get("state_sha256") != expected_state_hash:
            raise BackupError("internal and external manifests disagree")

    return {
        "stage": "verify-backup",
        "status": "pass",
        "archive": str(archive),
        "manifest": str(manifest_path),
        "archive_sha256": actual_archive_hash,
        "state_sha256": expected_state_hash,
        "state_validation_findings": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create")
    create.add_argument("--state", required=True)
    create.add_argument("--backup-dir", required=True)

    verify = subparsers.add_parser("verify")
    verify.add_argument("--backup", required=True)
    verify.add_argument("--manifest")

    args = parser.parse_args()

    try:
        if args.command == "create":
            result = create_backup(Path(args.state), Path(args.backup_dir))
        else:
            archive = Path(args.backup)
            manifest = Path(args.manifest) if args.manifest else manifest_path_for(archive)
            result = verify_backup(archive, manifest)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (BackupError, OSError, tarfile.TarError, json.JSONDecodeError) as exc:
        print(json.dumps({"stage": args.command, "status": "fail", "error": str(exc)}, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
