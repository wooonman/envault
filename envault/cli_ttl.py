"""CLI subcommands for TTL management."""

from __future__ import annotations

import argparse
import sys

from envault.ttl import (
    TTLError,
    clear_expiry,
    format_ttl_report,
    get_ttl_data,
    is_expired,
    purge_expired,
    set_expiry,
)


def cmd_ttl(args: argparse.Namespace) -> None:
    vault_path = args.vault

    if args.ttl_action == "set":
        try:
            expires_at = set_expiry(vault_path, args.key, args.seconds)
            print(f"TTL set for '{args.key}': expires at {expires_at.isoformat()}")
        except TTLError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.ttl_action == "clear":
        removed = clear_expiry(vault_path, args.key)
        if removed:
            print(f"TTL cleared for '{args.key}'.")
        else:
            print(f"No TTL was set for '{args.key}'.")

    elif args.ttl_action == "status":
        ttl_data = get_ttl_data(vault_path)
        print(format_ttl_report(ttl_data))

    elif args.ttl_action == "check":
        expired = is_expired(vault_path, args.key)
        if expired:
            print(f"'{args.key}' is EXPIRED.")
        else:
            ttl_data = get_ttl_data(vault_path)
            if args.key in ttl_data:
                print(f"'{args.key}' is active (expires {ttl_data[args.key]}).")
            else:
                print(f"'{args.key}' has no TTL set.")

    elif args.ttl_action == "purge":
        removed = purge_expired(vault_path)
        if removed:
            print(f"Purged {len(removed)} expired key(s): {', '.join(removed)}")
        else:
            print("No expired keys to purge.")


def add_ttl_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("ttl", help="Manage key expiry (TTL)")
    p.add_argument("--vault", default=".env.vault", help="Path to vault file")
    ttl_sub = p.add_subparsers(dest="ttl_action", required=True)

    s = ttl_sub.add_parser("set", help="Set TTL on a key")
    s.add_argument("key", help="Key name")
    s.add_argument("seconds", type=int, help="Seconds until expiry")

    c = ttl_sub.add_parser("clear", help="Remove TTL from a key")
    c.add_argument("key", help="Key name")

    ttl_sub.add_parser("status", help="Show all TTL entries")

    ck = ttl_sub.add_parser("check", help="Check if a specific key is expired")
    ck.add_argument("key", help="Key name")

    ttl_sub.add_parser("purge", help="Delete all expired keys from vault")

    p.set_defaults(func=cmd_ttl)
