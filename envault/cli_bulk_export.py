"""CLI subcommand: bulk-export — decrypt and export all vault entries."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.cli import get_password
from envault.env_bulk_export import BulkExportError, bulk_export


def cmd_bulk_export(args: argparse.Namespace) -> None:
    password = get_password(confirm=False)
    output_path = Path(args.output) if args.output else None

    try:
        result = bulk_export(
            vault_path=Path(args.vault),
            password=password,
            fmt=args.format,
            output_path=output_path,
            tags=args.tags or None,
        )
    except BulkExportError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: vault not found: {args.vault}", file=sys.stderr)
        sys.exit(1)

    if output_path is None:
        print(result.content, end="")
    else:
        print(result)


def add_bulk_export_subcommand(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "bulk-export",
        help="Decrypt and export all vault entries to a file or stdout.",
    )
    p.add_argument("vault", help="Path to the vault file.")
    p.add_argument(
        "-f",
        "--format",
        default="dotenv",
        choices=("dotenv", "json", "shell", "csv"),
        help="Output format (default: dotenv).",
    )
    p.add_argument("-o", "--output", default=None, help="Output file path (default: stdout).")
    p.add_argument(
        "-t",
        "--tags",
        nargs="+",
        default=[],
        metavar="TAG",
        help="Only export entries that have at least one of these tags.",
    )
    p.set_defaults(func=cmd_bulk_export)
