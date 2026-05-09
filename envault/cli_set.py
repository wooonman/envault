"""CLI subcommand: envault set KEY VALUE"""

from __future__ import annotations

import argparse
import sys

from envault.cli import get_password
from envault.env_set import set_entry, SetError, format_set_report


def cmd_set(args: argparse.Namespace) -> None:
    password = get_password(confirm=False)
    try:
        result = set_entry(
            args.vault,
            args.key,
            args.value,
            password,
            overwrite=not args.no_overwrite,
        )
        print(format_set_report([result]))
    except SetError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def add_set_subcommand(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "set",
        help="Add or update a single key in the vault.",
    )
    parser.add_argument("key", help="Environment variable name.")
    parser.add_argument("value", help="Plaintext value to encrypt and store.")
    parser.add_argument(
        "--vault",
        default=".envault",
        help="Path to the vault file (default: .envault).",
    )
    parser.add_argument(
        "--no-overwrite",
        action="store_true",
        default=False,
        help="Fail if the key already exists instead of overwriting it.",
    )
    parser.set_defaults(func=cmd_set)
