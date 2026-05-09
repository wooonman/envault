"""CLI subcommand for managing per-key notes."""

from __future__ import annotations

import argparse
import sys

from envault.notes import NoteError, clear_note, format_notes_report, get_note, list_notes, set_note


def cmd_notes(args: argparse.Namespace) -> None:
    if args.notes_action == "set":
        try:
            set_note(args.vault, args.key, args.text, password="")
            print(f"Note set for '{args.key}'.")
        except NoteError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

    elif args.notes_action == "get":
        note = get_note(args.vault, args.key)
        if note is None:
            print(f"No note for '{args.key}'.")
        else:
            print(f"{args.key}: {note}")

    elif args.notes_action == "clear":
        removed = clear_note(args.vault, args.key)
        if removed:
            print(f"Note cleared for '{args.key}'.")
        else:
            print(f"No note found for '{args.key}'.")

    elif args.notes_action == "list":
        notes = list_notes(args.vault)
        print(format_notes_report(notes))

    else:
        print("Unknown notes action.", file=sys.stderr)
        sys.exit(1)


def add_notes_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("notes", help="manage per-key notes")
    p.add_argument("--vault", default=".env.vault", help="vault file path")
    sub = p.add_subparsers(dest="notes_action", required=True)

    s = sub.add_parser("set", help="attach a note to a key")
    s.add_argument("key")
    s.add_argument("text", help="note text")

    g = sub.add_parser("get", help="show note for a key")
    g.add_argument("key")

    c = sub.add_parser("clear", help="remove note for a key")
    c.add_argument("key")

    sub.add_parser("list", help="list all notes")

    p.set_defaults(func=cmd_notes)
