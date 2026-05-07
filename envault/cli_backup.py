"""CLI subcommands for vault backup and restore."""

import argparse
import sys

from envault.backup import (
    backup_vault,
    list_backups,
    restore_vault,
    format_backup_list,
)

DEFAULT_BACKUP_DIR = ".envault_backups"
DEFAULT_VAULT = ".vault.json"


def cmd_backup(args: argparse.Namespace) -> None:
    action = args.backup_action

    if action == "create":
        try:
            path = backup_vault(
                vault_path=args.vault,
                backup_dir=args.backup_dir,
            )
            print(f"Backup created: {path}")
        except FileNotFoundError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

    elif action == "list":
        entries = list_backups(
            backup_dir=args.backup_dir,
            vault_stem=args.vault_stem,
        )
        print(format_backup_list(entries))

    elif action == "restore":
        try:
            restore_vault(
                backup_path=args.backup_file,
                vault_path=args.vault,
                overwrite=args.overwrite,
            )
            print(f"Vault restored from {args.backup_file} to {args.vault}")
        except (FileNotFoundError, FileExistsError) as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)


def add_backup_subcommand(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("backup", help="Backup and restore vault files")
    parser.add_argument(
        "--vault", default=DEFAULT_VAULT, help="Path to vault file"
    )
    parser.add_argument(
        "--backup-dir", default=DEFAULT_BACKUP_DIR, help="Directory to store backups"
    )
    sub = parser.add_subparsers(dest="backup_action", required=True)

    sub.add_parser("create", help="Create a new backup of the vault")

    list_p = sub.add_parser("list", help="List available backups")
    list_p.add_argument(
        "--vault-stem", default="vault", help="Vault filename stem to filter by"
    )

    restore_p = sub.add_parser("restore", help="Restore vault from a backup")
    restore_p.add_argument("backup_file", help="Path to the backup file")
    restore_p.add_argument(
        "--overwrite", action="store_true", help="Overwrite existing vault"
    )

    parser.set_defaults(func=cmd_backup)
