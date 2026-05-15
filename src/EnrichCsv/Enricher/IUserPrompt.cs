using EnrichCsv.Api;
using EnrichCsv.Models;

namespace EnrichCsv.Enricher;

public interface IUserPrompt
{
    string AskDestinationAccount(string proposed);
    string AskCategory(IReadOnlyList<string> categories, string proposed);
    void DisplayTransaction(Transaction tx, SireneResult? apiResult, string proposedAccount);
}
