using EnrichCsv.Models;

namespace EnrichCsv.Parsers;

public interface IBankParser
{
    string BankKey { get; }
    IReadOnlyList<Transaction> Parse(FileInfo file, string account);
}
