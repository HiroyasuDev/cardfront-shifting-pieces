using System;
using System.Collections.Generic;
using Synapse.TcgEngine.Data;

namespace Synapse.TcgEngine.Core
{
    /// <summary>
    /// FFTA-Style Judge Law & Triple Triad Regional Rule Edicts for Synapse.TcgEngine (PROJECT CF & CardCraft).
    /// Governed by the High Magisterium of Aethelgard to enforce tactical constraints and regional combo rules
    /// across the 3x3 Frontier Grid.
    /// </summary>
    [Flags]
    public enum JudgeLawType
    {
        None                                    = 0,
        DecreeOfSilence_NoMagicSynergy          = 1 << 0, // Suppresses Magic-theme adjacency synergies; penalizes Arcane casts
        IronMobilization_TechBonus              = 1 << 1, // Grants +1 all sides to Tech/Steampunk frames; rewards Tech deployment
        SolarBenediction_DivineBonus            = 1 << 2, // Grants +1 all sides to Divine/Cosmic frames; forces Daytime unless eclipsed
        LunarEclipse_ForceNighttime             = 1 << 3, // Forces Nighttime on the 3x3 grid (activates Moonlight Blessing globally)
        ChronoLock_DisableOncePerGameAbilities  = 1 << 4, // Prohibits once-per-game active & reactive abilities (Teleport, Vanish, TemporalRift, Rebirth, ElementalBurst)
        ReverseOrder_LowStatWinsCapture         = 1 << 5, // Inverted tactical combat: strictly lower directional stat captures higher stat
        PlusAndSameComboRule                    = 1 << 6  // Triple Triad Regional Rule: triggers Same (2+ equal opposing sides) & Plus (2+ equal sums) combo cascades
    }

    /// <summary>
    /// Represents a Judge Commendation ("Law Card" privilege token) awarded for strict adherence
    /// to Magisterium Edicts during a 3x3 tactical match.
    /// </summary>
    [Serializable]
    public struct JudgeCommendation
    {
        public string commendationId;
        public string title;
        public JudgeLawType upheldLaw;
        public int bonusConfidencePoints;
        public int bonusAllSidesStatModifier;

        public JudgeCommendation(string id, string title, JudgeLawType law, int bonusCp, int statMod)
        {
            commendationId = id;
            this.title = title;
            upheldLaw = law;
            bonusConfidencePoints = bonusCp;
            bonusAllSidesStatModifier = statMod;
        }
    }

    /// <summary>
    /// Immutable codex metadata describing a Magisterium Judge Law edict.
    /// </summary>
    [Serializable]
    public sealed class JudgeLawDescriptor
    {
        public JudgeLawType LawType { get; }
        public string EdictTitle { get; }
        public string MagisteriumCitation { get; }
        public string TacticalRuleSummary { get; }
        public int ObedienceBonusCp { get; }
        public int ViolationPenaltyCp { get; }

        public JudgeLawDescriptor(
            JudgeLawType lawType,
            string edictTitle,
            string magisteriumCitation,
            string tacticalRuleSummary,
            int obedienceBonusCp,
            int violationPenaltyCp)
        {
            LawType = lawType;
            EdictTitle = edictTitle;
            MagisteriumCitation = magisteriumCitation;
            TacticalRuleSummary = tacticalRuleSummary;
            ObedienceBonusCp = obedienceBonusCp;
            ViolationPenaltyCp = violationPenaltyCp;
        }
    }

    /// <summary>
    /// Clean-room FFTA-style Judge Law & Triple Triad Regional Rule Engine for Synapse.TcgEngine.
    /// Evaluates active Magisterium Edicts on the 3x3 board, computes law-modified directional stats,
    /// resolves ReverseOrder and Plus/Same regional combo captures, and awards Confidence Points (CP)
    /// and JudgeCommendation Law Cards for obeying active laws.
    /// </summary>
    public static class SynapseJudgeLawEngine
    {
        public const string JudgeCommendationBadgePrefix = "JudgeCommendation:";
        public const int DefaultObedienceCpReward = 15;
        public const int DefaultViolationCpPenalty = 10;
        public const int ComboCascadeCpPerFlip = 12;

