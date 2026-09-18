#!/usr/bin/env python3

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "firewall-policy" / "policy-fixture.json"
TEST_PATH = ROOT / "validation" / "test-flows.json"


def load_json(path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def evaluate(policy, flow):
    for rule in policy["rules"]:
        if (
            rule["source_zone"] == flow["source_zone"]
            and rule["destination_zone"] == flow["destination_zone"]
            and rule["protocol"] == flow["protocol"]
            and rule["destination_port"] == flow["destination_port"]
        ):
            return rule["action"], rule["id"]

    return policy["default_action"], "FW-999"


def main():
    policy = load_json(POLICY_PATH)
    test_data = load_json(TEST_PATH)

    failures = []

    if policy.get("default_action") != "deny":
        failures.append("Policy default_action is not deny.")

    for test in test_data["test_cases"]:
        actual_action, actual_rule = evaluate(policy, test)

        action_ok = actual_action == test["expected_action"]
        rule_ok = (
            actual_rule == test["expected_rule"]
            or (
                test["expected_rule"] == "FW-999"
                and actual_action == "deny"
            )
        )

        result = "PASS" if action_ok and rule_ok else "FAIL"

        print(
            f"{result} {test['id']} | "
            f"expected={test['expected_action']}/{test['expected_rule']} | "
            f"actual={actual_action}/{actual_rule}"
        )

        if result == "FAIL":
            failures.append(test["id"])

    print()
    print(f"Total tests: {len(test_data['test_cases'])}")
    print(f"Failures: {len(failures)}")

    if failures:
        print("Failed tests:", ", ".join(failures))
        return 1

    print("Policy validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
