namespace EnrichCsv.Models;

public enum TransactionType
{
    Expense,
    Income,
    Transfer,
}

public static class TransactionTypeExtensions
{
    public static string ToFireflyValue(this TransactionType type) =>
        type switch
        {
            TransactionType.Expense => "withdrawal",
            TransactionType.Income => "deposit",
            TransactionType.Transfer => "transfer",
            _ => throw new ArgumentOutOfRangeException(nameof(type), type, null),
        };
}
