import csv
import io
from datetime import date
from decimal import Decimal

from enrich_csv.models import Transaction, TransactionType
from enrich_csv.output import to_firefly_csv

EXPECTED_HEADERS = [
    "date",
    "description",
    "amount",
    "currency_code",
    "source_name",
    "destination_name",
    "category",
    "type",
]


def make_transaction(
    *,
    date: date = date(2026, 1, 15),
    raw_label: str = "PRLV OPERATEUR MOBILE",
    clean_label: str = "OPERATEUR MOBILE",
    amount: Decimal = Decimal("9.99"),
    type: TransactionType = TransactionType.EXPENSE,
    source_account: str = "CMB Perso",
    merchant_name: str = "Opérateur Mobile",
    category: str = "Abonnements",
) -> Transaction:
    return Transaction(
        date=date,
        raw_label=raw_label,
        clean_label=clean_label,
        amount=amount,
        type=type,
        source_account=source_account,
        merchant_name=merchant_name,
        category=category,
    )


def parse_csv(text: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(text)))


def test_headers():
    result = to_firefly_csv([make_transaction()])
    reader = csv.reader(io.StringIO(result))
    headers = next(reader)
    assert headers == EXPECTED_HEADERS


def test_expense_type_maps_to_withdrawal():
    rows = parse_csv(to_firefly_csv([make_transaction(type=TransactionType.EXPENSE)]))
    assert rows[0]["type"] == "withdrawal"


def test_income_type_maps_to_deposit():
    rows = parse_csv(to_firefly_csv([make_transaction(type=TransactionType.INCOME)]))
    assert rows[0]["type"] == "deposit"


def test_transfer_type_maps_to_transfer():
    rows = parse_csv(to_firefly_csv([make_transaction(type=TransactionType.TRANSFER)]))
    assert rows[0]["type"] == "transfer"


def test_date_is_iso_format():
    rows = parse_csv(to_firefly_csv([make_transaction(date=date(2026, 5, 9))]))
    assert rows[0]["date"] == "2026-05-09"


def test_amount_has_two_decimals():
    rows = parse_csv(to_firefly_csv([make_transaction(amount=Decimal("9.9"))]))
    assert rows[0]["amount"] == "9.90"


def test_currency_is_eur():
    rows = parse_csv(to_firefly_csv([make_transaction()]))
    assert rows[0]["currency_code"] == "EUR"


def test_source_name_is_account():
    rows = parse_csv(to_firefly_csv([make_transaction(source_account="CMB Perso")]))
    assert rows[0]["source_name"] == "CMB Perso"


def test_destination_name_for_expense():
    rows = parse_csv(
        to_firefly_csv([make_transaction(type=TransactionType.EXPENSE, merchant_name="Carrefour")])
    )
    assert rows[0]["destination_name"] == "Carrefour"


def test_destination_name_empty_for_income():
    rows = parse_csv(to_firefly_csv([make_transaction(type=TransactionType.INCOME)]))
    assert rows[0]["destination_name"] == ""


def test_destination_name_empty_for_transfer():
    rows = parse_csv(to_firefly_csv([make_transaction(type=TransactionType.TRANSFER)]))
    assert rows[0]["destination_name"] == ""


def test_description_is_raw_label():
    rows = parse_csv(to_firefly_csv([make_transaction(raw_label="PRLV OPERATEUR MOBILE")]))
    assert rows[0]["description"] == "PRLV OPERATEUR MOBILE"


def test_category_is_preserved():
    rows = parse_csv(to_firefly_csv([make_transaction(category="Santé")]))
    assert rows[0]["category"] == "Santé"


def test_multiple_transactions():
    txs = [make_transaction(), make_transaction(amount=Decimal("50.00"), category="Courses")]
    rows = parse_csv(to_firefly_csv(txs))
    assert len(rows) == 2


def test_output_is_utf8_encoded():
    result = to_firefly_csv([make_transaction(merchant_name="Café de la Paix", category="Loisirs")])
    assert "Café de la Paix" in result


def test_empty_list():
    result = to_firefly_csv([])
    rows = parse_csv(result)
    assert rows == []
