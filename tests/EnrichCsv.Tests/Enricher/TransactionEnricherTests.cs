using EnrichCsv.Api;
using EnrichCsv.Config;
using EnrichCsv.Enricher;
using EnrichCsv.Models;
using FluentAssertions;
using NSubstitute;

namespace EnrichCsv.Tests.Enricher;

public sealed class TransactionEnricherTests : IDisposable
{
    private readonly DirectoryInfo _dir = Directory.CreateTempSubdirectory("enrich_csv_test_");
    private readonly ISireneClient _sireneClient = Substitute.For<ISireneClient>();
    private readonly IUserPrompt _userPrompt = Substitute.For<IUserPrompt>();

    public void Dispose() => _dir.Delete(recursive: true);

    private CacheStore MakeCacheStore(string name = "cache.json") =>
        new(new FileInfo(Path.Combine(_dir.FullName, name)));

    private static Transaction MakeTx(
        string rawLabel = "PRLV OPERATEUR MOBILE",
        string cleanLabel = "OPERATEUR MOBILE",
        TransactionType type = TransactionType.Expense
    ) => new(new DateOnly(2026, 1, 15), rawLabel, cleanLabel, 9.99m, type, "CMB Perso");

    private CacheStore KnownCacheStore()
    {
        var store = MakeCacheStore();
        var cache = store.Load();
        store.Store(cache, "OPERATEUR MOBILE", "Opérateur Mobile", "Abonnements");
        store.Save(cache);
        return store;
    }

    [Fact]
    public async Task Enrich_DoesNotMutateInputTransaction()
    {
        var store = KnownCacheStore();
        var enricher = new TransactionEnricher(_sireneClient, _userPrompt, store);
        var tx = MakeTx();

        var result = await enricher.EnrichAsync([tx]);

        tx.DestinationAccount.Should().BeEmpty("input was mutated");
        tx.Category.Should().BeEmpty("input was mutated");
        result[0].Should().NotBeSameAs(tx, "must return a new instance");
    }

    [Fact]
    public async Task Enrich_KnownDestination_EnrichesValues()
    {
        var store = KnownCacheStore();
        var enricher = new TransactionEnricher(_sireneClient, _userPrompt, store);

        var result = await enricher.EnrichAsync([MakeTx()]);

        result[0].DestinationAccount.Should().Be("Opérateur Mobile");
        result[0].Category.Should().Be("Abonnements");
    }

    [Fact]
    public async Task Enrich_Transfer_IsNotEnriched()
    {
        var store = KnownCacheStore();
        var enricher = new TransactionEnricher(_sireneClient, _userPrompt, store);
        var tx = MakeTx(
            rawLabel: "VIR INST vers COMPTE COMMUN",
            cleanLabel: "COMPTE COMMUN",
            type: TransactionType.Transfer
        );

        var result = await enricher.EnrichAsync([tx]);

        result[0].DestinationAccount.Should().BeEmpty();
        result[0].Category.Should().BeEmpty();
    }

    [Fact]
    public async Task Enrich_Interactive_WithApiResult()
    {
        var store = MakeCacheStore();
        var cache = store.Load();
        store.Store(cache, "_SEED_", "seed", "Abonnements");
        store.Save(cache);

        var apiResult = new SireneResult
        {
            Name = "Bouygues Telecom SA",
            Naf = "61.20",
            Siren = "397480930",
        };
        _sireneClient
            .SearchCompanyAsync(Arg.Any<string>(), Arg.Any<CancellationToken>())
            .Returns(apiResult);
        _userPrompt.AskDestinationAccount(Arg.Any<string>()).Returns("Bouygues Telecom");
        _userPrompt
            .AskCategory(Arg.Any<IReadOnlyList<string>>(), Arg.Any<string>())
            .Returns("Abonnements");

        var enricher = new TransactionEnricher(_sireneClient, _userPrompt, store);
        var tx = MakeTx(rawLabel: "PRLV BOUYGUES TELECOM", cleanLabel: "BOUYGUES TELECOM");

        var result = await enricher.EnrichAsync([tx]);

        result[0].DestinationAccount.Should().Be("Bouygues Telecom");
        result[0].Category.Should().Be("Abonnements");
    }

    [Fact]
    public async Task Enrich_Interactive_WithoutApiResult()
    {
        var store = MakeCacheStore();
        var cache = store.Load();
        store.Store(cache, "_SEED_", "seed", "Courses");
        store.Save(cache);

        _sireneClient
            .SearchCompanyAsync(Arg.Any<string>(), Arg.Any<CancellationToken>())
            .Returns((SireneResult?)null);
        _userPrompt.AskDestinationAccount(Arg.Any<string>()).Returns("Épicerie du coin");
        _userPrompt
            .AskCategory(Arg.Any<IReadOnlyList<string>>(), Arg.Any<string>())
            .Returns("Courses");

        var enricher = new TransactionEnricher(_sireneClient, _userPrompt, store);
        var tx = MakeTx(rawLabel: "CARTE 10/01 EPICERIE", cleanLabel: "EPICERIE");

        var result = await enricher.EnrichAsync([tx]);

        result[0].DestinationAccount.Should().Be("Épicerie du coin");
        result[0].Category.Should().Be("Courses");
    }

    [Fact]
    public async Task Enrich_Interactive_NewCategory_IsPersisted()
    {
        var store = MakeCacheStore();
        _sireneClient
            .SearchCompanyAsync(Arg.Any<string>(), Arg.Any<CancellationToken>())
            .Returns((SireneResult?)null);
        _userPrompt.AskDestinationAccount(Arg.Any<string>()).Returns("Test Shop");
        _userPrompt
            .AskCategory(Arg.Any<IReadOnlyList<string>>(), Arg.Any<string>())
            .Returns("Vacances");

        var enricher = new TransactionEnricher(_sireneClient, _userPrompt, store);
        await enricher.EnrichAsync([
            MakeTx(rawLabel: "CARTE 10/01 TEST SHOP", cleanLabel: "TEST SHOP"),
        ]);

        var reloaded = store.Load();
        reloaded.Destinations.Should().ContainKey("TEST SHOP");
        reloaded.Destinations["TEST SHOP"].Category.Should().Be("Vacances");
    }

    [Fact]
    public async Task Enrich_Interactive_Skip_LeavesUnenriched()
    {
        var store = MakeCacheStore();
        _sireneClient
            .SearchCompanyAsync(Arg.Any<string>(), Arg.Any<CancellationToken>())
            .Returns((SireneResult?)null);
        _userPrompt.AskCategory(Arg.Any<IReadOnlyList<string>>(), Arg.Any<string>()).Returns("");

        var enricher = new TransactionEnricher(_sireneClient, _userPrompt, store);
        var result = await enricher.EnrichAsync([
            MakeTx(rawLabel: "CARTE 10/01 MYSTERE", cleanLabel: "MYSTERE"),
        ]);

        result[0].DestinationAccount.Should().BeEmpty();
        result[0].Category.Should().BeEmpty();
        _userPrompt.DidNotReceive().AskDestinationAccount(Arg.Any<string>());
    }
}
