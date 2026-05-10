# CLAUDE.md

## Project

CLI tool that enriches French bank CSV exports with Firefly III categories and destination account names, producing an import-ready CSV.

## Toolchain

- **uv** — package manager and runner (`uv sync`, `uv run <cmd>`)
- **ruff** — linter and formatter (`uv run ruff check .`, `uv run ruff format .`)
- **ty** — type checker (`uvx ty check .`)
- **pytest** — test runner (`uv run pytest tests/ -m "not e2e" -q`)

Run all checks before committing:

```bash
uvx ty check . && uv run ruff check . && uv run ruff format --check . && uv run pytest tests/ -m "not e2e" -q
```

## Conventions

- All **code** is in English: variable names, function names, class names, comments, docstrings.
- All **display strings** are in French: category names, CLI messages.
- Firefly III field names: `source_name` (bank account), `destination_name` (payee for withdrawals), `type` (`withdrawal` / `deposit` / `transfer`).
- No personal data in the repository — fixtures use invented names; real CSVs are passed as base64 CI secrets.
