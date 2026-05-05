# envault

> Minimal tool to encrypt and version-control `.env` files safely alongside your repo.

---

## Installation

```bash
pip install envault
```

---

## Usage

**Lock (encrypt) your `.env` file before committing:**

```bash
envault lock .env
```

This produces a `.env.vault` file that is safe to commit to your repository.

**Unlock (decrypt) on another machine or in CI:**

```bash
envault unlock .env.vault
```

You will be prompted for the passphrase, or you can provide it via the `ENVAULT_KEY` environment variable:

```bash
ENVAULT_KEY=mysecretkey envault unlock .env.vault
```

**Typical workflow:**

```bash
# Add .env to .gitignore, track the encrypted version instead
echo ".env" >> .gitignore
envault lock .env
git add .env.vault
git commit -m "chore: update encrypted env"
```

---

## How It Works

`envault` uses AES-256-GCM encryption (via the `cryptography` library) to encrypt your `.env` file. The resulting `.vault` file is a versioned, tamper-evident binary that can be safely stored in version control without exposing secrets.

---

## Requirements

- Python 3.8+
- `cryptography >= 41.0`

---

## License

[MIT](LICENSE) © 2024 envault contributors