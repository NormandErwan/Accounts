import locale
from pathlib import Path

from rich.console import Console
from rich.table import Table

from enrich_csv.api import search_company
from enrich_csv.cache import load_cache, lookup, save_cache, store
from enrich_csv.models import VALID_CATEGORIES, Transaction, TransactionType
from enrich_csv.naf import naf_to_category
from enrich_csv.normalizer import cache_key, simplify_name

_CATEGORIES = sorted(VALID_CATEGORIES)
_console = Console()

try:
    locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
except locale.Error:
    pass  # fall back to default locale on systems without fr_FR


def _format_date(tx: Transaction) -> str:
    return tx.date.strftime("%A %d %B %Y")


def _ask_merchant_name(proposed: str) -> str:
    _console.print(f"  [bold]Nom commercial[/bold] [[cyan]{proposed}[/cyan]] : ", end="")
    raw = input()
    return raw.strip() if raw.strip() else proposed


def _ask_category(proposed: str) -> str:
    _console.print("  [bold]Catégorie[/bold] :")
    for i, cat in enumerate(_CATEGORIES, 1):
        marker = " [green]←[/green]" if cat == proposed else ""
        _console.print(f"    {i:2}. {cat}{marker}")
    _console.print(f"  [[cyan]{proposed}[/cyan]] ([dim]s = ignorer[/dim]) : ", end="")
    raw = input().strip()
    if raw.lower() == "s":
        return ""
    if raw.isdigit():
        idx = int(raw) - 1
        if 0 <= idx < len(_CATEGORIES):
            return _CATEGORIES[idx]
    return proposed


def _display_transaction(tx: Transaction, api_result: dict | None, proposed_name: str) -> None:
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
    _console.rule(f"[bold]{tx.type.value}[/bold] — {tx.source_account}")
    _console.print(table)


def enrich(transactions: list[Transaction], cache_path: Path) -> list[Transaction]:
    """Interactively enrich transactions with merchant names and categories.

    Known transactions (found in cache) are enriched silently.
    Unknown ones trigger an interactive prompt.
    """
    cache = load_cache(cache_path)
    enriched: list[Transaction] = []

    for tx in transactions:
        if tx.type == TransactionType.TRANSFER:
            enriched.append(tx)
            continue

        key = cache_key(tx.raw_label)
        cached = lookup(cache, key)

        if cached:
            tx.merchant_name = cached["merchant_name"]
            tx.category = cached["category"]
            enriched.append(tx)
            continue

        # Unknown transaction: query SIRENE and prompt user.
        api_result = search_company(tx.clean_label)
        if api_result:
            proposed_name = simplify_name(api_result["name"])
            proposed_category = naf_to_category(api_result["naf"])
            siren = api_result["siren"]
        else:
            proposed_name = tx.clean_label
            proposed_category = "À classer"
            siren = ""

        _display_transaction(tx, api_result, proposed_name)
        merchant_name = _ask_merchant_name(proposed_name)
        category = _ask_category(proposed_category)

        if category:
            tx.merchant_name = merchant_name
            tx.category = category
            store(cache, key, merchant_name=merchant_name, category=category, siren=siren)
            save_cache(cache, cache_path)

        enriched.append(tx)

    return enriched
