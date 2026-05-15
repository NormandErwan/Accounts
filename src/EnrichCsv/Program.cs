using System.Diagnostics.CodeAnalysis;
using EnrichCsv.Api;
using EnrichCsv.Config;
using EnrichCsv.Enricher;
using EnrichCsv.Models;
using EnrichCsv.Output;
using EnrichCsv.Parsers;
using Microsoft.Extensions.DependencyInjection;
using Spectre.Console.Cli;

[ExcludeFromCodeCoverage]
internal static class Program
{
    public static async Task<int> Main(string[] args)
    {
        System.Text.Encoding.RegisterProvider(System.Text.CodePagesEncodingProvider.Instance);

        var services = new ServiceCollection();
        services.AddHttpClient<ISireneClient, SireneClient>(c =>
            c.Timeout = TimeSpan.FromSeconds(5)
        );
        services.AddSingleton<IBankParser, CmbParser>();
        services.AddSingleton<IBankParser, FortuneoParser>();
        services.AddSingleton<IUserPrompt, SpectreUserPrompt>();
        services.AddSingleton<FireflyCsvWriter>();

        var app = new CommandApp<EnrichCommand>(new TypeRegistrar(services));
        return await app.RunAsync(args);
    }
}

[ExcludeFromCodeCoverage]
internal sealed class TypeRegistrar(IServiceCollection services) : ITypeRegistrar
{
    public ITypeResolver Build() => new TypeResolver(services.BuildServiceProvider());

    public void Register(Type service, Type implementation) =>
        services.AddSingleton(service, implementation);

    public void RegisterInstance(Type service, object implementation) =>
        services.AddSingleton(service, implementation);

    public void RegisterLazy(Type service, Func<object> factory) =>
        services.AddSingleton(service, _ => factory());
}

[ExcludeFromCodeCoverage]
internal sealed class TypeResolver(IServiceProvider provider) : ITypeResolver, IDisposable
{
    public object? Resolve(Type? type) => type is null ? null : provider.GetService(type);

    public void Dispose()
    {
        if (provider is IDisposable d)
            d.Dispose();
    }
}

[ExcludeFromCodeCoverage]
internal sealed class EnrichSettings : CommandSettings
{
    [CommandArgument(0, "<files>")]
    public string[] Files { get; init; } = [];

    [CommandOption("--bank")]
    public string? Bank { get; init; }

    [CommandOption("--account")]
    public required string Account { get; init; }

    [CommandOption("--cache")]
    public string Cache { get; init; } = "cache.json";

    [CommandOption("--output")]
    public string? Output { get; init; }
}

[ExcludeFromCodeCoverage]
internal sealed class EnrichCommand(
    IEnumerable<IBankParser> parsers,
    ISireneClient sireneClient,
    IUserPrompt userPrompt,
    FireflyCsvWriter writer
) : AsyncCommand<EnrichSettings>
{
    protected override async Task<int> ExecuteAsync(
        CommandContext context,
        EnrichSettings settings,
        CancellationToken cancellationToken
    )
    {
        var parserMap = parsers.ToDictionary(p => p.BankKey, p => p);

        var transactions = new List<Transaction>();
        foreach (var filePath in settings.Files)
        {
            var file = new FileInfo(filePath);
            var bankKey = settings.Bank ?? DetectBank(file);
            if (bankKey is null || !parserMap.TryGetValue(bankKey, out var parser))
            {
                Console.Error.WriteLine(
                    $"Impossible de détecter le format bancaire pour {filePath}. Utilisez --bank."
                );
                return 1;
            }
            transactions.AddRange(parser.Parse(file, settings.Account));
        }

        transactions.Sort((a, b) => a.Date.CompareTo(b.Date));

        var cacheStore = new CacheStore(new FileInfo(settings.Cache));
        var enricher = new TransactionEnricher(sireneClient, userPrompt, cacheStore);
        var enriched = await enricher.EnrichAsync(transactions, cancellationToken);

        var csv = writer.Write(enriched);

        if (settings.Output is not null)
        {
            File.WriteAllText(settings.Output, csv);
            Console.WriteLine($"Written to {settings.Output}");
        }
        else
        {
            Console.Write(csv);
        }

        return 0;
    }

    private static string? DetectBank(FileInfo file)
    {
        if (file.Extension.Equals(".zip", StringComparison.OrdinalIgnoreCase))
            return "fortuneo";

        try
        {
            var firstLine = File.ReadLines(file.FullName).FirstOrDefault() ?? "";
            if (firstLine.Contains("Date operation") && firstLine.Contains("Libelle"))
                return "cmb";
            if (firstLine.Contains("Date opération") || firstLine.Contains("libellé"))
                return "fortuneo";
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"Erreur lors de la lecture de {file.FullName} : {ex.Message}");
        }

        return null;
    }
}
