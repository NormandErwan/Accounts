using System.Globalization;
using EnrichCsv.Api;
using EnrichCsv.Models;
using Spectre.Console;

namespace EnrichCsv.Enricher;

public sealed class SpectreUserPrompt : IUserPrompt
{
    private static readonly Dictionary<TransactionType, string> TypeLabels = new()
    {
        [TransactionType.Expense] = "Dépense",
        [TransactionType.Income] = "Revenu",
        [TransactionType.Transfer] = "Virement",
    };

    public string AskDestinationAccount(string proposed)
    {
        AnsiConsole.Markup(
            $"  [bold]Nom commercial[/] [[cyan]{Markup.Escape(proposed)}[/cyan]] : "
        );
        var raw = Console.ReadLine() ?? "";
        return raw.Trim().Length > 0 ? raw.Trim() : proposed;
    }

    public string AskCategory(IReadOnlyList<string> categories, string proposed)
    {
        AnsiConsole.MarkupLine("  [bold]Catégorie[/] :");
        for (var i = 0; i < categories.Count; i++)
        {
            var marker = categories[i] == proposed ? " [green]←[/green]" : "";
            AnsiConsole.MarkupLine($"    {i + 1, 2}. {Markup.Escape(categories[i])}{marker}");
        }
        AnsiConsole.Markup(
            $"  [[cyan]{Markup.Escape(proposed)}[/cyan]] ([dim]s = ignorer, autre = nouvelle catégorie[/dim]) : "
        );
        var raw = (Console.ReadLine() ?? "").Trim();

        if (raw.Equals("s", StringComparison.OrdinalIgnoreCase))
            return "";
        if (raw.Length == 0)
            return proposed;
        if (int.TryParse(raw, out var idx) && idx >= 1 && idx <= categories.Count)
            return categories[idx - 1];
        return raw;
    }

    public void DisplayTransaction(Transaction tx, SireneResult? apiResult, string proposedAccount)
    {
        var table = new Table()
            .HideHeaders()
            .NoBorder()
            .AddColumn(new TableColumn("").Width(14))
            .AddColumn("");
        table.AddRow("[dim]Date[/]", $"[bold]{FormatDate(tx.Date)}[/]");
        table.AddRow("[dim]Libellé[/]", Markup.Escape(tx.RawLabel));
        table.AddRow("[dim]Extrait[/]", Markup.Escape(tx.CleanLabel));

        var apiInfo = apiResult is not null
            ? $"{Markup.Escape(apiResult.Name)} → simplifié : [cyan]{Markup.Escape(proposedAccount)}[/cyan]"
            : "[dim](aucun résultat SIRENE)[/dim]";
        table.AddRow("[dim]API SIRENE[/]", apiInfo);

        AnsiConsole.Write(
            new Rule($"[bold]{TypeLabels[tx.Type]}[/] — {Markup.Escape(tx.SourceAccount)}")
        );
        AnsiConsole.Write(table);
    }

    private static string FormatDate(DateOnly date)
    {
        var dt = date.ToDateTime(TimeOnly.MinValue);
        return dt.ToString("dddd dd MMMM yyyy", new CultureInfo("fr-FR"));
    }
}
