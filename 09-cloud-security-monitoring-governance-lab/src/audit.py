import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

READ_ONLY_VERBS = {"get", "list", "watch"}


def load_json(path):
    # Accept normal UTF-8 and Windows PowerShell UTF-8 files with a BOM.
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2)
        handle.write("\n")


def write_text(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    # Python 3.9 Path.write_text does not accept newline=.
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(value)


def severity_for(rules, control_id, default):
    for control in rules.get("controls", []):
        if control.get("id") == control_id:
            return control.get("severity", default)
    return default


def compliance_finding(control_id, severity, resource, message):
    return {
        "control_id": control_id,
        "severity": severity,
        "resource": resource,
        "message": message,
    }


def drift_finding(kind, resource, message):
    return {
        "type": kind,
        "resource": resource,
        "message": message,
    }


def namespace_map(state):
    return {
        item.get("name", ""): item
        for item in state.get("namespaces", [])
    }


def workload_map(state):
    return {
        (
            item.get("namespace", ""),
            item.get("kind", ""),
            item.get("name", ""),
        ): item
        for item in state.get("workloads", [])
    }


def rbac_map(state):
    return {
        (
            item.get("namespace", ""),
            item.get("identity", ""),
        ): item
        for item in state.get("rbac", [])
    }


def evaluate_compliance(state, rules):
    findings = []

    def severity(control_id, default):
        return severity_for(rules, control_id, default)

    for namespace in state.get("namespaces", []):
        name = namespace.get("name", "unknown")
        labels = namespace.get("labels", {})
        policies = set(namespace.get("network_policies", []))

        if labels.get("pod-security.kubernetes.io/enforce") != "restricted":
            findings.append(
                compliance_finding(
                    "NS-001",
                    severity("NS-001", "high"),
                    "namespace/" + name,
                    "Namespace does not declare restricted Pod Security enforcement.",
                )
            )

        for label_name in ("security-owner", "environment"):
            if not labels.get(label_name):
                findings.append(
                    compliance_finding(
                        "NS-002",
                        severity("NS-002", "medium"),
                        "namespace/" + name,
                        "Required namespace label is missing: " + label_name + ".",
                    )
                )

        if "default-deny-ingress-egress" not in policies:
            findings.append(
                compliance_finding(
                    "NP-001",
                    severity("NP-001", "high"),
                    "namespace/" + name,
                    "Namespace does not contain default-deny-ingress-egress.",
                )
            )

    for workload in state.get("workloads", []):
        namespace = workload.get("namespace", "unknown")
        kind = workload.get("kind", "resource")
        name = workload.get("name", "unknown")
        resource = "%s/%s/%s" % (kind, namespace, name)
        security = workload.get("security", {})
        resources = workload.get("resources", {})

        if security.get("run_as_non_root") is not True:
            findings.append(
                compliance_finding(
                    "WL-001",
                    severity("WL-001", "high"),
                    resource,
                    "Workload is not configured to run as a non-root user.",
                )
            )

        if security.get("allow_privilege_escalation") is not False:
            findings.append(
                compliance_finding(
                    "WL-002",
                    severity("WL-002", "high"),
                    resource,
                    "Privilege escalation is not explicitly disabled.",
                )
            )

        if security.get("capabilities_drop_all") is not True:
            findings.append(
                compliance_finding(
                    "WL-003",
                    severity("WL-003", "high"),
                    resource,
                    "The workload does not drop all Linux capabilities.",
                )
            )

        if (
            resources.get("requests_defined") is not True
            or resources.get("limits_defined") is not True
        ):
            findings.append(
                compliance_finding(
                    "WL-004",
                    severity("WL-004", "medium"),
                    resource,
                    "CPU and memory requests and limits must be defined.",
                )
            )

    for access in state.get("rbac", []):
        namespace = access.get("namespace", "unknown")
        identity = access.get("identity", "unknown")
        resource = "rbac/%s/%s" % (namespace, identity)
        verbs = set(access.get("verbs", []))

        if access.get("can_read_secrets") is True:
            findings.append(
                compliance_finding(
                    "RB-001",
                    severity("RB-001", "high"),
                    resource,
                    "Read-only identity has secret-read capability.",
                )
            )

        if access.get("can_write_workloads") is True:
            findings.append(
                compliance_finding(
                    "RB-001",
                    severity("RB-001", "high"),
                    resource,
                    "Read-only identity has workload-write capability.",
                )
            )

        unexpected_verbs = sorted(verbs - READ_ONLY_VERBS)
        if unexpected_verbs:
            findings.append(
                compliance_finding(
                    "RB-001",
                    severity("RB-001", "high"),
                    resource,
                    "Read-only identity contains unexpected verbs: "
                    + ", ".join(unexpected_verbs)
                    + ".",
                )
            )

    return findings


def compare_baseline(baseline, current):
    findings = []
    approved_namespaces = namespace_map(baseline)
    observed_namespaces = namespace_map(current)

    for name in sorted(set(approved_namespaces) - set(observed_namespaces)):
        findings.append(
            drift_finding(
                "missing-resource",
                "namespace/" + name,
                "Approved namespace is missing from the current snapshot.",
            )
        )

    for name in sorted(set(observed_namespaces) - set(approved_namespaces)):
        findings.append(
            drift_finding(
                "unexpected-resource",
                "namespace/" + name,
                "Current snapshot contains a namespace not present in the approved baseline.",
            )
        )

    for name in sorted(set(approved_namespaces) & set(observed_namespaces)):
        approved = approved_namespaces[name]
        observed = observed_namespaces[name]

        for label_name, approved_value in approved.get("labels", {}).items():
            observed_value = observed.get("labels", {}).get(label_name)
            if observed_value != approved_value:
                findings.append(
                    drift_finding(
                        "changed-configuration",
                        "namespace/" + name,
                        "Label %s changed from %r to %r."
                        % (label_name, approved_value, observed_value),
                    )
                )

        approved_policies = set(approved.get("network_policies", []))
        observed_policies = set(observed.get("network_policies", []))

        for policy in sorted(approved_policies - observed_policies):
            findings.append(
                drift_finding(
                    "removed-control",
                    "namespace/" + name,
                    "Approved network policy is missing: " + policy + ".",
                )
            )

        for policy in sorted(observed_policies - approved_policies):
            findings.append(
                drift_finding(
                    "unexpected-control",
                    "namespace/" + name,
                    "Unexpected network policy detected: " + policy + ".",
                )
            )

    approved_workloads = workload_map(baseline)
    observed_workloads = workload_map(current)

    for key in sorted(set(approved_workloads) - set(observed_workloads)):
        namespace, kind, name = key
        findings.append(
            drift_finding(
                "missing-resource",
                "%s/%s/%s" % (kind, namespace, name),
                "Approved workload is missing from the current snapshot.",
            )
        )

    for key in sorted(set(observed_workloads) - set(approved_workloads)):
        namespace, kind, name = key
        findings.append(
            drift_finding(
                "unexpected-resource",
                "%s/%s/%s" % (kind, namespace, name),
                "Current snapshot contains a workload not present in the approved baseline.",
            )
        )

    for key in sorted(set(approved_workloads) & set(observed_workloads)):
        approved = approved_workloads[key]
        observed = observed_workloads[key]
        resource = "%s/%s/%s" % (key[1], key[0], key[2])

        for field in ("replicas", "security", "resources"):
            if approved.get(field) != observed.get(field):
                findings.append(
                    drift_finding(
                        "changed-configuration",
                        resource,
                        "Workload field changed: " + field + ".",
                    )
                )

    approved_rbac = rbac_map(baseline)
    observed_rbac = rbac_map(current)

    for key in sorted(set(approved_rbac) - set(observed_rbac)):
        findings.append(
            drift_finding(
                "missing-resource",
                "rbac/%s/%s" % (key[0], key[1]),
                "Approved RBAC identity is missing from the current snapshot.",
            )
        )

    for key in sorted(set(observed_rbac) - set(approved_rbac)):
        findings.append(
            drift_finding(
                "unexpected-resource",
                "rbac/%s/%s" % (key[0], key[1]),
                "Current snapshot contains an RBAC identity not present in the approved baseline.",
            )
        )

    for key in sorted(set(approved_rbac) & set(observed_rbac)):
        if approved_rbac[key] != observed_rbac[key]:
            findings.append(
                drift_finding(
                    "changed-configuration",
                    "rbac/%s/%s" % (key[0], key[1]),
                    "RBAC permissions changed from the approved baseline.",
                )
            )

    return findings


def markdown_report(report):
    lines = [
        "# Cloud Security Governance Audit",
        "",
        "Status: **%s**" % report["status"].upper(),
        "",
        "Platform: `%s`" % report["platform"],
        "Environment: `%s`" % report["environment"],
        "Generated: `%s`" % report["generated_at"],
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "|---|---:|",
        "| Compliance findings | %d |" % len(report["compliance_findings"]),
        "| Drift findings | %d |" % len(report["drift_findings"]),
        "| Total findings | %d |" % report["summary"]["total_findings"],
        "",
        "## Compliance findings",
        "",
    ]

    if report["compliance_findings"]:
        lines.extend([
            "| Control | Severity | Resource | Message |",
            "|---|---|---|---|",
        ])
        for item in report["compliance_findings"]:
            lines.append(
                "| %s | %s | `%s` | %s |"
                % (
                    item["control_id"],
                    item["severity"],
                    item["resource"],
                    item["message"],
                )
            )
    else:
        lines.append("No compliance findings.")

    lines.extend(["", "## Drift findings", ""])

    if report["drift_findings"]:
        lines.extend([
            "| Type | Resource | Message |",
            "|---|---|---|",
        ])
        for item in report["drift_findings"]:
            lines.append(
                "| %s | `%s` | %s |"
                % (item["type"], item["resource"], item["message"])
            )
    else:
        lines.append("No drift findings.")

    lines.extend([
        "",
        "## Interpretation",
        "",
        "This report evaluates configuration assurance and approved-state drift. "
        "It is governance evidence for the local training platform, not a SOC alert stream.",
        "",
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Audit local cloud-security governance state."
    )
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--state", required=True, type=Path)
    parser.add_argument("--rules", required=True, type=Path)
    parser.add_argument("--output-json", required=True, type=Path)
    parser.add_argument("--output-md", required=True, type=Path)
    parser.add_argument("--fail-on-findings", action="store_true")
    args = parser.parse_args()

    baseline = load_json(args.baseline)
    current = load_json(args.state)
    rules = load_json(args.rules)

    compliance_findings = evaluate_compliance(current, rules)
    drift_findings = compare_baseline(baseline, current)
    total_findings = len(compliance_findings) + len(drift_findings)

    report = {
        "report_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "platform": current.get("platform", "unknown"),
        "environment": current.get("environment", "unknown"),
        "status": "pass" if total_findings == 0 else "fail",
        "summary": {
            "compliance_findings": len(compliance_findings),
            "drift_findings": len(drift_findings),
            "total_findings": total_findings,
        },
        "compliance_findings": compliance_findings,
        "drift_findings": drift_findings,
    }

    write_json(args.output_json, report)
    write_text(args.output_md, markdown_report(report))

    print(json.dumps(report["summary"], indent=2))
    print("Status: %s" % report["status"])
    print("JSON report: %s" % args.output_json)
    print("Markdown report: %s" % args.output_md)

    if args.fail_on_findings and total_findings > 0:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
