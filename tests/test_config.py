import json
from pathlib import Path

import pytest

from enrich_csv.config import (
    add_category,
    load_config,
    lookup_destination,
    save_config,
    store_destination,
)


@pytest.fixture
def config_path(tmp_path: Path) -> Path:
    return tmp_path / "config.json"


@pytest.fixture
def populated_config_path(tmp_path: Path) -> Path:
    path = tmp_path / "config.json"
    data = {
        "categories": ["Logement", "Courses"],
        "naf_to_category": {"47.11": "Courses"},
        "destination_cache": {
            "OPERATEUR MOBILE": {
                "destination_name": "Opérateur Mobile",
                "category": "Abonnements",
                "siren": "123456789",
            }
        },
    }
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return path


def test_load_config_missing_file_returns_empty_defaults(config_path: Path):
    config = load_config(config_path)
    assert config["categories"] == []
    assert config["naf_to_category"] == {}
    assert config["destination_cache"] == {}


def test_load_config_existing_file_returns_custom_values(populated_config_path: Path):
    config = load_config(populated_config_path)
    assert config["categories"] == ["Logement", "Courses"]
    assert config["naf_to_category"] == {"47.11": "Courses"}
    assert "OPERATEUR MOBILE" in config["destination_cache"]


def test_save_config_creates_valid_json(config_path: Path):
    config = load_config(config_path)
    save_config(config, config_path)
    raw = json.loads(config_path.read_text(encoding="utf-8"))
    assert "categories" in raw
    assert "naf_to_category" in raw
    assert "destination_cache" in raw


def test_save_config_round_trips(config_path: Path):
    config = load_config(config_path)
    store_destination(config, "TEST", destination_name="Test", category="Services")
    save_config(config, config_path)
    reloaded = load_config(config_path)
    assert lookup_destination(reloaded, "TEST") is not None
    assert reloaded["destination_cache"]["TEST"]["destination_name"] == "Test"


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
    add_category(config, "Logement", config_path)
    add_category(config, "Logement", config_path)
    assert config["categories"].count("Logement") == 1


def test_lookup_destination_existing_key(populated_config_path: Path):
    config = load_config(populated_config_path)
    result = lookup_destination(config, "OPERATEUR MOBILE")
    assert result is not None
    assert result["destination_name"] == "Opérateur Mobile"
    assert result["category"] == "Abonnements"


def test_lookup_destination_missing_key(populated_config_path: Path):
    config = load_config(populated_config_path)
    assert lookup_destination(config, "UNKNOWN") is None


def test_lookup_destination_case_sensitive(populated_config_path: Path):
    config = load_config(populated_config_path)
    assert lookup_destination(config, "operateur mobile") is None


def test_store_destination_adds_entry(config_path: Path):
    config = load_config(config_path)
    store_destination(config, "NOUVEAU", destination_name="Nouveau", category="Achats")
    assert "NOUVEAU" in config["destination_cache"]
    assert config["destination_cache"]["NOUVEAU"]["destination_name"] == "Nouveau"
    assert config["destination_cache"]["NOUVEAU"]["category"] == "Achats"


def test_store_destination_with_siren(config_path: Path):
    config = load_config(config_path)
    store_destination(
        config, "MARCHAND", destination_name="Marchand", category="Achats", siren="987654321"
    )
    assert config["destination_cache"]["MARCHAND"]["siren"] == "987654321"


def test_store_destination_without_siren_defaults_empty(config_path: Path):
    config = load_config(config_path)
    store_destination(config, "MARCHAND", destination_name="Marchand", category="Achats")
    assert config["destination_cache"]["MARCHAND"]["siren"] == ""


def test_saved_file_preserves_non_ascii(config_path: Path):
    config = load_config(config_path)
    store_destination(config, "TEST", destination_name="Tëst café", category="Loisirs")
    save_config(config, config_path)
    raw = config_path.read_text(encoding="utf-8")
    parsed = json.loads(raw)
    assert parsed["destination_cache"]["TEST"]["destination_name"] == "Tëst café"
