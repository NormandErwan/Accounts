using EnrichCsv.Models;
using FluentAssertions;

namespace EnrichCsv.Tests.Models;

public sealed class TransactionTests
{
    private static Transaction MakeTransaction(
        DateOnly? date = null,
        string rawLabel = "PRLV OPERATEUR MOBILE",
        string cleanLabel = "OPERATEUR MOBILE",
        decimal amount = 9.99m,
        TransactionType type = TransactionType.Expense,
        string sourceAccount = "CMB Perso",
        string destinationAccount = "",
        string category = ""
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

    [Fact]
    public void ValidTransaction_HasExpectedValues()
    {
        var tx = MakeTransaction();
        tx.Amount.Should().Be(9.99m);
        tx.Type.Should().Be(TransactionType.Expense);
        tx.DestinationAccount.Should().BeEmpty();
        tx.Category.Should().BeEmpty();
    }

    [Fact]
    public void ValidTransaction_WithCategory()
    {
        var tx = MakeTransaction(destinationAccount: "Opérateur Mobile", category: "Abonnements");
        tx.DestinationAccount.Should().Be("Opérateur Mobile");
        tx.Category.Should().Be("Abonnements");
    }

    [Theory]
    [InlineData(TransactionType.Expense)]
    [InlineData(TransactionType.Income)]
    [InlineData(TransactionType.Transfer)]
    public void AllTransactionTypes_AreValid(TransactionType type)
    {
        var tx = MakeTransaction(type: type);
        tx.Type.Should().Be(type);
    }

    [Theory]
    [InlineData(TransactionType.Expense, "withdrawal")]
    [InlineData(TransactionType.Income, "deposit")]
    [InlineData(TransactionType.Transfer, "transfer")]
    public void TransactionType_FireflyValues(TransactionType type, string expected)
    {
        type.ToFireflyValue().Should().Be(expected);
    }

    [Fact]
    public void NegativeAmount_Throws()
    {
        var act = () => MakeTransaction(amount: -1.00m);
        act.Should().Throw<ArgumentOutOfRangeException>();
    }

    [Fact]
    public void ZeroAmount_IsAllowed()
    {
        var tx = MakeTransaction(amount: 0m);
        tx.Amount.Should().Be(0m);
    }

    [Fact]
    public void EmptySourceAccount_Throws()
    {
        var act = () => MakeTransaction(sourceAccount: "");
        act.Should().Throw<ArgumentException>().WithMessage("*non-empty*");
    }

    [Fact]
    public void WhitespaceSourceAccount_Throws()
    {
        var act = () => MakeTransaction(sourceAccount: "   ");
        act.Should().Throw<ArgumentException>().WithMessage("*non-empty*");
    }

    [Fact]
    public void FrenchSourceAccount_IsAllowed()
    {
        var tx = MakeTransaction(sourceAccount: "Compte Épargne Logement");
        tx.SourceAccount.Should().Be("Compte Épargne Logement");
    }

    [Fact]
    public void EmptyCategory_IsAllowed()
    {
        var tx = MakeTransaction(category: "");
        tx.Category.Should().BeEmpty();
    }

    [Fact]
    public void FrenchCategory_IsPreserved()
    {
        var tx = MakeTransaction(category: "Vacances");
        tx.Category.Should().Be("Vacances");
    }

    [Fact]
    public void WithExpression_ReturnsNewInstance()
    {
        var tx = MakeTransaction();
        var enriched = tx with { DestinationAccount = "Test", Category = "Courses" };
        enriched.Should().NotBeSameAs(tx);
        tx.DestinationAccount.Should().BeEmpty();
    }
}
