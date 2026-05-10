import json
from pathlib import Path

import pytest

from enrich_csv.config import (
    add_category,
    load_config,
    lookup_merchant,
    save_config,
    store_merchant,
)
from enrich_csv.defaults import DEFAULT_CATEGORIES, DEFAULT_NAF_TO_CATEGORY


@pytest.fixture
def config_path(tmp_path: Path) -> Path:
    return tmp_path / "config.json"


@pytest.fixture
def populated_config_path(tmp_path: Path) -> Path:
    path = tmp_path / "config.json"
    data = {
        "categories": ["Logement", "Courses"],
        "naf_to_category": {"47.11": "Courses"},
        "merchant_cache": {
            "OPERATEUR MOBILE": {
                "destination_name": "Opérateur Mobile",
                "category": "Abonnements",
                "siren": "123456789",
            }
        },
    }
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return path


def test_load_config_missing_file_returns_defaults(config_path: Path):
    config = load_config(config_path)
    assert config["categories"] == DEFAULT_CATEGORIES
    assert config["naf_to_category"] == DEFAULT_NAF_TO_CATEGORY
    assert config["merchant_cache"] == {}


def test_load_config_existing_file_returns_custom_values(populated_config_path: Path):
    config = load_config(populated_config_path)
    assert config["categories"] == ["Logement", "Courses"]
    assert config["naf_to_category"] == {"47.11": "Courses"}
    assert "OPERATEUR MOBILE" in config["merchant_cache"]


def test_save_config_creates_valid_json(config_path: Path):
    config = load_config(config_path)
    save_config(config, config_path)
    raw = json.loads(config_path.read_text(encoding="utf-8"))
    assert "categories" in raw
    assert "naf_to_category" in raw
    assert "merchant_cache" in raw


def test_save_config_round_trips(config_path: Path):
    config = load_config(config_path)
    store_merchant(config, "TEST", destination_name="Test", category="Services")
    save_config(config, config_path)
    reloaded = load_config(config_path)
    assert lookup_merchant(reloaded, "TEST") is not None
    assert reloaded["merchant_cache"]["TEST"]["destination_name"] == "Test"


def test_save_config_creates_parent_dirs(tmp_path: Path):
    path = tmp_path / "subdir" / "config.json"
    config = load_config(path)
    save_config(config, path)
    assert path.exists()


def test_add_category_appends_and_persists(config_path: Path):
    config = load_config(config_path)
    add_category(config, "Vacances", config_path)
    assert "Vacances" in config["categories"]
    reloaded = load_config(config_path)
    assert "Vacances" in reloaded["categories"]


def test_add_category_no_duplicate(config_path: Path):
    config = load_config(config_path)
    original_count = len(config["categories"])
    add_category(config, config["categories"][0], config_path)
    assert len(config["categories"]) == original_count


def test_lookup_merchant_existing_key(populated_config_path: Path):
    config = load_config(populated_config_path)
    result = lookup_merchant(config, "OPERATEUR MOBILE")
    assert result is not None
    assert result["destination_name"] == "Opérateur Mobile"
    assert result["category"] == "Abonnements"


def test_lookup_merchant_missing_key(populated_config_path: Path):
    config = load_config(populated_config_path)
    assert lookup_merchant(config, "UNKNOWN MERCHANT") is None


def test_lookup_merchant_case_sensitive(populated_config_path: Path):
    config = load_config(populated_config_path)
    assert lookup_merchant(config, "operateur mobile") is None


def test_store_merchant_adds_entry(config_path: Path):
    config = load_config(config_path)
    store_merchant(
        config, "NOUVEAU MARCHAND", destination_name="Nouveau Marchand", category="Achats"
    )
    assert "NOUVEAU MARCHAND" in config["merchant_cache"]
    assert config["merchant_cache"]["NOUVEAU MARCHAND"]["destination_name"] == "Nouveau Marchand"
    assert config["merchant_cache"]["NOUVEAU MARCHAND"]["category"] == "Achats"


def test_store_merchant_with_siren(config_path: Path):
    config = load_config(config_path)
    store_merchant(
        config, "MARCHAND", destination_name="Marchand", category="Achats", siren="987654321"
    )
    assert config["merchant_cache"]["MARCHAND"]["siren"] == "987654321"


def test_store_merchant_without_siren_defaults_empty(config_path: Path):
    config = load_config(config_path)
    store_merchant(config, "MARCHAND", destination_name="Marchand", category="Achats")
    assert config["merchant_cache"]["MARCHAND"]["siren"] == ""


def test_saved_file_preserves_non_ascii(config_path: Path):
    config = load_config(config_path)
    store_merchant(config, "TEST", destination_name="Tëst café", category="Loisirs")
    save_config(config, config_path)
    raw = config_path.read_text(encoding="utf-8")
    parsed = json.loads(raw)
    assert parsed["merchant_cache"]["TEST"]["destination_name"] == "Tëst café"
