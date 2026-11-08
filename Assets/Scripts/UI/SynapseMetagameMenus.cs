using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Cryptography;
using UnityEngine;
using Synapse.TcgEngine.Data;
using Synapse.TcgEngine.Api;

namespace Synapse.TcgEngine.UI
{
    [Serializable]
    public class SavedDeckConfiguration
    {
        public string deckName = "Frontier Legends Squad";
        public List<string> tacticalSquadCardIds = new List<string>(5); // 5-card 3x3 Tactical Squad
        public List<string> fullDeckCardIds = new List<string>(15);     // 15-card Full Tournament Deck
    }

    [Serializable]
    public struct DeckValidationReport
    {
        public bool isTacticalSquadValid;
        public bool isFullDeckValid;
        public int tacticalSquadCount;
        public int fullDeckCount;
        public string validationMessage;
    }

    [Serializable]
    public struct MatchmakingStatusView
    {
        public bool isSearching;
        public int localElo;
        public int matchedOpponentElo;
        public string opponentName;
        public float estimatedWaitSeconds;
    }

    /// <summary>
    /// Clean-room Collection Manager, Deck Builder (5-card tactical squad + 15-card full deck validation),
    /// Cryptographic Pack Opening UI Controller, and Elo Matchmaking Lobby Controller for Synapse.TcgEngine.
    /// </summary>
    public class SynapseMetagameMenus : MonoBehaviour
    {
        public const int RequiredTacticalSquadSize = 5;
        public const int RequiredFullDeckSize = 15;
        public const int MaxCopiesPerCardInSquad = 1;
        public const int MaxCopiesPerCardInFullDeck = 2;
        public const int PackCostCoins = 100;
        public const int CardsPerBoosterPack = 5;

        public SynapseUserProfile Profile { get; private set; } = new SynapseUserProfile
        {
            userId = "local_commander",
            username = "FrontierCommander",
            eloRating = 1200,
            coins = 1000,
            confidencePoints = 150,
            xp = 300
        };

        public List<CardDataSO> Catalog { get; private set; } = new List<CardDataSO>();
        public SavedDeckConfiguration ActiveDeck { get; private set; } = new SavedDeckConfiguration();
        public MatchmakingStatusView MatchmakingStatus { get; private set; }

        public event Action<PackOpenResult, List<CardDataSO>> OnBoosterPackOpened;
        public event Action<DeckValidationReport> OnDeckUpdated;
        public event Action<MatchmakingStatusView> OnMatchmakingChanged;
        public event Action<CardDataSO, CardDataSO> OnCardEvolved;

        private void Awake()
        {
            InitializeCatalogAndStarterCollection();
        }

        public void InitializeCatalogAndStarterCollection()
        {
            Catalog = ProjectCfCardCatalog.CreateDefaultRoster();
            if (Profile.ownedCards.Count == 0)
            {
                // Grant starter copies of all 14 PROJECT CF & CardCraft cards
                foreach (var c in Catalog)
                {
                    Profile.ownedCards.Add(c.id);
                    Profile.ownedCards.Add(c.id);
                }
            }

            if (ActiveDeck.tacticalSquadCardIds.Count == 0)
            {
                for (int i = 0; i < Mathf.Min(RequiredTacticalSquadSize, Catalog.Count); i++)
                {
                    ActiveDeck.tacticalSquadCardIds.Add(Catalog[i].id);
                }
            }

            if (ActiveDeck.fullDeckCardIds.Count == 0)
            {
                for (int i = 0; i < RequiredFullDeckSize; i++)
                {
                    ActiveDeck.fullDeckCardIds.Add(Catalog[i % Catalog.Count].id);
                }
            }
        }

        // =====================================================================
        // 1. COLLECTION FILTERING & CARDCRAFT CREATIVE EVOLUTION
        // =====================================================================

