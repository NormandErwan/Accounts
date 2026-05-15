using EnrichCsv.Normalizer;
using FluentAssertions;

namespace EnrichCsv.Tests.Normalizer;

public sealed class NormalizeLabelTests
{
    [Theory]
    [InlineData("CARTE 15/01 SUPERMARCHE VILLE", "SUPERMARCHE VILLE")]
    [InlineData("CARTE 08/01 SUPERMARCHE 35000 RENNES", "SUPERMARCHE")]
    [InlineData("PRLV OPERATEUR MOBILE", "OPERATEUR MOBILE")]
    [InlineData("VIR INST vers COMPTE COMMUN FORT", "COMPTE COMMUN FORT")]
    [InlineData("VIR INST de PARTENAIRE", "PARTENAIRE")]
    [InlineData("VIR INST PARTENAIRE", "PARTENAIRE")]
    [InlineData("VIR de COMPTE PARTENAIRE - loyer", "COMPTE PARTENAIRE - loyer")]
    [InlineData("VIR EMPLOYEUR SA", "EMPLOYEUR SA")]
    [InlineData("ANN CARTE BOUTIQUE LIGNE", "BOUTIQUE LIGNE")]
    [InlineData("ECH PRET 0123456789", "Échéance prêt")]
    [InlineData("ECH PRET 0110866344104", "Échéance prêt")]
    [InlineData("F COTISATION EUROCOMPTE 04/26", "COTISATION EUROCOMPTE 04/26")]
    [InlineData("vers NORMAND / PARTENAIRE", "NORMAND / PARTENAIRE")]
    [InlineData("CARTE 10/01 ADEO*BRICOLEUR VILLE", "BRICOLEUR VILLE")]
    [InlineData("CARTE 12/01 SumUp *ARTISAN NOM", "ARTISAN NOM")]
    [InlineData("CARTE 12/01 SumUp  *ARTISAN NOM", "ARTISAN NOM")]
    [InlineData("CARTE 03/04 SQ *BOUTIQUE PLACE", "BOUTIQUE PLACE")]
    [InlineData("CARTE 02/04 OVH SAS Roubaix", "OVH SAS")]
    [InlineData("VIR LBC FRANCE SAS", "FRANCE SAS")]
    public void NormalizeLabel_Cases(string raw, string expected)
    {
        LabelNormalizer.NormalizeLabel(raw).Should().Be(expected);
    }

    [Fact]
    public void NormalizeLabel_ReturnsString() =>
        LabelNormalizer.NormalizeLabel("PRLV OPERATEUR").Should().BeOfType<string>();

    [Fact]
    public void NormalizeLabel_EmptyString() =>
        LabelNormalizer.NormalizeLabel("").Should().BeOfType<string>();
}

public sealed class SimplifyNameTests
{
    [Theory]
    [InlineData("Bouygues Telecom SA", "Bouygues Telecom")]
    [InlineData("OVH SAS", "OVH")]
    [InlineData("INTERMARCHE DAC RENNES SAS", "Intermarche Dac Rennes")]
    [InlineData("Adobe Systems Inc", "Adobe Systems")]
    [InlineData("Leroy Merlin SARL", "Leroy Merlin")]
    [InlineData("Amazon EU SARL", "Amazon EU")]
    [InlineData("Carrefour SNC", "Carrefour")]
    [InlineData("Anthropic", "Anthropic")]
    [InlineData("E.Leclerc", "E.Leclerc")]
    [InlineData("CPAM", "CPAM")]
    public void SimplifyName_Cases(string name, string expected)
    {
        LabelNormalizer.SimplifyName(name).Should().Be(expected);
    }

    [Fact]
    public void SimplifyName_ReturnsString() =>
        LabelNormalizer.SimplifyName("Test SA").Should().BeOfType<string>();

    [Fact]
    public void SimplifyName_EmptyString() =>
        LabelNormalizer.SimplifyName("").Should().BeOfType<string>();
}

public sealed class DestinationKeyTests
{
    [Theory]
    [InlineData("PRLV Bouygues Telecom", "BOUYGUES TELECOM")]
    [InlineData("CARTE 08/01 SUPERMARCHE VILLE", "SUPERMARCHE VILLE")]
    public void DestinationKey_IsUpperStripped(string input, string expected)
    {
        LabelNormalizer.DestinationKey(input).Should().Be(expected);
    }
}
