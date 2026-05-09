from datetime import date
from decimal import Decimal
from typing import Any

import pytest

from enrich_csv.models import VALID_CATEGORIES, Transaction, TransactionType


def make_transaction(
    *,
    date: date = date(2026, 1, 15),
    raw_label: str = "PRLV OPERATEUR MOBILE",
    clean_label: str = "OPERATEUR MOBILE",
    amount: Decimal = Decimal("9.99"),
    type: TransactionType = TransactionType.EXPENSE,
    source_account: str = "CMB Perso",
    merchant_name: str = "",
    category: str = "",
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


def test_valid_transaction():
    tx = make_transaction()
    assert tx.amount == Decimal("9.99")
    assert tx.type == TransactionType.EXPENSE
    assert tx.merchant_name == ""
    assert tx.category == ""


def test_valid_transaction_with_category():
    tx = make_transaction(merchant_name="Opérateur Mobile", category="Abonnements")
    assert tx.merchant_name == "Opérateur Mobile"
    assert tx.category == "Abonnements"


def test_all_transaction_types():
    for tx_type in TransactionType:
        tx = make_transaction(type=tx_type)
        assert tx.type == tx_type


def test_transaction_type_french_values():
    assert TransactionType.EXPENSE.value == "Dépense"
    assert TransactionType.INCOME.value == "Revenu"
    assert TransactionType.TRANSFER.value == "Virement"


def test_amount_negative_raises():
    with pytest.raises(ValueError, match="positive Decimal"):
        make_transaction(amount=Decimal("-1.00"))


def test_amount_zero_allowed():
    tx = make_transaction(amount=Decimal("0"))
    assert tx.amount == Decimal("0")


def test_amount_wrong_type_raises():
    bad: Any = 9.99
    with pytest.raises((ValueError, TypeError)):
        make_transaction(amount=bad)


def test_type_string_raises():
    bad: Any = "Dépense"
    with pytest.raises(TypeError, match="TransactionType"):
        make_transaction(type=bad)


def test_date_string_raises():
    bad: Any = "2026-01-15"
    with pytest.raises(TypeError, match="datetime.date"):
        make_transaction(date=bad)


def test_source_account_empty_raises():
    with pytest.raises(ValueError, match="non-empty"):
        make_transaction(source_account="")


def test_source_account_whitespace_raises():
    with pytest.raises(ValueError, match="non-empty"):
        make_transaction(source_account="   ")


def test_source_account_free_string():
    tx = make_transaction(source_account="Compte Épargne Logement")
    assert tx.source_account == "Compte Épargne Logement"


def test_category_invalid_raises():
    with pytest.raises(ValueError, match="unknown category"):
        make_transaction(category="Vacances")


def test_category_empty_allowed():
    tx = make_transaction(category="")
    assert tx.category == ""


def test_all_valid_categories():
    for cat in VALID_CATEGORIES:
        tx = make_transaction(category=cat)
        assert tx.category == cat
