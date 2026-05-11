"""CLI subcommand: envault list"""

import argparse
import sys
from envault.env_list import list_entries, format_list


def cmd_list(args: argparse.Namespace) -> None:
    try:
        entries = list_entries(
            vault_path=args.vault,
            tag_filter=args.tag,
            pinned_only=args.pinned,
            include_expired=not args.hide_expired,
        )
    except FileNotFoundError:
        print(f"error: vault file not found: {args.vault}", file=sys.stderr)
        sys.exit(1)

    output = format_list(entries, verbose=args.verbose)
    print(output)

    if args.count:
        print(f"\n{len(entries)} key(s) found.")


def add_list_subcommand(subparsers) -> None:
    p = subparsers.add_parser(
        "list",
        help="list keys stored in the vault",
    )
    p.add_argument(
        "--vault",
        default=".envault",
        help="path to vault file (default: .envault)",
    )
    p.add_argument(
        "--tag",
        default=None,
        metavar="TAG",
        help="filter entries by tag",
    )
    p.add_argument(
        "--pinned",
        action="store_true",
        help="show only pinned entries",
    )
    p.add_argument(
        "--hide-expired",
        action="store_true",
        help="exclude expired entries from output",
    )
    p.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="show tags, description, and flags",
    )
    p.add_argument(
        "--count",
        action="store_true",
        help="print total count after listing",
    )
    p.set_defaults(func=cmd_list)
