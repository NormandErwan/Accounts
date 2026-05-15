using System.Text.Json.Serialization;

namespace EnrichCsv.Config;

public sealed class DestinationEntry
{
    [JsonPropertyName("destination_account")]
    public string DestinationAccount { get; set; } = "";

    [JsonPropertyName("category")]
    public string Category { get; set; } = "";

    [JsonPropertyName("siren")]
    public string Siren { get; set; } = "";
}
