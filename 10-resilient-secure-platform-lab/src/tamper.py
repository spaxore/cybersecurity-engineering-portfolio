#!/usr/bin/env python3
"""Project 10: create a deliberately modified backup copy for testing."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict


class TamperError(Exception):
    """Expected tamper-test error."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def create_tampered_copy(source: Path, destination: Path) -> Dict[str, Any]:
    if not source.exists():
        raise TamperError(f"source backup not found: {source}")

    original = bytearray(source.read_bytes())
    if len(original) < 32:
        raise TamperError("backup archive is unexpectedly small")

    modified_offset = len(original) // 2
    original[modified_offset] ^= 0x01

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(bytes(original))

    return {
        "stage": "tamper-create",
        "status": "pass",
        "source": str(source),
        "tampered_copy": str(destination),
        "modified_offset": modified_offset,
        "original_sha256": sha256_file(source),
        "tampered_sha256": sha256_file(destination),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--destination", required=True)
    args = parser.parse_args()

    try:
        result = create_tampered_copy(
            Path(args.source),
            Path(args.destination),
        )
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (TamperError, OSError) as exc:
        print(
            json.dumps(
                {"stage": "tamper-create", "status": "fail", "error": str(exc)},
                indent=2,
            )
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
