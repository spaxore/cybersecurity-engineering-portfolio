#!/usr/bin/env python3
"""NetMap scope declaration and authorization-boundary validation."""

from __future__ import annotations

import argparse
import ipaddress
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


UTC = timezone.utc
MAX_DEFAULT_ADDRESSES = 256


class ScopeError(Exception):
    """Expected scope-validation error."""


def utc_now() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def load_json(path: Path) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as handle:
            value = json.load(handle)
    except FileNotFoundError as exc:
        raise ScopeError(f"Scope file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ScopeError(f"Invalid JSON in {path}: {exc}") from exc

    if not isinstance(value, dict):
        raise ScopeError("Scope document must be a JSON object")
    return value


def validate_scope(scope: Dict[str, Any], max_addresses: int) -> Dict[str, Any]:
    required = ("owner", "authorization_note", "targets")
    missing = [name for name in required if not scope.get(name)]
    if missing:
        raise ScopeError("Missing required fields: " + ", ".join(missing))

    owner = scope["owner"]
    note = scope["authorization_note"]
    targets = scope["targets"]

    if not isinstance(owner, str) or len(owner.strip()) < 2:
        raise ScopeError("owner must be a meaningful text value")
    if not isinstance(note, str) or len(note.strip()) < 10:
        raise ScopeError("authorization_note must explain the permission")
    if not isinstance(targets, list) or not targets:
        raise ScopeError("targets must be a non-empty JSON list")

    normalized_targets: List[str] = []
    total_addresses = 0
    public_targets: List[str] = []

    for raw_target in targets:
        if not isinstance(raw_target, str):
            raise ScopeError("Every target must be a CIDR string")

        try:
            network = ipaddress.ip_network(raw_target.strip(), strict=False)
        except ValueError as exc:
            raise ScopeError(f"Invalid CIDR target: {raw_target}") from exc

        if network.prefixlen == 0:
            raise ScopeError("Default routes such as 0.0.0.0/0 are not allowed")

        address_count = network.num_addresses
        if address_count > max_addresses:
            raise ScopeError(
                f"Target {network} contains {address_count} addresses; "
                f"the limit is {max_addresses}"
            )

        total_addresses += address_count
        normalized = str(network)
        normalized_targets.append(normalized)

        if not (
            network.is_private
            or network.is_loopback
            or network.is_link_local
            or network.is_reserved
        ):
            public_targets.append(normalized)

    if total_addresses > max_addresses:
        raise ScopeError(
            f"Combined target scope contains {total_addresses} addresses; "
            f"the limit is {max_addresses}"
        )

    if public_targets and scope.get("allow_public_targets") is not True:
        raise ScopeError(
            "Public targets require allow_public_targets=true and explicit authorization"
        )

    expires_utc = scope.get("expires_utc")
    if expires_utc:
        try:
            expires = datetime.fromisoformat(str(expires_utc).replace("Z", "+00:00"))
        except ValueError as exc:
            raise ScopeError("expires_utc must be ISO-8601 or omitted") from exc

        if expires.tzinfo is None:
            raise ScopeError("expires_utc must include a timezone")
        if expires.astimezone(UTC) <= utc_now():
            raise ScopeError("Scope authorization has expired")

    return {
        "owner": owner.strip(),
        "authorization_note": note.strip(),
        "targets": sorted(set(normalized_targets)),
        "target_address_count": total_addresses,
        "public_targets": sorted(set(public_targets)),
        "allow_public_targets": bool(scope.get("allow_public_targets", False)),
        "expires_utc": expires_utc,
        "validated_at_utc": utc_now().isoformat().replace("+00:00", "Z"),
    }


def command_validate(args: argparse.Namespace) -> int:
    scope = load_json(Path(args.scope))
    normalized = validate_scope(scope, args.max_addresses)
    print(json.dumps({"stage": "scope-validation", "status": "pass", **normalized}, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate an authorized CIDR scope")
    validate.add_argument("--scope", required=True)
    validate.add_argument("--max-addresses", type=int, default=MAX_DEFAULT_ADDRESSES)
    validate.set_defaults(function=command_validate)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        return int(args.function(args))
    except ScopeError as exc:
        print(json.dumps({"stage": "scope-validation", "status": "fail", "error": str(exc)}, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
