#!/usr/bin/env python
"""
Single Command Test Runner for EHR-NLP ML System

Run all tests with: python run_tests.py
Run with coverage: python run_tests.py --coverage
Run specific markers: python run_tests.py --marker version_b
Run fast tests only: python run_tests.py --fast

This script provides a convenient way to run the full test suite
with various options for filtering and reporting.
"""

import subprocess
import sys
import argparse
from pathlib import Path


def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(
        description='EHR-NLP ML System Test Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all tests
  python run_tests.py --coverage         # Run with coverage report
  python run_tests.py --fast             # Skip slow ML model tests
  python run_tests.py --marker version_b # Run only Version B tests
  python run_tests.py --verbose          # Extra verbose output
  python run_tests.py --failed           # Re-run failed tests only
        """
    )

    parser.add_argument(
        '--coverage', '-c',
        action='store_true',
        help='Generate coverage report (HTML in htmlcov/)'
    )

    parser.add_argument(
        '--fast', '-f',
        action='store_true',
        help='Skip slow tests (ML model loading)'
    )

    parser.add_argument(
        '--marker', '-m',
        type=str,
        default=None,
        help='Run tests with specific marker (e.g., version_a, version_b, api)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Extra verbose output'
    )

    parser.add_argument(
        '--failed', '-lf',
        action='store_true',
        help='Re-run only failed tests from last run'
    )

    parser.add_argument(
        '--unit',
        action='store_true',
        help='Run only unit tests (fast, no external deps)'
    )

    parser.add_argument(
        '--integration',
        action='store_true',
        help='Run only integration tests'
    )

    parser.add_argument(
        '--version',
        type=str,
        choices=['a', 'b', 'c', 'd', 'A', 'B', 'C', 'D'],
        help='Run tests for specific version (a, b, c, or d)'
    )

    parser.add_argument(
        '--parallel', '-n',
        type=int,
        default=None,
        help='Run tests in parallel with N workers (requires pytest-xdist)'
    )

    parser.add_argument(
        '--html',
        action='store_true',
        help='Generate HTML test report'
    )

    args = parser.parse_args()

    # Build pytest command
    cmd = ['python', '-m', 'pytest', 'tests/']

    # Always add verbose flag
    cmd.append('-v')

    # Extra verbose
    if args.verbose:
        cmd.append('-vv')

    # Coverage
    if args.coverage:
        cmd.extend([
            '--cov=backend',
            '--cov-report=html',
            '--cov-report=term-missing'
        ])

    # Skip slow tests
    if args.fast:
        cmd.extend(['-m', 'not slow'])

    # Specific marker
    if args.marker:
        cmd.extend(['-m', args.marker])

    # Unit tests only
    if args.unit:
        cmd.extend(['-m', 'unit'])

    # Integration tests only
    if args.integration:
        cmd.extend(['-m', 'integration'])

    # Version-specific tests
    if args.version:
        version = args.version.lower()
        cmd.extend(['-m', f'version_{version}'])

    # Re-run failed tests
    if args.failed:
        cmd.append('--lf')

    # Parallel execution
    if args.parallel:
        cmd.extend(['-n', str(args.parallel)])

    # HTML report
    if args.html:
        cmd.extend(['--html=tests/report.html', '--self-contained-html'])

    # Print command being run
    print("=" * 60)
    print("EHR-NLP ML System Test Runner")
    print("=" * 60)
    print(f"\nRunning: {' '.join(cmd)}\n")
    print("=" * 60)

    # Run pytest
    result = subprocess.run(cmd, cwd=Path(__file__).parent)

    # Print summary
    print("\n" + "=" * 60)
    if result.returncode == 0:
        print("ALL TESTS PASSED!")
    else:
        print(f"TESTS FAILED (exit code: {result.returncode})")

    if args.coverage:
        print("\nCoverage report generated in: htmlcov/index.html")

    if args.html:
        print("\nHTML report generated in: tests/report.html")

    print("=" * 60)

    return result.returncode


if __name__ == '__main__':
    sys.exit(main())
