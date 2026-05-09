"""CLI subcommand for managing per-key descriptions."""

from __future__ import annotations

import argparse
import sys

from envault.description import (
    DescriptionError,
    clear_description,
    format_description_report,
    get_description,
    list_descriptions,
    set_description,
)


def cmd_description(args: argparse.Namespace) -> None:
    action = args.desc_action

    if action == "set":
        try:
            set_description(args.vault, args.key, args.text)
            print(f"Description set for '{args.key}'.")
        except DescriptionError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

    elif action == "get":
        text = get_description(args.vault, args.key)
        print(format_description_report(args.key, text))

    elif action == "clear":
        removed = clear_description(args.vault, args.key)
        if removed:
            print(f"Description cleared for '{args.key}'.")
        else:
            print(f"No description found for '{args.key}'.")

    elif action == "list":
        descriptions = list_descriptions(args.vault)
        if not descriptions:
            print("No descriptions set.")
        else:
            for k, v in sorted(descriptions.items()):
                print(format_description_report(k, v))


def add_description_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("desc", help="Manage per-key descriptions")
    p.add_argument("--vault", default=".envault", help="Vault file path")
    sub = p.add_subparsers(dest="desc_action", required=True)

    s = sub.add_parser("set", help="Set description for a key")
    s.add_argument("key")
    s.add_argument("text", help="Description text")

    g = sub.add_parser("get", help="Get description for a key")
    g.add_argument("key")

    c = sub.add_parser("clear", help="Remove description for a key")
    c.add_argument("key")

    sub.add_parser("list", help="List all descriptions")

    p.set_defaults(func=cmd_description)
