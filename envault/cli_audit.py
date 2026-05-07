"""CLI subcommand for viewing the envault audit log."""

from __future__ import annotations

import argparse
import sys

from envault.audit import DEFAULT_AUDIT_FILE, load_audit, format_audit_log


def cmd_audit(args: argparse.Namespace) -> None:
    """Print the audit log to stdout."""
    entries = load_audit(args.audit_file)

    if args.action:
        entries = [e for e in entries if e.get("action") == args.action]

    if args.user:
        entries = [e for e in entries if e.get("user") == args.user]

    if args.last:
        entries = entries[-args.last :]

    if args.json:
        import json
        print(json.dumps(entries, indent=2))
    else:
        print(format_audit_log(entries))

    if not entries:
        sys.exit(0)


def add_audit_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the 'audit' subcommand on an existing subparsers object."""
    p = subparsers.add_parser("audit", help="View the envault audit log")
    p.add_argument(
        "--audit-file",
        default=DEFAULT_AUDIT_FILE,
        help="Path to audit log file (default: %(default)s)",
    )
    p.add_argument("--action", default=None, help="Filter by action name")
    p.add_argument("--user", default=None, help="Filter by username")
    p.add_argument(
        "--last",
        type=int,
        default=None,
        metavar="N",
        help="Show only the last N events",
    )
    p.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output raw JSON instead of formatted text",
    )
    p.set_defaults(func=cmd_audit)
