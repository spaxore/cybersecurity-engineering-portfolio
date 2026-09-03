from __future__ import annotations

import argparse
import datetime as dt
import ipaddress
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            value = json.load(handle)
    except FileNotFoundError as exc:
        raise ValueError(f"File not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc

    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(value, indent=2, sort_keys=True) + "\n"
    path.write_text(content, encoding="utf-8")


def load_authorized_networks(scope_path: Path) -> tuple[dict[str, Any], list[ipaddress._BaseNetwork]]:
    scope = load_json(scope_path)
    targets = scope.get("targets")

    if not isinstance(targets, list) or not targets:
        raise ValueError("The authorized scope must contain a non-empty 'targets' list")

    networks: list[ipaddress._BaseNetwork] = []
    for target in targets:
        try:
            network = ipaddress.ip_network(str(target), strict=False)
        except ValueError as exc:
            raise ValueError(f"Invalid authorized network: {target}") from exc

        if network.version != 4:
            raise ValueError(f"Only IPv4 targets are supported by this stage: {target}")

        if not scope.get("allow_public_targets", False) and not network.is_private and not network.is_loopback:
            raise ValueError(f"Public target rejected by scope policy: {target}")

        networks.append(network)

    return scope, networks


def authorized_ip(address: str, networks: list[ipaddress._BaseNetwork]) -> bool:
    try:
        parsed = ipaddress.ip_address(address)
    except ValueError:
        return False
    return any(parsed in network for network in networks)


def get_discovered_hosts(discovery: dict[str, Any], networks: list[ipaddress._BaseNetwork]) -> list[str]:
    hosts = discovery.get("hosts")
    if not isinstance(hosts, list):
        raise ValueError("Discovery inventory does not contain a valid 'hosts' list")

    addresses: set[str] = set()
    for host in hosts:
        if not isinstance(host, dict):
            continue
        address = host.get("primary_address")
        if isinstance(address, str) and authorized_ip(address, networks):
            addresses.add(address)

    result = sorted(addresses, key=lambda item: ipaddress.ip_address(item))
    if not result:
        raise ValueError("No authorized hosts were found in the discovery inventory")
    return result


def parse_ports(xml_text: str, target: str) -> dict[str, Any]:
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        raise ValueError(f"Nmap returned invalid XML for {target}: {exc}") from exc

    host_node = root.find(".//host")
    if host_node is None:
        return {
            "address": target,
            "status": "not-reported",
            "ports": [],
            "hostnames": [],
        }

    status_node = host_node.find("status")
    status = status_node.get("state", "unknown") if status_node is not None else "unknown"

    hostnames: list[str] = []
    for hostname in host_node.findall("./hostnames/hostname"):
        name = hostname.get("name")
        if name:
            hostnames.append(name)

    ports: list[dict[str, Any]] = []
    for port in host_node.findall("./ports/port"):
        state_node = port.find("state")
        service_node = port.find("service")

        port_record: dict[str, Any] = {
            "protocol": port.get("protocol"),
            "port": int(port.get("portid", "0")),
            "state": state_node.get("state") if state_node is not None else "unknown",
            "reason": state_node.get("reason") if state_node is not None else None,
            "service": service_node.get("name") if service_node is not None else None,
            "product": service_node.get("product") if service_node is not None else None,
            "version": service_node.get("version") if service_node is not None else None,
            "extra_info": service_node.get("extrainfo") if service_node is not None else None,
            "cpe": [node.text for node in service_node.findall("cpe") if node.text] if service_node is not None else [],
        }
        ports.append(port_record)

    return {
        "address": target,
        "status": status,
        "ports": ports,
        "hostnames": sorted(set(hostnames)),
    }


def run_scan(nmap_path: str, target: str, top_ports: int) -> tuple[list[str], dict[str, Any]]:
    command = [
        nmap_path,
        "-sV",
        "--version-light",
        "--top-ports",
        str(top_ports),
        "-T3",
        "--host-timeout",
        "90s",
        "-n",
        "-oX",
        "-",
        target,
    ]

    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
        check=False,
    )

    if completed.returncode not in (0, 1):
        detail = completed.stderr.strip() or completed.stdout.strip() or "unknown Nmap error"
        raise RuntimeError(f"Nmap failed for {target} with exit code {completed.returncode}: {detail}")

    return command, parse_ports(completed.stdout, target)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Identify services on hosts already discovered inside an authorized scope."
    )
    parser.add_argument("--nmap", default="nmap", help="Path to nmap.exe")
    parser.add_argument("--scope", required=True, type=Path, help="Authorized scope JSON")
    parser.add_argument("--discovery", required=True, type=Path, help="Live discovery inventory JSON")
    parser.add_argument("--output", required=True, type=Path, help="Service inventory output JSON")
    parser.add_argument(
        "--top-ports",
        type=int,
        default=100,
        help="Number of common TCP ports to test per host; default: 100",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    started = utc_now()

    try:
        if args.top_ports < 1 or args.top_ports > 1000:
            raise ValueError("--top-ports must be between 1 and 1000")

        scope, networks = load_authorized_networks(args.scope)
        discovery = load_json(args.discovery)
        targets = get_discovered_hosts(discovery, networks)

        commands: list[list[str]] = []
        services: list[dict[str, Any]] = []
        for target in targets:
            command, record = run_scan(args.nmap, target, args.top_ports)
            commands.append(command)
            services.append(record)

        output = {
            "schema_version": SCHEMA_VERSION,
            "stage": "service-identification",
            "status": "pass",
            "started_at_utc": started,
            "completed_at_utc": utc_now(),
            "nmap_path": args.nmap,
            "top_ports": args.top_ports,
            "source_discovery": str(args.discovery),
            "commands": commands,
            "scope": scope,
            "target_count": len(targets),
            "targets": targets,
            "services": services,
        }
        write_json(args.output, output)

        open_port_count = sum(
            1
            for host in services
            for port in host.get("ports", [])
            if port.get("state") == "open"
        )
        print(json.dumps({
            "stage": "service-identification",
            "status": "pass",
            "target_count": len(targets),
            "open_port_count": open_port_count,
            "output": str(args.output),
        }, indent=2))
        return 0

    except (OSError, subprocess.TimeoutExpired, ValueError, RuntimeError) as exc:
        error = {
            "stage": "service-identification",
            "status": "fail",
            "error": str(exc),
            "started_at_utc": started,
            "completed_at_utc": utc_now(),
        }
        print(json.dumps(error, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
