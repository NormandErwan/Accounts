using EnrichCsv.Models;
using EnrichCsv.Parsers;
using FluentAssertions;

namespace EnrichCsv.Tests.Parsers;

public sealed class ParserTests : IDisposable
{
    private readonly DirectoryInfo _dir = Directory.CreateTempSubdirectory("enrich_csv_test_");

    public void Dispose() => _dir.Delete(recursive: true);

    private FileInfo ExtractFixture(string name)
    {
        var assembly = typeof(ParserTests).Assembly;
        var resourceName = assembly
            .GetManifestResourceNames()
            .First(n => n.EndsWith(name, StringComparison.OrdinalIgnoreCase));

        var dest = new FileInfo(Path.Combine(_dir.FullName, name));
        using var stream = assembly.GetManifestResourceStream(resourceName)!;
        using var file = dest.OpenWrite();
        stream.CopyTo(file);
        return dest;
    }

    // ---- CmbParser ----

    [Fact]
    public void Cmb_ParsesFiveRows()
    {
        var txs = new CmbParser().Parse(ExtractFixture("cmb_perso_sample.csv"), "CMB Perso");
        txs.Should().HaveCount(5);
    }

    [Fact]
    public void Cmb_SourceNameMatchesArgument()
    {
        var txs = new CmbParser().Parse(ExtractFixture("cmb_perso_sample.csv"), "Mon Compte");
        txs.Should().AllSatisfy(tx => tx.SourceAccount.Should().Be("Mon Compte"));
    }

    [Fact]
    public void Cmb_DebitRowIsExpense()
    {
        var txs = new CmbParser().Parse(ExtractFixture("cmb_perso_sample.csv"), "CMB Perso");
        var prlv = txs.First(tx => tx.RawLabel.Contains("OPERATEUR MOBILE"));
        prlv.Type.Should().Be(TransactionType.Expense);
        prlv.Amount.Should().Be(9.99m);
    }

    [Fact]
    public void Cmb_CreditRowIsIncome()
    {
        var txs = new CmbParser().Parse(ExtractFixture("cmb_perso_sample.csv"), "CMB Perso");
        var vir = txs.First(tx => tx.RawLabel.Contains("EMPLOYEUR"));
        vir.Type.Should().Be(TransactionType.Income);
        vir.Amount.Should().Be(2000.00m);
    }

    [Fact]
    public void Cmb_TransferDetection()
    {
        var txs = new CmbParser().Parse(ExtractFixture("cmb_perso_sample.csv"), "CMB Perso");
        var transfer = txs.First(tx => tx.RawLabel.Contains("COMPTE COMMUN"));
        transfer.Type.Should().Be(TransactionType.Transfer);
    }

    [Fact]
    public void Cmb_RefundIsIncome()
    {
        var txs = new CmbParser().Parse(ExtractFixture("cmb_perso_sample.csv"), "CMB Perso");
        var ann = txs.First(tx => tx.RawLabel.Contains("ANN CARTE"));
        ann.Type.Should().Be(TransactionType.Income);
        ann.Amount.Should().Be(12.00m);
    }

    [Fact]
    public void Cmb_DatesAreDateOnly()
    {
        var txs = new CmbParser().Parse(ExtractFixture("cmb_perso_sample.csv"), "CMB Perso");
        txs.Should().AllSatisfy(tx => tx.Date.Should().NotBe(default(DateOnly)));
    }

    [Fact]
    public void Cmb_DateParsedCorrectly()
    {
        var txs = new CmbParser().Parse(ExtractFixture("cmb_perso_sample.csv"), "CMB Perso");
        var prlv = txs.First(tx => tx.RawLabel.Contains("OPERATEUR MOBILE"));
        prlv.Date.Should().Be(new DateOnly(2026, 1, 15));
    }

    [Fact]
    public void Cmb_AmountsAlwaysPositive()
    {
        var txs = new CmbParser().Parse(ExtractFixture("cmb_perso_sample.csv"), "CMB Perso");
        txs.Should().AllSatisfy(tx => tx.Amount.Should().BeGreaterThanOrEqualTo(0));
    }

    [Fact]
    public void Cmb_EchPretIsExpense()
    {
        var txs = new CmbParser().Parse(ExtractFixture("cmb_commun_sample.csv"), "CMB Commun");
        var pret = txs.First(tx => tx.RawLabel.Contains("ECH PRET"));
        pret.Type.Should().Be(TransactionType.Expense);
        pret.Amount.Should().Be(350.56m);
    }

    [Fact]
    public void Cmb_VirDeCompteIsIncome()
    {
        var txs = new CmbParser().Parse(ExtractFixture("cmb_commun_sample.csv"), "CMB Commun");
        var vir = txs.First(tx => tx.RawLabel.Contains("VIR de COMPTE"));
        vir.Type.Should().Be(TransactionType.Income);
    }

