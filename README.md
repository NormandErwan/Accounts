# Expenses

CLI tool that enriches French bank CSV exports (CMB, Fortuneo) with destination names and categories, then outputs a CSV ready for [Firefly III](https://www.firefly-iii.org/) import.

## Installation

Requires [.NET 10](https://dotnet.microsoft.com/).

```bash
dotnet build
```

## Usage

```bash
dotnet run --project src/EnrichCsv -- RELEVE_COMPTE.csv --bank cmb --account "CMB Perso"
dotnet run --project src/EnrichCsv -- HistoriqueOperations_12345678.zip --bank fortuneo --account "Fortuneo"
dotnet run --project src/EnrichCsv -- jan.csv feb.csv --bank cmb --account "CMB Perso" --output firefly.csv
```

Bank format is auto-detected from the file header; use `--bank` only when detection is ambiguous.

For each unknown transaction the tool queries the [SIRENE API](https://recherche-entreprises.api.gouv.fr) and prompts to confirm the destination name and category.

## Cache file

Default location: `./cache.json` (next to the bank exports). Created automatically on first run.

Two sections:

- **`naf_to_category`** — mapping from NAF/APE codes (e.g. `"47.11"`) to category names; edit by hand
- **`destinations`** — confirmed destination names and categories, keyed by normalised label; written by the tool
