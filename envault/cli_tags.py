"""CLI subcommands for managing vault entry tags."""

from __future__ import annotations

import argparse

from envault.cli import get_password
from envault.vault import load_vault, save_vault
from envault.tags import (
    add_tag,
    remove_tag,
    filter_by_tag,
    format_tags_report,
    get_tags,
)


def cmd_tags(args: argparse.Namespace) -> None:
    password = get_password(confirm=False)
    vault = load_vault(args.vault)

    if args.tags_cmd == "add":
        if args.entry not in vault or args.entry.startswith("__"):
            print(f"Entry '{args.entry}' not found in vault.")
            return
        add_tag(vault, args.entry, args.tag)
        save_vault(args.vault, vault)
        print(f"Tag '{args.tag}' added to '{args.entry}'.")

    elif args.tags_cmd == "remove":
        remove_tag(vault, args.entry, args.tag)
        save_vault(args.vault, vault)
        print(f"Tag '{args.tag}' removed from '{args.entry}'.")

    elif args.tags_cmd == "list":
        if args.entry:
            tags = get_tags(vault, args.entry)
            if tags:
                print(f"{args.entry}: " + ", ".join(tags))
            else:
                print(f"{args.entry}: (no tags)")
        else:
            print(format_tags_report(vault))

    elif args.tags_cmd == "filter":
        entries = filter_by_tag(vault, args.tag)
        if entries:
            print("\n".join(sorted(entries)))
        else:
            print(f"No entries with tag '{args.tag}'.")


def add_tags_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("tags", help="manage entry tags")
    p.add_argument("--vault", default=".envault", help="vault file path")
    sub = p.add_subparsers(dest="tags_cmd", required=True)

    p_add = sub.add_parser("add", help="add a tag to an entry")
    p_add.add_argument("entry")
    p_add.add_argument("tag")

    p_rm = sub.add_parser("remove", help="remove a tag from an entry")
    p_rm.add_argument("entry")
    p_rm.add_argument("tag")

    p_ls = sub.add_parser("list", help="list tags")
    p_ls.add_argument("entry", nargs="?", default=None)

    p_f = sub.add_parser("filter", help="filter entries by tag")
    p_f.add_argument("tag")

    p.set_defaults(func=cmd_tags)
