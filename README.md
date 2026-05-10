# Expenses

CLI tool that enriches French bank CSV exports (CMB, Fortuneo) with merchant names and categories, then outputs a CSV ready for [Firefly III](https://www.firefly-iii.org/) import.

## Installation

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run enrich-csv --help
```

## Usage

```bash
# CMB account
uv run enrich-csv RELEVE_COMPTE.csv --bank cmb --account "CMB Perso"

# Fortuneo (accepts .zip or .csv)
uv run enrich-csv HistoriqueOperations_12345678.zip --bank fortuneo --account "Fortuneo"

# Multiple files → merged and sorted by date
uv run enrich-csv jan.csv feb.csv --bank cmb --account "CMB Perso"

# Write to a file instead of stdout
uv run enrich-csv RELEVE.csv --bank cmb --account "CMB Perso" --output firefly.csv

# Use a custom config file
uv run enrich-csv RELEVE.csv --bank cmb --account "CMB Perso" --config ~/my-config.json
```

For each unknown transaction the tool queries the [SIRENE API](https://recherche-entreprises.api.gouv.fr) and opens an interactive prompt to confirm the merchant name and pick a category.

## Config file

The config file is a single JSON file that stores three things:

- **`categories`** — list of category names shown in the interactive prompt
- **`naf_to_category`** — mapping from NAF/APE business codes to categories
- **`merchant_cache`** — previously confirmed merchant names and categories

Default location: `~/.config/expenses/config.json`

The file is created automatically on first run with built-in defaults. You can edit it manually at any time.

### Example

```json
{
  "categories": [
    "Logement",
    "Courses",
    "Santé",
    "Transport",
    "Loisirs",
    "Maison",
    "Services",
    "Abonnements",
    "Achats",
    "Impôts",
    "Épargne",
    "Revenus",
    "À classer"
  ],
  "naf_to_category": {
    "47.11": "Courses",
    "86.21": "Santé",
    "61.20": "Abonnements"
  },
  "merchant_cache": {
    "BOUYGUES TELECOM": {
      "merchant_name": "Bouygues Telecom",
      "category": "Abonnements",
      "siren": "397480930"
    }
  }
}
```

### Adding a category

During an interactive session, type any string that is not a menu number to create a new category on the fly — it is persisted to the config immediately.

To add a category manually, edit the `categories` list in the JSON file.

### Adding NAF mappings

Add entries to `naf_to_category` using the 4- or 5-character NAF code (e.g. `"47.11"`) as the key and a category name as the value. The tool tries an exact match first, then falls back to shorter prefixes.

## CI — E2E tests with real bank files

Real CSV files are never committed. Pass them as base64-encoded GitHub Actions secrets:

```bash
# Encode and register a secret
base64 -w0 RELEVE_COMPTE_*.csv | gh secret set E2E_CMB_PERSO_CSV
base64 -w0 HistoriqueOperations_*.zip | gh secret set E2E_FORTUNEO_ZIP
```

E2E tests are skipped automatically when the secrets are absent.