        private static readonly (int dx, int dy)[] OrthogonalDirs = new[]
        {
            (0, 1),  // Up    (neighbor's Down opposes our Up)
            (0, -1), // Down  (neighbor's Up opposes our Down)
            (-1, 0), // Left  (neighbor's Right opposes our Left)
            (1, 0)   // Right (neighbor's Left opposes our Right)
        };

        private static readonly Dictionary<JudgeLawType, JudgeLawDescriptor> LawCodex =
            new Dictionary<JudgeLawType, JudgeLawDescriptor>
            {
                {
                    JudgeLawType.DecreeOfSilence_NoMagicSynergy,
                    new JudgeLawDescriptor(
                        JudgeLawType.DecreeOfSilence_NoMagicSynergy,
                        "Edict I: Decree of Silence",
                        "Codex Aethelgard, Article IV — Nullification of Unsanctioned Ether",
                        "Magic-theme adjacency synergies are suppressed to 0. Deploying non-Magic frames grants +15 CP and a Judge Commendation.",
                        15, 10)
                },
                {
                    JudgeLawType.IronMobilization_TechBonus,
                    new JudgeLawDescriptor(
                        JudgeLawType.IronMobilization_TechBonus,
                        "Edict II: Iron Mobilization",
                        "Iron Vanguard War Measure — Foundry Priority Act",
                        "All Tech and Steampunk Guardian Frames receive +1 to all directional stats. Deploying Tech frames awards +15 CP.",
                        15, 0)
                },
                {
                    JudgeLawType.SolarBenediction_DivineBonus,
                    new JudgeLawDescriptor(
                        JudgeLawType.SolarBenediction_DivineBonus,
                        "Edict III: Solar Benediction",
                        "Cathedral of the First Dawn — Liturgical Mandate",
                        "All Divine and Cosmic Guardian Frames receive +1 to all directional stats. Deploying Divine frames awards +15 CP.",
                        15, 0)
                },
                {
                    JudgeLawType.LunarEclipse_ForceNighttime,
                    new JudgeLawDescriptor(
                        JudgeLawType.LunarEclipse_ForceNighttime,
                        "Edict IV: Lunar Eclipse",
                        "Observatory of Celestial Insight — Umbral Convergence",
                        "Forces perpetual Nighttime across the 3x3 Frontier Grid, activating Lunar Oracle's Moonlight Blessing and rewarding Lunar/Shadow deployments.",
                        15, 0)
                },
                {
                    JudgeLawType.ChronoLock_DisableOncePerGameAbilities,
                    new JudgeLawDescriptor(
                        JudgeLawType.ChronoLock_DisableOncePerGameAbilities,
                        "Edict V: Chrono-Lock Stasis",
                        "High Judiciar's Temporal Seal — Prohibition of Singular Anomalies",
                        "Disables all once-per-game active and reactive abilities (Teleport, Vanish, TemporalRift, Rebirth, ElementalBurst). Upholding stasis grants +20 CP.",
                        20, 15)
                },
                {
                    JudgeLawType.ReverseOrder_LowStatWinsCapture,
                    new JudgeLawDescriptor(
                        JudgeLawType.ReverseOrder_LowStatWinsCapture,
                        "Edict VI: Reverse Order (Treaty of the Meek)",
                        "Frontier Armistice Protocol — Inversion of Arms",
                        "Inverts directional capture comparisons: strictly lower opposing stat captures higher stat (atkVal < defVal).",
                        20, 0)
                },
                {
                    JudgeLawType.PlusAndSameComboRule,
                    new JudgeLawDescriptor(
                        JudgeLawType.PlusAndSameComboRule,
                        "Edict VII: Plus & Same Regional Combo Law",
                        "Triple Frontier Concordat — Harmonic Resonance Clause",
                        "Placing a card that matches 2+ opposing directional values (Same) or 2+ directional sums (Plus) captures those neighbors and triggers a cascade.",
                        25, 0)
                }
            };

