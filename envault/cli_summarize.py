"""CLI subcommand: summarize — print a human-readable vault overview."""
from __future__ import annotations

import argparse
import sys

from envault.env_summarize import summarize_vault, format_summary


def cmd_summarize(args: argparse.Namespace) -> None:
    try:
        summary = summarize_vault(args.vault)
    except FileNotFoundError:
        print(f"error: vault file not found: {args.vault}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:  # pragma: no cover
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(format_summary(summary))

    if args.json:
        import json

        data = {
            "vault": summary.vault_path,
            "total_keys": summary.total_keys,
            "pinned": summary.pinned_keys,
            "tags": summary.tagged_keys,
            "keys_with_expiry": summary.keys_with_expiry,
            "keys_with_notes": summary.keys_with_notes,
            "groups": summary.groups,
        }
        print(json.dumps(data, indent=2))


def add_summarize_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("summarize", help="Print an overview of the vault")
    p.add_argument("vault", help="Path to the vault file")
    p.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Also emit a JSON representation",
    )
    p.set_defaults(func=cmd_summarize)