    // ---- FortuneoParser (CSV) ----

    [Fact]
    public void Fortuneo_ParsesFiveRowsFromCsv()
    {
        var txs = new FortuneoParser().Parse(ExtractFixture("fortuneo_sample.csv"), "Fortuneo");
        txs.Should().HaveCount(5);
    }

    [Fact]
    public void Fortuneo_NegativeDebitBecomesExpense()
    {
        var txs = new FortuneoParser().Parse(ExtractFixture("fortuneo_sample.csv"), "Fortuneo");
        var supermarche = txs.First(tx => tx.RawLabel.Contains("SUPERMARCHE"));
        supermarche.Type.Should().Be(TransactionType.Expense);
        supermarche.Amount.Should().Be(40.03m);
    }

    [Fact]
    public void Fortuneo_CreditIsIncome()
    {
        var txs = new FortuneoParser().Parse(ExtractFixture("fortuneo_sample.csv"), "Fortuneo");
        var vir = txs.First(tx => tx.RawLabel.Contains("PARTENAIRE"));
        vir.Type.Should().Be(TransactionType.Income);
        vir.Amount.Should().Be(2000m);
    }

    [Fact]
    public void Fortuneo_AnnCarteIsIncome()
    {
        var txs = new FortuneoParser().Parse(ExtractFixture("fortuneo_sample.csv"), "Fortuneo");
        var ann = txs.First(tx => tx.RawLabel.Contains("ANN CARTE"));
        ann.Type.Should().Be(TransactionType.Income);
        ann.Amount.Should().Be(41.98m);
    }

    [Fact]
    public void Fortuneo_AmountsAlwaysPositive()
    {
        var txs = new FortuneoParser().Parse(ExtractFixture("fortuneo_sample.csv"), "Fortuneo");
        txs.Should().AllSatisfy(tx => tx.Amount.Should().BeGreaterThanOrEqualTo(0));
    }

    [Fact]
    public void Fortuneo_SourceNameMatchesArgument()
    {
        var txs = new FortuneoParser().Parse(ExtractFixture("fortuneo_sample.csv"), "Fortuneo");
        txs.Should().AllSatisfy(tx => tx.SourceAccount.Should().Be("Fortuneo"));
    }

    [Fact]
    public void Cmb_SkipsFooterRowWithEmptyDebitAndCredit()
    {
        var csv =
            "\"Date operation\";\"Date valeur\";\"Libelle\";\"Debit\";\"Credit\"\n"
            + "\"15/01/2026\";\"15/01/2026\";\"PRLV OPERATEUR MOBILE\";\"9,99\";\"\"\n"
            + "\"\";\"\";\"Solde au 15/01/2026\";\"\";\"\"\n";
        var file = new FileInfo(Path.Combine(_dir.FullName, "cmb_footer.csv"));
        File.WriteAllText(file.FullName, csv, System.Text.Encoding.UTF8);
        var txs = new CmbParser().Parse(file, "CMB Perso");
        txs.Should().HaveCount(1);
    }

    [Fact]
    public void Fortuneo_SkipsFooterRowWithEmptyDebitAndCredit()
    {
        var csv =
            "Date opération;Date valeur;libellé;Débit;Crédit;\n"
            + "30/01/2026;30/01/2026;VIR INST PARTENAIRE;; 2000;\n"
            + ";; Solde final ;;;\n";
        var file = new FileInfo(Path.Combine(_dir.FullName, "fortuneo_footer.csv"));
        File.WriteAllText(file.FullName, csv, System.Text.Encoding.UTF8);
        var txs = new FortuneoParser().Parse(file, "Fortuneo");
        txs.Should().HaveCount(1);
    }

    // ---- FortuneoParser (ZIP) ----

    [Fact]
    public void Fortuneo_ZipProducesSameResultAsCsv()
    {
        var fromCsv = new FortuneoParser().Parse(ExtractFixture("fortuneo_sample.csv"), "Fortuneo");
        var fromZip = new FortuneoParser().Parse(ExtractFixture("fortuneo_sample.zip"), "Fortuneo");

        fromZip.Should().HaveCount(fromCsv.Count);
        for (var i = 0; i < fromCsv.Count; i++)
        {
            fromZip[i].Date.Should().Be(fromCsv[i].Date);
            fromZip[i].RawLabel.Should().Be(fromCsv[i].RawLabel);
            fromZip[i].Amount.Should().Be(fromCsv[i].Amount);
            fromZip[i].Type.Should().Be(fromCsv[i].Type);
        }
    }
}