        /// <summary>
        /// Retrieves the Magisterium codex descriptor for a specific single JudgeLawType flag.
        /// </summary>
        public static JudgeLawDescriptor GetLawDescriptor(JudgeLawType law)
        {
            return LawCodex.TryGetValue(law, out var desc) ? desc : null;
        }

        /// <summary>
        /// Applies environmental Judge Laws (such as LunarEclipse_ForceNighttime) at the start of a turn or match.
        /// </summary>
        public static void ApplyTurnStartLawEnvironment(TcgGameLogic game, JudgeLawType activeLaws)
        {
            if (game == null) return;

            if ((activeLaws & JudgeLawType.LunarEclipse_ForceNighttime) != 0)
            {
                game.isNighttime = true;
            }
            else if ((activeLaws & JudgeLawType.SolarBenediction_DivineBonus) != 0)
            {
                game.isNighttime = false;
            }
        }

        /// <summary>
        /// Evaluates a card's effective directional stats at (x, y) under the active Judge Laws.
        /// Respects DecreeOfSilence_NoMagicSynergy, IronMobilization_TechBonus, SolarBenediction_DivineBonus,
        /// and LunarEclipse_ForceNighttime.
        /// </summary>
        public static DirectionalStats GetLawModifiedEffectiveStats(TcgGameLogic game, int x, int y, JudgeLawType activeLaws)
        {
            if (game == null || !game.InBounds(x, y) || game.grid[x, y].IsEmpty)
                return default;

            var card = game.grid[x, y].occupant;
            var stats = card.baseStats.AddAll(card.permanentStatBonus);

            bool hasSynergyNeighbor = false;
            bool hasLunarNeighbor = false;

            foreach (var (dx, dy) in OrthogonalDirs)
            {
                int nx = x + dx, ny = y + dy;
                if (!game.InBounds(nx, ny) || game.grid[nx, ny].IsEmpty) continue;
                var neighbor = game.grid[nx, ny].occupant;

                if (card.synergyRequiredTheme != CardTheme.None &&
                    (neighbor.themes & card.synergyRequiredTheme) != 0)
                {
                    hasSynergyNeighbor = true;
                }
                if ((neighbor.themes & CardTheme.Lunar) != 0)
                {
                    hasLunarNeighbor = true;
                }
            }

            // Law 1: DecreeOfSilence_NoMagicSynergy suppresses Magic-theme adjacency bonuses
            bool magicSynergySuppressed =
                (activeLaws & JudgeLawType.DecreeOfSilence_NoMagicSynergy) != 0 &&
                ((card.themes & CardTheme.Magic) != 0 || (card.synergyRequiredTheme & CardTheme.Magic) != 0);

            if (hasSynergyNeighbor && !magicSynergySuppressed)
            {
                stats = stats.AddAll(card.synergyAllSidesBonus);
            }

            // Law 4: LunarEclipse_ForceNighttime counts as nighttime for Moonlight Blessing
            bool effectiveNighttime = game.isNighttime || (activeLaws & JudgeLawType.LunarEclipse_ForceNighttime) != 0;
            if (card.specialAbility == SpecialAbilityType.MoonlightBlessing && (effectiveNighttime || hasLunarNeighbor))
            {
                stats = stats.AddAll(1);
            }

            // Law 2: IronMobilization_TechBonus grants +1 all sides to Tech or Steampunk cards
            if ((activeLaws & JudgeLawType.IronMobilization_TechBonus) != 0 &&
                (card.themes & (CardTheme.Tech | CardTheme.Steampunk)) != 0)
            {
                stats = stats.AddAll(1);
            }

            // Law 3: SolarBenediction_DivineBonus grants +1 all sides to Divine or Cosmic cards
            if ((activeLaws & JudgeLawType.SolarBenediction_DivineBonus) != 0 &&
                (card.themes & (CardTheme.Divine | CardTheme.Cosmic)) != 0)
            {
                stats = stats.AddAll(1);
            }

            // Clockwork Sorcerer's Temporal Rift stat reversal
            if (card.temporalRiftReversedTurns > 0)
            {
                stats = new DirectionalStats(stats.down, stats.up, stats.right, stats.left);
            }

            return stats;
        }

