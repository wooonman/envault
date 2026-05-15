"""CLI subcommand: envault stats — show vault statistics."""
from __future__ import annotations

import argparse
import sys

from envault.env_stats import compute_stats, format_stats


def cmd_stats(args: argparse.Namespace) -> None:
    """Handle the 'stats' subcommand."""
    try:
        stats = compute_stats(args.vault, warn_days=args.warn_days)
    except FileNotFoundError:
        print(f"error: vault file not found: {args.vault}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:  # pragma: no cover
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        import json
        data = {
            "total": stats.total,
            "pinned": stats.pinned,
            "tagged": stats.tagged,
            "with_notes": stats.with_notes,
            "with_description": stats.with_description,
            "expired": stats.expired,
            "expiring_soon": stats.expiring_soon,
            "tag_counts": stats.tag_counts,
            "keys": stats.keys,
        }
        print(json.dumps(data, indent=2))
    else:
        print(format_stats(stats))

    if args.warn and stats.expired > 0:
        print(
            f"\nwarning: {stats.expired} key(s) have expired.",
            file=sys.stderr,
        )


def add_stats_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "stats",
        help="show statistics and summary for a vault",
    )
    p.add_argument("vault", help="path to the vault file")
    p.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="output as JSON",
    )
    p.add_argument(
        "--warn",
        action="store_true",
        default=True,
        help="print a warning if any keys are expired (default: on)",
    )
    p.add_argument(
        "--warn-days",
        type=int,
        default=7,
        dest="warn_days",
        help="days ahead to consider 'expiring soon' (default: 7)",
    )
    p.set_defaults(func=cmd_stats)
