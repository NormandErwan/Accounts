from pathlib import Path

import click

from enrich_csv.enricher import enrich
from enrich_csv.models import Transaction
from enrich_csv.output import to_firefly_csv
from enrich_csv.parsers import parse_cmb, parse_fortuneo

_DEFAULT_CONFIG = Path.home() / ".config" / "expenses" / "config.json"


@click.command()
@click.argument("files", nargs=-1, required=True, type=click.Path(exists=True, path_type=Path))
@click.option(
    "--bank",
    type=click.Choice(["cmb", "fortuneo"], case_sensitive=False),
    required=True,
    help="Bank format of the input file(s).",
)
@click.option(
    "--account",
    required=True,
    help='Name of the source account (e.g. "CMB Perso", "Fortuneo").',
)
@click.option(
    "--config",
    "config_path",
    default=_DEFAULT_CONFIG,
    show_default=True,
    type=click.Path(path_type=Path),
    help="Path to JSON config file (categories, NAF map, destinations).",
)
@click.option(
    "--output",
    default=None,
    type=click.Path(path_type=Path),
    help="Output CSV file path. Defaults to stdout.",
)
def main(
    files: tuple[Path, ...],
    bank: str,
    account: str,
    config_path: Path,
    output: Path | None,
) -> None:
    """Enrich bank CSV exports with destination names and categories for Firefly III import."""
    transactions: list[Transaction] = []
    for path in files:
        if bank == "cmb":
            transactions.extend(parse_cmb(path, account=account))
        else:
            transactions.extend(parse_fortuneo(path, account=account))

    transactions.sort(key=lambda tx: tx.date)
    enriched = enrich(transactions, config_path=config_path)
    csv_output = to_firefly_csv(enriched)

    if output:
        output.write_text(csv_output, encoding="utf-8")
        click.echo(f"Written to {output}")
    else:
        click.echo(csv_output, nl=False)


if __name__ == "__main__":
    main()
