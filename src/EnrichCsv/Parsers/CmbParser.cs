using System.Globalization;
using CsvHelper;
using CsvHelper.Configuration;
using CsvHelper.TypeConversion;
using EnrichCsv.Models;
using EnrichCsv.Normalizer;

namespace EnrichCsv.Parsers;

public sealed class CmbParser : IBankParser
{
    private static readonly string[] TransferKeywords = ["vers ", "WERO", "COMPTE COMMUN"];

    public string BankKey => "cmb";

    public IReadOnlyList<Transaction> Parse(FileInfo file, string account)
    {
        using var reader = new StreamReader(file.FullName, System.Text.Encoding.UTF8);
        using var csv = new CsvReader(
            reader,
            new CsvConfiguration(CultureInfo.InvariantCulture)
            {
                Delimiter = ";",
                HasHeaderRecord = true,
            }
        );
        csv.Context.RegisterClassMap<CmbRowMap>();

        var transactions = new List<Transaction>();
        foreach (var row in csv.GetRecords<CmbRow>())
        {
            var label = row.Label.Trim();
            if (string.IsNullOrWhiteSpace(row.Debit) && string.IsNullOrWhiteSpace(row.Credit))
                continue;

            decimal amount;
            TransactionType type;

            if (!string.IsNullOrWhiteSpace(row.Debit))
            {
                amount = ParseFrenchDecimal(row.Debit);
                type = IsTransfer(label) ? TransactionType.Transfer : TransactionType.Expense;
            }
            else
            {
                amount = ParseFrenchDecimal(row.Credit);
                type = TransactionType.Income;
            }

            transactions.Add(
                new Transaction(
                    date: DateOnly.ParseExact(
                        row.Date.Trim(),
                        "dd/MM/yyyy",
                        CultureInfo.InvariantCulture
                    ),
                    rawLabel: label,
                    cleanLabel: LabelNormalizer.NormalizeLabel(label),
                    amount: amount,
                    type: type,
                    sourceAccount: account
                )
            );
        }
        return transactions;
    }

    private static bool IsTransfer(string label) =>
        TransferKeywords.Any(kw => label.Contains(kw, StringComparison.Ordinal));

    private static decimal ParseFrenchDecimal(string value) =>
        decimal.Parse(
            value.Trim().Replace(" ", "").Replace(" ", "").Replace(",", "."),
            CultureInfo.InvariantCulture
        );

    private sealed class CmbRow
    {
        public string Date { get; set; } = "";
        public string DateValeur { get; set; } = "";
        public string Label { get; set; } = "";
        public string Debit { get; set; } = "";
        public string Credit { get; set; } = "";
    }

    private sealed class CmbRowMap : ClassMap<CmbRow>
    {
        public CmbRowMap()
        {
            Map(m => m.Date).Index(0);
            Map(m => m.DateValeur).Index(1);
            Map(m => m.Label).Index(2);
            Map(m => m.Debit).Index(3);
            Map(m => m.Credit).Index(4);
        }
    }
}
