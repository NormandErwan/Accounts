NAF_TO_CATEGORY: dict[str, str] = {
    # Courses
    "47.11": "Courses",
    "47.19": "Courses",
    "47.21": "Courses",
    "47.22": "Courses",
    "47.24": "Courses",
    # Santé
    "86.21": "Santé",
    "86.22": "Santé",
    "86.23": "Santé",
    "86.90": "Santé",
    "47.73": "Santé",
    "75.00": "Santé",
    # Transport
    "49.10": "Transport",
    "49.20": "Transport",
    "49.31": "Transport",
    "49.32": "Transport",
    "49.41": "Transport",
    "52.21": "Transport",
    "45.20": "Transport",
    "45.11": "Transport",
    "77.11": "Transport",
    # Loisirs
    "56.10": "Loisirs",
    "56.21": "Loisirs",
    "56.30": "Loisirs",
    "90.01": "Loisirs",
    "90.02": "Loisirs",
    "90.03": "Loisirs",
    "93.11": "Loisirs",
    "93.12": "Loisirs",
    "93.13": "Loisirs",
    "93.19": "Loisirs",
    "93.21": "Loisirs",
    "93.29": "Loisirs",
    "59.14": "Loisirs",
    # Abonnements
    "61.10": "Abonnements",
    "61.20": "Abonnements",
    "61.30": "Abonnements",
    "63.12": "Abonnements",
    "60.10": "Abonnements",
    # Services
    "62.01": "Services",
    "62.02": "Services",
    "62.09": "Services",
    "63.11": "Services",
    "64.19": "Services",
    "69.10": "Services",
    "69.20": "Services",
    "74.10": "Services",
    # Maison
    "47.52": "Maison",
    "47.53": "Maison",
    "47.59": "Maison",
    "43.21": "Maison",
    "43.22": "Maison",
    "52.10": "Maison",
    # Logement
    "68.20": "Logement",
    "68.10": "Logement",
    "41.10": "Logement",
    # Achats
    "47.41": "Achats",
    "47.42": "Achats",
    "47.43": "Achats",
    "47.51": "Achats",
    "47.61": "Achats",
    "47.62": "Achats",
    "47.63": "Achats",
    "47.64": "Achats",
    "47.65": "Achats",
    "47.71": "Achats",
    "47.72": "Achats",
    "47.74": "Achats",
    "47.75": "Achats",
    "47.76": "Achats",
    "47.77": "Achats",
    "47.78": "Achats",
    "47.79": "Achats",
    "47.91": "Achats",
    "47.99": "Achats",
    # Impôts
    "84.11": "Impôts",
    "84.12": "Impôts",
    # Épargne
    "65.11": "Épargne",
    "65.12": "Épargne",
    "65.20": "Épargne",
    "65.30": "Épargne",
    "64.11": "Épargne",
}


def naf_to_category(code: str) -> str:
    """Map a NAF/APE code to a category.

    Tries exact match, then 5-char prefix (e.g. "47.11"), then 4-char prefix (e.g. "47.1").
    Returns "À classer" if nothing matches.
    """
    if not code:
        return "À classer"
    return (
        NAF_TO_CATEGORY.get(code)
        or NAF_TO_CATEGORY.get(code[:5])
        or NAF_TO_CATEGORY.get(code[:4])
        or "À classer"
    )
