import importlib
import locale
from datetime import date
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from enrich_csv.config import load_config, save_config, store_destination
from enrich_csv.enricher import (
    _ask_category,
    _ask_destination_name,
    _display_transaction,
    _ensure_locale,
    _format_date,
    enrich,
)
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
# _ensure_locale / _format_date
# ---------------------------------------------------------------------------


def test_ensure_locale_calls_setlocale_on_first_use(monkeypatch):
    monkeypatch.setattr("enrich_csv.enricher._locale_configured", False)
    with patch("locale.setlocale") as mock_set:
        _ensure_locale()
    mock_set.assert_called_once_with(locale.LC_TIME, "fr_FR.UTF-8")


def test_ensure_locale_skips_setlocale_on_subsequent_calls(monkeypatch):
    monkeypatch.setattr("enrich_csv.enricher._locale_configured", True)
    with patch("locale.setlocale") as mock_set:
        _ensure_locale()
    mock_set.assert_not_called()


def test_format_date_returns_string():
    tx = make_tx()
    result = _format_date(tx)
    assert isinstance(result, str)
    assert "2026" in result


# ---------------------------------------------------------------------------
# _ask_destination_name
# ---------------------------------------------------------------------------


def test_ask_destination_name_returns_user_input(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda: "Carrefour")
    assert _ask_destination_name("Proposed") == "Carrefour"


def test_ask_destination_name_returns_proposed_on_empty(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda: "")
    assert _ask_destination_name("Proposed") == "Proposed"


def test_ask_destination_name_strips_whitespace(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda: "  Carrefour  ")
    assert _ask_destination_name("Proposed") == "Carrefour"


# ---------------------------------------------------------------------------
# _ask_category
# ---------------------------------------------------------------------------


def test_ask_category_skip_returns_empty(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda: "s")
    assert _ask_category(["Courses", "Santé"], "À classer") == ""


def test_ask_category_empty_input_returns_proposed(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda: "")
    assert _ask_category(["Courses"], "Courses") == "Courses"


def test_ask_category_by_number(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda: "2")
    assert _ask_category(["Courses", "Santé"], "À classer") == "Santé"


def test_ask_category_out_of_range_number_treated_as_new(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda: "99")
    assert _ask_category(["Courses"], "À classer") == "99"


def test_ask_category_free_text_returns_new_category(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda: "Vacances")
    assert _ask_category(["Courses"], "À classer") == "Vacances"


# ---------------------------------------------------------------------------
# _display_transaction
# ---------------------------------------------------------------------------


def test_display_transaction_with_api_result(monkeypatch):
    monkeypatch.setattr("enrich_csv.enricher._console", MagicMock())
    tx = make_tx()
    _display_transaction(tx, {"name": "Test SA"}, "Test")


def test_display_transaction_without_api_result(monkeypatch):
    monkeypatch.setattr("enrich_csv.enricher._console", MagicMock())
    tx = make_tx()
    _display_transaction(tx, None, "Test")


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


# ---------------------------------------------------------------------------
# Interactive enrich() path
# ---------------------------------------------------------------------------


@pytest.fixture
def empty_config(tmp_path: Path) -> Path:
    config_path = tmp_path / "config.json"
    config = load_config(config_path)
    config["categories"] = ["Courses", "Abonnements"]
    save_config(config, config_path)
    return config_path


def test_enrich_interactive_with_api_result(monkeypatch, empty_config: Path):
    """Unknown transaction: SIRENE returns a result, user accepts and picks category."""
    monkeypatch.setattr("enrich_csv.enricher._console", MagicMock())
    api = {"name": "Bouygues Telecom SA", "naf": "61.20", "siren": "397480930"}
    monkeypatch.setattr("enrich_csv.enricher.search_company", lambda _: api)
    inputs = iter(["Bouygues Telecom", "2"])
    monkeypatch.setattr("builtins.input", lambda: next(inputs))

    tx = make_tx(raw_label="PRLV BOUYGUES TELECOM", clean_label="BOUYGUES TELECOM")
    result = enrich([tx], empty_config)

    assert result[0].destination_name == "Bouygues Telecom"
    assert result[0].category == "Abonnements"


def test_enrich_interactive_without_api_result(monkeypatch, empty_config: Path):
    """Unknown transaction: SIRENE returns None, user provides name and category."""
    monkeypatch.setattr("enrich_csv.enricher._console", MagicMock())
    monkeypatch.setattr("enrich_csv.enricher.search_company", lambda _: None)
    inputs = iter(["Épicerie du coin", "1"])
    monkeypatch.setattr("builtins.input", lambda: next(inputs))

    tx = make_tx(raw_label="CARTE 10/01 EPICERIE", clean_label="EPICERIE")
    result = enrich([tx], empty_config)

    assert result[0].destination_name == "Épicerie du coin"
    assert result[0].category == "Courses"


def test_enrich_interactive_new_category_persisted(monkeypatch, empty_config: Path):
    """A new free-text category is appended to the config and persisted."""
    monkeypatch.setattr("enrich_csv.enricher._console", MagicMock())
    monkeypatch.setattr("enrich_csv.enricher.search_company", lambda _: None)
    inputs = iter(["Test Shop", "Vacances"])
    monkeypatch.setattr("builtins.input", lambda: next(inputs))

    tx = make_tx(raw_label="CARTE 10/01 TEST SHOP", clean_label="TEST SHOP")
    enrich([tx], empty_config)

    reloaded = load_config(empty_config)
    assert "Vacances" in reloaded["categories"]


def test_enrich_interactive_skip_leaves_transaction_unenriched(monkeypatch, empty_config: Path):
    """User presses 's' to skip — transaction is appended without destination/category."""
    monkeypatch.setattr("enrich_csv.enricher._console", MagicMock())
    monkeypatch.setattr("enrich_csv.enricher.search_company", lambda _: None)
    inputs = iter(["", "s"])
    monkeypatch.setattr("builtins.input", lambda: next(inputs))

    tx = make_tx(raw_label="CARTE 10/01 MYSTERE", clean_label="MYSTERE")
    result = enrich([tx], empty_config)

    assert result[0].destination_name == ""
    assert result[0].category == ""