        /// <summary>
        /// Checks whether activating or triggering a special ability is legal under the active Judge Laws.
        /// Under ChronoLock_DisableOncePerGameAbilities, once-per-game abilities are prohibited.
        /// </summary>
        public static bool IsAbilityPermittedByLaw(SpecialAbilityType ability, JudgeLawType activeLaws)
        {
            if ((activeLaws & JudgeLawType.ChronoLock_DisableOncePerGameAbilities) == 0)
                return true;

            switch (ability)
            {
                case SpecialAbilityType.Teleport:
                case SpecialAbilityType.Vanish:
                case SpecialAbilityType.TemporalRift:
                case SpecialAbilityType.Rebirth:
                case SpecialAbilityType.ElementalBurst:
                    return false;
                default:
                    return true;
            }
        }

        /// <summary>
        /// Evaluates law obedience when a player deploys a card onto the 3x3 board, awarding Confidence Points (CP)
        /// and issuing a JudgeCommendation Law Card when the player upholds active Magisterium Edicts.
        /// </summary>
        public static List<JudgeCommendation> EvaluatePlacementLawCompliance(
            TcgGameLogic game,
            int playerId,
            RuntimeCard placedCard,
            JudgeLawType activeLaws)
        {
            var commendations = new List<JudgeCommendation>();
            if (game == null || placedCard == null || activeLaws == JudgeLawType.None)
                return commendations;

            var player = game.players[playerId];

            // 1. Decree of Silence compliance: deploying non-Magic cards is commended; Magic cards incur a CP penalty
            if ((activeLaws & JudgeLawType.DecreeOfSilence_NoMagicSynergy) != 0)
            {
                if ((placedCard.themes & CardTheme.Magic) == 0)
                {
                    AwardCommendation(player, commendations,
                        "cmd_silence_upheld",
                        "Judge Commendation: Seal of Silence",
                        JudgeLawType.DecreeOfSilence_NoMagicSynergy,
                        DefaultObedienceCpReward, 1);
                }
                else
                {
                    player.confidencePoints = Math.Max(0, player.confidencePoints - DefaultViolationCpPenalty);
                }
            }

            // 2. Iron Mobilization compliance: deploying Tech/Steampunk cards grants bonus CP & Commendation
            if ((activeLaws & JudgeLawType.IronMobilization_TechBonus) != 0 &&
                (placedCard.themes & (CardTheme.Tech | CardTheme.Steampunk)) != 0)
            {
                AwardCommendation(player, commendations,
                    "cmd_iron_vanguard",
                    "Judge Commendation: Iron Mobilization Writ",
                    JudgeLawType.IronMobilization_TechBonus,
                    DefaultObedienceCpReward, 1);
            }

            // 3. Solar Benediction compliance: deploying Divine/Cosmic cards grants bonus CP & Commendation
            if ((activeLaws & JudgeLawType.SolarBenediction_DivineBonus) != 0 &&
                (placedCard.themes & (CardTheme.Divine | CardTheme.Cosmic)) != 0)
            {
                AwardCommendation(player, commendations,
                    "cmd_solar_benediction",
                    "Judge Commendation: Solar Writ of Grace",
                    JudgeLawType.SolarBenediction_DivineBonus,
                    DefaultObedienceCpReward, 1);
            }

            // 4. Lunar Eclipse compliance: deploying Lunar/Shadow cards grants bonus CP & Commendation
            if ((activeLaws & JudgeLawType.LunarEclipse_ForceNighttime) != 0 &&
                (placedCard.themes & (CardTheme.Lunar | CardTheme.Shadow)) != 0)
            {
                AwardCommendation(player, commendations,
                    "cmd_lunar_eclipse",
                    "Judge Commendation: Umbral Concordat",
                    JudgeLawType.LunarEclipse_ForceNighttime,
                    DefaultObedienceCpReward, 1);
            }

            // 5. Chrono-Lock compliance: deploying cards that do not rely on once-per-game anomalies
            if ((activeLaws & JudgeLawType.ChronoLock_DisableOncePerGameAbilities) != 0 &&
                IsAbilityPermittedByLaw(placedCard.specialAbility, activeLaws))
            {
                AwardCommendation(player, commendations,
                    "cmd_chrono_orthodoxy",
                    "Judge Commendation: Temporal Orthodoxy",
                    JudgeLawType.ChronoLock_DisableOncePerGameAbilities,
                    20, 1);
            }

            return commendations;
        }

