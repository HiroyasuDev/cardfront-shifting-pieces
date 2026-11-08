using System;
using System.Collections.Generic;
using System.Linq;
using Synapse.TcgEngine.Data;

namespace Synapse.TcgEngine.Core
{
    public enum TurnPhase { StartTurn, Draw, Main, EndTurn, GameOver }
    public enum ZoneType { Deck, Hand, Board, Discard, Exile }

    [Serializable]
    public class RuntimeCard
    {
        public string uid;
        public string cardId;
        public string title;
        public string codeName;
        public int ownerId;
        public int originalOwnerId;
        public DirectionalStats baseStats;
        public int permanentStatBonus = 0;
        public CardTheme themes;
        public SpecialAbilityType specialAbility;
        public CardTheme synergyRequiredTheme;
        public int synergyAllSidesBonus;
        public string evolvesToCardId;

        // Ability & status tracking
        public bool oncePerGameAbilityUsed = false;
        public bool movedThisTurn = false;
        public int vanishImmuneTurns = 0;
        public int temporalRiftReversedTurns = 0;
        public int matchesPlayedCount = 0;
        public ZoneType currentZone = ZoneType.Deck;

        public static RuntimeCard FromCardData(CardDataSO so, int ownerId, string uid)
        {
            return new RuntimeCard
            {
                uid = uid,
                cardId = so.id,
                title = so.title,
                codeName = so.codeName,
                ownerId = ownerId,
                originalOwnerId = ownerId,
                baseStats = so.baseStats,
                themes = so.themes,
                specialAbility = so.specialAbility,
                synergyRequiredTheme = so.synergyRequiredTheme,
                synergyAllSidesBonus = so.synergyAllSidesBonus,
                evolvesToCardId = so.evolvesToCardId
            };
        }

        public RuntimeCard Clone() => (RuntimeCard)MemberwiseClone();
    }

    [Serializable]
    public class BoardCell
    {
        public int x;
        public int y;
        public RuntimeCard occupant;
        public bool IsEmpty => occupant == null;
    }

    [Serializable]
    public class PlayerState
    {
        public int playerId;
        public int confidencePoints = 0; // CP from CardCraft
        public int xp = 0;
        public HashSet<string> badges = new HashSet<string>();
        public List<RuntimeCard> deck = new List<RuntimeCard>();
        public List<RuntimeCard> hand = new List<RuntimeCard>();
        public List<RuntimeCard> discard = new List<RuntimeCard>();

        public List<RuntimeCard> GetZone(ZoneType z) => z switch
        {
            ZoneType.Deck => deck,
            ZoneType.Hand => hand,
            ZoneType.Discard => discard,
            _ => discard
        };
    }

    /// <summary>
    /// Core Deterministic Rules Engine for Card Front Tactics: Frontier Legends (PROJECT CF) & CardCraft.
    /// Implements a 3x3 Grid-Based Directional Capture TCG (Up/Down/Left/Right 1-10) with:
    /// - Orthogonal directional comparison & card flipping
    /// - Dynamic Theme/Elemental Adjacency Synergies (+1/+2/+3 all sides)
    /// - All 10 Official PROJECT CF Guardian Frame Special Abilities (Teleport, Charge, HealingAura,
    ///   Vanish, ElementalBurst, WarpDrive, TemporalRift, Rebirth, TechnoStealth, MoonlightBlessing)
    /// - CardCraft Confidence Points (CP), XP, Badge Unlocks, and Card Evolution.
    /// </summary>
    public class TcgGameLogic
    {
        public const int GridWidth = 3;
        public const int GridHeight = 3;
        public const int StartingHandSize = 5;
        public const int MaxHandSize = 7;

        public BoardCell[,] grid = new BoardCell[GridWidth, GridHeight];
        public PlayerState[] players = new PlayerState[2]
        {
            new PlayerState { playerId = 0 },
            new PlayerState { playerId = 1 }
        };

        public int activePlayerId = 0;
        public int turnNumber = 1;
        public bool isNighttime = false; // For Lunar Oracle's Moonlight Blessing
        public int? bonusMovePlayerId = null; // For Mech Knight's Charge second move
        public TurnPhase phase = TurnPhase.StartTurn;
        public int? winnerId = null;
        private readonly System.Random _rng;

