# Expenses

CLI tool that enriches French bank CSV exports (CMB, Fortuneo) with destination names and categories, then outputs a CSV ready for [Firefly III](https://www.firefly-iii.org/) import.

## Installation

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run enrich-csv --help
```

## Usage

```bash
uv run enrich-csv RELEVE_COMPTE.csv --bank cmb --account "CMB Perso"
uv run enrich-csv HistoriqueOperations_12345678.zip --bank fortuneo --account "Fortuneo"
uv run enrich-csv jan.csv feb.csv --bank cmb --account "CMB Perso" --output firefly.csv
uv run enrich-csv RELEVE.csv --bank cmb --account "CMB Perso" --config ~/my-config.json
```

For each unknown transaction the tool queries the [SIRENE API](https://recherche-entreprises.api.gouv.fr) and prompts to confirm the destination name and category.

## Config file

Default location: `~/.config/expenses/config.json`. Created automatically on first run (empty — add your own categories and NAF mappings).

Three sections:

- **`categories`** — list of category names shown in the interactive prompt
- **`naf_to_category`** — mapping from NAF/APE codes (e.g. `"47.11"`) to category names
- **`destination_cache`** — confirmed destination names and categories, keyed by normalised label

New categories can be added interactively during a session or by editing the file directly.