        /// <summary>
        /// Places a card on the 3x3 board and resolves captures using the active JudgeLawType rules:
        /// - Applies environmental laws (LunarEclipse_ForceNighttime)
        /// - Evaluates law compliance, Confidence Points (CP), and JudgeCommendation Law Cards
        /// - Resolves Plus & Same regional combo captures and cascades if PlusAndSameComboRule is active
        /// - Resolves standard or ReverseOrder directional captures while respecting ChronoLock
        /// </summary>
        public static bool PlaceCardWithJudgeLaws(
            TcgGameLogic game,
            int playerId,
            string cardUid,
            int x,
            int y,
            JudgeLawType activeLaws,
            out int totalCapturedCount,
            out List<JudgeCommendation> issuedCommendations)
        {
            totalCapturedCount = 0;
            issuedCommendations = new List<JudgeCommendation>();

            if (game == null || game.winnerId.HasValue || playerId != game.activePlayerId || game.phase != TurnPhase.Main)
                return false;
            if (!game.InBounds(x, y) || !game.grid[x, y].IsEmpty)
                return false;

            ApplyTurnStartLawEnvironment(game, activeLaws);

            var player = game.players[playerId];
            var card = player.hand.Find(c => c.uid == cardUid);
            if (card == null)
                return false;

            // Remove from hand and place onto 3x3 board
            player.hand.Remove(card);
            card.currentZone = ZoneType.Board;
            card.ownerId = playerId;
            game.grid[x, y].occupant = card;
            card.matchesPlayedCount++;

            // Evaluate law compliance & issue JudgeCommendation Law Cards
            issuedCommendations = EvaluatePlacementLawCompliance(game, playerId, card, activeLaws);

            // Resolve captures (including Plus/Same regional combos and ReverseOrder)
            totalCapturedCount = ResolveLawModifiedCapturesFrom(game, x, y, playerId, activeLaws);

            // Mech Knight (Charge): grant immediate bonus move if a capture occurred
            if (card.specialAbility == SpecialAbilityType.Charge &&
                totalCapturedCount > 0 &&
                game.HasEmptyCell() &&
                player.hand.Count > 0)
            {
                game.bonusMovePlayerId = playerId;
            }
            else
            {
                game.bonusMovePlayerId = null;
                game.EndTurn();
            }

            return true;
        }

