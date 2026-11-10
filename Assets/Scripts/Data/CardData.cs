using System;
using UnityEngine;
using Synapse.TcgEngine.Core;

namespace Synapse.TcgEngine.Data
{
    /// <summary>
    /// Data-layer Collector Identification ScriptableObject & bridge for Shadowverse EVOLVE / BP05
    /// and CARDFRONT: Cradle of Echoes bilingual card metadata.
    /// Complements Synapse.TcgEngine.Core.CardData and Synapse.TcgEngine.Data.CardDataSO.
    /// </summary>
    [Serializable]
    public class CardCollectorMetadataBridge
    {
        [Header("Collector Identification (Shadowverse EVOLVE / BP Standard)")]
        public string originalTitleJp = "機構翼の少女・ローザ(進化前)";
        public string cardGameTitle = "Shadowverse EVOLVE";
        public string boosterVersionEn = "[BP05] Eternal omens";
        public string originalVersionJp = "ブースターパック第5弾 永劫なる絶傑";
        public string collectorCardNumber = "BP05-110 SR";
        public string collectorRarity = "SR";
        public string evolutionStateJp = "進化前";

        public CardCollectorIdentification ToCollectorIdentification(string cardId = "bp05_110_rosa_unevolved", string titleEn = "Rosa, Mechawing Maiden (Unevolved)")
        {
            CollectorRarityTier parsedRarity = CollectorRarityTier.SR;
            if (!string.IsNullOrEmpty(collectorRarity))
            {
                Enum.TryParse<CollectorRarityTier>(collectorRarity.Trim(), true, out parsedRarity);
            }

            CardEvolutionState evoState = CardEvolutionState.Unevolved_ShinkaMae;
            if (!string.IsNullOrEmpty(evolutionStateJp) && evolutionStateJp.Contains("進化後"))
            {
                evoState = CardEvolutionState.Evolved_ShinkaGo;
            }

            CardCollectorIdentification entry = new CardCollectorIdentification
            {
                cardId = cardId,
                titleEn = titleEn,
                originalTitleJp = originalTitleJp,
                cardGame = cardGameTitle,
                versionEn = boosterVersionEn,
                originalVersionJp = originalVersionJp,
                cardNumber = collectorCardNumber,
                rarity = parsedRarity,
                evolutionState = evoState,
                sha256CollectorHash = string.Empty
            };
            entry.sha256CollectorHash = SynapseCardIdentificationCatalog.ComputeCollectorSha256(entry);
            return entry;
        }
    }
}
