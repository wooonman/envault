"""CLI subcommand: envault access-log"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.env_access_log import format_access_log, get_access_log, record_access


def cmd_access_log(args: argparse.Namespace) -> None:
    vault_path = Path(args.vault)

    if not vault_path.exists():
        print(f"error: vault not found: {vault_path}", file=sys.stderr)
        sys.exit(1)

    if args.subaction == "list":
        entries = get_access_log(
            vault_path,
            key=getattr(args, "key", None),
            action=getattr(args, "filter_action", None),
        )
        print(format_access_log(entries))

    elif args.subaction == "record":
        try:
            entry = record_access(vault_path, args.key, args.action)
            print(f"Recorded: {entry}")
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        print("error: unknown subaction", file=sys.stderr)
        sys.exit(1)


def add_access_log_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "access-log", help="View or record per-key access events"
    )
    p.add_argument("vault", help="Path to vault file")
    sub = p.add_subparsers(dest="subaction", required=True)

    lst = sub.add_parser("list", help="List access log entries")
    lst.add_argument("--key", default=None, help="Filter by key name")
    lst.add_argument(
        "--action", dest="filter_action", default=None,
        choices=["read", "write", "delete"],
        help="Filter by action type",
    )

    rec = sub.add_parser("record", help="Manually record an access event")
    rec.add_argument("key", help="Key name")
    rec.add_argument(
        "action", choices=["read", "write", "delete"], help="Action type"
    )

    p.set_defaults(func=cmd_access_log)