        /// <summary>
        /// Resolves directional and regional-rule captures from (x, y) under active Judge Laws.
        /// Supports ReverseOrder_LowStatWinsCapture, PlusAndSameComboRule (with cascade), and ChronoLock.
        /// </summary>
        public static int ResolveLawModifiedCapturesFrom(
            TcgGameLogic game,
            int x,
            int y,
            int attackerPlayerId,
            JudgeLawType activeLaws)
        {
            if (game == null || !game.InBounds(x, y) || game.grid[x, y].IsEmpty)
                return 0;

            int totalCaptures = 0;
            var comboCapturedCells = new List<(int cx, int cy)>();

            // 1. Evaluate Triple Triad Regional Rule: Plus & Same
            if ((activeLaws & JudgeLawType.PlusAndSameComboRule) != 0)
            {
                var plusSameTargets = EvaluatePlusAndSameTargets(game, x, y, activeLaws);
                foreach (var (nx, ny) in plusSameTargets)
                {
                    var defender = game.grid[nx, ny].occupant;
                    if (defender != null && defender.ownerId != attackerPlayerId && !game.IsCardCaptureImmune(nx, ny))
                    {
                        ExecuteCardCapture(game, x, y, nx, ny, attackerPlayerId, activeLaws, out bool remainedOnBoard);
                        totalCaptures++;
                        if (remainedOnBoard)
                        {
                            comboCapturedCells.Add((nx, ny));
                        }
                    }
                }

                if (totalCaptures > 0)
                {
                    game.players[attackerPlayerId].confidencePoints += totalCaptures * ComboCascadeCpPerFlip;
                    AwardCommendation(
                        game.players[attackerPlayerId],
                        null,
                        "cmd_plus_same_combo",
                        "Judge Commendation: Harmonic Combo Mastery",
                        JudgeLawType.PlusAndSameComboRule,
                        DefaultObedienceCpReward,
                        1);
                }
            }

            // 2. Evaluate orthogonal directional captures (Normal or ReverseOrder)
            totalCaptures += ResolveDirectionalCapturesAtCell(game, x, y, attackerPlayerId, activeLaws, comboCapturedCells);

            // 3. Resolve Combo Cascade (cards flipped by Plus/Same trigger standard/ReverseOrder directional captures)
            var cascadeQueue = new Queue<(int cx, int cy)>(comboCapturedCells);
            var visitedCascade = new HashSet<(int, int)>(comboCapturedCells);

            while (cascadeQueue.Count > 0)
            {
                var (cx, cy) = cascadeQueue.Dequeue();
                var newlyFlipped = new List<(int, int)>();
                int cascadeFlips = ResolveDirectionalCapturesAtCell(game, cx, cy, attackerPlayerId, activeLaws, newlyFlipped);
                totalCaptures += cascadeFlips;

                foreach (var cell in newlyFlipped)
                {
                    if (visitedCascade.Add(cell))
                    {
                        cascadeQueue.Enqueue(cell);
                    }
                }
            }

            // Award standard CP for captures
            game.players[attackerPlayerId].confidencePoints += totalCaptures * 10;
            return totalCaptures;
        }

        /// <summary>
        /// Activates an on-board Special Ability if permitted by active Judge Laws.
        /// If ChronoLock_DisableOncePerGameAbilities is active, once-per-game abilities are blocked.
        /// </summary>
        public static bool ActivateSpecialAbilityWithJudgeLaws(
            TcgGameLogic game,
            int playerId,
            int fromX,
            int fromY,
            JudgeLawType activeLaws,
            int targetX = -1,
            int targetY = -1)
        {
            if (game == null || !game.InBounds(fromX, fromY) || game.grid[fromX, fromY].IsEmpty)
                return false;

            var card = game.grid[fromX, fromY].occupant;
            if (card.ownerId != playerId)
                return false;

            if (!IsAbilityPermittedByLaw(card.specialAbility, activeLaws))
            {
                // Violation penalty for attempting a forbidden once-per-game anomaly under Chrono-Lock
                game.players[playerId].confidencePoints =
                    Math.Max(0, game.players[playerId].confidencePoints - DefaultViolationCpPenalty);
                return false;
            }

            return game.ActivateSpecialAbility(playerId, fromX, fromY, targetX, targetY);
        }