        public List<CardDataSO> FilterCollectionByTheme(CardTheme themeFilter, string searchQuery = "")
        {
            return Catalog.Where(c =>
            {
                bool themeMatch = (themeFilter == CardTheme.None) || ((c.themes & themeFilter) != 0);
                bool textMatch = string.IsNullOrWhiteSpace(searchQuery) ||
                                 c.title.IndexOf(searchQuery, StringComparison.OrdinalIgnoreCase) >= 0 ||
                                 c.codeName.IndexOf(searchQuery, StringComparison.OrdinalIgnoreCase) >= 0;
                return themeMatch && textMatch;
            }).ToList();
        }

        /// <summary>
        /// Evolves a Tier-1 CardCraft card (`cc_01_sketching` -> `cc_02_concept_art` or
        /// `cc_03_storyboard` -> `cc_04_animatic`) using Confidence Points (CP).
        /// </summary>
        public bool TryEvolveCardCraftSkill(string baseCardId, int cpCost = 50)
        {
            var baseCard = Catalog.Find(c => c.id == baseCardId);
            if (baseCard == null || string.IsNullOrEmpty(baseCard.evolvesToCardId)) return false;
            if (Profile.confidencePoints < cpCost) return false;

            var evolvedCard = Catalog.Find(c => c.id == baseCard.evolvesToCardId);
            if (evolvedCard == null) return false;

            Profile.confidencePoints -= cpCost;
            Profile.ownedCards.Add(evolvedCard.id);
            OnCardEvolved?.Invoke(baseCard, evolvedCard);
            return true;
        }

        // =====================================================================
        // 2. DECK BUILDER (5-CARD TACTICAL SQUAD + 15-CARD FULL DECK VALIDATION)
        // =====================================================================

        public bool ToggleCardInTacticalSquad(string cardId)
        {
            if (ActiveDeck.tacticalSquadCardIds.Contains(cardId))
            {
                ActiveDeck.tacticalSquadCardIds.Remove(cardId);
                OnDeckUpdated?.Invoke(ValidateActiveDeck());
                return true;
            }

            if (ActiveDeck.tacticalSquadCardIds.Count >= RequiredTacticalSquadSize)
                return false;

            if (!Catalog.Exists(c => c.id == cardId))
                return false;

            ActiveDeck.tacticalSquadCardIds.Add(cardId);
            OnDeckUpdated?.Invoke(ValidateActiveDeck());
            return true;
        }

        public bool AddCardToFullDeck(string cardId)
        {
            if (ActiveDeck.fullDeckCardIds.Count >= RequiredFullDeckSize) return false;
            int copies = ActiveDeck.fullDeckCardIds.Count(id => id == cardId);
            if (copies >= MaxCopiesPerCardInFullDeck) return false;
            if (!Catalog.Exists(c => c.id == cardId)) return false;

            ActiveDeck.fullDeckCardIds.Add(cardId);
            OnDeckUpdated?.Invoke(ValidateActiveDeck());
            return true;
        }

        public bool RemoveCardFromFullDeck(string cardId)
        {
            bool removed = ActiveDeck.fullDeckCardIds.Remove(cardId);
            if (removed) OnDeckUpdated?.Invoke(ValidateActiveDeck());
            return removed;
        }

        public DeckValidationReport ValidateActiveDeck()
        {
            int squadCount = ActiveDeck.tacticalSquadCardIds.Count;
            int fullCount = ActiveDeck.fullDeckCardIds.Count;

            bool uniqueSquad = ActiveDeck.tacticalSquadCardIds.Distinct().Count() == squadCount;
            bool squadValid = (squadCount == RequiredTacticalSquadSize) && uniqueSquad;

            bool copyLimitOk = ActiveDeck.fullDeckCardIds
                .GroupBy(id => id)
                .All(g => g.Count() <= MaxCopiesPerCardInFullDeck);
            bool fullValid = (fullCount == RequiredFullDeckSize) && copyLimitOk;

            string msg = (squadValid && fullValid)
                ? "Deck Ready: 5/5 Tactical Squad & 15/15 Frontier Deck Validated."
                : $"Tactical Squad: {squadCount}/{RequiredTacticalSquadSize} (Singleton) | Full Deck: {fullCount}/{RequiredFullDeckSize} (Max {MaxCopiesPerCardInFullDeck}x).";

            return new DeckValidationReport
            {
                isTacticalSquadValid = squadValid,
                isFullDeckValid = fullValid,
                tacticalSquadCount = squadCount,
                fullDeckCount = fullCount,
                validationMessage = msg
            };
        }

