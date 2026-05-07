"""CLI subcommand: rename / copy a vault key."""

from __future__ import annotations

import argparse
import sys

from envault.cli import get_password
from envault.rename import RenameError, format_rename_report, rename_key


def cmd_rename(args: argparse.Namespace) -> None:
    password = get_password(confirm=False)
    try:
        result = rename_key(
            args.vault,
            args.old_key,
            args.new_key,
            password,
            overwrite=args.overwrite,
            copy=args.copy,
        )
    except RenameError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(format_rename_report(result))


def add_rename_subcommand(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "rename",
        help="Rename or copy a key inside the vault",
    )
    p.add_argument("old_key", help="Existing key name")
    p.add_argument("new_key", help="Desired new key name")
    p.add_argument(
        "--vault",
        default=".envault",
        help="Path to the vault file (default: .envault)",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite new_key if it already exists",
    )
    p.add_argument(
        "--copy",
        action="store_true",
        help="Keep the original key (copy instead of rename)",
    )
    p.set_defaults(func=cmd_rename)
