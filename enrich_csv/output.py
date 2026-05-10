import csv
import io
from typing import NamedTuple

from enrich_csv.models import Transaction, TransactionType


class _FireflyRow(NamedTuple):
    date: str
    description: str
    amount: str
    currency_code: str
    source_name: str
    destination_name: str
    category: str
    type: str


def _to_row(tx: Transaction) -> _FireflyRow:
    return _FireflyRow(
        date=tx.date.isoformat(),
        description=tx.raw_label,
        amount=f"{tx.amount:.2f}",
        currency_code="EUR",
        source_name=tx.source_name,
        destination_name=tx.destination_name if tx.type == TransactionType.EXPENSE else "",
        category=tx.category,
        type=tx.type.value,
    )


def to_firefly_csv(transactions: list[Transaction]) -> str:
    """Serialise transactions to a Firefly III-compatible CSV string (UTF-8, comma-separated)."""
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(_FireflyRow._fields)
    for tx in transactions:
        writer.writerow(_to_row(tx))
    return buf.getvalue()
