"""CLI subcommand: copy a key within or across vaults."""

from __future__ import annotations

import argparse
import getpass
import sys

from envault.copy import copy_key, format_copy_report, CopyError


def cmd_copy(args: argparse.Namespace) -> None:
    src_password = getpass.getpass("Source vault password: ")

    dst_password = src_password
    if args.dst_vault and args.dst_vault != args.vault:
        dst_password = getpass.getpass("Destination vault password (leave blank to reuse): ")
        if not dst_password:
            dst_password = src_password

    dst_vault = args.dst_vault if args.dst_vault else args.vault
    dst_key = args.dst_key if args.dst_key else args.src_key

    try:
        report = copy_key(
            src_vault=args.vault,
            src_key=args.src_key,
            dst_vault=dst_vault,
            dst_key=dst_key,
            src_password=src_password,
            dst_password=dst_password,
            overwrite=args.overwrite,
        )
        print(format_copy_report(report))
    except CopyError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def add_copy_subcommand(subparsers) -> None:
    p = subparsers.add_parser("copy", help="Copy a key within or across vaults.")
    p.add_argument("vault", help="Source vault file (.vault.json)")
    p.add_argument("src_key", help="Key to copy")
    p.add_argument(
        "--dst-key",
        dest="dst_key",
        default=None,
        help="Destination key name (default: same as src_key)",
    )
    p.add_argument(
        "--dst-vault",
        dest="dst_vault",
        default=None,
        help="Destination vault file (default: same vault)",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Overwrite destination key if it already exists",
    )
    p.set_defaults(func=cmd_copy)
