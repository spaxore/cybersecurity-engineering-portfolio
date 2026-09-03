# NetMap — Authorized Network Inventory

Project 11 in the cybersecurity engineering portfolio.

## Objective

NetMap is a local network-inventory tool for networks that the user owns or is explicitly authorized to assess. It validates an assessment scope, discovers reachable hosts, identifies visible services, classifies exposure indicators, creates an approved baseline, and reports changes in later scans.

The tool is designed for Windows PowerShell, Linux, and Kali Linux. It provides inventory and exposure evidence; it does not exploit services, attempt authentication, access device data, or change network configuration.

## Authorized-use boundary

Use NetMap only on networks that you own or have explicit permission to assess. A hotel, university, café, workplace, or public Wi-Fi network is not automatically authorized merely because it is visible or accessible. The scope file must describe the approved CIDR ranges and authorization note before scanning begins.

NetMap does not guess passwords, access camera streams, retrieve personal files, exploit services, bypass isolation, jam signals, or determine the physical location of a device. A camera-like service result is only a network indicator and is not proof that a hidden camera exists. An open port is an observation that requires human review, not proof of a vulnerability.

## Capabilities

| Capability | Implementation | Result |
| --- | --- | --- |
| Scope validation | `src/scope.py` | Rejects malformed or unauthorized target ranges. |
| Host discovery | `src/discovery.py` | Uses Nmap host discovery and stores structured host records. |
| Service inventory | `src/service_scan.py` | Performs controlled version detection on discovered authorized hosts. |
| Risk classification | `src/risk_report.py` | Applies transparent review indicators to observed open services. |
| Baseline comparison | `src/risk_report.py` | Detects new services, missing baseline services, and changed fingerprints. |
| Repeatable execution | `scripts/run-netmap.ps1` | Runs the complete workflow from scope validation through reporting. |
| JSON evidence | `workspace/` | Stores local machine-readable results while remaining ignored by Git. |

## Architecture

```
Authorized scope declaration
            |
            v
Scope validation and target confirmation
            |
            v
Nmap host discovery
            |
            v
Nmap service and version identification
            |
            v
Service risk classification
            |
            v
Approved baseline comparison
            |
            v
Structured JSON inventory and review report
```

Network discovery can identify only what is reachable from the assessment host and visible to the selected scan method. Firewalls, wireless isolation, virtual-network configuration, host-based filtering, cloud-only devices, and service configuration can limit visibility. NetMap therefore reports observed evidence rather than claiming complete knowledge of a network.

## Project structure

```
11-netmap-authorized-inventory/
|-- README.md
|-- .gitignore
|-- architecture/
|-- evidence/
|-- reports/
|-- scripts/
|   `-- run-netmap.ps1
|-- src/
|   |-- discovery.py
|   |-- risk_report.py
|   |-- scope.py
|   `-- service_scan.py
`-- workspace/
```

Generated inventories, baselines, and reports are intentionally ignored by Git because they can contain host-specific network information. Share only sanitized evidence.

## Requirements

NetMap requires Python 3.9 or newer and Nmap. On Windows, the Nmap executable can be installed from the [official Nmap download page](https://nmap.org/download.html). If Nmap is not on the system PATH, pass its absolute path with `--nmap` or set the path when using the PowerShell runner.

The implementation uses Python's standard library and does not require a Python package installation.

## Scope declaration

Create an authorized scope file such as `workspace/scope.json`:

```json
{
  "owner": "local lab owner",
  "authorization_note": "Authorized testing of my local loopback and private lab network.",
  "targets": [
    "127.0.0.1/32",
    "192.168.56.0/29"
  ],
  "allow_public_targets": false
}
```

Replace the example ranges only with networks for which you have explicit authorization. Do not enable public targets unless the authorization is clear, current, and documented.

## Manual workflow

From the project directory, validate the scope first:

```
python ".\\src\\scope.py" validate --scope ".\\workspace\\scope.json"
```

Run host discovery with the local Nmap executable:

```
python ".\\src\\discovery.py" `
    --nmap "C:\\Program Files (x86)\\Nmap\\nmap.exe" `
    --scope ".\\workspace\\scope.json" `
    --output ".\\workspace\\live-inventory.json"
```

Identify services on hosts already returned by discovery:

```
python ".\\src\\service_scan.py" `
    --nmap "C:\\Program Files (x86)\\Nmap\\nmap.exe" `
    --scope ".\\workspace\\scope.json" `
    --discovery ".\\workspace\\live-inventory.json" `
    --output ".\\workspace\\service-inventory.json" `
    --top-ports 100
```

Create an approved baseline only after reviewing the observed services:

```
python ".\\src\\risk_report.py" baseline `
    --inventory ".\\workspace\\service-inventory.json" `
    --baseline ".\\workspace\\approved-services.json" `
    --output ".\\workspace\\approved-services.json"
```

Compare a later inventory with the approved baseline:

```
python ".\\src\\risk_report.py" compare `
    --inventory ".\\workspace\\service-inventory.json" `
    --baseline ".\\workspace\\approved-services.json" `
    --output ".\\workspace\\risk-report.json"
```

## One-command workflow

After the baseline has been reviewed and created, run:

```
powershell -ExecutionPolicy Bypass -File ".\\scripts\\run-netmap.ps1"
```

The runner validates the scope, performs discovery, identifies services on discovered hosts, preserves the existing approved baseline, and writes a current risk report. To intentionally create or refresh the baseline, use the explicit switch below and review the resulting services before treating them as approved:

```
powershell -ExecutionPolicy Bypass -File ".\\scripts\\run-netmap.ps1" -CreateBaseline
```

## Risk interpretation

The risk classifier uses transparent indicators rather than vulnerability claims. Administrative and file-sharing ports receive a review indicator because they may expand the attack surface. Cleartext or remote-access services receive stronger review indicators. Recognized low-risk service fingerprints still require confirmation that the service is expected for the host.

Baseline comparison reports three main conditions: a new open service, a baseline service that is no longer observed, and a changed service fingerprint. A finding is a prompt for an authorized administrator to investigate; it is not an instruction to exploit the service.

## Local validation completed

The project was validated against the authorized local scope containing `127.0.0.1/32` and `192.168.56.0/29`.

| Validation stage | Result |
| --- | --- |
| Scope validation | Passed; 9 authorized IPv4 addresses were accepted. |
| Host discovery | Passed; 9 hosts were reported by Nmap. |
| Service identification | Passed; 3 open TCP services were recorded. |
| Baseline creation | Passed; 3 reviewed service records were stored. |
| Baseline comparison | Passed; 0 findings against the approved baseline. |
| Repeatable PowerShell runner | Passed end to end. |

The observed local services included Microsoft RPC on TCP 135, Microsoft-DS/SMB on TCP 445, and Microsoft HTTPAPI on TCP 5357. These results document the test environment only and must not be generalized to another host or network.

## Evidence and privacy

Do not commit raw host inventories, public IP addresses, MAC addresses, device names, credentials, tokens, private keys, or other sensitive network information. Use the `evidence/` guidance to prepare sanitized screenshots or summaries. Keep generated JSON under `workspace/` for local review unless it has been explicitly sanitized.

## Project status

**Complete.** NetMap now provides authorized scope validation, Nmap host discovery, service identification, transparent risk classification, baseline comparison, and a repeatable PowerShell workflow.

## License and responsible use

This project is intended for defensive administration, authorized inventory, education, and controlled lab testing. The user is responsible for obtaining permission before scanning any network and for complying with applicable laws, policies, and terms of service.