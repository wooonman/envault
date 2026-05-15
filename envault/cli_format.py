"""CLI subcommand: envault format-keys"""

from __future__ import annotations

import argparse
import sys

from envault.env_format import format_keys, FormatError
from envault.cli import get_password


def cmd_format(args: argparse.Namespace) -> None:
    password = get_password(confirm=False)
    try:
        result = format_keys(
            vault_path=args.vault,
            password=password,
            style=args.style,
            dry_run=args.dry_run,
        )
    except FormatError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: vault file not found: {args.vault}", file=sys.stderr)
        sys.exit(1)

    if args.dry_run and result.renamed:
        print("[dry-run] The following keys would be reformatted:")
        for old, new in result.renamed:
            print(f"  {old!r} -> {new!r}")
        if result.skipped:
            print(f"  (skipped: {', '.join(result.skipped)})")
    else:
        print(result)


def add_format_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "format-keys",
        help="Normalize key names in the vault (upper, lower, snake)",
    )
    p.add_argument(
        "vault",
        help="Path to the .vault.json file",
    )
    p.add_argument(
        "--style",
        choices=["upper", "lower", "snake"],
        default="upper",
        help="Key naming style to enforce (default: upper)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing to disk",
    )
    p.set_defaults(func=cmd_format)
