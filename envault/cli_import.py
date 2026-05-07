"""CLI sub-command: envault import"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.cli import get_password
from envault.import_env import (
    parse_dotenv,
    parse_json_env,
    import_entries,
    format_import_report,
)


def cmd_import(args: argparse.Namespace) -> None:
    source = Path(args.source)
    if not source.exists():
        print(f"error: source file not found: {source}", file=sys.stderr)
        sys.exit(1)

    vault_path = Path(args.vault)
    text = source.read_text()

    fmt = args.format
    if fmt == "auto":
        fmt = "json" if source.suffix == ".json" else "dotenv"

    try:
        if fmt == "json":
            entries = parse_json_env(text)
        else:
            entries = parse_dotenv(text)
    except Exception as exc:
        print(f"error: could not parse source file: {exc}", file=sys.stderr)
        sys.exit(1)

    if not entries:
        print("No entries found in source file.")
        return

    password = get_password(confirm=False)

    try:
        imported, skipped = import_entries(
            vault_path, password, entries, overwrite=args.overwrite
        )
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(format_import_report(imported, skipped))


def add_import_subcommand(subparsers: argparse.Action) -> None:
    p = subparsers.add_parser(
        "import",
        help="import entries from a .env or JSON file into the vault",
    )
    p.add_argument("source", help="path to source .env or .json file")
    p.add_argument(
        "--vault",
        default=".envault",
        help="vault file path (default: .envault)",
    )
    p.add_argument(
        "--format",
        choices=["auto", "dotenv", "json"],
        default="auto",
        help="source file format (default: auto-detect)",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="overwrite existing keys in the vault",
    )
    p.set_defaults(func=cmd_import)
