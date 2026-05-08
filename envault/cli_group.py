"""CLI subcommand for group management."""
from __future__ import annotations

import argparse
import sys

from envault.group import (
    GroupError,
    add_to_group,
    filter_by_group,
    format_group_report,
    get_groups,
    remove_from_group,
)


def cmd_group(args: argparse.Namespace) -> None:
    action = args.group_action

    if action == "list":
        groups = get_groups(args.vault)
        if args.key:
            keys = [args.key]
        else:
            keys = sorted(groups.keys())
        if not keys:
            print("No group assignments found.")
            return
        for k in keys:
            print(format_group_report(k, groups.get(k, [])))

    elif action == "add":
        try:
            add_to_group(args.vault, args.key, args.group)
            print(f"Added '{args.key}' to group '{args.group}'.")
        except GroupError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

    elif action == "remove":
        try:
            remove_from_group(args.vault, args.key, args.group)
            print(f"Removed '{args.key}' from group '{args.group}'.")
        except GroupError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

    elif action == "filter":
        keys = filter_by_group(args.vault, args.group)
        if not keys:
            print(f"No keys in group '{args.group}'.")
        else:
            for k in keys:
                print(k)


def add_group_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("group", help="Manage entry groups")
    p.add_argument("--vault", default=".envault", help="Vault file path")
    sub = p.add_subparsers(dest="group_action", required=True)

    lst = sub.add_parser("list", help="List groups")
    lst.add_argument("key", nargs="?", default=None, help="Filter by key")

    add = sub.add_parser("add", help="Add key to group")
    add.add_argument("key")
    add.add_argument("group")

    rm = sub.add_parser("remove", help="Remove key from group")
    rm.add_argument("key")
    rm.add_argument("group")

    flt = sub.add_parser("filter", help="List keys in a group")
    flt.add_argument("group")

    p.set_defaults(func=cmd_group)
