using EnrichCsv.Naf;
using FluentAssertions;

namespace EnrichCsv.Tests.Naf;

public sealed class NafMapperTests
{
    private static readonly Dictionary<string, string> NafMap = new()
    {
        ["47.11"] = "Courses",
        ["47.73"] = "Santé",
        ["86.21"] = "Santé",
        ["49.41"] = "Transport",
        ["52.21"] = "Transport",
        ["56.10"] = "Loisirs",
        ["56.30"] = "Loisirs",
        ["61.20"] = "Abonnements",
        ["62.01"] = "Services",
        ["47.52"] = "Maison",
        ["68.20"] = "Logement",
        ["47.91"] = "Achats",
        ["84.11"] = "Impôts",
        ["65.30"] = "Épargne",
    };

    [Theory]
    [InlineData("47.11B", "Courses")]
    [InlineData("47.11", "Courses")]
    [InlineData("86.21Z", "Santé")]
    [InlineData("86.21", "Santé")]
    [InlineData("47.73Z", "Santé")]
    [InlineData("49.41A", "Transport")]
    [InlineData("52.21Z", "Transport")]
    [InlineData("56.10A", "Loisirs")]
    [InlineData("56.30Z", "Loisirs")]
    [InlineData("61.20Z", "Abonnements")]
    [InlineData("61.20", "Abonnements")]
    [InlineData("62.01Z", "Services")]
    [InlineData("47.52A", "Maison")]
    [InlineData("68.20A", "Logement")]
    [InlineData("47.91A", "Achats")]
    [InlineData("84.11Z", "Impôts")]
    [InlineData("65.30Z", "Épargne")]
    [InlineData("99.99Z", "")]
    [InlineData("", "")]
    [InlineData("XX.XX", "")]
    public void MapCode_Cases(string code, string expected)
    {
        NafMapper.MapCode(code, NafMap).Should().Be(expected);
    }

    [Fact]
    public void MapCode_CustomMap()
    {
        var custom = new Dictionary<string, string> { ["99.99"] = "Custom" };
        NafMapper.MapCode("99.99", custom).Should().Be("Custom");
        NafMapper.MapCode("47.11", custom).Should().Be("");
    }

    [Fact]
    public void MapCode_EmptyStringValue_DoesNotFallThrough()
    {
        var map = new Dictionary<string, string> { ["47.11"] = "" };
        NafMapper.MapCode("47.11", map).Should().Be("");
    }
}
