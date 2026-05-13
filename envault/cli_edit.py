"""CLI sub-command: envault edit KEY"""

import argparse
import sys

from envault.env_edit import edit_entry, format_edit_report, EditError
from envault.cli import get_password


def cmd_edit(args: argparse.Namespace) -> None:
    """Handle the `envault edit` sub-command."""
    password = get_password(confirm=False)

    # If --value not supplied, prompt interactively
    if args.value is None:
        try:
            import getpass
            new_value = getpass.getpass(f"New value for '{args.key}': ")
        except (KeyboardInterrupt, EOFError):
            print("\nAborted.", file=sys.stderr)
            sys.exit(1)
    else:
        new_value = args.value

    try:
        result = edit_entry(
            args.vault,
            args.key,
            new_value,
            password,
            create=args.create,
        )
    except EditError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(format_edit_report(result))


def add_edit_subcommand(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Register the `edit` sub-command with *subparsers*."""
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "edit",
        help="Edit the value of an existing vault entry.",
    )
    parser.add_argument("key", help="Entry key to edit.")
    parser.add_argument(
        "--value",
        default=None,
        help="New plaintext value (prompted securely if omitted).",
    )
    parser.add_argument(
        "--vault",
        default=".envault",
        help="Path to vault file (default: .envault).",
    )
    parser.add_argument(
        "--create",
        action="store_true",
        help="Create the key if it does not exist.",
    )
    parser.set_defaults(func=cmd_edit)
