import contextlib
import locale
from pathlib import Path

from rich.console import Console
from rich.table import Table

from enrich_csv.api import search_company
from enrich_csv.config import load_config, lookup_destination, save_config, store_destination
from enrich_csv.models import Transaction, TransactionType
from enrich_csv.naf import naf_to_category
from enrich_csv.normalizer import destination_key, simplify_name

_console = Console()

with contextlib.suppress(locale.Error):
    locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")


def _format_date(tx: Transaction) -> str:
    return tx.date.strftime("%A %d %B %Y")


def _ask_destination_name(proposed: str) -> str:
    _console.print(f"  [bold]Nom commercial[/bold] [[cyan]{proposed}[/cyan]] : ", end="")
    raw = input()
    return raw.strip() if raw.strip() else proposed


def _ask_category(categories: list[str], proposed: str) -> str:
    _console.print("  [bold]Catégorie[/bold] :")
    for i, cat in enumerate(categories, 1):
        marker = " [green]←[/green]" if cat == proposed else ""
        _console.print(f"    {i:2}. {cat}{marker}")
    _console.print(
        f"  [[cyan]{proposed}[/cyan]] ([dim]s = ignorer, autre = nouvelle catégorie[/dim]) : ",
        end="",
    )
    raw = input().strip()
    if raw.lower() == "s":
        return ""
    if not raw:
        return proposed
    if raw.isdigit():
        idx = int(raw) - 1
        if 0 <= idx < len(categories):
            return categories[idx]
    return raw


def _display_transaction(
    tx: Transaction, api_result: dict[str, str] | None, proposed_name: str
) -> None:
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column(style="dim", width=14)
    table.add_column()
    table.add_row("Date", f"[bold]{_format_date(tx)}[/bold]")
    table.add_row("Libellé", tx.raw_label)
    table.add_row("Extrait", tx.clean_label)
    if api_result:
        api_info = f"{api_result['name']} → simplifié : [cyan]{proposed_name}[/cyan]"
    else:
        api_info = "[dim](aucun résultat SIRENE)[/dim]"
    table.add_row("API SIRENE", api_info)
    _console.rule(f"[bold]{tx.type.value}[/bold] — {tx.source_name}")
    _console.print(table)


def enrich(transactions: list[Transaction], config_path: Path) -> list[Transaction]:
    """Interactively enrich transactions with destination names and categories.

    Known transactions are enriched silently; unknown ones trigger an interactive prompt.
    """
    config = load_config(config_path)
    enriched: list[Transaction] = []

    for tx in transactions:
        if tx.type == TransactionType.TRANSFER:
            enriched.append(tx)
            continue

        key = destination_key(tx.raw_label)
        entry = lookup_destination(config, key)

        if entry:
            tx.destination_name = entry["destination_name"]
            tx.category = entry["category"]
            enriched.append(tx)
            continue

        # Unknown transaction: query SIRENE and prompt user.
        api_result = search_company(tx.clean_label)
        if api_result:
            proposed_name = simplify_name(api_result["name"])
            proposed_category = naf_to_category(api_result["naf"], config["naf_to_category"])
            siren = api_result["siren"]
        else:
            proposed_name = tx.clean_label
            proposed_category = "À classer"
            siren = ""

        _display_transaction(tx, api_result, proposed_name)
        destination_name = _ask_destination_name(proposed_name)
        category = _ask_category(config["categories"], proposed_category)

        if category:
            if category not in config["categories"]:
                config["categories"].append(category)
            tx.destination_name = destination_name
            tx.category = category
            store_destination(
                config, key, destination_name=destination_name, category=category, siren=siren
            )
            save_config(config, config_path)

        enriched.append(tx)

    return enriched
