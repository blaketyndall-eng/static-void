"""Local CI-equivalent checks for Sprint 6 rollout."""

from __future__ import annotations

import subprocess
import sys


COMMANDS = [
    ["python", "-m", "compileall", "decision-intelligence-farm/src"],
    [
        "python",
        "-m",
        "unittest",
        "discover",
        "-s",
        "decision-intelligence-farm/src",
        "-p",
        "test_*.py",
    ],
    [
        "python",
        "decision-intelligence-farm/src/automation_intelligence_audit_cli.py",
        "--repo-root",
        ".",
        "--as-json",
    ],
]


def main() -> int:
    for command in COMMANDS:
        print("$", " ".join(command))
        result = subprocess.run(command)
        if result.returncode != 0:
            return result.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
