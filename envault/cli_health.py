"""CLI subcommand: envault health — run a health check on a vault."""

from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace

from envault.cli import get_password
from envault.env_health import run_health_check


def cmd_health(args: Namespace) -> None:
    password = get_password(confirm=False)
    report = run_health_check(args.vault, password)

    print(str(report))

    if args.fail_on_warning:
        if report.issues:
            sys.exit(1)
    else:
        if not report.ok:
            sys.exit(1)


def add_health_subcommand(subparsers) -> None:
    p: ArgumentParser = subparsers.add_parser(
        "health",
        help="Run a health check on the vault and report issues",
    )
    p.add_argument(
        "--vault",
        default=".env.vault",
        help="Path to the vault file (default: .env.vault)",
    )
    p.add_argument(
        "--fail-on-warning",
        action="store_true",
        default=False,
        help="Exit with code 1 if there are any warnings (not just errors)",
    )
    p.set_defaults(func=cmd_health)
