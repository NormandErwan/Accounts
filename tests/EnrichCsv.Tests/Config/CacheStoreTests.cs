using System.Text.Json;
using EnrichCsv.Config;
using FluentAssertions;

namespace EnrichCsv.Tests.Config;

public sealed class CacheStoreTests : IDisposable
{
    private readonly DirectoryInfo _dir = Directory.CreateTempSubdirectory("enrich_csv_test_");

    public void Dispose() => _dir.Delete(recursive: true);

    private CacheStore Store(string name = "cache.json") =>
        new(new FileInfo(Path.Combine(_dir.FullName, name)));

    private static DestinationCache PopulatedCache() =>
        new()
        {
            NafToCategory = new Dictionary<string, string> { ["47.11"] = "Courses" },
            Destinations = new Dictionary<string, DestinationEntry>
            {
                ["OPERATEUR MOBILE"] = new()
                {
                    DestinationAccount = "Opérateur Mobile",
                    Category = "Abonnements",
                    Siren = "123456789",
                },
            },
        };

    [Fact]
    public void Load_MissingFile_ReturnsEmptyDefaults()
    {
        var cache = Store().Load();
        cache.NafToCategory.Should().BeEmpty();
        cache.Destinations.Should().BeEmpty();
    }

    [Fact]
    public void Load_ExistingFile_ReturnsCustomValues()
    {
        var store = Store();
        store.Save(PopulatedCache());

        var cache = store.Load();
        cache.NafToCategory.Should().ContainKey("47.11");
        cache.Destinations.Should().ContainKey("OPERATEUR MOBILE");
    }

    [Fact]
    public void Save_CreatesValidJson()
    {
        var store = Store();
        store.Save(new DestinationCache());

        var file = new FileInfo(Path.Combine(_dir.FullName, "cache.json"));
        var raw = JsonDocument.Parse(File.ReadAllText(file.FullName));
        raw.RootElement.TryGetProperty("naf_to_category", out _).Should().BeTrue();
        raw.RootElement.TryGetProperty("destinations", out _).Should().BeTrue();
    }

    [Fact]
    public void Save_RoundTrips()
    {
        var store = Store();
        var cache = new DestinationCache();
        store.Store(cache, "TEST", "Test", "Services");
        store.Save(cache);

        var reloaded = store.Load();
        store.Lookup(reloaded, "TEST").Should().NotBeNull();
        reloaded.Destinations["TEST"].DestinationAccount.Should().Be("Test");
    }

    [Fact]
    public void Save_CreatesParentDirs()
    {
        var store = new CacheStore(
            new FileInfo(Path.Combine(_dir.FullName, "subdir", "cache.json"))
        );
        store.Save(new DestinationCache());
        File.Exists(Path.Combine(_dir.FullName, "subdir", "cache.json")).Should().BeTrue();
    }

    [Fact]
    public void Lookup_ExistingKey_ReturnsEntry()
    {
        var store = Store();
        var cache = PopulatedCache();
        var entry = store.Lookup(cache, "OPERATEUR MOBILE");
        entry.Should().NotBeNull();
        entry!.DestinationAccount.Should().Be("Opérateur Mobile");
        entry.Category.Should().Be("Abonnements");
    }

    [Fact]
    public void Lookup_MissingKey_ReturnsNull()
    {
        var store = Store();
        store.Lookup(PopulatedCache(), "UNKNOWN").Should().BeNull();
    }

    [Fact]
    public void Lookup_IsCaseSensitive()
    {
        var store = Store();
        store.Lookup(PopulatedCache(), "operateur mobile").Should().BeNull();
    }

    [Fact]
    public void Store_AddsEntry()
    {
        var store = Store();
        var cache = new DestinationCache();
        store.Store(cache, "NOUVEAU", "Nouveau", "Achats");
        cache.Destinations.Should().ContainKey("NOUVEAU");
        cache.Destinations["NOUVEAU"].DestinationAccount.Should().Be("Nouveau");
        cache.Destinations["NOUVEAU"].Category.Should().Be("Achats");
    }

    [Fact]
    public void Store_WithSiren()
    {
        var store = Store();
        var cache = new DestinationCache();
        store.Store(cache, "MARCHAND", "Marchand", "Achats", "987654321");
        cache.Destinations["MARCHAND"].Siren.Should().Be("987654321");
    }

    [Fact]
    public void Store_WithoutSiren_DefaultsEmpty()
    {
        var store = Store();
        var cache = new DestinationCache();
        store.Store(cache, "MARCHAND", "Marchand", "Achats");
        cache.Destinations["MARCHAND"].Siren.Should().BeEmpty();
    }

    [Fact]
    public void Save_PreservesNonAsciiCharacters()
    {
        var store = Store();
        var cache = new DestinationCache();
        store.Store(cache, "TEST", "Tëst café", "Loisirs");
        store.Save(cache);

        var raw = File.ReadAllText(Path.Combine(_dir.FullName, "cache.json"));
        raw.Should().Contain("Tëst café");
    }

    [Fact]
    public void Categories_DerivedFromDestinations()
    {
        var store = Store();
        var cache = new DestinationCache();
        store.Store(cache, "A", "A", "Courses");
        store.Store(cache, "B", "B", "Santé");
        store.Store(cache, "C", "C", "Courses");

        var categories = store.Categories(cache);
        categories.Should().BeEquivalentTo(["Courses", "Santé"]);
        categories.Should().BeInAscendingOrder();
    }

    [Fact]
    public void NafToCategory_RoundTrips()
    {
        var store = Store();
        var cache = new DestinationCache
        {
            NafToCategory = new() { ["47.11"] = "Courses", ["86.21"] = "Santé" },
        };
        store.Save(cache);

        var reloaded = store.Load();
        reloaded.NafToCategory.Should().ContainKey("47.11").WhoseValue.Should().Be("Courses");
        reloaded.NafToCategory.Should().ContainKey("86.21").WhoseValue.Should().Be("Santé");
    }
}
