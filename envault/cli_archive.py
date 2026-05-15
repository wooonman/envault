"""CLI subcommand for archiving and restoring vault keys."""

from __future__ import annotations

import argparse
import sys

from envault.env_archive import (
    ArchiveError,
    archive_key,
    format_archive_list,
    list_archived,
    restore_key,
)


def cmd_archive(args: argparse.Namespace) -> None:
    action = args.archive_action

    if action == "list":
        keys = list_archived(args.vault)
        print(format_archive_list(keys))
        return

    if action == "add":
        try:
            result = archive_key(args.vault, args.key)
            print(str(result))
        except ArchiveError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)
        return

    if action == "restore":
        try:
            result = restore_key(args.vault, args.key)
            print(str(result))
        except ArchiveError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)
        return

    print(f"Unknown archive action: {action}", file=sys.stderr)
    sys.exit(1)


def add_archive_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser("archive", help="Archive or restore vault keys")
    parser.add_argument("--vault", default=".envault", help="Path to vault file")

    sub = parser.add_subparsers(dest="archive_action", required=True)

    sub.add_parser("list", help="List archived keys")

    add_p = sub.add_parser("add", help="Archive (soft-delete) a key")
    add_p.add_argument("key", help="Key to archive")

    restore_p = sub.add_parser("restore", help="Restore an archived key")
    restore_p.add_argument("key", help="Key to restore")

    parser.set_defaults(func=cmd_archive)
