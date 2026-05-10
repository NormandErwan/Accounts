def naf_to_category(code: str, naf_map: dict[str, str]) -> str:
    """Map a NAF/APE code to a category using the provided mapping.

    Tries exact match, then 5-char prefix (e.g. "47.11"), then 4-char prefix (e.g. "47.1").
    Returns "À classer" if nothing matches.
    """
    if not code:
        return "À classer"
    return naf_map.get(code) or naf_map.get(code[:5]) or naf_map.get(code[:4]) or "À classer"
