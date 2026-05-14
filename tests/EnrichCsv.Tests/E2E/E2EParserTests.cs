using System.Diagnostics.CodeAnalysis;
using EnrichCsv.Models;
using EnrichCsv.Parsers;
using FluentAssertions;

namespace EnrichCsv.Tests.E2E;

[Trait("Category", "e2e")]
public sealed class E2EParserTests
{
    private static FileInfo? DecodeSecret(string envVar)
    {
        var value = Environment.GetEnvironmentVariable(envVar);
        if (string.IsNullOrEmpty(value))
            return null;

        var suffix = envVar.Contains("ZIP") ? ".zip" : ".csv";
        var tmp = Path.GetTempFileName() + suffix;
        File.WriteAllBytes(tmp, Convert.FromBase64String(value));
        return new FileInfo(tmp);
    }

    private static void AssertTransactionsValid(IReadOnlyList<Transaction> transactions)
    {
        transactions.Should().NotBeEmpty();
        foreach (var tx in transactions)
        {
            tx.Amount.Should().BeGreaterThanOrEqualTo(0);
            tx.SourceAccount.Should().NotBeEmpty();
            tx.RawLabel.Should().NotBeEmpty();
        }
    }

    [SkippableFact]
    public void CmbPerso_FullParse()
    {
        var file = DecodeSecret("E2E_CMB_PERSO_CSV");
        Skip.If(file is null, "E2E_CMB_PERSO_CSV not set");
        try
        {
            var transactions = new CmbParser().Parse(file!, "CMB Perso");
            AssertTransactionsValid(transactions);
        }
        finally
        {
            file?.Delete();
        }
    }

    [SkippableFact]
    public void CmbCommun_FullParse()
    {
        var file = DecodeSecret("E2E_CMB_COMMUN_CSV");
        Skip.If(file is null, "E2E_CMB_COMMUN_CSV not set");
        try
        {
            var transactions = new CmbParser().Parse(file!, "CMB Commun");
            AssertTransactionsValid(transactions);
        }
        finally
        {
            file?.Delete();
        }
    }

    [SkippableFact]
    public void Fortuneo_FullParse()
    {
        var file = DecodeSecret("E2E_FORTUNEO_ZIP");
        Skip.If(file is null, "E2E_FORTUNEO_ZIP not set");
        try
        {
            var transactions = new FortuneoParser().Parse(file!, "Fortuneo");
            AssertTransactionsValid(transactions);
        }
        finally
        {
            file?.Delete();
        }
    }
}
