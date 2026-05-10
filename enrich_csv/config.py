import json
from pathlib import Path
from typing import TypedDict


class Config(TypedDict):
    categories: list[str]
    naf_to_category: dict[str, str]
    destinations: dict[str, dict[str, str]]


def load_config(path: Path) -> Config:
    """Load config from disk, filling missing keys with empty defaults."""
    data: dict = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    return Config(
        categories=data.get("categories", []),
        naf_to_category=data.get("naf_to_category", {}),
        destinations=data.get("destinations", {}),
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


def lookup_destination(config: Config, key: str) -> dict[str, str] | None:
    """Return the destination entry for key, or None if absent."""
    return config["destinations"].get(key)


def store_destination(
    config: Config,
    key: str,
    *,
    destination_name: str,
    category: str,
    siren: str = "",
) -> None:
    """Insert or update a destination entry in the in-memory config."""
    config["destinations"][key] = {
        "destination_name": destination_name,
        "category": category,
        "siren": siren,
    }
