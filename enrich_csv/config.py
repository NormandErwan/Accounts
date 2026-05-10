import json
from pathlib import Path
from typing import TypedDict

from enrich_csv.defaults import DEFAULT_CATEGORIES, DEFAULT_NAF_TO_CATEGORY


class Config(TypedDict):
    categories: list[str]
    naf_to_category: dict[str, str]
    merchant_cache: dict[str, dict[str, str]]


def load_config(path: Path) -> Config:
    """Load config from disk, filling missing keys with defaults."""
    data: dict = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    return Config(
        categories=data.get("categories", list(DEFAULT_CATEGORIES)),
        naf_to_category=data.get("naf_to_category", dict(DEFAULT_NAF_TO_CATEGORY)),
        merchant_cache=data.get("merchant_cache", {}),
    )


def save_config(config: Config, path: Path) -> None:
    """Write config to JSON, creating parent dirs if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")


def add_category(config: Config, name: str, path: Path) -> None:
    """Append a new category and persist immediately."""
    if name not in config["categories"]:
        config["categories"].append(name)
        save_config(config, path)


def lookup_merchant(config: Config, key: str) -> dict[str, str] | None:
    """Return the cached merchant entry for key, or None if absent."""
    return config["merchant_cache"].get(key)


def store_merchant(
    config: Config,
    key: str,
    *,
    merchant_name: str,
    category: str,
    siren: str = "",
) -> None:
    """Insert or update a merchant entry in the in-memory config."""
    config["merchant_cache"][key] = {
        "merchant_name": merchant_name,
        "category": category,
        "siren": siren,
    }
