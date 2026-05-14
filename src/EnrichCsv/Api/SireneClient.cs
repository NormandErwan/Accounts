using System.Net.Http.Json;
using System.Text.Json;

namespace EnrichCsv.Api;

public sealed class SireneClient(HttpClient httpClient) : ISireneClient
{
    private const string SearchUrl = "https://recherche-entreprises.api.gouv.fr/search";

    public async Task<SireneResult?> SearchCompanyAsync(
        string name,
        CancellationToken cancellationToken = default
    )
    {
        try
        {
            var url = $"{SearchUrl}?q={Uri.EscapeDataString(name)}&per_page=1";
            var response = await httpClient.GetAsync(url, cancellationToken);
            response.EnsureSuccessStatusCode();

            using var doc = await JsonDocument.ParseAsync(
                await response.Content.ReadAsStreamAsync(cancellationToken),
                cancellationToken: cancellationToken
            );

            if (!doc.RootElement.TryGetProperty("results", out var results))
                return null;

            if (results.GetArrayLength() == 0)
                return null;

            var hit = results[0];
            var naf = "";
            if (
                hit.TryGetProperty("siege", out var siege)
                && siege.TryGetProperty("activite_principale", out var nafEl)
            )
                naf = nafEl.GetString() ?? "";

            return new SireneResult
            {
                Name = hit.TryGetProperty("nom_complet", out var nomEl)
                    ? nomEl.GetString() ?? ""
                    : "",
                Naf = naf,
                Siren = hit.TryGetProperty("siren", out var sirenEl)
                    ? sirenEl.GetString() ?? ""
                    : "",
            };
        }
        catch (OperationCanceledException) when (cancellationToken.IsCancellationRequested)
        {
            throw;
        }
        catch (Exception ex)
            when (ex
                    is OperationCanceledException
                        or HttpRequestException
                        or JsonException
                        or InvalidOperationException
            )
        {
            return null;
        }
    }
}