        public List<CardDataSO> BuildTacticalSquadAssets()
        {
            var list = new List<CardDataSO>(ActiveDeck.tacticalSquadCardIds.Count);
            foreach (var id in ActiveDeck.tacticalSquadCardIds)
            {
                var found = Catalog.Find(c => c.id == id);
                if (found != null) list.Add(found);
            }
            return list;
        }

        // =====================================================================
        // 3. CRYPTOGRAPHIC CSPRNG BOOSTER PACK OPENER
        // =====================================================================

        /// <summary>
        /// Opens a 5-card Frontier Booster Pack using cryptographic randomness (`RandomNumberGenerator`)
        /// to guarantee fair, tamper-proof drop rates.
        /// </summary>
        public PackOpenResult OpenCryptographicBoosterPack()
        {
            if (Catalog == null || Catalog.Count == 0)
            {
                InitializeCatalogAndStarterCollection();
            }

            if (Profile.coins < PackCostCoins)
            {
                return null;
            }

            Profile.coins -= PackCostCoins;
            var result = new PackOpenResult
            {
                packId = Guid.NewGuid().ToString("N"),
                remainingCoins = Profile.coins
            };

            var drawnAssets = new List<CardDataSO>(CardsPerBoosterPack);
            byte[] entropy = new byte[4];

            using (var csprng = RandomNumberGenerator.Create())
            {
                for (int i = 0; i < CardsPerBoosterPack; i++)
                {
                    csprng.GetBytes(entropy);
                    uint rand = BitConverter.ToUInt32(entropy, 0);
                    int idx = (int)(rand % (uint)Catalog.Count);
                    var card = Catalog[idx];
                    result.drawnCardIds.Add(card.id);
                    Profile.ownedCards.Add(card.id);
                    drawnAssets.Add(card);
                }
            }

            OnBoosterPackOpened?.Invoke(result, drawnAssets);
            return result;
        }

        // =====================================================================
        // 4. ELO MATCHMAKING LOBBY CONTROLLER
        // =====================================================================

        public void StartEloMatchmakingQueue()
        {
            MatchmakingStatus = new MatchmakingStatusView
            {
                isSearching = true,
                localElo = Profile.eloRating,
                matchedOpponentElo = Profile.eloRating + 18,
                opponentName = "Searching Frontier Node...",
                estimatedWaitSeconds = 1.5f
            };
            OnMatchmakingChanged?.Invoke(MatchmakingStatus);
        }

        public MatchmakingStatusView SimulateMatchmakingFound(string rivalName = "Archon_Minimax_v3", int rivalElo = 1224)
        {
            MatchmakingStatus = new MatchmakingStatusView
            {
                isSearching = false,
                localElo = Profile.eloRating,
                matchedOpponentElo = rivalElo,
                opponentName = rivalName,
                estimatedWaitSeconds = 0f
            };
            OnMatchmakingChanged?.Invoke(MatchmakingStatus);
            return MatchmakingStatus;
        }

        /// <summary>
        /// Computes standard FIDE Elo rating adjustment (`K = 32`) after a match concludes.
        /// </summary>
        public int RecordMatchEloOutcome(int opponentElo, float actualScore)
        {
            const float K = 32f;
            float expected = 1f / (1f + Mathf.Pow(10f, (opponentElo - Profile.eloRating) / 400f));
            int delta = Mathf.RoundToInt(K * (actualScore - expected));
            Profile.eloRating = Mathf.Max(100, Profile.eloRating + delta);
            return delta;
        }
    }
}
