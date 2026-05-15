namespace EnrichCsv.Naf;

public static class NafMapper
{
    /// <summary>
    /// Maps a NAF/APE code to a category using the provided dictionary.
    /// Tries exact match, then 5-char prefix, then 4-char prefix.
    /// Returns "" if nothing matches (no built-in fallback map).
    /// A key explicitly mapped to "" returns "" — not a fallback.
    /// </summary>
    public static string MapCode(string nafCode, IDictionary<string, string> nafToCategory)
    {
        if (string.IsNullOrEmpty(nafCode))
            return "";

        foreach (var key in CandidateKeys(nafCode))
        {
            if (nafToCategory.TryGetValue(key, out var category))
                return category;
        }

        return "";
    }

    private static IEnumerable<string> CandidateKeys(string code)
    {
        yield return code;
        if (code.Length >= 5)
            yield return code[..5];
        if (code.Length >= 4)
            yield return code[..4];
    }
}
