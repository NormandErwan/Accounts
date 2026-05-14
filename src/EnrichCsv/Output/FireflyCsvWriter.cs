using System.Globalization;
using CsvHelper;
using CsvHelper.Configuration;
using CsvHelper.Configuration.Attributes;
using EnrichCsv.Models;

namespace EnrichCsv.Output;

public sealed class FireflyCsvWriter
{
    public string Write(IReadOnlyList<Transaction> transactions)
    {
        using var writer = new StringWriter();
        using var csv = new CsvWriter(
            writer,
            new CsvConfiguration(CultureInfo.InvariantCulture) { NewLine = "\n" }
        );

        csv.WriteHeader<FireflyRow>();
        csv.NextRecord();

        foreach (var tx in transactions)
        {
            csv.WriteRecord(ToRow(tx));
            csv.NextRecord();
        }

        return writer.ToString();
    }

    private static FireflyRow ToRow(Transaction tx) =>
        new()
        {
            Date = tx.Date.ToString("yyyy-MM-dd"),
            Description = tx.RawLabel,
            Amount = tx.Amount.ToString("F2", CultureInfo.InvariantCulture),
            CurrencyCode = "EUR",
            SourceName = tx.SourceAccount,
            DestinationName = tx.Type != TransactionType.Income ? tx.DestinationAccount : "",
            Category = tx.Category,
            Type = tx.Type.ToFireflyValue(),
        };

    private sealed class FireflyRow
    {
        [Name("date")]
        public string Date { get; init; } = "";

        [Name("description")]
        public string Description { get; init; } = "";

        [Name("amount")]
        public string Amount { get; init; } = "";

        [Name("currency_code")]
        public string CurrencyCode { get; init; } = "";

        [Name("source_name")]
        public string SourceName { get; init; } = "";

        [Name("destination_name")]
        public string DestinationName { get; init; } = "";

        [Name("category")]
        public string Category { get; init; } = "";

        [Name("type")]
        public string Type { get; init; } = "";
    }
}
