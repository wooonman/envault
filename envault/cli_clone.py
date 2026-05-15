"""CLI subcommand: envault clone"""

from __future__ import annotations

import argparse
import sys

from envault.env_clone import clone_key, CloneError, format_clone_report
from envault.cli import get_password


def cmd_clone(args: argparse.Namespace) -> None:
    password = get_password("Vault password: ")

    dest_password = password
    if args.dest_vault and args.dest_vault != args.vault:
        dest_password = get_password("Destination vault password: ")

    dest_vault = args.dest_vault or args.vault
    dest_key = args.dest_key or args.src_key

    try:
        result = clone_key(
            src_vault_path=args.vault,
            src_key=args.src_key,
            dest_vault_path=dest_vault,
            dest_key=dest_key,
            password=password,
            dest_password=dest_password,
            overwrite=args.overwrite,
        )
    except CloneError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(format_clone_report(result))


def add_clone_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "clone",
        help="Clone a key to a new name or vault",
    )
    p.add_argument("vault", help="Source vault file")
    p.add_argument("src_key", help="Key to clone")
    p.add_argument(
        "--dest-key",
        default=None,
        help="Name for the cloned key (default: same as src_key)",
    )
    p.add_argument(
        "--dest-vault",
        default=None,
        help="Destination vault file (default: same vault)",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite destination key if it already exists",
    )
    p.set_defaults(func=cmd_clone)
