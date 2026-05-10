import csv
import io

from enrich_csv.models import FIREFLY_TYPE_MAP, Transaction, TransactionType

_HEADERS = [
    "date",
    "description",
    "amount",
    "currency_code",
    "source_name",
    "destination_name",
    "category",
    "type",
]


def to_firefly_csv(transactions: list[Transaction]) -> str:
    """Serialise transactions to a Firefly III-compatible CSV string (UTF-8, comma-separated)."""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=_HEADERS, lineterminator="\n")
    writer.writeheader()
    for tx in transactions:
        firefly_type = FIREFLY_TYPE_MAP[tx.type]
        destination = tx.destination_name if tx.type == TransactionType.EXPENSE else ""
        writer.writerow(
            {
                "date": tx.date.isoformat(),
                "description": tx.raw_label,
                "amount": f"{tx.amount:.2f}",
                "currency_code": "EUR",
                "source_name": tx.source_name,
                "destination_name": destination,
                "category": tx.category,
                "type": firefly_type,
            }
        )
    return buf.getvalue()
