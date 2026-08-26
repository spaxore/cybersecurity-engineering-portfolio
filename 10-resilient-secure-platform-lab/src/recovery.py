#!/usr/bin/env python3
"""Project 10: controlled failure simulation and isolated restoration."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from backup import manifest_path_for, verify_backup
from resilience import load_json, validate_platform_state


UTC = timezone.utc


class RecoveryError(Exception):
    """Expected recovery error."""


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(value, indent=2, sort_keys=True) + "\n"
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def simulate_failure(workspace: Path) -> Dict[str, Any]:
    runtime_state = workspace / "runtime" / "active-state.json"
    if not runtime_state.exists():
        raise RecoveryError(f"runtime state not found: {runtime_state}")

    failure_dir = workspace / "failure"
    failure_dir.mkdir(parents=True, exist_ok=True)
    preserved_state = failure_dir / "active-state.failed.json"
    shutil.move(str(runtime_state), str(preserved_state))

    marker = failure_dir / "failure-marker.json"
    write_json(
        marker,
        {
            "failure_type": "active-state-unavailable",
            "simulated_at_utc": utc_now(),
            "source_runtime_state": str(runtime_state),
        },
    )

    return {
        "stage": "failure-simulation",
        "status": "pass",
        "active_state_available": False,
        "preserved_failed_state": str(preserved_state),
        "failure_marker": str(marker),
    }


def validate_member(name: str) -> None:
    member_path = Path(name)
    if member_path.is_absolute() or ".." in member_path.parts:
        raise RecoveryError(f"unsafe archive member path: {name}")


def extract_safely(archive: Path, destination: Path) -> None:
    with tarfile.open(archive, "r:gz") as handle:
        members = handle.getmembers()
        for member in members:
            validate_member(member.name)
            if member.issym() or member.islnk():
                raise RecoveryError(
                    f"symbolic or hard link is not allowed: {member.name}"
                )
            if not (member.isfile() or member.isdir()):
                raise RecoveryError(
                    f"unsupported archive entry type: {member.name}"
                )
        handle.extractall(destination, members=members)


def restore_backup(
    archive: Path,
    manifest: Path,
    destination: Path,
) -> Dict[str, Any]:
    verification = verify_backup(archive, manifest)

    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)
    extract_safely(archive, destination)

    restored_state = destination / "state.json"
    if not restored_state.exists():
        raise RecoveryError("restored archive does not contain state.json")

    state = load_json(restored_state)
    findings = validate_platform_state(state)
    if findings:
        raise RecoveryError(
            "restored state failed security validation: "
            + "; ".join(findings)
        )

    restore_record = destination / "restore-record.json"
    write_json(
        restore_record,
        {
            "restored_at_utc": utc_now(),
            "source_archive": str(archive),
            "source_manifest": str(manifest),
            "security_findings": [],
            "verification": verification,
        },
    )

    return {
        "stage": "restore",
        "status": "pass",
        "destination": str(destination),
        "restored_state": str(restored_state),
        "restore_record": str(restore_record),
        "security_findings": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    failure = subparsers.add_parser("simulate-failure")
    failure.add_argument("--workspace", required=True)

    restore = subparsers.add_parser("restore")
    restore.add_argument("--backup", required=True)
    restore.add_argument("--manifest")
    restore.add_argument("--destination", required=True)

    args = parser.parse_args()

    try:
        if args.command == "simulate-failure":
            result = simulate_failure(Path(args.workspace))
        else:
            archive = Path(args.backup)
            manifest = (
                Path(args.manifest)
                if args.manifest
                else manifest_path_for(archive)
            )
            result = restore_backup(
                archive,
                manifest,
                Path(args.destination),
            )
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (RecoveryError, OSError, tarfile.TarError, json.JSONDecodeError) as exc:
        print(
            json.dumps(
                {
                    "stage": args.command,
                    "status": "fail",
                    "error": str(exc),
                },
                indent=2,
            )
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
