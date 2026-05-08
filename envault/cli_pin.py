"""CLI subcommands for pinning and unpinning vault entries."""

from __future__ import annotations

import argparse
import sys

from envault.cli import get_password
from envault.pin import PinError, format_pin_report, get_pins, pin_key, unpin_key
from envault.vault import load_vault, save_vault


def cmd_pin(args: argparse.Namespace) -> None:
    password = get_password(confirm=False)
    vault = load_vault(args.vault_file, password)

    if args.list:
        print(format_pin_report(get_pins(vault)))
        return

    if not args.key:
        print("Error: provide a KEY or use --list.", file=sys.stderr)
        sys.exit(1)

    try:
        if args.unpin:
            pins = unpin_key(vault, args.key)
            save_vault(args.vault_file, vault, password)
            print(f"Unpinned '{args.key}'.")
        else:
            pins = pin_key(vault, args.key)
            save_vault(args.vault_file, vault, password)
            print(f"Pinned '{args.key}'.")
        print(format_pin_report(pins))
    except PinError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def add_pin_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "pin",
        help="Pin or unpin vault entries to protect them from accidental changes.",
    )
    parser.add_argument("key", nargs="?", default=None, help="Entry key to pin/unpin.")
    parser.add_argument(
        "--unpin", action="store_true", help="Unpin the specified entry."
    )
    parser.add_argument(
        "--list", action="store_true", help="List all currently pinned entries."
    )
    parser.add_argument(
        "--vault-file", default=".envault", help="Path to the vault file."
    )
    parser.set_defaults(func=cmd_pin)
