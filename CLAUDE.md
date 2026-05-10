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

### Language

- All **code** is in English: variable names, function names, class names, comments, docstrings.
- All **display strings** are in French: enum values (`"Dépense"`, `"Revenu"`, `"Virement"`), category names, CLI messages.

### Firefly III terminology

Field names follow the [Firefly III API](https://api-docs.firefly-iii.org/) exactly:

| Field | Meaning |
|---|---|
| `source_name` | The bank account the money comes from (set via `--account`) |
| `destination_name` | The destination account (merchant name for expenses) |
| `category` | User-defined Firefly III category |
| `type` | `withdrawal` / `deposit` / `transfer` |

### No personal data in the repository

- Fixtures in `tests/fixtures/` use invented names and amounts.
- Real CSV files are passed as base64-encoded GitHub Actions secrets (`E2E_*`).
- No real names or account numbers in code or comments.

### Config file (`config.json`)

Single JSON file (default: `~/.config/expenses/config.json`) with three sections:

```json
{
  "categories": ["Logement", "Courses", ...],
  "naf_to_category": {"47.11": "Courses", ...},
  "merchant_cache": {
    "BOUYGUES TELECOM": {"destination_name": "Bouygues Telecom", "category": "Abonnements", "siren": "..."}
  }
}
```

## Key modules

| Module | Role |
|---|---|
| `parsers.py` | Parse CMB and Fortuneo CSV → `list[Transaction]` |
| `normalizer.py` | Strip bank prefixes, simplify merchant names |
| `api.py` | Query SIRENE API for company name and NAF code |
| `naf.py` | Map NAF/APE codes to categories |
| `enricher.py` | Interactive enrichment loop (prompts user, updates config) |
| `config.py` | Load/save config; merchant cache helpers |
| `defaults.py` | Factory defaults for categories and NAF map |
| `output.py` | Serialize to Firefly III CSV format |
| `cli.py` | Click entry point |
