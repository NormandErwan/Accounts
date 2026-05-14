using System.Globalization;
using CsvHelper;
using EnrichCsv.Models;
using EnrichCsv.Output;
using FluentAssertions;

namespace EnrichCsv.Tests.Output;

public sealed class FireflyCsvWriterTests
{
    private readonly FireflyCsvWriter _writer = new();

    private static Transaction MakeTransaction(
        DateOnly? date = null,
        string rawLabel = "PRLV OPERATEUR MOBILE",
        string cleanLabel = "OPERATEUR MOBILE",
        decimal amount = 9.99m,
        TransactionType type = TransactionType.Expense,
        string sourceAccount = "CMB Perso",
        string destinationAccount = "Opérateur Mobile",
        string category = "Abonnements"
    ) =>
        new(
            date ?? new DateOnly(2026, 1, 15),
            rawLabel,
            cleanLabel,
            amount,
            type,
            sourceAccount,
            destinationAccount,
            category
        );

    private static List<Dictionary<string, string>> ParseCsv(string csv)
    {
        using var reader = new StringReader(csv);
        using var csvReader = new CsvReader(reader, CultureInfo.InvariantCulture);
        var rows = new List<Dictionary<string, string>>();
        csvReader.Read();
        csvReader.ReadHeader();
        var headers = csvReader.HeaderRecord!;
        while (csvReader.Read())
        {
            var row = new Dictionary<string, string>();
            foreach (var h in headers)
                row[h] = csvReader.GetField(h) ?? "";
            rows.Add(row);
        }
        return rows;
    }

    [Fact]
    public void Headers_AreCorrect()
    {
        var result = _writer.Write([MakeTransaction()]);
        result
            .Should()
            .StartWith(
                "date,description,amount,currency_code,source_name,destination_name,category,type"
            );
    }

    [Fact]
    public void ExpenseType_MapsToWithdrawal()
    {
        var rows = ParseCsv(_writer.Write([MakeTransaction(type: TransactionType.Expense)]));
        rows[0]["type"].Should().Be("withdrawal");
    }

    [Fact]
    public void IncomeType_MapsToDeposit()
    {
        var rows = ParseCsv(_writer.Write([MakeTransaction(type: TransactionType.Income)]));
        rows[0]["type"].Should().Be("deposit");
    }

    [Fact]
    public void TransferType_MapsToTransfer()
    {
        var rows = ParseCsv(_writer.Write([MakeTransaction(type: TransactionType.Transfer)]));
        rows[0]["type"].Should().Be("transfer");
    }

    [Fact]
    public void Date_IsIsoFormat()
    {
        var rows = ParseCsv(_writer.Write([MakeTransaction(date: new DateOnly(2026, 5, 9))]));
        rows[0]["date"].Should().Be("2026-05-09");
    }

    [Fact]
    public void Amount_HasTwoDecimals()
    {
        var rows = ParseCsv(_writer.Write([MakeTransaction(amount: 9.9m)]));
        rows[0]["amount"].Should().Be("9.90");
    }

    [Fact]
    public void CurrencyCode_IsEur()
    {
        var rows = ParseCsv(_writer.Write([MakeTransaction()]));
        rows[0]["currency_code"].Should().Be("EUR");
    }

    [Fact]
    public void SourceName_IsAccount()
    {
        var rows = ParseCsv(_writer.Write([MakeTransaction(sourceAccount: "CMB Perso")]));
        rows[0]["source_name"].Should().Be("CMB Perso");
    }

    [Fact]
    public void DestinationName_ForExpense()
    {
        var rows = ParseCsv(
            _writer.Write([
                MakeTransaction(type: TransactionType.Expense, destinationAccount: "Carrefour"),
            ])
        );
        rows[0]["destination_name"].Should().Be("Carrefour");
    }

    [Fact]
    public void DestinationName_EmptyForIncome()
    {
        var rows = ParseCsv(_writer.Write([MakeTransaction(type: TransactionType.Income)]));
        rows[0]["destination_name"].Should().BeEmpty();
    }

    [Fact]
    public void DestinationName_ForTransfer()
    {
        var rows = ParseCsv(
            _writer.Write([
                MakeTransaction(
                    type: TransactionType.Transfer,
                    destinationAccount: "Compte Commun"
                ),
            ])
        );
        rows[0]["destination_name"].Should().Be("Compte Commun");
    }

    [Fact]
    public void Description_IsRawLabel()
    {
        var rows = ParseCsv(_writer.Write([MakeTransaction(rawLabel: "PRLV OPERATEUR MOBILE")]));
        rows[0]["description"].Should().Be("PRLV OPERATEUR MOBILE");
    }

    [Fact]
    public void Category_IsPreserved()
    {
        var rows = ParseCsv(_writer.Write([MakeTransaction(category: "Santé")]));
        rows[0]["category"].Should().Be("Santé");
    }

    [Fact]
    public void MultipleTransactions_AllWritten()
    {
        var txs = new[] { MakeTransaction(), MakeTransaction(amount: 50m, category: "Courses") };
        var rows = ParseCsv(_writer.Write(txs));
        rows.Should().HaveCount(2);
    }

    [Fact]
    public void FrenchChars_PreservedInOutput()
    {
        var result = _writer.Write([
            MakeTransaction(destinationAccount: "Café de la Paix", category: "Loisirs"),
        ]);
        result.Should().Contain("Café de la Paix");
    }

    [Fact]
    public void EmptyList_HasOnlyHeader()
    {
        var result = _writer.Write([]);
        ParseCsv(result).Should().BeEmpty();
    }
}
