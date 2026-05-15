using System.Text.RegularExpressions;

namespace EnrichCsv.Normalizer;

public static partial class LabelNormalizer
{
    private static readonly (Regex Pattern, string Replacement)[] StripPrefixes =
    [
        (CardeDatePrefix(), ""),
        (AnnCartePrefix(), ""),
        (VirInstPrefix(), ""),
        (VirPrefix(), ""),
        (PrlvPrefix(), ""),
        (EchPretPrefix(), "Échéance prêt"),
        (FPrefix(), ""),
        (VersPrefix(), ""),
    ];

    private static readonly (Regex Pattern, string Replacement)[] CleanSuffixes =
    [
        (PostcodeCity(), ""),
        (TitleCaseCity(), ""),
        (BankRefCode(), ""),
    ];

    private static readonly (Regex Pattern, string Replacement)[] CleanInfixes =
    [
        (SumUpInfix(), ""),
        (SqInfix(), ""),
        (AdeoInfix(), ""),
    ];

    private static readonly Regex LegalSuffixPattern = LegalSuffix();

    public static string NormalizeLabel(string label)
    {
        var result = label.Trim();

        foreach (var (pattern, replacement) in StripPrefixes)
        {
            var updated = pattern.Replace(result, replacement, 1);
            if (updated != result)
            {
                if (replacement != "")
                    return updated;
                result = updated.Trim();
                break;
            }
        }

        foreach (var (pattern, replacement) in CleanSuffixes)
            result = pattern.Replace(result, replacement).Trim();

        foreach (var (pattern, replacement) in CleanInfixes)
        {
            var updated = pattern.Replace(result, replacement, 1);
            if (updated != result)
            {
                result = updated.Trim();
                break;
            }
        }

        return result.Trim();
    }

    public static string SimplifyName(string name)
    {
        var result = name.Trim();
        while (true)
        {
            var cleaned = LegalSuffixPattern.Replace(result, "").Trim();
            if (cleaned == result)
                break;
            result = cleaned;
        }

        if (result.Length == 0)
            return result;

        var words = result.Split(' ');
        if (result == result.ToUpper() && words.Length > 1)
            return string.Join(' ', words.Select(w => char.ToUpper(w[0]) + w[1..].ToLower()));

        return result;
    }

    public static string DestinationKey(string rawLabel) =>
        NormalizeLabel(rawLabel).ToUpperInvariant().Trim();

    [GeneratedRegex(@"^CARTE \d{2}/\d{2} ")]
    private static partial Regex CardeDatePrefix();

    [GeneratedRegex(@"^ANN CARTE ")]
    private static partial Regex AnnCartePrefix();

    [GeneratedRegex(@"^VIR INST (vers |de )?")]
    private static partial Regex VirInstPrefix();

    [GeneratedRegex(@"^VIR (de |LBC )?")]
    private static partial Regex VirPrefix();

    [GeneratedRegex(@"^PRLV ")]
    private static partial Regex PrlvPrefix();

    [GeneratedRegex(@"^ECH PRET \S+")]
    private static partial Regex EchPretPrefix();

    [GeneratedRegex(@"^F ")]
    private static partial Regex FPrefix();

    [GeneratedRegex(@"^vers ")]
    private static partial Regex VersPrefix();

    [GeneratedRegex(@"\s+\d{5}\s+\S+$")]
    private static partial Regex PostcodeCity();

    [GeneratedRegex(@"(?<=[A-Z])\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$")]
    private static partial Regex TitleCaseCity();

    [GeneratedRegex(@"\s+(?=[A-Z0-9]*\d)[A-Z0-9]{8,}/?.*$")]
    private static partial Regex BankRefCode();

    [GeneratedRegex(@"(?i)^SumUp\s*\*\s*")]
    private static partial Regex SumUpInfix();

    [GeneratedRegex(@"(?i)^SQ \*\s*")]
    private static partial Regex SqInfix();

    [GeneratedRegex(@"(?i)^ADEO\*\s*")]
    private static partial Regex AdeoInfix();

    [GeneratedRegex(
        @"\s+\b(SA|SAS|SARL|EURL|SNC|SASU|EIRL|SCE|SCP|SE|NV|BV|GmbH|Ltd|LLC|Inc|Corp|PLC)\b\.?\s*$",
        RegexOptions.IgnoreCase
    )]
    private static partial Regex LegalSuffix();
}
