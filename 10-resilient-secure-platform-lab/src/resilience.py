#!/usr/bin/env python3
"""Project 10: synthetic platform-state modelling and security validation."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


UTC = timezone.utc


class ResilienceError(Exception):
    """Expected project validation error."""


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(value, indent=2, sort_keys=True) + "\n"
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def load_json(path: Path) -> Any:
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        raise ResilienceError(f"State file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ResilienceError(f"Invalid JSON in {path}: {exc}") from exc


def healthy_platform_state() -> Dict[str, Any]:
    """Return synthetic state containing the controls recovery must preserve."""
    return {
        "schema_version": 1,
        "snapshot_type": "synthetic-platform-state",
        "generated_at_utc": utc_now(),
        "platform": {
            "name": "cloudsec-platform",
            "environment": "local-recovery-lab",
            "classification": "synthetic-internal",
        },
        "services": [
            {
                "name": "identity-control-plane",
                "criticality": "high",
                "backup_required": True,
                "restore_order": 10,
                "security": {
                    "encrypted_at_rest": True,
                    "least_privilege": True,
                },
            },
            {
                "name": "policy-control-plane",
                "criticality": "high",
                "backup_required": True,
                "restore_order": 20,
                "security": {
                    "encrypted_at_rest": True,
                    "least_privilege": True,
                },
            },
            {
                "name": "workload-control-plane",
                "criticality": "medium",
                "backup_required": True,
                "restore_order": 30,
                "security": {
                    "encrypted_at_rest": True,
                    "least_privilege": True,
                },
            },
        ],
        "continuity": {
            "rto_minutes": 30,
            "rpo_minutes": 15,
            "restore_test_required": True,
            "backup_frequency": "on-demand-lab-run",
        },
    }


def validate_platform_state(state: Any) -> List[str]:
    """Return all security and continuity findings in a platform state."""
    findings: List[str] = []

    if not isinstance(state, dict):
        return ["state must be a JSON object"]

    if state.get("schema_version") != 1:
        findings.append("schema_version must equal 1")

    platform = state.get("platform")
    if not isinstance(platform, dict) or not platform.get("name"):
        findings.append("platform.name must be defined")

    services = state.get("services")
    if not isinstance(services, list) or not services:
        findings.append("services must be a non-empty list")
        services = []

    service_names = set()
    for index, service in enumerate(services):
        prefix = f"services[{index}]"

        if not isinstance(service, dict):
            findings.append(f"{prefix} must be an object")
            continue

        name = service.get("name")
        if not name:
            findings.append(f"{prefix}.name must be defined")
        elif name in service_names:
            findings.append(f"duplicate service name: {name}")
        else:
            service_names.add(name)

        if service.get("backup_required") is not True:
            findings.append(f"{prefix}.backup_required must be true")

        if not isinstance(service.get("restore_order"), int):
            findings.append(f"{prefix}.restore_order must be an integer")

        security = service.get("security")
        if not isinstance(security, dict):
            findings.append(f"{prefix}.security must be an object")
            continue

        if security.get("encrypted_at_rest") is not True:
            findings.append(f"{prefix}.security.encrypted_at_rest must be true")

        if security.get("least_privilege") is not True:
            findings.append(f"{prefix}.security.least_privilege must be true")

    continuity = state.get("continuity")
    if not isinstance(continuity, dict):
        findings.append("continuity must be an object")
    else:
        for key in ("rto_minutes", "rpo_minutes"):
            value = continuity.get(key)
            if not isinstance(value, int) or value <= 0:
                findings.append(f"continuity.{key} must be a positive integer")

        if continuity.get("restore_test_required") is not True:
            findings.append("continuity.restore_test_required must be true")

    return findings


def print_result(stage: str, status: str, **details: Any) -> None:
    result = {
        "stage": stage,
        "status": status,
        **details,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


def command_seed(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace)
    state_path = workspace / "active-state.json"
    state = healthy_platform_state()
    findings = validate_platform_state(state)

    if findings:
        print_result(
            "seed",
            "fail",
            state=str(state_path),
            security_findings=findings,
        )
        return 1

    write_json(state_path, state)
    print_result(
        "seed",
        "pass",
        state=str(state_path),
        service_count=len(state["services"]),
        security_findings=[],
    )
    return 0


def command_validate(args: argparse.Namespace) -> int:
    state_path = Path(args.state)
    state = load_json(state_path)
    findings = validate_platform_state(state)

    print_result(
        "validate",
        "pass" if not findings else "fail",
        state=str(state_path),
        finding_count=len(findings),
        security_findings=findings,
    )
    return 0 if not findings else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    seed = subparsers.add_parser(
        "seed",
        help="create a synthetic healthy platform-state snapshot",
    )
    seed.add_argument("--workspace", required=True)
    seed.set_defaults(function=command_seed)

    validate = subparsers.add_parser(
        "validate",
        help="validate platform security and continuity requirements",
    )
    validate.add_argument("--state", required=True)
    validate.set_defaults(function=command_validate)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        return int(args.function(args))
    except ResilienceError as exc:
        print_result("error", "fail", error=str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main())
