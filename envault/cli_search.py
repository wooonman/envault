"""CLI subcommands for vault search."""

from __future__ import annotations

import argparse
import sys

from envault.cli import get_password
from envault.search import format_search_results, search_keys, search_values


def cmd_search(args: argparse.Namespace) -> None:
    """Handle the 'search' subcommand."""
    password = get_password(confirm=False)

    try:
        if args.values:
            results = search_values(
                args.vault,
                password,
                args.pattern,
                case_sensitive=args.case_sensitive,
            )
            label = f"Values containing '{args.pattern}'"
        else:
            results = search_keys(
                args.vault,
                password,
                args.pattern,
                use_glob=not args.regex,
            )
            label = f"Keys matching '{args.pattern}'"
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"{label}: {len(results)} result(s)")
    print(format_search_results(results, reveal=args.reveal))


def add_search_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the 'search' subcommand onto *subparsers*."""
    p = subparsers.add_parser(
        "search",
        help="search keys or values in the vault",
    )
    p.add_argument("pattern", help="glob pattern (or regex with --regex)")
    p.add_argument(
        "--vault",
        default=".env.vault",
        help="vault file path (default: .env.vault)",
    )
    p.add_argument(
        "--regex",
        action="store_true",
        help="treat pattern as a regular expression",
    )
    p.add_argument(
        "--values",
        action="store_true",
        help="search inside decrypted values instead of key names",
    )
    p.add_argument(
        "--case-sensitive",
        action="store_true",
        help="case-sensitive value search (only with --values)",
    )
    p.add_argument(
        "--reveal",
        action="store_true",
        help="print actual values instead of masking them",
    )
    p.set_defaults(func=cmd_search)
