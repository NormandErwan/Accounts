import pytest

from enrich_csv.naf import naf_to_category


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
    assert naf_to_category(code) == expected
