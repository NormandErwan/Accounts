"""End-to-end tests using real bank CSV files injected via base64-encoded env vars.

Set the following GitHub Actions secrets (base64-encoded file content):
  E2E_CMB_PERSO_CSV    — CMB personal account CSV
  E2E_CMB_COMMUN_CSV   — CMB joint account CSV
  E2E_FORTUNEO_ZIP     — Fortuneo zip archive

Run with: pytest tests/e2e/ -m e2e
"""

import base64
import os
import tempfile
from decimal import Decimal
from pathlib import Path

import pytest

from enrich_csv.models import Transaction
from enrich_csv.parsers import parse_cmb, parse_fortuneo


def _decode_secret(env_var: str) -> Path | None:
    """Decode a base64 secret from an env var to a temporary file. Returns None if unset."""
    value = os.environ.get(env_var)
    if not value:
        return None
    suffix = ".zip" if "ZIP" in env_var else ".csv"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(base64.b64decode(value))
    return Path(tmp.name)


def _assert_transactions_valid(transactions: list[Transaction]) -> None:
    assert len(transactions) > 0
    for tx in transactions:
        assert isinstance(tx.amount, Decimal)
        assert tx.amount >= 0
        assert tx.source_account
        assert tx.raw_label


@pytest.mark.e2e
def test_cmb_perso_full_parse():
    path = _decode_secret("E2E_CMB_PERSO_CSV")
    if path is None:
        pytest.skip("E2E_CMB_PERSO_CSV not set")
    try:
        transactions = parse_cmb(path, account="CMB Perso")
        _assert_transactions_valid(transactions)
    finally:
        path.unlink(missing_ok=True)


@pytest.mark.e2e
def test_cmb_commun_full_parse():
    path = _decode_secret("E2E_CMB_COMMUN_CSV")
    if path is None:
        pytest.skip("E2E_CMB_COMMUN_CSV not set")
    try:
        transactions = parse_cmb(path, account="CMB Commun")
        _assert_transactions_valid(transactions)
    finally:
        path.unlink(missing_ok=True)


@pytest.mark.e2e
def test_fortuneo_full_parse():
    path = _decode_secret("E2E_FORTUNEO_ZIP")
    if path is None:
        pytest.skip("E2E_FORTUNEO_ZIP not set")
    try:
        transactions = parse_fortuneo(path, account="Fortuneo")
        _assert_transactions_valid(transactions)
    finally:
        path.unlink(missing_ok=True)
