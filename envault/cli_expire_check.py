"""CLI subcommand: envault expire-check — show expired/expiring-soon entries."""

from __future__ import annotations

import argparse
import sys

from envault.env_expire_check import check_expiry


def cmd_expire_check(args: argparse.Namespace) -> None:
    try:
        result = check_expiry(args.vault, warn_days=args.warn_days)
    except FileNotFoundError:
        print(f"error: vault file not found: {args.vault}", file=sys.stderr)
        sys.exit(1)

    if args.expired_only:
        entries = result.expired
    elif args.warn_only:
        entries = result.expiring_soon
    else:
        entries = result.entries

    if not entries:
        print("No issues found.")
        return

    for entry in entries:
        print(entry)

    print(f"\nTotal: {len(result.entries)}  Expired: {len(result.expired)}  Expiring soon: {len(result.expiring_soon)}")

    if result.expired:
        sys.exit(2)


def add_expire_check_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "expire-check",
        help="show entries that are expired or expiring soon",
    )
    p.add_argument("vault", help="path to the vault file")
    p.add_argument(
        "--warn-days",
        type=int,
        default=7,
        metavar="N",
        help="warn if expiry is within N days (default: 7)",
    )
    p.add_argument(
        "--expired-only",
        action="store_true",
        help="only show expired entries",
    )
    p.add_argument(
        "--warn-only",
        action="store_true",
        help="only show entries expiring soon",
    )
    p.set_defaults(func=cmd_expire_check)
