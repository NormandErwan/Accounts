import json
from pathlib import Path


def load_cache(path: Path) -> dict:
    """Load the JSON cache from disk. Returns an empty dict if the file does not exist."""
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def lookup(cache: dict, key: str) -> dict | None:
    """Return the cached entry for key, or None if absent."""
    return cache.get(key)


def store(
    cache: dict,
    key: str,
    *,
    merchant_name: str,
    category: str,
    siren: str = "",
) -> None:
    """Insert or update an entry in the in-memory cache."""
    cache[key] = {"merchant_name": merchant_name, "category": category, "siren": siren}


def save_cache(cache: dict, path: Path) -> None:
    """Persist the cache to disk, creating parent directories if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
