namespace EnrichCsv.Api;

public interface ISireneClient
{
    Task<SireneResult?> SearchCompanyAsync(
        string name,
        CancellationToken cancellationToken = default
    );
}
