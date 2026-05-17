"""CLI subcommand: envault resolve — show resolved variable references."""

from __future__ import annotations

import argparse
import sys

from envault.env_resolve import resolve_references, ResolveError
from envault.cli import get_password


def cmd_resolve(args: argparse.Namespace) -> None:
    password = get_password(confirm=False)
    try:
        result = resolve_references(args.vault, password)
    except FileNotFoundError:
        print(f"error: vault not found: {args.vault}", file=sys.stderr)
        sys.exit(1)
    except ResolveError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(str(result))

    if result.cycles:
        print("warning: circular references detected — some keys not resolved.", file=sys.stderr)
        sys.exit(2)

    if result.unresolved:
        print("warning: some references could not be resolved.", file=sys.stderr)
        sys.exit(3)


def add_resolve_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "resolve",
        help="resolve ${VAR} references between vault entries",
    )
    parser.add_argument(
        "vault",
        help="path to the .vault.json file",
    )
    parser.set_defaults(func=cmd_resolve)
