"""CLI subcommand for batch-deleting keys from a vault."""

import argparse
import sys
from envault.cli import get_password
from envault.env_batch_delete import batch_delete, BatchDeleteError


def cmd_batch_delete(args: argparse.Namespace) -> None:
    if not args.keys:
        print("No keys specified.", file=sys.stderr)
        sys.exit(1)

    try:
        result = batch_delete(
            args.vault,
            args.keys,
            skip_missing=args.skip_missing,
            skip_pinned=not args.force_pinned,
        )
    except BatchDeleteError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(str(result))

    if args.fail_on_missing and result.missing:
        sys.exit(2)


def add_batch_delete_subcommand(subparsers) -> None:
    p = subparsers.add_parser(
        "batch-delete",
        help="Delete multiple keys from the vault in one shot",
    )
    p.add_argument("vault", help="Path to the vault file")
    p.add_argument("keys", nargs="+", help="Keys to delete")
    p.add_argument(
        "--skip-missing",
        action="store_true",
        help="Silently skip keys that don't exist instead of raising an error",
    )
    p.add_argument(
        "--force-pinned",
        action="store_true",
        help="Also delete pinned keys (default: skip them)",
    )
    p.add_argument(
        "--fail-on-missing",
        action="store_true",
        help="Exit with code 2 if any requested keys were not found",
    )
    p.set_defaults(func=cmd_batch_delete)
