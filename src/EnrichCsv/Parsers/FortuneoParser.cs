using System.Globalization;
using System.IO.Compression;
using System.Text;
using CsvHelper;
using CsvHelper.Configuration;
using EnrichCsv.Models;
using EnrichCsv.Normalizer;

namespace EnrichCsv.Parsers;

public sealed class FortuneoParser : IBankParser
{
    public string BankKey => "fortuneo";

    public IReadOnlyList<Transaction> Parse(FileInfo file, string account)
    {
        byte[] content;
        if (file.Extension.Equals(".zip", StringComparison.OrdinalIgnoreCase))
        {
            using var zip = ZipFile.OpenRead(file.FullName);
            var entry = zip.Entries.First(e =>
                e.Name.EndsWith(".csv", StringComparison.OrdinalIgnoreCase)
            );
            using var stream = entry.Open();
            using var ms = new MemoryStream();
            stream.CopyTo(ms);
            content = ms.ToArray();
        }
        else
        {
            content = File.ReadAllBytes(file.FullName);
        }

        return ParseContent(content, account);
    }

    static FortuneoParser() => Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);

    private static IReadOnlyList<Transaction> ParseContent(byte[] content, string account)
    {
        var text = Encoding.GetEncoding(1252).GetString(content);

        using var reader = new StringReader(text);
        using var csv = new CsvReader(
            reader,
            new CsvConfiguration(CultureInfo.InvariantCulture)
            {
                Delimiter = ";",
                HasHeaderRecord = true,
            }
        );

        var transactions = new List<Transaction>();
        csv.Read();
        csv.ReadHeader();

        while (csv.Read())
        {
            var rawDate = csv.GetField(0) ?? "";
            var label = (csv.GetField(2) ?? "").Trim();
            var debitStr = (csv.GetField(3) ?? "").Trim();
            var creditStr = (csv.GetField(4) ?? "").Trim();

            if (string.IsNullOrWhiteSpace(rawDate) && string.IsNullOrWhiteSpace(label))
                continue;
            if (string.IsNullOrWhiteSpace(debitStr) && string.IsNullOrWhiteSpace(creditStr))
                continue;

            decimal amount;
            TransactionType type;

            if (!string.IsNullOrWhiteSpace(debitStr))
            {
                amount = Math.Abs(ParseFrenchDecimal(debitStr));
                type = TransactionType.Expense;
            }
            else
            {
                amount = ParseFrenchDecimal(creditStr);
                type = TransactionType.Income;
            }

            transactions.Add(
                new Transaction(
                    date: DateOnly.ParseExact(
                        rawDate.Trim(),
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

    private static decimal ParseFrenchDecimal(string value) =>
        decimal.Parse(
            value.Trim().Replace(" ", "").Replace(" ", "").Replace(",", "."),
            CultureInfo.InvariantCulture
        );
}
