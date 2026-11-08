using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Text;
using UnityEngine;
#if UNITY_EDITOR
using UnityEditor;
#endif
using Synapse.TcgEngine.AI;
using Synapse.TcgEngine.Campaign;
using Synapse.TcgEngine.Core;
using Synapse.TcgEngine.Data;
using Debug = UnityEngine.Debug;

namespace Synapse.TcgEngine.EditorTools
{
    /// <summary>
    /// ScriptableObject representing a prebuilt or player-saved Deck Preset for PROJECT CF & CardCraft.
    /// </summary>
    [CreateAssetMenu(fileName = "NewSynapseDeck", menuName = "Synapse TCG/Deck Preset (Project CF)")]
    public class SynapseDeckAssetSO : ScriptableObject
    {
        public string deckId;
        public string deckTitle;
        public FactionId faction;
        [TextArea(2, 4)]
        public string strategyDescription;
        public List<CardDataSO> cards = new List<CardDataSO>();
    }

    [Serializable]
    public class BalanceTestReport
    {
        public int totalMatches;
        public int player0Wins;
        public int player1Wins;
        public int draws;
        public float averageTurnsPerMatch;
        public long elapsedMilliseconds;
        public int puzzlesVerified;
        public int puzzlesPassed;
        public Dictionary<string, int> cardPlayCounts = new Dictionary<string, int>();
        public Dictionary<string, int> cardWinContributions = new Dictionary<string, int>();
    }

    /// <summary>
    /// Clean-room Unity Editor Asset Pipeline & Headless AI Self-Play Diagnostic Tool for Synapse TCG Engine.
    /// Generates `.asset` ScriptableObjects for all 14 PROJECT CF & CardCraft cards, binds their rendered
    /// sprites from `Assets/Resources/CardArt/*.png`, creates starter faction decks, and executes a
    /// 100-match Minimax AI vs AI balance & puzzle verification suite.
    /// </summary>
    public static class SynapseCardAssetGenerator
    {
        public const string CardArtFolder = "Assets/Resources/CardArt";
        public const string GeneratedCardsFolder = "Assets/Resources/Cards";
        public const string GeneratedDecksFolder = "Assets/Resources/Decks";

