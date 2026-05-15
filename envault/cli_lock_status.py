"""CLI subcommand: envault status — show lock/encryption status of vault."""

from __future__ import annotations

import argparse
import sys

from envault.env_lock_status import check_lock_status, format_status_report


def cmd_lock_status(args: argparse.Namespace) -> None:
    """Handle the 'status' subcommand."""
    try:
        result = check_lock_status(args.vault)
    except FileNotFoundError:
        print(f"Error: vault file not found: {args.vault}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:  # pragma: no cover
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    report = format_status_report(result)
    print(report)

    if args.fail_unencrypted and result.encrypted_count < result.total:
        unenc = result.total - result.encrypted_count
        print(
            f"\n{unenc} unencrypted entry/entries found.",
            file=sys.stderr,
        )
        sys.exit(2)


def add_lock_status_subcommand(subparsers: argparse._SubParsersAction) -> None:
    """Register 'status' subcommand on the given subparsers object."""
    p = subparsers.add_parser(
        "status",
        help="Show encryption/lock status of all vault entries.",
    )
    p.add_argument(
        "--vault",
        default=".envault",
        help="Path to vault file (default: .envault)",
    )
    p.add_argument(
        "--fail-unencrypted",
        action="store_true",
        default=False,
        help="Exit with code 2 if any entry is not encrypted.",
    )
    p.set_defaults(func=cmd_lock_status)
