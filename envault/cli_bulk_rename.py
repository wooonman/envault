"""CLI sub-command: bulk-rename."""

from __future__ import annotations

import argparse
import sys

from envault.cli import get_password
from envault.env_rename_bulk import bulk_rename_prefix, bulk_rename_map, BulkRenameError


def cmd_bulk_rename(args: argparse.Namespace) -> None:
    password = get_password(confirm=False)

    try:
        if args.from_prefix is not None:
            result = bulk_rename_prefix(
                args.vault,
                password,
                args.from_prefix,
                args.to_prefix,
                dry_run=args.dry_run,
            )
        else:
            # parse KEY=NEW_KEY pairs
            mapping: dict[str, str] = {}
            for pair in args.map:
                if "=" not in pair:
                    print(f"error: invalid mapping '{pair}' (expected OLD=NEW)", file=sys.stderr)
                    sys.exit(1)
                old, new = pair.split("=", 1)
                mapping[old.strip()] = new.strip()
            result = bulk_rename_map(
                args.vault,
                password,
                mapping,
                dry_run=args.dry_run,
            )
    except BulkRenameError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    prefix = "[dry-run] " if args.dry_run else ""
    print(f"{prefix}bulk-rename results:")
    print(result)


def add_bulk_rename_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "bulk-rename",
        help="rename multiple keys at once by prefix swap or explicit mapping",
    )
    p.add_argument("vault", help="path to the vault file")
    p.add_argument("--dry-run", action="store_true", help="preview changes without writing")

    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--from-prefix",
        metavar="OLD_PREFIX",
        help="rename keys starting with this prefix",
    )
    p.add_argument(
        "--to-prefix",
        metavar="NEW_PREFIX",
        default="",
        help="replacement prefix (used with --from-prefix)",
    )
    mode.add_argument(
        "--map",
        nargs="+",
        metavar="OLD=NEW",
        help="explicit rename pairs",
    )
    p.set_defaults(func=cmd_bulk_rename)
