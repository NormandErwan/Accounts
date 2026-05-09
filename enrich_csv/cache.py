import json
from pathlib import Path
from typing import Any

Cache = dict[str, dict[str, str]]


def load_cache(path: Path) -> Cache:
    """Load the JSON cache from disk. Returns an empty dict if the file does not exist."""
    if not path.exists():
        return {}
    data: Any = json.loads(path.read_text(encoding="utf-8"))
    return data


def lookup(cache: Cache, key: str) -> dict[str, str] | None:
    """Return the cached entry for key, or None if absent."""
    return cache.get(key)


def store(
    cache: Cache,
    key: str,
    *,
    merchant_name: str,
    category: str,
    siren: str = "",
) -> None:
    """Insert or update an entry in the in-memory cache."""
    cache[key] = {"merchant_name": merchant_name, "category": category, "siren": siren}


def save_cache(cache: Cache, path: Path) -> None:
    """Persist the cache to disk, creating parent directories if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
