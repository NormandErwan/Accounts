import pytest

from enrich_csv.naf import naf_to_category

_NAF_MAP = {
    "47.11": "Courses",
    "47.73": "Santé",
    "86.21": "Santé",
    "49.41": "Transport",
    "52.21": "Transport",
    "56.10": "Loisirs",
    "56.30": "Loisirs",
    "61.20": "Abonnements",
    "62.01": "Services",
    "47.52": "Maison",
    "68.20": "Logement",
    "47.91": "Achats",
    "84.11": "Impôts",
    "65.30": "Épargne",
}


@pytest.mark.parametrize(
    "code, expected",
    [
        ("47.11B", "Courses"),
        ("47.11", "Courses"),
        ("86.21Z", "Santé"),
        ("86.21", "Santé"),
        ("47.73Z", "Santé"),
        ("49.41A", "Transport"),
        ("52.21Z", "Transport"),
        ("56.10A", "Loisirs"),
        ("56.30Z", "Loisirs"),
        ("61.20Z", "Abonnements"),
        ("61.20", "Abonnements"),
        ("62.01Z", "Services"),
        ("47.52A", "Maison"),
        ("68.20A", "Logement"),
        ("47.91A", "Achats"),
        ("84.11Z", "Impôts"),
        ("65.30Z", "Épargne"),
        ("99.99Z", "À classer"),
        ("", "À classer"),
        ("XX.XX", "À classer"),
    ],
)
def test_naf_to_category(code: str, expected: str):
    assert naf_to_category(code, _NAF_MAP) == expected


def test_naf_to_category_custom_map():
    custom = {"99.99": "Custom"}
    assert naf_to_category("99.99", custom) == "Custom"
    assert naf_to_category("47.11", custom) == "À classer"
