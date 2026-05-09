import httpx

_SEARCH_URL = "https://recherche-entreprises.api.gouv.fr/search"
_TIMEOUT = 5.0


def search_company(name: str) -> dict | None:
    """Search the French SIRENE database for a company by name.

    Returns a dict with keys "name", "naf", "siren" on success, or None if not found
    or if a network error occurs.
    """
    try:
        response = httpx.get(
            _SEARCH_URL,
            params={"q": name, "per_page": 1},
            timeout=_TIMEOUT,
        )
        response.raise_for_status()
        results = response.json().get("results", [])
        if not results:
            return None
        hit = results[0]
        return {
            "name": hit.get("nom_complet", ""),
            "naf": hit.get("siege", {}).get("activite_principale", ""),
            "siren": hit.get("siren", ""),
        }
    except Exception:
        return None
