"""CLI wiring for the `envault rotate` sub-command."""

from __future__ import annotations

import argparse
import sys

from envault.cli import get_password
from envault.rotate import rotate_key, rotation_summary


def cmd_rotate(args: argparse.Namespace) -> None:
    """Handle the `rotate` sub-command."""
    print("Enter the CURRENT vault password:")
    old_password = get_password(confirm=False)

    print("Enter the NEW vault password:")
    new_password = get_password(confirm=True)

    if old_password == new_password:
        print("error: new password must differ from the current password.", file=sys.stderr)
        sys.exit(1)

    try:
        rotated = rotate_key(args.vault, old_password, new_password)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(rotation_summary(rotated))


def add_rotate_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the `rotate` sub-command on an existing subparser group."""
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "rotate",
        help="Re-encrypt the vault with a new password.",
    )
    parser.add_argument(
        "--vault",
        default=".env.vault",
        help="Path to the vault file (default: .env.vault).",
    )
    parser.set_defaults(func=cmd_rotate)