        private static readonly (int dx, int dy)[] OrthogonalDirs = new[]
        {
            (0, 1),  // Up    (neighbor's Down opposes our Up)
            (0, -1), // Down  (neighbor's Up opposes our Down)
            (-1, 0), // Left  (neighbor's Right opposes our Left)
            (1, 0)   // Right (neighbor's Left opposes our Right)
        };

        public TcgGameLogic(int seed = 1337, bool isNighttime = false)
        {
            _rng = new System.Random(seed);
            this.isNighttime = isNighttime;
            for (int x = 0; x < GridWidth; x++)
            {
                for (int y = 0; y < GridHeight; y++)
                {
                    grid[x, y] = new BoardCell { x = x, y = y, occupant = null };
                }
            }
        }

        public bool InBounds(int x, int y) => x >= 0 && x < GridWidth && y >= 0 && y < GridHeight;

        public bool HasOrthogonalNeighborWithTheme(int x, int y, CardTheme requiredTheme)
        {
            if (requiredTheme == CardTheme.None) return false;
            foreach (var (dx, dy) in OrthogonalDirs)
            {
                int nx = x + dx, ny = y + dy;
                if (InBounds(nx, ny) && !grid[nx, ny].IsEmpty &&
                    (grid[nx, ny].occupant.themes & requiredTheme) != 0)
                {
                    return true;
                }
            }
            return false;
        }

        /// <summary>
        /// Fast deep clone of the entire game state for multi-depth Alpha-Beta Minimax lookahead.
        /// </summary>
        public TcgGameLogic CloneState()
        {
            var copy = new TcgGameLogic(1337, isNighttime)
            {
                activePlayerId = activePlayerId,
                turnNumber = turnNumber,
                bonusMovePlayerId = bonusMovePlayerId,
                phase = phase,
                winnerId = winnerId
            };

            for (int p = 0; p < 2; p++)
            {
                copy.players[p].playerId = players[p].playerId;
                copy.players[p].confidencePoints = players[p].confidencePoints;
                copy.players[p].xp = players[p].xp;
                foreach (var b in players[p].badges) copy.players[p].badges.Add(b);
                foreach (var c in players[p].deck) copy.players[p].deck.Add(c.Clone());
                foreach (var c in players[p].hand) copy.players[p].hand.Add(c.Clone());
                foreach (var c in players[p].discard) copy.players[p].discard.Add(c.Clone());
            }

            for (int x = 0; x < GridWidth; x++)
            {
                for (int y = 0; y < GridHeight; y++)
                {
                    copy.grid[x, y].occupant = grid[x, y].occupant?.Clone();
                }
            }
            return copy;
        }

        /// <summary>
        /// Computes a deterministic 64-bit FNV-1a hash of the authoritative board & hand state for lockstep verification.
        /// </summary>
        public ulong ComputeStateHash()
        {
            ulong hash = 14695981039346656037UL;
            void Mix(long v)
            {
                hash ^= (ulong)v;
                hash *= 1099511628211UL;
            }

            Mix(activePlayerId);
            Mix(turnNumber);
            Mix((int)phase);
            Mix(winnerId ?? -99);

            for (int x = 0; x < GridWidth; x++)
            {
                for (int y = 0; y < GridHeight; y++)
                {
                    var occ = grid[x, y].occupant;
                    if (occ == null) { Mix(0); continue; }
                    Mix(occ.ownerId + 1);
                    var st = GetEffectiveStats(x, y);
                    Mix((st.up << 24) | (st.down << 16) | (st.left << 8) | st.right);
                }
            }
            return hash;
        }

        /// <summary>
        /// Single-Zone Invariant Move between non-board zones.
        /// </summary>
        public bool MoveCard(PlayerState p, RuntimeCard card, ZoneType fromZone, ZoneType toZone)
        {
            var src = p.GetZone(fromZone);
            var dst = p.GetZone(toZone);
            if (!src.Remove(card)) return false;
            card.currentZone = toZone;
            dst.Add(card);
            return true;
        }

        /// <summary>
        /// Unbiased seeded Fisher-Yates shuffle.
        /// </summary>
        public void ShuffleDeck(PlayerState p)
        {
            for (int i = p.deck.Count - 1; i > 0; i--)
            {
                int j = _rng.Next(0, i + 1);
                (p.deck[i], p.deck[j]) = (p.deck[j], p.deck[i]);
            }
        }

