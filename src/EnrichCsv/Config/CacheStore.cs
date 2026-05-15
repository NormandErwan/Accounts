using System.Text.Encodings.Web;
using System.Text.Json;

namespace EnrichCsv.Config;

public sealed class CacheStore(FileInfo path)
{
    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        WriteIndented = true,
        Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping,
    };

    public DestinationCache Load()
    {
        if (!File.Exists(path.FullName))
            return new DestinationCache();

        var json = File.ReadAllText(path.FullName);
        return JsonSerializer.Deserialize<DestinationCache>(json, JsonOptions)
            ?? new DestinationCache();
    }

    public void Save(DestinationCache cache)
    {
        Directory.CreateDirectory(path.DirectoryName!);
        var json = JsonSerializer.Serialize(cache, JsonOptions);
        File.WriteAllText(path.FullName, json);
    }

    public DestinationEntry? Lookup(DestinationCache cache, string key) =>
        cache.Destinations.TryGetValue(key, out var entry) ? entry : null;

    public void Store(
        DestinationCache cache,
        string key,
        string destinationAccount,
        string category,
        string siren = ""
    )
    {
        cache.Destinations[key] = new DestinationEntry
        {
            DestinationAccount = destinationAccount,
            Category = category,
            Siren = siren,
        };
    }

    public IReadOnlyList<string> Categories(DestinationCache cache) =>
        cache
            .Destinations.Values.Select(e => e.Category)
            .Where(c => c.Length > 0)
            .Distinct()
            .Order()
            .ToList();
}
