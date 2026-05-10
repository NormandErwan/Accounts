import pytest

from enrich_csv.normalizer import normalize_label, simplify_name


class TestNormalizeLabel:
    @pytest.mark.parametrize(
        "raw, expected",
        [
            ("CARTE 15/01 SUPERMARCHE VILLE", "SUPERMARCHE VILLE"),
            ("CARTE 08/01 SUPERMARCHE 35000 RENNES", "SUPERMARCHE"),
            ("PRLV OPERATEUR MOBILE", "OPERATEUR MOBILE"),
            ("VIR INST vers COMPTE COMMUN FORT", "COMPTE COMMUN FORT"),
            ("VIR INST de PARTENAIRE", "PARTENAIRE"),
            ("VIR INST PARTENAIRE", "PARTENAIRE"),
            ("VIR de COMPTE PARTENAIRE - loyer", "COMPTE PARTENAIRE - loyer"),
            ("VIR EMPLOYEUR SA", "EMPLOYEUR SA"),
            ("ANN CARTE BOUTIQUE LIGNE", "BOUTIQUE LIGNE"),
            ("ECH PRET 0123456789", "Échéance prêt"),
            ("ECH PRET 0110866344104", "Échéance prêt"),
            ("F COTISATION EUROCOMPTE 04/26", "COTISATION EUROCOMPTE 04/26"),
            ("vers NORMAND / PARTENAIRE", "NORMAND / PARTENAIRE"),
            ("CARTE 10/01 ADEO*BRICOLEUR VILLE", "BRICOLEUR VILLE"),
            ("CARTE 12/01 SumUp *ARTISAN NOM", "ARTISAN NOM"),
            ("CARTE 12/01 SumUp  *ARTISAN NOM", "ARTISAN NOM"),
            ("CARTE 03/04 SQ *BOUTIQUE PLACE", "BOUTIQUE PLACE"),
            ("CARTE 02/04 OVH SAS Roubaix", "OVH SAS"),
            ("VIR LBC FRANCE SAS", "FRANCE SAS"),
        ],
    )
    def test_normalize(self, raw, expected):
        assert normalize_label(raw) == expected

    def test_returns_string(self):
        assert isinstance(normalize_label("PRLV OPERATEUR"), str)

    def test_empty_string(self):
        result = normalize_label("")
        assert isinstance(result, str)


class TestSimplifyName:
    @pytest.mark.parametrize(
        "name, expected",
        [
            ("Bouygues Telecom SA", "Bouygues Telecom"),
            ("OVH SAS", "OVH"),
            ("INTERMARCHE DAC RENNES SAS", "Intermarche Dac Rennes"),
            ("Adobe Systems Inc", "Adobe Systems"),
            ("Leroy Merlin SARL", "Leroy Merlin"),
            ("Amazon EU SARL", "Amazon EU"),
            ("Carrefour SNC", "Carrefour"),
            ("Anthropic", "Anthropic"),
            ("E.Leclerc", "E.Leclerc"),
            ("CPAM", "CPAM"),
        ],
    )
    def test_simplify(self, name, expected):
        assert simplify_name(name) == expected

    def test_returns_string(self):
        assert isinstance(simplify_name("Test SA"), str)

    def test_empty_string(self):
        result = simplify_name("")
        assert isinstance(result, str)


class TestCacheKey:
    def test_cache_key_is_upper_stripped(self):
        from enrich_csv.normalizer import cache_key

        assert cache_key("PRLV Bouygues Telecom") == "BOUYGUES TELECOM"
        assert cache_key("CARTE 08/01 SUPERMARCHE VILLE") == "SUPERMARCHE VILLE"
