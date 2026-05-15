# `envault summarize` — Vault Overview Command

Print a concise, human-readable summary of everything stored in a vault file.

## Usage

```
envault summarize <vault-file> [--json]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `vault`  | Path to the `.vault` file |
| `--json` | Also emit a machine-readable JSON block |

## Example output

```
Vault : secrets.vault
Keys  : 5
Pinned: 2 (DB_PASSWORD, API_KEY)
Tags  : 2 unique tag(s)
  [prod] API_KEY, DB_PASSWORD
  [dev] DEV_TOKEN
Expiry: 1 key(s) have TTL set
Notes : 1 key(s) have notes
Groups: 1 group(s)
  (infra) DB_HOST, DB_PASSWORD
```

## JSON output (`--json`)

When `--json` is passed the text summary is printed first, followed by a
JSON object on stdout:

```json
{
  "vault": "secrets.vault",
  "total_keys": 5,
  "pinned": ["API_KEY", "DB_PASSWORD"],
  "tags": {
    "prod": ["API_KEY", "DB_PASSWORD"],
    "dev": ["DEV_TOKEN"]
  },
  "keys_with_expiry": ["API_KEY"],
  "keys_with_notes": ["DB_HOST"],
  "groups": {
    "infra": ["DB_HOST", "DB_PASSWORD"]
  }
}
```

## Notes

- No password is required — the summary only inspects metadata and key names,
  never decrypting values.
- Pinned keys, tags, notes, TTL, and groups are all read from the vault's
  internal `__meta__` sections.
