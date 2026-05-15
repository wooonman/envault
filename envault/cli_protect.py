"""CLI subcommand for protecting/unprotecting vault keys."""

from __future__ import annotations

import argparse
import sys

from envault.env_protect import (
    ProtectError,
    format_protect_report,
    get_protected,
    protect_key,
    unprotect_key,
)


def cmd_protect(args: argparse.Namespace) -> None:
    if args.list:
        try:
            keys = get_protected(args.vault)
            print(format_protect_report(keys))
        except FileNotFoundError:
            print("Vault not found.", file=sys.stderr)
            sys.exit(1)
        return

    if not args.key:
        print("Error: a key name is required unless --list is specified.", file=sys.stderr)
        sys.exit(1)

    try:
        if args.unprotect:
            unprotect_key(args.vault, args.key)
            print(f"Key '{args.key}' is no longer protected.")
        else:
            protect_key(args.vault, args.key)
            print(f"Key '{args.key}' is now protected.")
    except ProtectError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Vault not found.", file=sys.stderr)
        sys.exit(1)


def add_protect_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "protect",
        help="Protect or unprotect a key from accidental changes.",
    )
    p.add_argument("vault", help="Path to the vault file.")
    p.add_argument("key", nargs="?", default=None, help="Key to protect/unprotect.")
    p.add_argument(
        "--unprotect",
        action="store_true",
        help="Remove protection from the key.",
    )
    p.add_argument(
        "--list",
        action="store_true",
        help="List all protected keys.",
    )
    p.set_defaults(func=cmd_protect)
