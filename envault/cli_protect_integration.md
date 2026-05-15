# `envault protect` — Key Protection

Protect vault keys from accidental modification or deletion.

## Usage

```bash
# Protect a key
envault protect vault.json API_KEY

# Remove protection
envault protect vault.json API_KEY --unprotect

# List all protected keys
envault protect vault.json --list
```

## How it works

Protected keys are stored under `__meta__.protected` inside the vault JSON file.
Any envault command that modifies or deletes a key should call
`assert_not_protected()` before making changes.

## Example output

```
$ envault protect vault.json API_KEY
Key 'API_KEY' is now protected.

$ envault protect vault.json --list
Protected keys:
  🔒 API_KEY

$ envault protect vault.json API_KEY --unprotect
Key 'API_KEY' is no longer protected.
```

## Integration with other commands

Import and call `assert_not_protected` in any command that writes to a key:

```python
from envault.env_protect import assert_not_protected

assert_not_protected(vault_path, key, operation="delete")
```

This raises `ProtectError` with a clear message if the key is currently
protected, preventing silent data loss.
