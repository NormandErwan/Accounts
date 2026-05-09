import json
from pathlib import Path

import pytest

from enrich_csv.cache import load_cache, lookup, save_cache, store


@pytest.fixture
def empty_cache(tmp_path: Path) -> Path:
    path = tmp_path / "cache.json"
    path.write_text("{}")
    return path


@pytest.fixture
def populated_cache(tmp_path: Path) -> Path:
    path = tmp_path / "cache.json"
    data = {
        "OPERATEUR MOBILE": {
            "merchant_name": "Opérateur Mobile",
            "category": "Abonnements",
            "siren": "123456789",
        }
    }
    path.write_text(json.dumps(data, ensure_ascii=False))
    return path


def test_load_empty_cache(empty_cache: Path):
    cache = load_cache(empty_cache)
    assert cache == {}


def test_load_missing_file(tmp_path: Path):
    cache = load_cache(tmp_path / "nonexistent.json")
    assert cache == {}


def test_load_populated_cache(populated_cache: Path):
    cache = load_cache(populated_cache)
    assert "OPERATEUR MOBILE" in cache


def test_lookup_existing_key(populated_cache: Path):
    cache = load_cache(populated_cache)
    result = lookup(cache, "OPERATEUR MOBILE")
    assert result is not None
    assert result["merchant_name"] == "Opérateur Mobile"
    assert result["category"] == "Abonnements"


def test_lookup_missing_key(populated_cache: Path):
    cache = load_cache(populated_cache)
    assert lookup(cache, "UNKNOWN MERCHANT") is None


def test_lookup_is_case_sensitive(populated_cache: Path):
    cache = load_cache(populated_cache)
    assert lookup(cache, "operateur mobile") is None


def test_store_adds_entry(empty_cache: Path):
    cache = load_cache(empty_cache)
    store(cache, "NOUVEAU MARCHAND", merchant_name="Nouveau Marchand", category="Achats")
    assert "NOUVEAU MARCHAND" in cache
    assert cache["NOUVEAU MARCHAND"]["merchant_name"] == "Nouveau Marchand"
    assert cache["NOUVEAU MARCHAND"]["category"] == "Achats"


def test_store_with_siren(empty_cache: Path):
    cache = load_cache(empty_cache)
    store(cache, "MARCHAND", merchant_name="Marchand", category="Achats", siren="987654321")
    assert cache["MARCHAND"]["siren"] == "987654321"


def test_store_without_siren_defaults_empty(empty_cache: Path):
    cache = load_cache(empty_cache)
    store(cache, "MARCHAND", merchant_name="Marchand", category="Achats")
    assert cache["MARCHAND"]["siren"] == ""


def test_save_and_reload(tmp_path: Path):
    path = tmp_path / "cache.json"
    cache: dict = {}
    store(cache, "TEST", merchant_name="Test", category="Services")
    save_cache(cache, path)

    reloaded = load_cache(path)
    assert lookup(reloaded, "TEST") is not None
    assert reloaded["TEST"]["merchant_name"] == "Test"


def test_save_creates_parent_dirs(tmp_path: Path):
    path = tmp_path / "subdir" / "cache.json"
    cache: dict = {}
    save_cache(cache, path)
    assert path.exists()


def test_saved_file_is_valid_json(tmp_path: Path):
    path = tmp_path / "cache.json"
    cache: dict = {}
    store(cache, "TEST", merchant_name="Tëst café", category="Loisirs")
    save_cache(cache, path)

    raw = path.read_text(encoding="utf-8")
    parsed = json.loads(raw)
    assert parsed["TEST"]["merchant_name"] == "Tëst café"
