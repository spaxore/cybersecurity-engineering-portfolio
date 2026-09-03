#!/usr/bin/env python3
"""NetMap authorized host discovery using Nmap XML output."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from xml.etree import ElementTree

from scope import load_json, validate_scope


UTC = timezone.utc


class DiscoveryError(Exception):
    """Expected discovery error."""


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_nmap(nmap_path: str, target: str, timeout: int) -> str:
    executable = shutil.which(nmap_path) or nmap_path
    command = [
        executable,
        "-sn",
        "-n",
        "-T3",
        "--host-timeout",
        f"{timeout}s",
        "-oX",
        "-",
        target,
    ]

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout + 30,
            check=False,
        )
    except FileNotFoundError as exc:
        raise DiscoveryError(
            "Nmap was not found. Install Nmap or pass its executable path with --nmap."
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise DiscoveryError(f"Nmap timed out while scanning {target}") from exc

    if completed.returncode != 0:
        error = completed.stderr.strip() or "no error text returned"
        raise DiscoveryError(f"Nmap failed for {target}: {error}")

    return completed.stdout


def parse_nmap_xml(xml_text: str, target: str) -> List[Dict[str, Any]]:
    try:
        root = ElementTree.fromstring(xml_text)
    except ElementTree.ParseError as exc:
        raise DiscoveryError(f"Nmap returned invalid XML for {target}: {exc}") from exc

    hosts: List[Dict[str, Any]] = []
    for host in root.findall("host"):
        status = host.find("status")
        if status is None or status.get("state") != "up":
            continue

        addresses: List[Dict[str, str]] = []
        mac_address: Optional[str] = None
        mac_vendor: Optional[str] = None

        for address in host.findall("address"):
            address_type = address.get("addrtype", "unknown")
            address_value = address.get("addr", "")
            if not address_value:
                continue

            if address_type == "mac":
                mac_address = address_value
                mac_vendor = address.get("vendor")
            else:
                addresses.append(
                    {"type": address_type, "address": address_value}
                )

        hostnames = sorted(
            {
                hostname.get("name")
                for hostname in host.findall("hostnames/hostname")
                if hostname.get("name")
            }
        )

        primary_address = next(
            (item["address"] for item in addresses if item["type"] == "ipv4"),
            addresses[0]["address"] if addresses else None,
        )

        hosts.append(
            {
                "primary_address": primary_address,
                "addresses": addresses,
                "hostnames": hostnames,
                "mac_address": mac_address,
                "mac_vendor": mac_vendor,
                "discovery_method": "nmap-host-discovery",
                "source_target": target,
            }
        )

    return hosts


def discover(scope: Dict[str, Any], nmap_path: str, timeout: int, dry_run: bool) -> Dict[str, Any]:
    targets = scope["targets"]
    all_hosts: List[Dict[str, Any]] = []
    commands: List[List[str]] = []
    started_at = utc_now()

    for target in targets:
        executable = shutil.which(nmap_path) or nmap_path
        command = [
            executable,
            "-sn",
            "-n",
            "-T3",
            "--host-timeout",
            f"{timeout}s",
            "-oX",
            "-",
            target,
        ]
        commands.append(command)

        if dry_run:
            continue

        xml_text = run_nmap(nmap_path, target, timeout)
        all_hosts.extend(parse_nmap_xml(xml_text, target))

    return {
        "schema_version": 1,
        "stage": "host-discovery",
        "status": "dry-run" if dry_run else "pass",
        "started_at_utc": started_at,
        "completed_at_utc": utc_now(),
        "scope": scope,
        "nmap_path": nmap_path,
        "dry_run": dry_run,
        "commands": commands,
        "host_count": len(all_hosts),
        "hosts": sorted(
            all_hosts,
            key=lambda item: item.get("primary_address") or "",
        ),
    }


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(value, indent=2, sort_keys=True) + "\n"
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", required=True, help="validated scope JSON file")
    parser.add_argument("--output", required=True, help="JSON inventory output path")
    parser.add_argument("--nmap", default="nmap", help="Nmap executable or full path")
    parser.add_argument("--timeout", type=int, default=90)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        scope = validate_scope(load_json(Path(args.scope)), 256)
        result = discover(scope, args.nmap, args.timeout, args.dry_run)
        write_json(Path(args.output), result)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (DiscoveryError, OSError, ValueError) as exc:
        print(
            json.dumps(
                {"stage": "host-discovery", "status": "fail", "error": str(exc)},
                indent=2,
            )
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
