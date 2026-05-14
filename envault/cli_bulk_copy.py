"""CLI subcommand: bulk-copy — copy all entries between vaults."""

import argparse
import sys

from envault.env_copy_all import bulk_copy, BulkCopyError
from envault.cli import get_password


def cmd_bulk_copy(args: argparse.Namespace) -> None:
    src_password = get_password(
        prompt=f"Password for source vault ({args.src}): ",
        env_var="ENVAULT_SRC_PASSWORD",
    )

    if args.src == args.dest:
        dest_password = src_password
    else:
        dest_password = get_password(
            prompt=f"Password for destination vault ({args.dest}): ",
            env_var="ENVAULT_DEST_PASSWORD",
        )

    try:
        result = bulk_copy(
            src_path=args.src,
            dest_path=args.dest,
            src_password=src_password,
            dest_password=dest_password,
            prefix=args.prefix or "",
            suffix=args.suffix or "",
            overwrite=args.overwrite,
        )
    except BulkCopyError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(result)


def add_bulk_copy_subcommand(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    parser = subparsers.add_parser(
        "bulk-copy",
        help="Copy all entries from one vault to another.",
    )
    parser.add_argument("src", help="Source vault file (.vault.json)")
    parser.add_argument("dest", help="Destination vault file (.vault.json)")
    parser.add_argument(
        "--prefix", default="", help="Prefix to add to every key in the destination."
    )
    parser.add_argument(
        "--suffix", default="", help="Suffix to append to every key in the destination."
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing keys in the destination vault.",
    )
    parser.set_defaults(func=cmd_bulk_copy)