        private static readonly Dictionary<SpecialAbilityType, string> AbilityDescriptions =
            new Dictionary<SpecialAbilityType, string>
            {
                { SpecialAbilityType.None, "Creative Portfolio Card: Evolves after repeated match mastery." },
                { SpecialAbilityType.Teleport, "Once per game, move Mystic Mage to any unoccupied space on the 3x3 grid and resolve captures." },
                { SpecialAbilityType.Charge, "When Mech Knight captures an opponent's card, immediately make a bonus placement this turn." },
                { SpecialAbilityType.HealingAura, "At the end of your turn, restore +1 permanent strength to all sides of adjacent friendly cards." },
                { SpecialAbilityType.Vanish, "Once per game, Shadow Assassin becomes immune to capture for 1 full turn." },
                { SpecialAbilityType.ElementalBurst, "Once per game after capturing an adjacent card, swap base stats with the captured card." },
                { SpecialAbilityType.WarpDrive, "Once per turn, move Galactic Explorer to any unoccupied space on the 3x3 grid." },
                { SpecialAbilityType.TemporalRift, "Once per game, reverse the directional strength values (Up<->Down, Left<->Right) of adjacent cards for 1 turn." },
                { SpecialAbilityType.Rebirth, "Once per game, if Phoenix Guardian is captured, it returns to its original owner's hand." },
                { SpecialAbilityType.TechnoStealth, "Cyber Ninja is immune to capture while orthogonally adjacent to any Tech card." },
                { SpecialAbilityType.MoonlightBlessing, "Lunar Oracle gains +1 to all sides during nighttime or while adjacent to a Lunar card." }
            };

#if UNITY_EDITOR
        [MenuItem("Synapse TCG/Generate All PROJECT CF & CardCraft Assets", priority = 100)]
        public static void GenerateAllCardAndDeckAssetsMenu()
        {
            EnsureFolderExists("Assets/Resources");
            EnsureFolderExists(GeneratedCardsFolder);
            EnsureFolderExists(GeneratedDecksFolder);

            var roster = ProjectCfCardCatalog.CreateDefaultRoster();
            var savedCardAssets = new Dictionary<string, CardDataSO>();

            int spritesBound = 0;
            foreach (var runtimeCardData in roster)
            {
                string assetPath = $"{GeneratedCardsFolder}/{runtimeCardData.id}.asset";
                var existing = AssetDatabase.LoadAssetAtPath<CardDataSO>(assetPath);
                if (existing == null)
                {
                    existing = ScriptableObject.CreateInstance<CardDataSO>();
                    AssetDatabase.CreateAsset(existing, assetPath);
                }

                existing.id = runtimeCardData.id;
                existing.title = runtimeCardData.title;
                existing.codeName = runtimeCardData.codeName;
                existing.baseStats = runtimeCardData.baseStats;
                existing.themes = runtimeCardData.themes;
                existing.specialAbility = runtimeCardData.specialAbility;
                existing.specialAbilityDescription = AbilityDescriptions.TryGetValue(runtimeCardData.specialAbility, out var desc)
                    ? desc
                    : string.Empty;
                existing.synergyRequiredTheme = runtimeCardData.synergyRequiredTheme;
                existing.synergyAllSidesBonus = runtimeCardData.synergyAllSidesBonus;
                existing.synergyName = runtimeCardData.synergyName;
                existing.evolvesToCardId = runtimeCardData.evolvesToCardId;

                // Bind sprite from Assets/Resources/CardArt/{id}.png
                string spritePath = $"{CardArtFolder}/{runtimeCardData.id}.png";
                EnsureTextureImportedAsSprite(spritePath);
                var sprite = AssetDatabase.LoadAssetAtPath<Sprite>(spritePath);
                if (sprite != null)
                {
                    existing.cardArt = sprite;
                    spritesBound++;
                }

                EditorUtility.SetDirty(existing);
                savedCardAssets[existing.id] = existing;
            }

            // Generate 3 Starter Faction Deck Assets
            CreateOrUpdateStarterDeck(
                "deck_arcane_clockwork",
                "Arcane & Clockwork Enclave",
                FactionId.ArcaneEnclave,
                "Combines Mystic Mage's Teleport, Clockwork Sorcerer's Temporal Rift, and CardCraft Concept Art for high-IQ spatial inversions.",
                new[] { "cf_01_mystic_mage", "cf_07_clockwork_sorcerer", "cc_01_sketching", "cc_02_concept_art", "cf_05_elemental_sprite", "cf_08_phoenix_guardian" },
                savedCardAssets);

            CreateOrUpdateStarterDeck(
                "deck_iron_vanguard_cyber",
                "Iron Vanguard & Digital Shadow",
                FactionId.IronVanguardDirectorate,
                "Aggressive tempo deck pairing Mech Knight's Charge double-deployment with Cyber Ninja's Techno Stealth immunity.",
                new[] { "cf_02_mech_knight", "cf_09_cyber_ninja", "cf_06_galactic_explorer", "cf_04_shadow_assassin", "cc_03_storyboard", "cc_04_animatic" },
                savedCardAssets);

            CreateOrUpdateStarterDeck(
                "deck_celestial_eclipse",
                "Celestial Order & Lunar Eclipse",
                FactionId.CelestialOrder,
                "Late-game powerhouse built around Celestial Guardian's Healing Aura and Lunar Oracle's +4 Moonlight convergence.",
                new[] { "cf_03_celestial_guardian", "cf_10_lunar_oracle", "cf_06_galactic_explorer", "cf_08_phoenix_guardian", "cf_01_mystic_mage", "cf_07_clockwork_sorcerer" },
                savedCardAssets);

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();

            Debug.Log($"[SynapseCardAssetGenerator] Generated {savedCardAssets.Count} CardDataSO assets in '{GeneratedCardsFolder}', " +
                      $"bound {spritesBound}/14 PNG sprites from '{CardArtFolder}', and created 3 Starter Deck assets in '{GeneratedDecksFolder}'.");
        }

