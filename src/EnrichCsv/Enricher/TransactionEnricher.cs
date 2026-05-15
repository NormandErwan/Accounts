using EnrichCsv.Api;
using EnrichCsv.Config;
using EnrichCsv.Models;
using EnrichCsv.Naf;
using EnrichCsv.Normalizer;

namespace EnrichCsv.Enricher;

public sealed class TransactionEnricher(
    ISireneClient sireneClient,
    IUserPrompt userPrompt,
    CacheStore cacheStore
)
{
    public async Task<IReadOnlyList<Transaction>> EnrichAsync(
        IReadOnlyList<Transaction> transactions,
        CancellationToken cancellationToken = default
    )
    {
        var cache = cacheStore.Load();
        var enriched = new List<Transaction>(transactions.Count);

        foreach (var tx in transactions)
        {
            if (tx.Type == TransactionType.Transfer)
            {
                enriched.Add(tx);
                continue;
            }

            var key = LabelNormalizer.DestinationKey(tx.RawLabel);
            var entry = cacheStore.Lookup(cache, key);

            if (entry is not null)
            {
                enriched.Add(
                    tx with
                    {
                        DestinationAccount = entry.DestinationAccount,
                        Category = entry.Category,
                    }
                );
                continue;
            }

            var apiResult = await sireneClient.SearchCompanyAsync(tx.CleanLabel, cancellationToken);
            string proposedAccount;
            string proposedCategory;
            string siren;

            if (apiResult is not null)
            {
                proposedAccount = LabelNormalizer.SimplifyName(apiResult.Name);
                proposedCategory = NafMapper.MapCode(apiResult.Naf, cache.NafToCategory);
                siren = apiResult.Siren;
            }
            else
            {
                proposedAccount = tx.CleanLabel;
                proposedCategory = "";
                siren = "";
            }

            userPrompt.DisplayTransaction(tx, apiResult, proposedAccount);
            var categories = cacheStore.Categories(cache).ToList();
            var category = userPrompt.AskCategory(categories, proposedCategory);

            if (string.IsNullOrEmpty(category))
            {
                enriched.Add(tx);
                continue;
            }

            var destinationAccount = userPrompt.AskDestinationAccount(proposedAccount);
            cacheStore.Store(cache, key, destinationAccount, category, siren);
            cacheStore.Save(cache);
            enriched.Add(tx with { DestinationAccount = destinationAccount, Category = category });
        }

        return enriched;
    }
}
