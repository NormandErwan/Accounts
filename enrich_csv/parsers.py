import csv
import io
import zipfile
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from enrich_csv.models import Transaction, TransactionType
from enrich_csv.normalizer import normalize_label

_TRANSFER_KEYWORDS = ("vers ", "WERO", "COMPTE COMMUN")


def _parse_french_decimal(value: str) -> Decimal:
    cleaned = value.strip().replace("\u00a0", "").replace(" ", "").replace(",", ".")
    return Decimal(cleaned)


def _detect_transfer(label: str) -> bool:
    return any(kw in label for kw in _TRANSFER_KEYWORDS)


def parse_cmb(path: Path, account: str) -> list[Transaction]:
    """Parse a CMB bank CSV export (UTF-8, semicolon-separated, quoted)."""
    transactions: list[Transaction] = []
    with open(path, encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh, delimiter=";")
        next(reader)  # skip header
        for row in reader:
            if len(row) < 5:
                continue
            raw_date, _, raw_label, raw_debit, raw_credit = row[:5]
            tx_date = datetime.strptime(raw_date.strip(), "%d/%m/%Y").date()
            label = raw_label.strip()

            if raw_debit.strip():
                amount = _parse_french_decimal(raw_debit)
                tx_type = (
                    TransactionType.TRANSFER if _detect_transfer(label) else TransactionType.EXPENSE
                )
            else:
                amount = _parse_french_decimal(raw_credit)
                tx_type = TransactionType.INCOME

            transactions.append(
                Transaction(
                    date=tx_date,
                    raw_label=label,
                    clean_label=normalize_label(label),
                    amount=amount,
                    type=tx_type,
                    source_name=account,
                )
            )
    return transactions


def _read_fortuneo_csv(content: bytes) -> list[tuple[str, ...]]:
    text = content.decode("windows-1252")
    reader = csv.reader(io.StringIO(text, newline=""), delimiter=";")
    next(reader)  # skip header
    rows = []
    for row in reader:
        if len(row) >= 5 and any(cell.strip() for cell in row[:5]):
            rows.append(tuple(row))
    return rows


def parse_fortuneo(path: Path, account: str) -> list[Transaction]:
    """Parse a Fortuneo CSV export (Windows-1252, semicolon-separated, unquoted).

    Accepts either a .csv file or a .zip archive containing the CSV.
    """
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as zf:
            csv_name = next(n for n in zf.namelist() if n.endswith(".csv"))
            content = zf.read(csv_name)
    else:
        content = path.read_bytes()

    transactions: list[Transaction] = []
    for row in _read_fortuneo_csv(content):
        raw_date, _, raw_label, raw_debit, raw_credit = row[:5]
        tx_date = datetime.strptime(raw_date.strip(), "%d/%m/%Y").date()
        label = raw_label.strip()

        debit_str = raw_debit.strip()
        credit_str = raw_credit.strip()

        if debit_str:
            amount = abs(_parse_french_decimal(debit_str))
            tx_type = TransactionType.EXPENSE
        else:
            amount = _parse_french_decimal(credit_str)
            tx_type = TransactionType.INCOME

        transactions.append(
            Transaction(
                date=tx_date,
                raw_label=label,
                clean_label=normalize_label(label),
                amount=amount,
                type=tx_type,
                source_name=account,
            )
        )
    return transactions