        [MenuItem("Synapse TCG/Run Headless 100-Match AI Balance Test", priority = 101)]
        public static void RunHeadlessBalanceTestMenu()
        {
            var report = RunHeadlessBalanceSimulation(100, aiDepthP0: 2, aiDepthP1: 2);
            var sb = new StringBuilder();
            sb.AppendLine("=== SYNAPSE TCG ENGINE: 100-MATCH HEADLESS AI BALANCE & PUZZLE REPORT ===");
            sb.AppendLine($"Total Matches: {report.totalMatches} ({report.elapsedMilliseconds} ms)");
            sb.AppendLine($"Player 0 Wins: {report.player0Wins} ({(report.player0Wins * 100f / report.totalMatches):F1}%)");
            sb.AppendLine($"Player 1 Wins: {report.player1Wins} ({(report.player1Wins * 100f / report.totalMatches):F1}%)");
            sb.AppendLine($"Draws:         {report.draws} ({(report.draws * 100f / report.totalMatches):F1}%)");
            sb.AppendLine($"Avg Turns:     {report.averageTurnsPerMatch:F2}");
            sb.AppendLine($"Tactical Puzzles Verified: {report.puzzlesPassed}/{report.puzzlesVerified} PASSED");
            sb.AppendLine("--- Card Play Frequency & Win Contribution ---");
            foreach (var kv in report.cardPlayCounts)
            {
                int wins = report.cardWinContributions.TryGetValue(kv.Key, out var w) ? w : 0;
                float winRate = kv.Value > 0 ? (wins * 100f / kv.Value) : 0f;
                sb.AppendLine($"  • {kv.Key,-26} | Played: {kv.Value,4} | Win Rate When Played: {winRate:F1}%");
            }
            Debug.Log(sb.ToString());
        }

        private static void EnsureFolderExists(string folderPath)
        {
            if (AssetDatabase.IsValidFolder(folderPath)) return;
            string parent = Path.GetDirectoryName(folderPath)?.Replace('\\', '/') ?? "Assets";
            string folderName = Path.GetFileName(folderPath);
            if (!AssetDatabase.IsValidFolder(parent))
            {
                EnsureFolderExists(parent);
            }
            AssetDatabase.CreateFolder(parent, folderName);
        }

        private static void EnsureTextureImportedAsSprite(string assetPath)
        {
            if (!File.Exists(assetPath)) return;
            var importer = AssetImporter.GetAtPath(assetPath) as TextureImporter;
            if (importer != null && importer.textureType != TextureImporterType.Sprite)
            {
                importer.textureType = TextureImporterType.Sprite;
                importer.spriteImportMode = SpriteImportMode.Single;
                importer.mipmapEnabled = false;
                importer.SaveAndReimport();
            }
        }

        private static void CreateOrUpdateStarterDeck(
            string deckId,
            string title,
            FactionId faction,
            string description,
            string[] cardIds,
            Dictionary<string, CardDataSO> cardLookup)
        {
            string path = $"{GeneratedDecksFolder}/{deckId}.asset";
            var deck = AssetDatabase.LoadAssetAtPath<SynapseDeckAssetSO>(path);
            if (deck == null)
            {
                deck = ScriptableObject.CreateInstance<SynapseDeckAssetSO>();
                AssetDatabase.CreateAsset(deck, path);
            }

            deck.deckId = deckId;
            deck.deckTitle = title;
            deck.faction = faction;
            deck.strategyDescription = description;
            deck.cards.Clear();

            foreach (var id in cardIds)
            {
                if (cardLookup.TryGetValue(id, out var card))
                {
                    deck.cards.Add(card);
                }
            }

            EditorUtility.SetDirty(deck);
        }
#endif

