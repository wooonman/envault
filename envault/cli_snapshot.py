"""CLI subcommand: envault snapshot."""

from __future__ import annotations

import argparse
import sys

from envault.vault import load_vault, save_vault
from envault.snapshot import (
    SnapshotError,
    delete_snapshot,
    format_snapshot_list,
    list_snapshots,
    restore_snapshot,
    save_snapshot,
)
from envault.cli import get_password


def cmd_snapshot(args: argparse.Namespace) -> None:
    password = get_password(confirm=False)
    vault = load_vault(args.vault)

    if args.snapshot_cmd == "save":
        try:
            updated = save_snapshot(vault, args.name)
            save_vault(args.vault, updated)
            print(f"Snapshot '{args.name}' saved ({len([k for k in vault if not k.startswith('__')])} entries).")
        except SnapshotError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

    elif args.snapshot_cmd == "restore":
        try:
            updated = restore_snapshot(vault, args.name)
            save_vault(args.vault, updated)
            print(f"Snapshot '{args.name}' restored.")
        except SnapshotError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

    elif args.snapshot_cmd == "delete":
        try:
            updated = delete_snapshot(vault, args.name)
            save_vault(args.vault, updated)
            print(f"Snapshot '{args.name}' deleted.")
        except SnapshotError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

    elif args.snapshot_cmd == "list":
        names = list_snapshots(vault)
        print(format_snapshot_list(names))

    else:
        print("Unknown snapshot subcommand.", file=sys.stderr)
        sys.exit(1)


def add_snapshot_subcommand(subparsers) -> None:
    p = subparsers.add_parser("snapshot", help="Save/restore named vault snapshots")
    p.add_argument("--vault", default=".envault", help="Vault file path")
    sub = p.add_subparsers(dest="snapshot_cmd", required=True)

    for cmd in ("save", "restore", "delete"):
        sp = sub.add_parser(cmd, help=f"{cmd.capitalize()} a snapshot")
        sp.add_argument("name", help="Snapshot name")

    sub.add_parser("list", help="List all snapshots")
    p.set_defaults(func=cmd_snapshot)