        /// <summary>
        /// Redeems a JudgeCommendation Law Card to bestow its permanent all-sides stat bonus onto a friendly card on the board.
        /// </summary>
        public static bool RedeemJudgeCommendationOnCard(
            TcgGameLogic game,
            int playerId,
            JudgeCommendation commendation,
            int targetX,
            int targetY)
        {
            if (game == null || !game.InBounds(targetX, targetY) || game.grid[targetX, targetY].IsEmpty)
                return false;

            var player = game.players[playerId];
            string badgeKey = JudgeCommendationBadgePrefix + commendation.commendationId;
            if (!player.badges.Contains(badgeKey))
                return false;

            var targetCard = game.grid[targetX, targetY].occupant;
            if (targetCard.ownerId != playerId)
                return false;

            player.badges.Remove(badgeKey);
            targetCard.permanentStatBonus += Math.Max(1, commendation.bonusAllSidesStatModifier);
            return true;
        }

        private static int ResolveDirectionalCapturesAtCell(
            TcgGameLogic game,
            int x,
            int y,
            int attackerPlayerId,
            JudgeLawType activeLaws,
            List<(int, int)> flippedCellsOut)
        {
            var attackerCard = game.grid[x, y].occupant;
            if (attackerCard == null) return 0;

            var attackerStats = GetLawModifiedEffectiveStats(game, x, y, activeLaws);
            bool reverseOrder = (activeLaws & JudgeLawType.ReverseOrder_LowStatWinsCapture) != 0;
            int captures = 0;

            foreach (var (dx, dy) in OrthogonalDirs)
            {
                int nx = x + dx, ny = y + dy;
                if (!game.InBounds(nx, ny) || game.grid[nx, ny].IsEmpty) continue;

                var defenderCard = game.grid[nx, ny].occupant;
                if (defenderCard.ownerId == attackerPlayerId) continue;
                if (game.IsCardCaptureImmune(nx, ny)) continue;

                var defenderStats = GetLawModifiedEffectiveStats(game, nx, ny, activeLaws);
                int atkVal = 0, defVal = 0;

                if (dx == 0 && dy == 1)       { atkVal = attackerStats.up;    defVal = defenderStats.down; }
                else if (dx == 0 && dy == -1) { atkVal = attackerStats.down;  defVal = defenderStats.up; }
                else if (dx == -1 && dy == 0) { atkVal = attackerStats.left;  defVal = defenderStats.right; }
                else if (dx == 1 && dy == 0)  { atkVal = attackerStats.right; defVal = defenderStats.left; }

                bool winsComparison = reverseOrder ? (atkVal < defVal) : (atkVal > defVal);
                if (winsComparison)
                {
                    ExecuteCardCapture(game, x, y, nx, ny, attackerPlayerId, activeLaws, out bool remainedOnBoard);
                    captures++;
                    if (remainedOnBoard && flippedCellsOut != null)
                    {
                        flippedCellsOut.Add((nx, ny));
                    }
                }
            }

            return captures;
        }

        private static void ExecuteCardCapture(
            TcgGameLogic game,
            int atkX,
            int atkY,
            int defX,
            int defY,
            int attackerPlayerId,
            JudgeLawType activeLaws,
            out bool remainedOnBoard)
        {
            var attackerCard = game.grid[atkX, atkY].occupant;
            var defenderCard = game.grid[defX, defY].occupant;
            bool chronoLocked = (activeLaws & JudgeLawType.ChronoLock_DisableOncePerGameAbilities) != 0;

            // Phoenix Guardian (Rebirth): returns to original owner's hand unless Chrono-Lock is active
            if (!chronoLocked &&
                defenderCard.specialAbility == SpecialAbilityType.Rebirth &&
                !defenderCard.oncePerGameAbilityUsed)
            {
                defenderCard.oncePerGameAbilityUsed = true;
                game.grid[defX, defY].occupant = null;
                defenderCard.ownerId = defenderCard.originalOwnerId;
                defenderCard.currentZone = ZoneType.Hand;
                game.players[defenderCard.originalOwnerId].hand.Add(defenderCard);
                remainedOnBoard = false;
                return;
            }

            defenderCard.ownerId = attackerPlayerId;
            remainedOnBoard = true;

            // Elemental Sprite (Elemental Burst): swap base stats once per game unless Chrono-Lock is active
            if (!chronoLocked &&
                attackerCard != null &&
                attackerCard.specialAbility == SpecialAbilityType.ElementalBurst &&
                !attackerCard.oncePerGameAbilityUsed)
            {
                attackerCard.oncePerGameAbilityUsed = true;
                (attackerCard.baseStats, defenderCard.baseStats) = (defenderCard.baseStats, attackerCard.baseStats);
            }
        }

