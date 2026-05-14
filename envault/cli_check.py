"""CLI subcommand: envault check — verify vault keys against an expected list."""

import argparse
import sys

from envault.env_check import check_entries, format_check_report


def cmd_check(args: argparse.Namespace) -> None:
    """Handle the 'check' subcommand."""
    expected_keys: list[str] = []

    if args.keys:
        expected_keys.extend(args.keys)

    if args.keys_file:
        try:
            with open(args.keys_file) as fh:
                for line in fh:
                    key = line.strip()
                    if key and not key.startswith("#"):
                        expected_keys.append(key)
        except FileNotFoundError:
            print(f"error: keys file not found: {args.keys_file}", file=sys.stderr)
            sys.exit(1)

    if not expected_keys:
        print("error: provide keys via --keys or --keys-file", file=sys.stderr)
        sys.exit(1)

    result = check_entries(
        vault_path=args.vault,
        expected_keys=expected_keys,
        strict=args.strict,
    )

    report = format_check_report(result, strict=args.strict)
    print(report)

    if not result.ok:
        sys.exit(1)


def add_check_subcommand(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    parser = subparsers.add_parser(
        "check",
        help="verify that expected keys are present in the vault",
    )
    parser.add_argument("vault", help="path to the vault file")
    parser.add_argument(
        "--keys",
        nargs="+",
        metavar="KEY",
        help="one or more expected key names",
    )
    parser.add_argument(
        "--keys-file",
        metavar="FILE",
        help="file with one expected key per line (# lines ignored)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="also flag keys present in vault but not in expected list",
    )
    parser.set_defaults(func=cmd_check)
