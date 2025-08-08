#!/usr/bin/env uv run
"""Simple test runner for Parliament backend tests."""

import subprocess
import sys
from pathlib import Path


def run_tests(*, verbose: bool = True, coverage: bool = False) -> int:
    """Run the test suite."""
    cmd = ["uv", "run", "pytest", "tests/"]

    if verbose:
        cmd.append("-v")

    if coverage:
        cmd.extend(["--cov=.", "--cov-report=html"])

    print(f"Running: {' '.join(cmd)}")  # noqa: T201
    print("-" * 50)  # noqa: T201

    result = subprocess.run(cmd, cwd=Path(__file__).parent, check=False)  # noqa: S603
    return result.returncode


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run Parliament backend tests")
    parser.add_argument("--quiet", "-q", action="store_true", help="Run tests quietly")
    parser.add_argument(
        "--coverage", "-c", action="store_true", help="Run with coverage"
    )

    args = parser.parse_args()

    exit_code = run_tests(verbose=not args.quiet, coverage=args.coverage)
    sys.exit(exit_code)
