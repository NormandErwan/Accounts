from datetime import date
from decimal import Decimal
from pathlib import Path

from enrich_csv.models import TransactionType
from enrich_csv.parsers import parse_cmb, parse_fortuneo

FIXTURES = Path(__file__).parent / "fixtures"


class TestParseCmb:
    def test_parses_five_rows(self):
        txs = parse_cmb(FIXTURES / "cmb_perso_sample.csv", account="CMB Perso")
        assert len(txs) == 5

    def test_source_name_matches_argument(self):
        txs = parse_cmb(FIXTURES / "cmb_perso_sample.csv", account="Mon Compte")
        assert all(tx.source_name == "Mon Compte" for tx in txs)

    def test_debit_row_is_expense(self):
        txs = parse_cmb(FIXTURES / "cmb_perso_sample.csv", account="CMB Perso")
        prlv = next(tx for tx in txs if "OPERATEUR MOBILE" in tx.raw_label)
        assert prlv.type == TransactionType.WITHDRAWAL
        assert prlv.amount == Decimal("9.99")

    def test_credit_row_is_income(self):
        txs = parse_cmb(FIXTURES / "cmb_perso_sample.csv", account="CMB Perso")
        vir = next(tx for tx in txs if "EMPLOYEUR" in tx.raw_label)
        assert vir.type == TransactionType.DEPOSIT
        assert vir.amount == Decimal("2000.00")

    def test_transfer_detection(self):
        txs = parse_cmb(FIXTURES / "cmb_perso_sample.csv", account="CMB Perso")
        transfer = next(tx for tx in txs if "COMPTE COMMUN" in tx.raw_label)
        assert transfer.type == TransactionType.TRANSFER

    def test_refund_is_income(self):
        txs = parse_cmb(FIXTURES / "cmb_perso_sample.csv", account="CMB Perso")
        ann = next(tx for tx in txs if "ANN CARTE" in tx.raw_label)
        assert ann.type == TransactionType.DEPOSIT
        assert ann.amount == Decimal("12.00")

    def test_dates_are_date_objects(self):
        txs = parse_cmb(FIXTURES / "cmb_perso_sample.csv", account="CMB Perso")
        assert all(isinstance(tx.date, date) for tx in txs)

    def test_date_parsed_correctly(self):
        txs = parse_cmb(FIXTURES / "cmb_perso_sample.csv", account="CMB Perso")
        prlv = next(tx for tx in txs if "OPERATEUR MOBILE" in tx.raw_label)
        assert prlv.date == date(2026, 1, 15)

    def test_amounts_always_positive(self):
        txs = parse_cmb(FIXTURES / "cmb_perso_sample.csv", account="CMB Perso")
        assert all(tx.amount >= 0 for tx in txs)

    def test_ech_pret_is_expense(self):
        txs = parse_cmb(FIXTURES / "cmb_commun_sample.csv", account="CMB Commun")
        pret = next(tx for tx in txs if "ECH PRET" in tx.raw_label)
        assert pret.type == TransactionType.WITHDRAWAL
        assert pret.amount == Decimal("350.56")

    def test_vir_de_compte_is_income(self):
        txs = parse_cmb(FIXTURES / "cmb_commun_sample.csv", account="CMB Commun")
        vir = next(tx for tx in txs if "VIR de COMPTE" in tx.raw_label)
        assert vir.type == TransactionType.DEPOSIT


class TestParseFortuneoFromCsv:
    def test_parses_five_rows(self):
        txs = parse_fortuneo(FIXTURES / "fortuneo_sample.csv", account="Fortuneo")
        assert len(txs) == 5

    def test_negative_debit_becomes_expense(self):
        txs = parse_fortuneo(FIXTURES / "fortuneo_sample.csv", account="Fortuneo")
        supermarche = next(tx for tx in txs if "SUPERMARCHE" in tx.raw_label)
        assert supermarche.type == TransactionType.WITHDRAWAL
        assert supermarche.amount == Decimal("40.03")

    def test_credit_is_income(self):
        txs = parse_fortuneo(FIXTURES / "fortuneo_sample.csv", account="Fortuneo")
        vir = next(tx for tx in txs if "PARTENAIRE" in tx.raw_label)
        assert vir.type == TransactionType.DEPOSIT
        assert vir.amount == Decimal("2000")

    def test_credit_with_leading_space(self):
        txs = parse_fortuneo(FIXTURES / "fortuneo_sample.csv", account="Fortuneo")
        vir = next(tx for tx in txs if "PARTENAIRE" in tx.raw_label)
        assert vir.amount == Decimal("2000")

    def test_ann_carte_is_income(self):
        txs = parse_fortuneo(FIXTURES / "fortuneo_sample.csv", account="Fortuneo")
        ann = next(tx for tx in txs if "ANN CARTE" in tx.raw_label)
        assert ann.type == TransactionType.DEPOSIT
        assert ann.amount == Decimal("41.98")

    def test_amounts_always_positive(self):
        txs = parse_fortuneo(FIXTURES / "fortuneo_sample.csv", account="Fortuneo")
        assert all(tx.amount >= 0 for tx in txs)

    def test_dates_are_date_objects(self):
        txs = parse_fortuneo(FIXTURES / "fortuneo_sample.csv", account="Fortuneo")
        assert all(isinstance(tx.date, date) for tx in txs)

    def test_source_name_matches_argument(self):
        txs = parse_fortuneo(FIXTURES / "fortuneo_sample.csv", account="Fortuneo")
        assert all(tx.source_name == "Fortuneo" for tx in txs)


class TestParseFortuneoFromZip:
    def test_zip_produces_same_result_as_csv(self):
        from_csv = parse_fortuneo(FIXTURES / "fortuneo_sample.csv", account="Fortuneo")
        from_zip = parse_fortuneo(FIXTURES / "fortuneo_sample.zip", account="Fortuneo")
        assert len(from_zip) == len(from_csv)
        for a, b in zip(from_zip, from_csv, strict=True):
            assert a.date == b.date
            assert a.raw_label == b.raw_label
            assert a.amount == b.amount
            assert a.type == b.type