        /// <summary>
        /// Runs a deterministic headless AI-vs-AI self-play diagnostic across `matchCount` matches
        /// and verifies all 5 Lethal 3x3 Tactical Board Puzzles from <see cref="SynapseStoryCampaign"/>.
        /// Callable from both the Unity Editor menu and automated test suites.
        /// </summary>
        public static BalanceTestReport RunHeadlessBalanceSimulation(int matchCount = 100, int aiDepthP0 = 2, int aiDepthP1 = 2)
        {
            var sw = Stopwatch.StartNew();
            var report = new BalanceTestReport { totalMatches = matchCount };
            var roster = ProjectCfCardCatalog.CreateDefaultRoster();

            foreach (var c in roster)
            {
                report.cardPlayCounts[c.id] = 0;
                report.cardWinContributions[c.id] = 0;
            }

            int totalTurns = 0;

            for (int m = 0; m < matchCount; m++)
            {
                bool isNight = (m % 2 == 1);
                var game = new TcgGameLogic(seed: 1000 + m * 37, isNighttime: isNight);

                // Build balanced 8-card decks sampled from the 14-card catalog
                for (int p = 0; p < 2; p++)
                {
                    for (int i = 0; i < 8; i++)
                    {
                        var template = roster[(m + p * 5 + i * 3) % roster.Count];
                        var rc = RuntimeCard.FromCardData(template, p, $"m{m}_p{p}_c{i}_{template.id}");
                        game.players[p].deck.Add(rc);
                    }
                    game.ShuffleDeck(game.players[p]);
                    game.DrawCards(game.players[p], TcgGameLogic.StartingHandSize);
                }

                // Alternate starting player every match to eliminate first-turn bias
                int firstPlayer = m % 2;
                game.StartTurn(firstPlayer);

                var playedByPlayer = new HashSet<string>[2]
                {
                    new HashSet<string>(),
                    new HashSet<string>()
                };

                int safetySteps = 0;
                while (!game.winnerId.HasValue && !game.IsGameOver() && safetySteps < 30)
                {
                    safetySteps++;
                    int active = game.activePlayerId;
                    int depth = (active == 0) ? aiDepthP0 : aiDepthP1;
                    var move = TcgMinimaxAI.ChooseBestPlacement(game, active, maxDepth: depth, beamWidth: 6);

                    if (move.kind == AIActionKind.PlaceCard && !string.IsNullOrEmpty(move.cardUid))
                    {
                        var cardObj = game.players[active].hand.Find(c => c.uid == move.cardUid);
                        if (cardObj != null)
                        {
                            playedByPlayer[active].Add(cardObj.cardId);
                            report.cardPlayCounts[cardObj.cardId] =
                                (report.cardPlayCounts.TryGetValue(cardObj.cardId, out var cnt) ? cnt : 0) + 1;
                        }

                        if (!game.PlaceCard(active, move.cardUid, move.x, move.y, out _))
                        {
                            game.EndTurn();
                        }
                    }
                    else
                    {
                        game.EndTurn();
                    }
                }

                if (!game.winnerId.HasValue)
                {
                    game.DetermineWinner();
                }

                totalTurns += game.turnNumber;
                if (game.winnerId == 0)
                {
                    report.player0Wins++;
                    foreach (var cid in playedByPlayer[0])
                        report.cardWinContributions[cid]++;
                }
                else if (game.winnerId == 1)
                {
                    report.player1Wins++;
                    foreach (var cid in playedByPlayer[1])
                        report.cardWinContributions[cid]++;
                }
                else
                {
                    report.draws++;
                }
            }

            report.averageTurnsPerMatch = matchCount > 0 ? (float)totalTurns / matchCount : 0f;

            // Verify all 5 Tactical Board Puzzles
            var puzzles = SynapseStoryCampaign.GetTacticalPuzzles();
            report.puzzlesVerified = puzzles.Count;
            foreach (var puz in puzzles)
            {
                if (SynapseStoryCampaign.ExecuteAndVerifyPuzzleSolution(
                        puz, out _, out _, out _, out _, out _))
                {
                    report.puzzlesPassed++;
                }
            }

            sw.Stop();
            report.elapsedMilliseconds = sw.ElapsedMilliseconds;
            return report;
        }
    }
}
