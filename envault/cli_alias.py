"""CLI subcommand: alias management."""

from __future__ import annotations

import argparse
import sys

from envault.alias import (
    AliasError,
    add_alias,
    format_alias_report,
    get_aliases,
    list_aliases,
    remove_alias,
)
from envault.vault import load_vault, save_vault
from envault.cli import get_password


def cmd_alias(args: argparse.Namespace) -> None:
    password = get_password(confirm=False)
    vault = load_vault(args.vault_file, password)

    if args.alias_action == "add":
        try:
            updated = add_alias(vault, args.alias, args.key)
        except AliasError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)
        save_vault(args.vault_file, updated, password)
        print(f"Alias '{args.alias}' -> '{args.key}' added.")

    elif args.alias_action == "remove":
        try:
            updated = remove_alias(vault, args.alias)
        except AliasError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)
        save_vault(args.vault_file, updated, password)
        print(f"Alias '{args.alias}' removed.")

    elif args.alias_action == "list":
        aliases = get_aliases(vault)
        print(format_alias_report(aliases))

    else:
        print("Unknown alias action.", file=sys.stderr)
        sys.exit(1)


def add_alias_subcommand(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("alias", help="Manage key aliases")
    parser.add_argument("--vault-file", default=".envault", help="Vault file path")
    sub = parser.add_subparsers(dest="alias_action", required=True)

    add_p = sub.add_parser("add", help="Add an alias")
    add_p.add_argument("alias", help="Alias name")
    add_p.add_argument("key", help="Real key name")

    rm_p = sub.add_parser("remove", help="Remove an alias")
    rm_p.add_argument("alias", help="Alias name to remove")

    sub.add_parser("list", help="List all aliases")

    parser.set_defaults(func=cmd_alias)
