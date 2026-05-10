import importlib
from datetime import date
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

import pytest

from enrich_csv.config import load_config, save_config, store_destination
from enrich_csv.enricher import enrich
from enrich_csv.models import Transaction, TransactionType


def make_tx(**kwargs) -> Transaction:
    defaults: dict = dict(
        date=date(2026, 1, 15),
        raw_label="PRLV OPERATEUR MOBILE",
        clean_label="OPERATEUR MOBILE",
        amount=Decimal("9.99"),
        type=TransactionType.EXPENSE,
        source_name="CMB Perso",
        destination_name="",
        category="",
    )
    defaults.update(kwargs)
    return Transaction(**defaults)


# ---------------------------------------------------------------------------
# Locale side effect (HP issue 2)
# ---------------------------------------------------------------------------


def test_importing_enricher_does_not_call_setlocale_at_module_level():
    """Reloading enricher must not call locale.setlocale at module level."""
    import enrich_csv.enricher

    with patch("locale.setlocale") as mock_setlocale:
        importlib.reload(enrich_csv.enricher)

    mock_setlocale.assert_not_called()


# ---------------------------------------------------------------------------
# In-place mutation (HP issue 3)
# ---------------------------------------------------------------------------


@pytest.fixture
def known_config(tmp_path: Path) -> Path:
    """Config with one known destination (OPERATEUR MOBILE → Abonnements)."""
    config_path = tmp_path / "config.json"
    config = load_config(config_path)
    store_destination(
        config,
        "OPERATEUR MOBILE",
        destination_name="Opérateur Mobile",
        category="Abonnements",
    )
    save_config(config, config_path)
    return config_path


def test_enrich_does_not_mutate_input_transaction(known_config: Path):
    """enrich() must return new objects; input transactions must be unchanged."""
    tx = make_tx()
    original_destination = tx.destination_name
    original_category = tx.category

    result = enrich([tx], known_config)

    assert tx.destination_name == original_destination, "input was mutated"
    assert tx.category == original_category, "input was mutated"
    assert result[0] is not tx, "returned object must be a new instance"


def test_enrich_returned_transaction_has_enriched_values(known_config: Path):
    tx = make_tx()
    result = enrich([tx], known_config)

    assert result[0].destination_name == "Opérateur Mobile"
    assert result[0].category == "Abonnements"


def test_enrich_transfer_is_not_mutated(known_config: Path):
    tx = make_tx(type=TransactionType.TRANSFER, raw_label="VIR INST vers COMPTE COMMUN")
    result = enrich([tx], known_config)

    assert result[0].destination_name == ""
    assert result[0].category == ""
