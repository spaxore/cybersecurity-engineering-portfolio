from __future__ import annotations

import argparse
import datetime as dt
import ipaddress
import json
import sys
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1

ADMIN_PORTS = {22, 135, 139, 445, 3389, 5900, 5985, 5986}
PLAINTEXT_PORTS = {21, 23, 25, 80, 110, 143, 8080, 8000, 8008}
HIGH_RISK_PORTS = {23, 3389, 5900}


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
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_address(address: str) -> str:
    try:
        return str(ipaddress.ip_address(address))
    except ValueError as exc:
        raise ValueError(f"Invalid inventory address: {address}") from exc


def risk_for_port(port: dict[str, Any]) -> tuple[str, str]:
    number = int(port.get("port", 0))
    service = str(port.get("service") or "unknown").lower()
    product = str(port.get("product") or "").strip()

    if number in HIGH_RISK_PORTS:
        return "high", f"High-impact administrative or remote-access port {number} is open"

    if number in ADMIN_PORTS:
        return "medium", f"Administrative or file-sharing port {number} is open"

    if number in PLAINTEXT_PORTS:
        return "medium", f"Common cleartext or web port {number} is open; confirm encrypted access requirements"

    if service in {"telnet", "ftp", "rlogin", "vnc"}:
        return "high", f"Service fingerprint indicates {service}, which requires explicit authorization and hardening review"

    if service in {"http", "https", "ssh", "msrpc", "microsoft-ds"}:
        return "low", f"Recognized service {service} is open; verify it is expected for this host"

    return "low", f"Unclassified open service on port {number}; review ownership and necessity"


def extract_open_ports(inventory: dict[str, Any] ) -> list[dict[str, Any]]:
    services = inventory.get("services")
    if not isinstance(services, list):
        raise ValueError("Service inventory does not contain a valid 'services' list")

    records: list[dict[str, Any]] = []
    for host in services:
        if not isinstance(host, dict):
            continue

        address_value = host.get("address")
        if not isinstance(address_value, str):
            continue
        address = validate_address(address_value)

        ports = host.get("ports")
        if not isinstance(ports, list):
            continue

        for port in ports:
            if not isinstance(port, dict) or port.get("state") != "open":
                continue

            port_number = int(port.get("port", 0))
            if not 1 <= port_number <= 65535:
                raise ValueError(f"Invalid port in inventory for {address}: {port_number}")

            severity, rationale = risk_for_port(port)
            records.append({
                "address": address,
                "protocol": str(port.get("protocol") or "unknown"),
                "port": port_number,
                "service": port.get("service"),
                "product": port.get("product"),
                "version": port.get("version"),
                "extra_info": port.get("extra_info"),
                "risk": severity,
                "risk_rationale": rationale,
            })

    return sorted(records, key=lambda item: (ipaddress.ip_address(item["address"]), item["protocol"], item["port"]))


def service_key(record: dict[str, Any]) -> str:
    return f"{record['address']}|{record['protocol']}|{record['port']}"


def fingerprint(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "service": record.get("service"),
        "product": record.get("product"),
        "version": record.get("version"),
        "extra_info": record.get("extra_info"),
    }


def create_baseline(inventory: dict[str, Any], records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "baseline_type": "approved-service-inventory",
        "created_at_utc": utc_now(),
        "source_inventory": inventory.get("source_discovery"),
        "authorization": inventory.get("scope", {}),
        "services": records,
    }


def compare_with_baseline(baseline: dict[str, Any], current: list[dict[str, Any]]) -> list[dict[str, Any]]:
    baseline_services = baseline.get("services")
    if not isinstance(baseline_services, list):
        raise ValueError("Baseline does not contain a valid 'services' list")

    old = {service_key(item): item for item in baseline_services if isinstance(item, dict)}
    new = {service_key(item): item for item in current}
    findings: list[dict[str, Any]] = []

    for key in sorted(set(new) - set(old)):
        item = new[key]
        findings.append({
            "type": "new-open-service",
            "severity": item["risk"],
            "service_key": key,
            "message": f"Service {item.get('service')} on port {item['port']} was not present in the approved baseline",
            "current": item,
        })

    for key in sorted(set(old) - set(new)):
        item = old[key]
        findings.append({
            "type": "missing-baseline-service",
            "severity": "info",
            "service_key": key,
            "message": f"Baseline service on port {item.get('port')} was not observed in the current inventory",
            "baseline": item,
        })

    for key in sorted(set(old) & set(new)):
        before = fingerprint(old[key])
        after = fingerprint(new[key])
        if before != after:
            findings.append({
                "type": "service-fingerprint-changed",
                "severity": "medium",
                "service_key": key,
                "message": "Service, product, version, or extra information changed from the approved baseline",
                "baseline": old[key],
                "current": new[key],
            })

    return findings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Classify observed services and compare them with an approved NetMap baseline."
    )
    parser.add_argument("mode", choices=("baseline", "compare"))
    parser.add_argument("--inventory", required=True, type=Path, help="Service inventory JSON")
    parser.add_argument("--baseline", required=True, type=Path, help="Approved baseline JSON")
    parser.add_argument("--output", required=True, type=Path, help="Output JSON")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        inventory = load_json(args.inventory)
        current_records = extract_open_ports(inventory)

        if args.mode == "baseline":
            output = create_baseline(inventory, current_records)
            write_json(args.output, output)
            print(json.dumps({
                "stage": "baseline-creation",
                "status": "pass",
                "service_count": len(current_records),
                "output": str(args.output),
            }, indent=2))
            return 0

        baseline = load_json(args.baseline)
        findings = compare_with_baseline(baseline, current_records)
        output = {
            "schema_version": SCHEMA_VERSION,
            "stage": "risk-and-baseline-comparison",
            "status": "pass" if not any(item["severity"] in {"high", "medium"} for item in findings) else "review",
            "generated_at_utc": utc_now(),
            "source_inventory": str(args.inventory),
            "baseline": str(args.baseline),
            "current_services": current_records,
            "finding_count": len(findings),
            "findings": findings,
        }
        write_json(args.output, output)

        severity_counts = {"high": 0, "medium": 0, "low": 0, "info": 0}
        for finding in findings:
            severity = finding.get("severity", "info")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        print(json.dumps({
            "stage": "risk-and-baseline-comparison",
            "status": output["status"],
            "service_count": len(current_records),
            "finding_count": len(findings),
            "severity_counts": severity_counts,
            "output": str(args.output),
        }, indent=2))
        return 0

    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({
            "stage": "risk-and-baseline-comparison",
            "status": "fail",
            "error": str(exc),
        }, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
