"""CLI subcommand: envault grep — grep vault values by pattern."""

from __future__ import annotations

import sys

from envault.env_grep import grep_vault, GrepError, format_grep_report
from envault.cli import get_password


def cmd_grep(args) -> None:
    password = get_password(confirm=False)
    try:
        result = grep_vault(
            args.vault,
            password,
            args.pattern,
            keys_only=args.keys_only,
            ignore_case=args.ignore_case,
            invert=args.invert,
            use_regex=args.regex,
        )
    except GrepError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    report = format_grep_report(result, show_line_numbers=args.line_numbers)
    print(report)

    if args.count:
        print(f"\n{result.count} match(es) found.")

    if result.count == 0:
        sys.exit(1)


def add_grep_subcommand(subparsers) -> None:
    p = subparsers.add_parser(
        "grep",
        help="Search vault entries by value (or key) pattern",
    )
    p.add_argument("vault", help="Path to the vault file")
    p.add_argument("pattern", help="Pattern to search for")
    p.add_argument("-k", "--keys-only", action="store_true",
                   help="Match against keys instead of values")
    p.add_argument("-i", "--ignore-case", action="store_true",
                   help="Case-insensitive matching")
    p.add_argument("-v", "--invert", action="store_true",
                   help="Invert match (show non-matching entries)")
    p.add_argument("-E", "--regex", action="store_true",
                   help="Treat pattern as a regular expression")
    p.add_argument("-n", "--line-numbers", action="store_true",
                   help="Show line numbers in output")
    p.add_argument("-c", "--count", action="store_true",
                   help="Print match count at the end")
    p.set_defaults(func=cmd_grep)
