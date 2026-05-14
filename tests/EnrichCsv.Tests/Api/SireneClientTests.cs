using System.Net;
using System.Text;
using EnrichCsv.Api;
using FluentAssertions;

namespace EnrichCsv.Tests.Api;

public sealed class SireneClientTests
{
    private static SireneClient ClientWith(HttpResponseMessage response)
    {
        var handler = new MockHttpMessageHandler(response);
        var httpClient = new HttpClient(handler) { BaseAddress = new Uri("https://example.com") };
        return new SireneClient(httpClient);
    }

    private static HttpResponseMessage JsonResponse(
        string json,
        HttpStatusCode status = HttpStatusCode.OK
    ) => new(status) { Content = new StringContent(json, Encoding.UTF8, "application/json") };

    private static string HitJson(
        string name = "Test SA",
        string naf = "47.11",
        string siren = "123456789"
    ) =>
        $$$"""{"results":[{"nom_complet":"{{{name}}}","siren":"{{{siren}}}","siege":{"activite_principale":"{{{naf}}}"}}]}""";

    [Fact]
    public async Task SearchCompany_ReturnsParsedResult()
    {
        var client = ClientWith(JsonResponse(HitJson()));
        var result = await client.SearchCompanyAsync("test");
        result.Should().NotBeNull();
        result!.Name.Should().Be("Test SA");
        result.Naf.Should().Be("47.11");
        result.Siren.Should().Be("123456789");
    }

    [Fact]
    public async Task SearchCompany_ReturnsNullOnEmptyResults()
    {
        var client = ClientWith(JsonResponse("""{"results":[]}"""));
        var result = await client.SearchCompanyAsync("unknown");
        result.Should().BeNull();
    }

    [Fact]
    public async Task SearchCompany_ReturnsNullOnHttpStatusError()
    {
        var client = ClientWith(JsonResponse("Not found", HttpStatusCode.NotFound));
        var result = await client.SearchCompanyAsync("test");
        result.Should().BeNull();
    }

    [Fact]
    public async Task SearchCompany_ReturnsNullOnTimeout()
    {
        var handler = new ThrowingHttpHandler(new TaskCanceledException("timeout"));
        var httpClient = new HttpClient(handler);
        var client = new SireneClient(httpClient);
        var result = await client.SearchCompanyAsync("test");
        result.Should().BeNull();
    }

    [Fact]
    public async Task SearchCompany_ReturnsNullOnConnectionError()
    {
        var handler = new ThrowingHttpHandler(new HttpRequestException("refused"));
        var httpClient = new HttpClient(handler);
        var client = new SireneClient(httpClient);
        var result = await client.SearchCompanyAsync("test");
        result.Should().BeNull();
    }

    [Fact]
    public async Task SearchCompany_ReturnsNullOnJsonDecodeError()
    {
        var client = ClientWith(JsonResponse("not json at all"));
        var result = await client.SearchCompanyAsync("test");
        result.Should().BeNull();
    }

    [Fact]
    public async Task SearchCompany_PropagatesOperationCanceled()
    {
        var cts = new CancellationTokenSource();
        await cts.CancelAsync();
        var handler = new ThrowingHttpHandler(new OperationCanceledException(cts.Token));
        var httpClient = new HttpClient(handler);
        var client = new SireneClient(httpClient);
        await Assert.ThrowsAsync<OperationCanceledException>(() =>
            client.SearchCompanyAsync("test", cts.Token)
        );
    }

    [Fact]
    public async Task SearchCompany_HandlesMissingSiegeKey()
    {
        var json = """{"results":[{"nom_complet":"Test","siren":"123","siege":{}}]}""";
        var client = ClientWith(JsonResponse(json));
        var result = await client.SearchCompanyAsync("test");
        result.Should().NotBeNull();
        result!.Naf.Should().BeEmpty();
    }
}

file sealed class MockHttpMessageHandler(HttpResponseMessage response) : HttpMessageHandler
{
    protected override Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request,
        CancellationToken cancellationToken
    ) => Task.FromResult(response);
}

file sealed class ThrowingHttpHandler(Exception exception) : HttpMessageHandler
{
    protected override Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request,
        CancellationToken cancellationToken
    ) => Task.FromException<HttpResponseMessage>(exception);
}
