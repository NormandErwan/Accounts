using System.Text.Json.Serialization;

namespace EnrichCsv.Config;

public sealed class DestinationCache
{
    [JsonPropertyName("naf_to_category")]
    public Dictionary<string, string> NafToCategory { get; set; } = [];

    [JsonPropertyName("destinations")]
    public Dictionary<string, DestinationEntry> Destinations { get; set; } = [];
}
