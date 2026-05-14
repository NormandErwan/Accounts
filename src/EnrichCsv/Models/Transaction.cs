namespace EnrichCsv.Models;

public sealed record Transaction
{
    public DateOnly Date { get; init; }
    public string RawLabel { get; init; }
    public string CleanLabel { get; init; }
    public decimal Amount { get; init; }
    public TransactionType Type { get; init; }
    public string SourceAccount { get; init; }
    public string DestinationAccount { get; init; } = "";
    public string Category { get; init; } = "";

    public Transaction(
        DateOnly date,
        string rawLabel,
        string cleanLabel,
        decimal amount,
        TransactionType type,
        string sourceAccount,
        string destinationAccount = "",
        string category = ""
    )
    {
        if (amount < 0)
            throw new ArgumentOutOfRangeException(nameof(amount), "amount must be >= 0");
        if (string.IsNullOrWhiteSpace(sourceAccount))
            throw new ArgumentException(
                "sourceAccount must be a non-empty string",
                nameof(sourceAccount)
            );

        Date = date;
        RawLabel = rawLabel;
        CleanLabel = cleanLabel;
        Amount = amount;
        Type = type;
        SourceAccount = sourceAccount;
        DestinationAccount = destinationAccount;
        Category = category;
    }
}
