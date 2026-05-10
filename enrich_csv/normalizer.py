import re

_STRIP_PREFIXES: list[tuple[str, str]] = [
    (r"^CARTE \d{2}/\d{2} ", ""),
    (r"^ANN CARTE ", ""),
    (r"^VIR INST (vers |de )?", ""),
    (r"^VIR (de |LBC )?", ""),
    (r"^PRLV ", ""),
    (r"^ECH PRET \S+", "Échéance prêt"),  # full replacement — returned immediately
    (r"^F ", ""),
    (r"^vers ", ""),
]

_CLEAN_SUFFIXES: list[tuple[str, str]] = [
    (r"\s+\d{5}\s+\S+$", ""),  # strips trailing postcode + city (e.g. "35000 RENNES")
    # Title-case city word(s) only when immediately after an uppercase char (e.g. "SAS Roubaix")
    (r"(?<=[A-Z])\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$", ""),
    # Bank reference codes: 8+ alphanum chars that contain at least one digit
    (r"\s+(?=[A-Z0-9]*\d)[A-Z0-9]{8,}/?.*$", ""),
]

_CLEAN_INFIXES: list[tuple[str, str]] = [
    (r"(?i)^SumUp\s*\*\s*", ""),
    (r"(?i)^SQ \*\s*", ""),
    (r"(?i)^ADEO\*\s*", ""),
]

_LEGAL_SUFFIXES = re.compile(
    r"\s+\b(SA|SAS|SARL|EURL|SNC|SASU|EIRL|SCE|SCP|SE|NV|BV|GmbH|Ltd|LLC|Inc|Corp|PLC)\b\.?\s*$",
    re.IGNORECASE,
)


def normalize_label(label: str) -> str:
    """Strip bank prefixes, payment platform markers, and trailing location/ref noise."""
    result = label.strip()

    for pattern, replacement in _STRIP_PREFIXES:
        new = re.sub(pattern, replacement, result, count=1)
        if new != result:
            if replacement != "":
                # Full substitution (e.g., ECH PRET → Échéance prêt): return immediately.
                return new
            result = new.strip()
            break  # prefix stripped; continue to suffix/infix cleanup

    for pattern, replacement in _CLEAN_SUFFIXES:
        result = re.sub(pattern, replacement, result).strip()

    for pattern, replacement in _CLEAN_INFIXES:
        new = re.sub(pattern, replacement, result, count=1)
        if new != result:
            result = new.strip()
            break

    return result.strip()


def simplify_name(name: str) -> str:
    """Remove legal-form suffixes and title-case multi-word all-caps names."""
    result = name.strip()
    while True:
        cleaned = _LEGAL_SUFFIXES.sub("", result).strip()
        if cleaned == result:
            break
        result = cleaned

    if not result:
        return result

    # Title-case only multi-word all-caps names (single-word all-caps = acronym, keep as-is).
    words = result.split()
    if result == result.upper() and len(words) > 1:
        return result.title()

    return result


def cache_key(raw_label: str) -> str:
    """Return upper-cased normalized label for cache lookup."""
    return normalize_label(raw_label).upper().strip()
