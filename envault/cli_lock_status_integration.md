# `envault status` — Lock Status Subcommand

Inspect the encryption and metadata status of every entry in your vault without decrypting values.

## Usage

```bash
envault status [--vault PATH] [--fail-unencrypted]
```

### Options

| Flag | Default | Description |
|---|---|---|
| `--vault` | `.envault` | Path to the vault file |
| `--fail-unencrypted` | off | Exit with code `2` if any entry is not encrypted |

## Example Output

```
API_KEY: [encrypted, tagged]
DB_PASS: [encrypted, pinned]
DEBUG:   [plain]

Total: 3 | Encrypted: 2
```

## Entry Flags

- **encrypted** — the value is stored as ciphertext (safe to commit)
- **tagged** — one or more tags are attached to the key
- **noted** — a note/comment is attached to the key
- **pinned** — the key is pinned (shown first in listings)
- **archived** — the key has been archived and excluded from normal listings
- **plain** — the value is stored in plaintext (not recommended)

## CI / Pre-commit Usage

Use `--fail-unencrypted` in CI pipelines to enforce that all secrets are encrypted before merging:

```yaml
# .github/workflows/check-vault.yml
- name: Verify vault encryption
  run: envault status --fail-unencrypted
```

## Notes

- No password is required — status inspection never decrypts values.
- The command reads `_tags`, `_notes`, `_pins`, and `_archive` metadata directly from the vault JSON.
- Entries are listed in alphabetical order.