        public void DrawCards(PlayerState p, int count = 1)
        {
            for (int i = 0; i < count; i++)
            {
                if (p.deck.Count == 0) return;
                var top = p.deck[p.deck.Count - 1];
                if (p.hand.Count >= MaxHandSize)
                {
                    MoveCard(p, top, ZoneType.Deck, ZoneType.Discard);
                }
                else
                {
                    MoveCard(p, top, ZoneType.Deck, ZoneType.Hand);
                }
            }
        }

        /// <summary>
        /// Computes a card's live directional stats at (x, y) including:
        /// - Permanent stat bonuses (e.g., Celestial Guardian's Healing Aura)
        /// - Adjacent Theme Synergy (+1/+2/+3 all sides when adjacent to matching theme)
        /// - Lunar Oracle's Moonlight Blessing (+1 all sides at night or adjacent to Lunar card)
        /// - Clockwork Sorcerer's Temporal Rift (reverses Up<->Down and Left<->Right for 1 turn)
        /// </summary>
        public DirectionalStats GetEffectiveStats(int x, int y)
        {
            if (!InBounds(x, y) || grid[x, y].IsEmpty) return default;
            var card = grid[x, y].occupant;
            var stats = card.baseStats.AddAll(card.permanentStatBonus);

            bool hasSynergyNeighbor = false;
            bool hasLunarNeighbor = false;

            foreach (var (dx, dy) in OrthogonalDirs)
            {
                int nx = x + dx, ny = y + dy;
                if (!InBounds(nx, ny) || grid[nx, ny].IsEmpty) continue;
                var neighbor = grid[nx, ny].occupant;

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

            if (hasSynergyNeighbor)
            {
                stats = stats.AddAll(card.synergyAllSidesBonus);
            }

            // 10. Lunar Oracle: Moonlight Blessing (+1 all sides during nighttime or adjacent to Lunar)
            if (card.specialAbility == SpecialAbilityType.MoonlightBlessing && (isNighttime || hasLunarNeighbor))
            {
                stats = stats.AddAll(1);
            }

            // 7. Clockwork Sorcerer: Temporal Rift stat reversal
            if (card.temporalRiftReversedTurns > 0)
            {
                stats = new DirectionalStats(stats.down, stats.up, stats.right, stats.left);
            }

            return stats;
        }

        /// <summary>
        /// Checks whether the card at (x, y) is currently immune to capture via:
        /// - 4. Shadow Assassin (Vanish: immune to capture for 1 turn)
        /// - 9. Cyber Ninja (Techno Stealth: immune to capture when adjacent to a Tech card)
        /// </summary>
        public bool IsCardCaptureImmune(int x, int y)
        {
            if (!InBounds(x, y) || grid[x, y].IsEmpty) return false;
            var card = grid[x, y].occupant;
            if (card.vanishImmuneTurns > 0) return true;

            if (card.specialAbility == SpecialAbilityType.TechnoStealth)
            {
                foreach (var (dx, dy) in OrthogonalDirs)
                {
                    int nx = x + dx, ny = y + dy;
                    if (InBounds(nx, ny) && !grid[nx, ny].IsEmpty &&
                        (grid[nx, ny].occupant.themes & CardTheme.Tech) != 0)
                    {
                        return true;
                    }
                }
            }
            return false;
        }

        /// <summary>
        /// Places a card from player's hand onto grid cell (x, y) and resolves directional captures,
        /// synergies, and special abilities. Returns the number of opponent cards captured.
        /// </summary>
        public bool PlaceCard(int playerId, string cardUid, int x, int y, out int capturedCount)
        {
            capturedCount = 0;
            if (winnerId.HasValue || playerId != activePlayerId || phase != TurnPhase.Main) return false;
            if (!InBounds(x, y) || !grid[x, y].IsEmpty) return false;

            var p = players[playerId];
            var card = p.hand.Find(c => c.uid == cardUid);
            if (card == null) return false;

            // Remove from hand and place on 3x3 board
            p.hand.Remove(card);
            card.currentZone = ZoneType.Board;
            card.ownerId = playerId;
            grid[x, y].occupant = card;
            card.matchesPlayedCount++;

            capturedCount = ResolveCapturesFrom(x, y, playerId);

            // 2. Mech Knight (Charge): If it captures an opponent's card, immediately grant a bonus move
            if (card.specialAbility == SpecialAbilityType.Charge && capturedCount > 0 && HasEmptyCell() && p.hand.Count > 0)
            {
                bonusMovePlayerId = playerId;
            }
            else
            {
                bonusMovePlayerId = null;
                EndTurn();
            }

            return true;
        }

        /// <summary>
        /// Resolves orthogonal directional comparisons around (x, y).
        /// Up compares against (x, y+1).Down; Down against (x, y-1).Up;
        /// Left against (x-1, y).Right; Right against (x+1, y).Left.
        /// </summary>
        public int ResolveCapturesFrom(int x, int y, int attackerPlayerId)
        {
            var attackerCard = grid[x, y].occupant;
            if (attackerCard == null) return 0;

            var attackerStats = GetEffectiveStats(x, y);
            int captures = 0;

            foreach (var (dx, dy) in OrthogonalDirs)
            {
                int nx = x + dx, ny = y + dy;
                if (!InBounds(nx, ny) || grid[nx, ny].IsEmpty) continue;

                var defenderCard = grid[nx, ny].occupant;
                if (defenderCard.ownerId == attackerPlayerId) continue;
                if (IsCardCaptureImmune(nx, ny)) continue;

                var defenderStats = GetEffectiveStats(nx, ny);
                int atkVal = 0, defVal = 0;

                if (dx == 0 && dy == 1)       { atkVal = attackerStats.up;    defVal = defenderStats.down; }
                else if (dx == 0 && dy == -1) { atkVal = attackerStats.down;  defVal = defenderStats.up; }
                else if (dx == -1 && dy == 0) { atkVal = attackerStats.left;  defVal = defenderStats.right; }
                else if (dx == 1 && dy == 0)  { atkVal = attackerStats.right; defVal = defenderStats.left; }

                if (atkVal > defVal)
                {
                    captures++;
                    // 8. Phoenix Guardian (Rebirth): If captured, returns to original owner's hand
                    if (defenderCard.specialAbility == SpecialAbilityType.Rebirth && !defenderCard.oncePerGameAbilityUsed)
                    {
                        defenderCard.oncePerGameAbilityUsed = true;
                        grid[nx, ny].occupant = null;
                        defenderCard.ownerId = defenderCard.originalOwnerId;
                        defenderCard.currentZone = ZoneType.Hand;
                        players[defenderCard.originalOwnerId].hand.Add(defenderCard);
                    }
                    else
                    {
                        defenderCard.ownerId = attackerPlayerId;
                        // 5. Elemental Sprite (Elemental Burst): Swap base stats with captured adjacent card once per game
                        if (attackerCard.specialAbility == SpecialAbilityType.ElementalBurst && !attackerCard.oncePerGameAbilityUsed)
                        {
                            attackerCard.oncePerGameAbilityUsed = true;
                            (attackerCard.baseStats, defenderCard.baseStats) = (defenderCard.baseStats, attackerCard.baseStats);
                        }
                    }
                }
            }

            // Award CardCraft Confidence Points (CP) for captures
            players[attackerPlayerId].confidencePoints += captures * 10;
            return captures;
        }

        /// <summary>
        /// Activates an on-board Special Ability:
        /// - Teleport (Mystic Mage): Once per game, move to any unoccupied space.
        /// - WarpDrive (Galactic Explorer): Once per turn, move to any unoccupied space.
        /// - Vanish (Shadow Assassin): Once per game, immune to capture for 1 turn.
        /// - TemporalRift (Clockwork Sorcerer): Once per game, reverse adjacent cards' stats for 1 turn.
        /// </summary>
        public bool ActivateSpecialAbility(int playerId, int fromX, int fromY, int targetX = -1, int targetY = -1)
        {
            if (!InBounds(fromX, fromY) || grid[fromX, fromY].IsEmpty) return false;
            var card = grid[fromX, fromY].occupant;
            if (card.ownerId != playerId) return false;

            switch (card.specialAbility)
            {
                case SpecialAbilityType.Teleport:
                    if (card.oncePerGameAbilityUsed || !InBounds(targetX, targetY) || !grid[targetX, targetY].IsEmpty)
                        return false;
                    card.oncePerGameAbilityUsed = true;
                    grid[fromX, fromY].occupant = null;
                    grid[targetX, targetY].occupant = card;
                    ResolveCapturesFrom(targetX, targetY, playerId);
                    return true;

                case SpecialAbilityType.WarpDrive:
                    if (card.movedThisTurn || !InBounds(targetX, targetY) || !grid[targetX, targetY].IsEmpty)
                        return false;
                    card.movedThisTurn = true;
                    grid[fromX, fromY].occupant = null;
                    grid[targetX, targetY].occupant = card;
                    ResolveCapturesFrom(targetX, targetY, playerId);
                    return true;

                case SpecialAbilityType.Vanish:
                    if (card.oncePerGameAbilityUsed) return false;
                    card.oncePerGameAbilityUsed = true;
                    card.vanishImmuneTurns = 2;
                    return true;

                case SpecialAbilityType.TemporalRift:
                    if (card.oncePerGameAbilityUsed) return false;
                    card.oncePerGameAbilityUsed = true;
                    foreach (var (dx, dy) in OrthogonalDirs)
                    {
                        int nx = fromX + dx, ny = fromY + dy;
                        if (InBounds(nx, ny) && !grid[nx, ny].IsEmpty)
                        {
                            grid[nx, ny].occupant.temporalRiftReversedTurns = 2;
                        }
                    }
                    return true;

                default:
                    return false;
            }
        }

        public void EndTurn()
        {
            phase = TurnPhase.EndTurn;

            // 3. Celestial Guardian (Healing Aura): Restore +1 strength to adjacent friendly cards at end of turn
            for (int x = 0; x < GridWidth; x++)
            {
                for (int y = 0; y < GridHeight; y++)
                {
                    var c = grid[x, y].occupant;
                    if (c == null) continue;
                    c.movedThisTurn = false;
                    if (c.vanishImmuneTurns > 0) c.vanishImmuneTurns--;
                    if (c.temporalRiftReversedTurns > 0) c.temporalRiftReversedTurns--;

                    if (c.specialAbility == SpecialAbilityType.HealingAura && c.ownerId == activePlayerId)
                    {
                        foreach (var (dx, dy) in OrthogonalDirs)
                        {
                            int nx = x + dx, ny = y + dy;
                            if (InBounds(nx, ny) && !grid[nx, ny].IsEmpty && grid[nx, ny].occupant.ownerId == activePlayerId)
                            {
                                grid[nx, ny].occupant.permanentStatBonus += 1;
                            }
                        }
                    }
                }
            }

            if (IsGameOver())
            {
                phase = TurnPhase.GameOver;
                DetermineWinner();
                return;
            }

            turnNumber++;
            StartTurn(1 - activePlayerId);
        }

        public void StartTurn(int playerId)
        {
            activePlayerId = playerId;
            phase = TurnPhase.StartTurn;
            phase = TurnPhase.Draw;
            DrawCards(players[playerId], 1);
            phase = TurnPhase.Main;
        }

        public bool HasEmptyCell()
        {
            for (int x = 0; x < GridWidth; x++)
                for (int y = 0; y < GridHeight; y++)
                    if (grid[x, y].IsEmpty) return true;
            return false;
        }

        public bool IsGameOver()
        {
            if (!HasEmptyCell()) return true;
            if (players[0].hand.Count == 0 && players[1].hand.Count == 0 &&
                players[0].deck.Count == 0 && players[1].deck.Count == 0)
                return true;
            return false;
        }

        public int CountControlledCards(int playerId)
        {
            int count = 0;
            for (int x = 0; x < GridWidth; x++)
                for (int y = 0; y < GridHeight; y++)
                    if (!grid[x, y].IsEmpty && grid[x, y].occupant.ownerId == playerId)
                        count++;
            return count;
        }

        public void DetermineWinner()
        {
            int p0 = CountControlledCards(0);
            int p1 = CountControlledCards(1);
            if (p0 > p1) winnerId = 0;
            else if (p1 > p0) winnerId = 1;
            else winnerId = -1; // Draw

            // Award CardCraft Post-Match XP & Badges
            if (winnerId >= 0)
            {
                players[winnerId.Value].xp += 100;
                players[winnerId.Value].confidencePoints += 25;
                players[winnerId.Value].badges.Add("Frontier Tactician");
            }
        }
    }
}