        /// <summary>
        /// Evaluates Triple Triad Regional Rules:
        /// - Same: 2 or more orthogonal neighbors have opposing directional stats equal to the placed card's facing stats.
        /// - Plus: 2 or more orthogonal neighbors produce the exact same sum (atkVal + defVal).
        /// Returns the distinct list of adjacent coordinates triggered by Same or Plus.
        /// </summary>
        private static List<(int nx, int ny)> EvaluatePlusAndSameTargets(
            TcgGameLogic game,
            int x,
            int y,
            JudgeLawType activeLaws)
        {
            var triggered = new HashSet<(int, int)>();
            var attackerStats = GetLawModifiedEffectiveStats(game, x, y, activeLaws);

            var sameCandidates = new List<(int nx, int ny)>();
            var sumGroups = new Dictionary<int, List<(int nx, int ny)>>();

            foreach (var (dx, dy) in OrthogonalDirs)
            {
                int nx = x + dx, ny = y + dy;
                if (!game.InBounds(nx, ny) || game.grid[nx, ny].IsEmpty) continue;

                var defenderStats = GetLawModifiedEffectiveStats(game, nx, ny, activeLaws);
                int atkVal = 0, defVal = 0;

                if (dx == 0 && dy == 1)       { atkVal = attackerStats.up;    defVal = defenderStats.down; }
                else if (dx == 0 && dy == -1) { atkVal = attackerStats.down;  defVal = defenderStats.up; }
                else if (dx == -1 && dy == 0) { atkVal = attackerStats.left;  defVal = defenderStats.right; }
                else if (dx == 1 && dy == 0)  { atkVal = attackerStats.right; defVal = defenderStats.left; }

                if (atkVal == defVal)
                {
                    sameCandidates.Add((nx, ny));
                }

                int sum = atkVal + defVal;
                if (!sumGroups.TryGetValue(sum, out var list))
                {
                    list = new List<(int nx, int ny)>();
                    sumGroups[sum] = list;
                }
                list.Add((nx, ny));
            }

            // Same rule triggers when 2 or more adjacent sides match equality
            if (sameCandidates.Count >= 2)
            {
                foreach (var cell in sameCandidates)
                    triggered.Add(cell);
            }

            // Plus rule triggers when 2 or more adjacent sides share an identical sum
            foreach (var kvp in sumGroups)
            {
                if (kvp.Value.Count >= 2)
                {
                    foreach (var cell in kvp.Value)
                        triggered.Add(cell);
                }
            }

            return new List<(int nx, int ny)>(triggered);
        }

        private static void AwardCommendation(
            PlayerState player,
            List<JudgeCommendation> commendationsOut,
            string id,
            string title,
            JudgeLawType law,
            int bonusCp,
            int statMod)
        {
            if (player == null) return;
            player.confidencePoints += bonusCp;
            player.badges.Add(JudgeCommendationBadgePrefix + id);

            var commendation = new JudgeCommendation(id, title, law, bonusCp, statMod);
            commendationsOut?.Add(commendation);
        }
    }
}
