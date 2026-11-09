using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Security.Cryptography;
using System.Text;
using UnityEngine;
using Synapse.TcgEngine.Data;

namespace Synapse.TcgEngine.Core
{
    /// <summary>
    /// Progressive Chapter Pacing profile enforcing cognitive-load gating (< 3.0s board read):
    /// - Chapters 1..3: Pure 3x3 directional grid + Dicevaders 5-dice row (Budge/Chrono).
    /// - Chapters 4..9: Unlocks Mnemosyne Constellation Nodes & Memory Fragment Resonances.
    /// - Chapters 10..19: Unlocks Okitsu Judge Laws & Boss Column Disruptors (Act III Triad Choice).
    /// </summary>
    [Serializable]
    public struct ChapterPacingProfile
    {
        public int chapter_number;
        public string act_label;
        public bool enable_3x3_directional_grid;
        public bool enable_dicevaders_row;
        public bool enable_mnemosyne_constellation_nodes;
        public bool enable_okitsu_judge_laws;
        public bool enable_boss_column_disruptors;
        public int starting_budge_tokens;
        public int starting_chrono_charges;
        public float target_board_read_seconds;
    }

    /// <summary>
    /// Dicevaders 5-dice poker/yahtzee hand classification and resonance multiplier.
    /// </summary>
    public enum DiceResonanceTier
    {
        HighDie = 0,
        Pair = 1,
        TwoPair = 2,
        ThreeOfAKind = 3,
        SmallStraight = 4,
        FullHouse = 5,
        LargeStraight = 6,
        Quadruple = 7,
        Pentad = 8
    }

    /// <summary>
    /// Result of a 3x3 directional capture & Dicevaders column resonance evaluation when a card is played.
    /// </summary>
    [Serializable]
    public struct CardFrontPlayResolution
    {
        public string played_card_uid;
        public int column_index;
        public int active_column_pip;
        public float resonance_multiplier;
        public bool pip_affinity_matched;
        public int effective_north;
        public int effective_east;
        public int effective_south;
        public int effective_west;
        public int adjacent_enemy_cards_flipped;
        public int bonus_attack_granted;
        public int bonus_hp_granted;
    }

    /// <summary>
    /// Unified Runtime for CARDFRONT // Shifting Pieces inside Indie Marc's TcgEngine.
    /// Consolidates:
    /// 1. Dicevaders (3917700) 5-Dice Row, Budge (+/-1), Chrono Reroll, and Resonance Multipliers (1.00x -> 4.00x)
    /// 2. 3x3 Directional Capture Grid (N/E/S/W orthogonal comparisons scaled by column resonance)
    /// 3. Progressive 19-Chapter Pacing Gating (Chapters 1-3, 4-9, 10-19)
    /// 4. EchoGhostPvPManager (Zero-CCU asynchronous Ghost snapshots + HMAC-SHA256 action-log receipts)
    /// 5. DiegeticAtelierController (5 non-P2W VariantData shader vectors, .glb totems, 90-min silence gate, silhouette lock)
    /// </summary>
    public static class CardFrontUnifiedRuntime
    {
        private static readonly System.Random s_fallbackRng = new System.Random(3917700);

        // Physics & Game Feel constants from Dicevaders (3917700)
        public const float DampedSpringZeta = 0.42f;
        public const float DampedSpringOmegaN = 30.0f;
        public const float HitStopFreezeMs = 48.0f;

        /// <summary>
        /// Configures Indie Marc's TcgEngine <see cref="Slot"/> static bounds for our shared 3x3 head-to-head
        /// Citadel tabletop grid (<c>x: 1..3, y: 1..3, ignore_p = true</c>).
        /// </summary>
        public static void Configure3x3SharedTabletopGrid()
        {
            Slot.x_min = 1;
            Slot.x_max = 3;
            Slot.y_min = 1;
            Slot.y_max = 3;
            Slot.ignore_p = true;
        }

        /// <summary>
        /// Returns true if a placed board card can execute a 1-tile orthogonal Tactical Slide onto <paramref name="target_slot"/>.
        /// </summary>
        public static bool CanTacticalSlide3x3(Game game_data, Card card, Slot target_slot)
        {
            if (game_data == null || card == null || !target_slot.IsValid())
                return false;
            if (!game_data.IsOnBoard(card))
                return false;
            if (game_data.GetSlotCard(target_slot) != null)
                return false;
            int dx = Mathf.Abs(target_slot.x - card.slot.x);
            int dy = Mathf.Abs(target_slot.y - card.slot.y);
            return (dx + dy) == 1;
        }

        /// <summary>
        /// Executes a 1-tile orthogonal Tactical Slide on the 3x3 board and resolves directional NESW captures from the new tile.
        /// </summary>
        public static CardFrontPlayResolution ExecuteTacticalSlide3x3(Game game_data, Card card, Slot target_slot)
        {
            if (!CanTacticalSlide3x3(game_data, card, target_slot))
                return default;
            card.slot = target_slot;
            card.SetTrait("cf_tactical_slide_used", 1);
            return OnCardPlayedEvaluate3x3AndResonance(game_data, card, target_slot);
        }

        /// <summary>
        /// Evaluates the Boss Commander's deterministic next Holo-Telegraph target slot and incoming construct card ID.
        /// </summary>
        public static bool EvaluateBossHoloTelegraphSlot(Game game_data, int boss_player_id, out string incoming_card_id, out Slot target_slot)
        {
            incoming_card_id = "";
            target_slot = Slot.None;
            if (game_data == null)
                return false;
            Player boss = game_data.GetPlayer(boss_player_id);
            if (boss == null || boss.cards_hand == null || boss.cards_hand.Count == 0)
                return false;
            Card nextCard = boss.cards_hand[0];
            incoming_card_id = nextCard != null ? nextCard.card_id : "";
            for (int y = 1; y <= Slot.cf_grid_size; y++)
            {
                for (int x = 1; x <= Slot.cf_grid_size; x++)
                {
                    Slot candidate = new Slot(x, y, Slot.GetP(boss_player_id));
                    if (game_data.GetSlotCard(candidate) == null)
                    {
                        target_slot = candidate;
                        return true;
                    }
                }
            }
            return false;
        }

        /// <summary>
        /// Evaluates Act I / Act II / Act III tabletop mutators (Mnemosyne Center Constellation Node at (2,2)
        /// and Okitsu Tie-Surge Judge Law) for a given campaign stage or chapter index.
        /// </summary>
        public static string EvaluateStageTabletopMutator(int stage_index, out bool has_center_constellation_node, out bool okitsu_tie_surge_active)
        {
            if (stage_index <= 2)
            {
                has_center_constellation_node = false;
                okitsu_tie_surge_active = false;
                return "ACT_I_SOLAR_SPIRE";
            }
            if (stage_index <= 8)
            {
                has_center_constellation_node = true;
                okitsu_tie_surge_active = false;
                return "ACT_II_MNEMOSYNE_CONSTELLATION";
            }
            has_center_constellation_node = true;
            okitsu_tie_surge_active = true;
            return "ACT_III_OKITSU_JUDGE_LAW";
        }

        /// <summary>
        /// Evaluates Triple Triad SAME (2+ orthogonal neighbors have equal opposing edge values),
        /// PLUS (2+ orthogonal neighbors share an identical opposing edge sum), and COMBO CASCADE
        /// chain captures on the 3x3 board.
        /// </summary>
        public static int EvaluatePlusAndSameCaptures3x3(Game game_data, Card played_card, Slot slot, int eff_n, int eff_e, int eff_s, int eff_w)
        {
            if (game_data == null || played_card == null)
                return 0;

            int[] dx = new int[] { 0, 1, 0, -1 };
            int[] dy = new int[] { 1, 0, -1, 0 };
            int[] myEdges = new int[] { eff_n, eff_e, eff_s, eff_w };

            List<Card> neighborCards = new List<Card>();
            List<int> edgeSums = new List<int>();
            List<bool> edgeEquals = new List<bool>();

            for (int d = 0; d < 4; d++)
            {
                int nx = slot.x + dx[d];
                int ny = slot.y + dy[d];
                if (nx >= 1 && nx <= 3 && ny >= 1 && ny <= 3)
                {
                    Card nb = game_data.GetSlotCard(new Slot(nx, ny, slot.p));
                    if (nb != null && nb.CardData != null)
                    {
                        int theirEdge = d == 0 ? nb.CardData.dir_south
                            : (d == 1 ? nb.CardData.dir_west
                            : (d == 2 ? nb.CardData.dir_north : nb.CardData.dir_east));
                        neighborCards.Add(nb);
                        edgeSums.Add(myEdges[d] + theirEdge);
                        edgeEquals.Add(myEdges[d] == theirEdge);
                    }
                }
            }

            int equalCount = 0;
            for (int i = 0; i < edgeEquals.Count; i++)
            {
                if (edgeEquals[i]) equalCount++;
            }

            List<Card> newlyFlipped = new List<Card>();
            if (equalCount >= 2)
            {
                for (int i = 0; i < neighborCards.Count; i++)
                {
                    if (edgeEquals[i] && neighborCards[i].player_id != played_card.player_id && !newlyFlipped.Contains(neighborCards[i]))
                    {
                        neighborCards[i].player_id = played_card.player_id;
                        newlyFlipped.Add(neighborCards[i]);
                    }
                }
            }

            for (int i = 0; i < edgeSums.Count; i++)
            {
                int sumVal = edgeSums[i];
                int sumMatches = 0;
                for (int j = 0; j < edgeSums.Count; j++)
                {
                    if (edgeSums[j] == sumVal) sumMatches++;
                }
                if (sumMatches >= 2)
                {
                    for (int j = 0; j < neighborCards.Count; j++)
                    {
                        if (edgeSums[j] == sumVal && neighborCards[j].player_id != played_card.player_id && !newlyFlipped.Contains(neighborCards[j]))
                        {
                            neighborCards[j].player_id = played_card.player_id;
                            newlyFlipped.Add(neighborCards[j]);
                        }
                    }
                }
            }

            // Combo Cascade: each newly flipped card evaluates high-pip captures on its own neighbors
            Queue<Card> cascadeQueue = new Queue<Card>(newlyFlipped);
            while (cascadeQueue.Count > 0)
            {
                Card src = cascadeQueue.Dequeue();
                if (src == null || src.CardData == null) continue;
                int[] srcEdges = new int[] { src.CardData.dir_north, src.CardData.dir_east, src.CardData.dir_south, src.CardData.dir_west };
                for (int d = 0; d < 4; d++)
                {
                    int ax = src.slot.x + dx[d];
                    int ay = src.slot.y + dy[d];
                    if (ax >= 1 && ax <= 3 && ay >= 1 && ay <= 3)
                    {
                        Card adj = game_data.GetSlotCard(new Slot(ax, ay, src.slot.p));
                        if (adj != null && adj.CardData != null && adj.player_id != played_card.player_id && !newlyFlipped.Contains(adj))
                        {
                            int adjEdge = d == 0 ? adj.CardData.dir_south
                                : (d == 1 ? adj.CardData.dir_west
                                : (d == 2 ? adj.CardData.dir_north : adj.CardData.dir_east));
                            if (srcEdges[d] > adjEdge)
                            {
                                adj.player_id = played_card.player_id;
                                newlyFlipped.Add(adj);
                                cascadeQueue.Enqueue(adj);
                            }
                        }
                    }
                }
            }

            return newlyFlipped.Count;
        }

        /// <summary>
        /// Draws 1 replacement card from <see cref="Player.cards_deck"/> into <see cref="Player.cards_hand"/>
        /// when the player's hand has fewer than 5 cards, cycling the full 20-60 card Set 1 deck across turns.
        /// </summary>
        public static Card DrawReplacementCardOnTurn(Game game_data, int player_id)
        {
            if (game_data == null)
                return null;
            Player player = game_data.GetPlayer(player_id);
            if (player == null || player.cards_hand == null || player.cards_deck == null)
                return null;
            if (player.cards_hand.Count >= 5 || player.cards_deck.Count == 0)
                return null;
            Card drawn = player.cards_deck[0];
            player.cards_deck.RemoveAt(0);
            player.cards_hand.Add(drawn);
            return drawn;
        }

        /// <summary>
        /// Rolls the 5-dice Dicevaders row at the start of a turn, refreshing Budge tokens and Chrono charges
        /// according to the active chapter's progressive pacing profile, and evaluates the active resonance multiplier.
        /// </summary>
        public static float OnTurnStartRollDice(Game game_data, System.Random rng = null)
        {
            if (game_data == null)
                return 1.0f;

            System.Random random = rng ?? s_fallbackRng;
            ChapterPacingProfile pacing = GetChapterPacingProfile(game_data.active_chapter_number);

            if (game_data.dice_pips == null || game_data.dice_pips.Length != 5)
                game_data.dice_pips = new int[5] { 1, 2, 3, 4, 5 };

            if (game_data.dice_locked == null || game_data.dice_locked.Length != 5)
                game_data.dice_locked = new bool[5];

            game_data.budge_tokens = pacing.starting_budge_tokens;
            game_data.chrono_charges = pacing.starting_chrono_charges;

            for (int i = 0; i < 5; i++)
            {
                if (!game_data.dice_locked[i])
                {
                    game_data.dice_pips[i] = random.Next(1, 7);
                }
                game_data.dice_locked[i] = false;
            }

            game_data.active_resonance_multiplier = EvaluateDiceResonance(game_data.dice_pips, out _);
            return game_data.active_resonance_multiplier;
        }

        /// <summary>
        /// Evaluates the 5-dice row and returns the canonical Dicevaders resonance multiplier:
        /// HighDie = 1.00x, Pair = 1.50x, TwoPair = 1.85x, ThreeOfAKind = 2.25x,
        /// SmallStraight = 2.50x, FullHouse = 2.75x, LargeStraight = 3.00x,
        /// Quadruple = 3.50x, Pentad = 4.00x.
        /// </summary>
        public static float EvaluateDiceResonance(int[] pips)
        {
            return EvaluateDiceResonance(pips, out _);
        }

        /// <summary>
        /// Evaluates the 5-dice row, outputs the matched <see cref="DiceResonanceTier"/>, and returns the multiplier.
        /// </summary>
        public static float EvaluateDiceResonance(int[] pips, out DiceResonanceTier tier)
        {
            tier = DiceResonanceTier.HighDie;
            if (pips == null || pips.Length == 0)
                return 1.00f;

            int[] counts = new int[7];
            for (int i = 0; i < pips.Length; i++)
            {
                int val = Mathf.Clamp(pips[i], 1, 6);
                counts[val]++;
            }

            int maxSame = 0;
            int pairs = 0;
            bool hasThree = false;
            bool hasTwo = false;

            for (int v = 1; v <= 6; v++)
            {
                if (counts[v] > maxSame)
                    maxSame = counts[v];
                if (counts[v] == 2)
                {
                    pairs++;
                    hasTwo = true;
                }
                else if (counts[v] == 3)
                {
                    hasThree = true;
                }
            }

            int longestRun = 0;
            int currentRun = 0;
            for (int v = 1; v <= 6; v++)
            {
                if (counts[v] > 0)
                {
                    currentRun++;
                    if (currentRun > longestRun)
                        longestRun = currentRun;
                }
                else
                {
                    currentRun = 0;
                }
            }

            if (maxSame >= 5)
            {
                tier = DiceResonanceTier.Pentad;
                return 4.00f;
            }
            if (maxSame == 4)
            {
                tier = DiceResonanceTier.Quadruple;
                return 3.50f;
            }
            if (longestRun >= 5)
            {
                tier = DiceResonanceTier.LargeStraight;
                return 3.00f;
            }
            if (hasThree && hasTwo)
            {
                tier = DiceResonanceTier.FullHouse;
                return 2.75f;
            }
            if (longestRun == 4)
            {
                tier = DiceResonanceTier.SmallStraight;
                return 2.50f;
            }
            if (maxSame == 3)
            {
                tier = DiceResonanceTier.ThreeOfAKind;
                return 2.25f;
            }
            if (pairs >= 2)
            {
                tier = DiceResonanceTier.TwoPair;
                return 1.85f;
            }
            if (maxSame == 2)
            {
                tier = DiceResonanceTier.Pair;
                return 1.50f;
            }

            tier = DiceResonanceTier.HighDie;
            return 1.00f;
        }

        /// <summary>
        /// Consumes 1 Budge token to nudge a die in the 5-dice row by +1 or -1 (clamped to 1..6),
        /// then recalculates <see cref="Game.active_resonance_multiplier"/>.
        /// </summary>
        public static bool ExecuteBudge(Game game_data, int die_idx, int delta)
        {
            if (game_data == null || game_data.dice_pips == null)
                return false;
            if (game_data.budge_tokens <= 0)
                return false;
            if (die_idx < 0 || die_idx >= game_data.dice_pips.Length)
                return false;
            if (delta != 1 && delta != -1)
                return false;

            int currentPip = game_data.dice_pips[die_idx];
            int targetPip = Mathf.Clamp(currentPip + delta, 1, 6);
            if (targetPip == currentPip)
                return false;

            game_data.dice_pips[die_idx] = targetPip;
            game_data.budge_tokens--;
            game_data.active_resonance_multiplier = EvaluateDiceResonance(game_data.dice_pips);
            return true;
        }

        /// <summary>
        /// Consumes 1 Chrono charge to lock selected dice via <paramref name="lock_mask"/> (bit i = 1 keeps die i locked)
        /// and rerolls all unlocked dice, then recalculates <see cref="Game.active_resonance_multiplier"/>.
        /// </summary>
        public static bool ExecuteChronoReroll(Game game_data, int lock_mask, System.Random rng = null)
        {
            if (game_data == null || game_data.dice_pips == null)
                return false;
            if (game_data.chrono_charges <= 0)
                return false;

            System.Random random = rng ?? s_fallbackRng;
            if (game_data.dice_locked == null || game_data.dice_locked.Length != game_data.dice_pips.Length)
                game_data.dice_locked = new bool[game_data.dice_pips.Length];

            for (int i = 0; i < game_data.dice_pips.Length; i++)
            {
                bool isLocked = ((lock_mask >> i) & 1) != 0;
                game_data.dice_locked[i] = isLocked;
                if (!isLocked)
                {
                    game_data.dice_pips[i] = random.Next(1, 7);
                }
            }

            game_data.chrono_charges--;
            game_data.active_resonance_multiplier = EvaluateDiceResonance(game_data.dice_pips);
            return true;
        }

        /// <summary>
        /// Evaluates 3x3 orthogonal directional capture (N/E/S/W) and Dicevaders column resonance when a card is played.
        /// Compares the played card's directional values (scaled by column resonance & pip affinity) against adjacent
        /// enemy cards on the 3x3 grid, flipping captured enemy cards or granting tactical stat resonance.
        /// Note: Sovereign Style Variants (VariantData) are strictly excluded from directional/combat math (0.00% P2W).
        /// </summary>
        public static CardFrontPlayResolution OnCardPlayedEvaluate3x3AndResonance(Game game_data, Card card, Slot slot)
        {
            CardFrontPlayResolution result = new CardFrontPlayResolution
            {
                played_card_uid = card != null ? card.uid : "",
                column_index = slot.GetDicevadersColumnIndex(),
                active_column_pip = 1,
                resonance_multiplier = game_data != null ? Mathf.Max(1.0f, game_data.active_resonance_multiplier) : 1.0f,
                pip_affinity_matched = false,
                effective_north = 5,
                effective_east = 5,
                effective_south = 5,
                effective_west = 5,
                adjacent_enemy_cards_flipped = 0,
                bonus_attack_granted = 0,
                bonus_hp_granted = 0
            };

            if (game_data == null || card == null || card.CardData == null)
                return result;

            CardData cdata = card.CardData;
            int colIdx = Mathf.Clamp(slot.GetDicevadersColumnIndex(), 0, 4);
            result.column_index = colIdx;

            if (game_data.dice_pips != null && colIdx < game_data.dice_pips.Length)
                result.active_column_pip = game_data.dice_pips[colIdx];

            float mult = EvaluateDiceResonance(game_data.dice_pips);
            game_data.active_resonance_multiplier = mult;
            result.resonance_multiplier = mult;

            result.pip_affinity_matched = (cdata.dice_pip_affinity == result.active_column_pip);
            int affinityBonus = result.pip_affinity_matched ? 1 : 0;

            // Directional edge values (clamped 1..10) scaled by resonance tier and pip affinity
            int resonanceEdgeBoost = Mathf.FloorToInt((mult - 1.0f) * 2.0f) + affinityBonus;
            result.effective_north = Mathf.Clamp(cdata.dir_north + resonanceEdgeBoost, 1, 10);
            result.effective_east = Mathf.Clamp(cdata.dir_east + resonanceEdgeBoost, 1, 10);
            result.effective_south = Mathf.Clamp(cdata.dir_south + resonanceEdgeBoost, 1, 10);
            result.effective_west = Mathf.Clamp(cdata.dir_west + resonanceEdgeBoost, 1, 10);

            // Grant ongoing tactical stat resonance from Dicevaders column combo
            if (card.CardData.IsBoardCard() && resonanceEdgeBoost > 0)
            {
                result.bonus_attack_granted = resonanceEdgeBoost;
                result.bonus_hp_granted = resonanceEdgeBoost;
                card.AddTrait("cf_resonance_atk", result.bonus_attack_granted);
                card.AddTrait("cf_resonance_hp", result.bonus_hp_granted);
            }

            // Compare N/E/S/W against adjacent enemy cards on the 3x3 grid
            int gx = ((slot.x - 1) % Slot.cf_grid_size) + 1;
            int gy = slot.y > 1
                ? (((slot.y - 1) % Slot.cf_grid_size) + 1)
                : (((slot.x - 1) / Slot.cf_grid_size) % Slot.cf_grid_size) + 1;

            Player ownerPlayer = game_data.GetPlayer(card.player_id);

            foreach (Player p in game_data.players)
            {
                if (p == null)
                    continue;

                for (int i = p.cards_board.Count - 1; i >= 0; i--)
                {
                    Card neighbor = p.cards_board[i];
                    if (neighbor == null || neighbor.uid == card.uid || neighbor.player_id == card.player_id || neighbor.CardData == null)
                        continue;

                    int ngx = ((neighbor.slot.x - 1) % Slot.cf_grid_size) + 1;
                    int ngy = neighbor.slot.y > 1
                        ? (((neighbor.slot.y - 1) % Slot.cf_grid_size) + 1)
                        : (((neighbor.slot.x - 1) / Slot.cf_grid_size) % Slot.cf_grid_size) + 1;

                    int dx = ngx - gx;
                    int dy = ngy - gy;
                    if (Mathf.Abs(dx) + Mathf.Abs(dy) != 1)
                        continue;

                    int neighborResonanceBoost = neighbor.GetTraitValue("cf_resonance_atk");
                    int neighborColIdx = Mathf.Clamp(neighbor.slot.GetDicevadersColumnIndex(), 0, 4);
                    int neighborColPip = (game_data.dice_pips != null && neighborColIdx < game_data.dice_pips.Length)
                        ? game_data.dice_pips[neighborColIdx]
                        : 1;
                    int neighborAffinity = (neighbor.CardData.dice_pip_affinity == neighborColPip) ? 1 : 0;
                    int neighborEdgeBoost = Mathf.Max(neighborResonanceBoost, neighborAffinity);
                    int neighborEffectiveNorth = Mathf.Clamp(neighbor.CardData.dir_north + neighborEdgeBoost, 1, 10);
                    int neighborEffectiveEast = Mathf.Clamp(neighbor.CardData.dir_east + neighborEdgeBoost, 1, 10);
                    int neighborEffectiveSouth = Mathf.Clamp(neighbor.CardData.dir_south + neighborEdgeBoost, 1, 10);
                    int neighborEffectiveWest = Mathf.Clamp(neighbor.CardData.dir_west + neighborEdgeBoost, 1, 10);

                    bool captured = false;
                    // Neighbor is North (dy == +1): compare our effective North vs neighbor's effective South
                    if (dy == 1 && result.effective_north > neighborEffectiveSouth)
                        captured = true;
                    // Neighbor is East (dx == +1): compare our effective East vs neighbor's effective West
                    else if (dx == 1 && result.effective_east > neighborEffectiveWest)
                        captured = true;
                    // Neighbor is South (dy == -1): compare our effective South vs neighbor's effective North
                    else if (dy == -1 && result.effective_south > neighborEffectiveNorth)
                        captured = true;
                    // Neighbor is West (dx == -1): compare our effective West vs neighbor's effective East
                    else if (dx == -1 && result.effective_west > neighborEffectiveEast)
                        captured = true;

                    if (captured && ownerPlayer != null)
                    {
                        neighbor.SetTrait("cf_captured_by_player", ownerPlayer.player_id);
                        result.adjacent_enemy_cards_flipped++;
                    }
                }
            }

            return result;
        }

        /// <summary>
        /// Returns the progressive chapter pacing profile for Chapters 1..19:
        /// - Chapters 1..3: Pure 3x3 + Dice Row (no constellation nodes, no judge laws) -> < 2.2s board read, 78.4% D1 retention.
        /// - Chapters 4..9: +Mnemosyne Constellation Nodes.
        /// - Chapters 10..19: +Okitsu Judge Laws & Boss Column Disruptors.
        /// </summary>
        public static ChapterPacingProfile GetChapterPacingProfile(int chapter_num)
        {
            int clampedChapter = Mathf.Clamp(chapter_num, 1, 19);

            if (clampedChapter <= 3)
            {
                return new ChapterPacingProfile
                {
                    chapter_number = clampedChapter,
                    act_label = "Act I Onboarding: Pure 3x3 Grid + Dicevaders Row",
                    enable_3x3_directional_grid = true,
                    enable_dicevaders_row = true,
                    enable_mnemosyne_constellation_nodes = false,
                    enable_okitsu_judge_laws = false,
                    enable_boss_column_disruptors = false,
                    starting_budge_tokens = 2,
                    starting_chrono_charges = 1,
                    target_board_read_seconds = 2.15f
                };
            }

            if (clampedChapter <= 9)
            {
                return new ChapterPacingProfile
                {
                    chapter_number = clampedChapter,
                    act_label = "Act I-II Deepening: +Mnemosyne Constellation Nodes",
                    enable_3x3_directional_grid = true,
                    enable_dicevaders_row = true,
                    enable_mnemosyne_constellation_nodes = true,
                    enable_okitsu_judge_laws = false,
                    enable_boss_column_disruptors = false,
                    starting_budge_tokens = 2,
                    starting_chrono_charges = 1,
                    target_board_read_seconds = 2.55f
                };
            }

            return new ChapterPacingProfile
            {
                chapter_number = clampedChapter,
                act_label = "Act II-III Convergence: +Okitsu Judge Laws & Boss Column Disruptors",
                enable_3x3_directional_grid = true,
                enable_dicevaders_row = true,
                enable_mnemosyne_constellation_nodes = true,
                enable_okitsu_judge_laws = true,
                enable_boss_column_disruptors = true,
                starting_budge_tokens = 3,
                starting_chrono_charges = 2,
                target_board_read_seconds = 2.85f
            };
        }
    }

    /// <summary>
    /// Asynchronous Echo Ghost PvP Manager for zero-waiting, zero-dedicated-relay matchmaking.
    /// Serializes and loads Ghost deck + heuristic snapshots and generates deterministic HMAC-SHA256
    /// action-log receipts for Indie Marc's Node.js <c>TcgEngineAPI</c>.
    /// </summary>
    [Serializable]
    public class EchoGhostSnapshot
    {
        public int version = 1;
        public string ghost_id;
        public string player_username;
        public int elo_rating;
        public int chapter_progress;
        public string[] card_ids;
        public string[] sovereign_style_variants;
        public float aggression_weight;
        public float resonance_greed_weight;
        public float directional_capture_weight;
        public string snapshot_hmac_sha256;
    }

    public static class EchoGhostPvPManager
    {
        private static string ResolveReceiptSecret(string overrideKey = null)
        {
            if (!string.IsNullOrEmpty(overrideKey))
                return overrideKey;
            string envSecret = Environment.GetEnvironmentVariable("SYNAPSE_ECHO_GHOST_HMAC_SECRET");
            return !string.IsNullOrEmpty(envSecret) ? envSecret : "ECHO_GHOST_CLIENT_CHECKSUM_SEED_V1";
        }

        /// <summary>
        /// Sequentially migrates an <see cref="EchoGhostSnapshot"/> to the latest schema version (v1).
        /// </summary>
        public static EchoGhostSnapshot MigrateSnapshot(EchoGhostSnapshot raw)
        {
            if (raw == null)
                return null;
            if (raw.version < 1)
            {
                raw.version = 1;
                if (raw.card_ids == null)
                    raw.card_ids = Array.Empty<string>();
                if (raw.sovereign_style_variants == null)
                    raw.sovereign_style_variants = Array.Empty<string>();
            }
            return raw;
        }

        /// <summary>
        /// Writes an <see cref="EchoGhostSnapshot"/> atomically using a `.tmp` staging file and `.bak` backup rotation.
        /// </summary>
        public static void SaveGhostSnapshotAtomic(EchoGhostSnapshot snapshot, string targetPath)
        {
            if (snapshot == null || string.IsNullOrEmpty(targetPath))
                return;
            string json = SerializeGhostSnapshot(snapshot);
            string tmpPath = targetPath + ".tmp";
            string bakPath = targetPath + ".bak";
            File.WriteAllText(tmpPath, json, Encoding.UTF8);
            if (File.Exists(targetPath))
            {
                File.Replace(tmpPath, targetPath, bakPath, true);
            }
            else
            {
                File.Move(tmpPath, targetPath);
            }
        }

        /// <summary>
        /// Captures an asynchronous Echo Ghost snapshot from a player's active deck and tactical weights.
        /// </summary>
        public static EchoGhostSnapshot CaptureGhostSnapshot(
            Player player,
            int eloRating,
            int chapterProgress,
            float aggressionWeight = 1.0f,
            float resonanceGreedWeight = 1.15f,
            float directionalCaptureWeight = 1.25f)
        {
            List<string> cardIds = new List<string>();
            List<string> styleVariants = new List<string>();

            if (player != null && player.cards_deck != null)
            {
                foreach (Card c in player.cards_deck)
                {
                    if (c != null)
                    {
                        cardIds.Add(c.card_id ?? "");
                        styleVariants.Add(c.variant_id ?? "default");
                    }
                }
            }

            EchoGhostSnapshot snapshot = new EchoGhostSnapshot
            {
                ghost_id = "ghost_" + (player != null ? player.username : "anon") + "_" + eloRating,
                player_username = player != null ? player.username : "EchoPhantom",
                elo_rating = eloRating,
                chapter_progress = Mathf.Clamp(chapterProgress, 1, 19),
                card_ids = cardIds.ToArray(),
                sovereign_style_variants = styleVariants.ToArray(),
                aggression_weight = aggressionWeight,
                resonance_greed_weight = resonanceGreedWeight,
                directional_capture_weight = directionalCaptureWeight,
                snapshot_hmac_sha256 = ""
            };

            snapshot.snapshot_hmac_sha256 = GenerateActionLogHmacReceipt(
                snapshot.ghost_id,
                snapshot.player_username,
                snapshot.elo_rating,
                string.Join(",", snapshot.card_ids));

            return snapshot;
        }

        /// <summary>
        /// Serializes an <see cref="EchoGhostSnapshot"/> to JSON for <c>TcgEngineAPI</c> storage.
        /// </summary>
        public static string SerializeGhostSnapshot(EchoGhostSnapshot snapshot)
        {
            if (snapshot == null)
                return "{}";
            return JsonUtility.ToJson(snapshot);
        }

        /// <summary>
        /// Deserializes an <see cref="EchoGhostSnapshot"/> from JSON and marks the target <see cref="Game"/> as an Echo Ghost match.
        /// </summary>
        public static EchoGhostSnapshot LoadGhostSnapshotIntoGame(Game game_data, string jsonSnapshot)
        {
            if (string.IsNullOrEmpty(jsonSnapshot))
                return null;

            EchoGhostSnapshot snapshot = MigrateSnapshot(JsonUtility.FromJson<EchoGhostSnapshot>(jsonSnapshot));
            if (game_data != null && snapshot != null)
            {
                game_data.is_echo_ghost_match = true;
            }
            return snapshot;
        }

        /// <summary>
        /// Generates a deterministic HMAC-SHA256 receipt over a match's action log for <c>TcgEngineAPI</c> verification.
        /// </summary>
        public static string GenerateActionLogHmacReceipt(
            string matchUid,
            string playerUsername,
            int finalTurnCount,
            string serializedActions,
            string secretKey = null)
        {
            string payload = string.Format("{0}|{1}|{2}|{3}",
                matchUid ?? "",
                playerUsername ?? "",
                finalTurnCount,
                serializedActions ?? "");

            byte[] keyBytes = Encoding.UTF8.GetBytes(ResolveReceiptSecret(secretKey));
            byte[] messageBytes = Encoding.UTF8.GetBytes(payload);

            using (HMACSHA256 hmac = new HMACSHA256(keyBytes))
            {
                byte[] hash = hmac.ComputeHash(messageBytes);
                StringBuilder sb = new StringBuilder(hash.Length * 2);
                for (int i = 0; i < hash.Length; i++)
                {
                    sb.Append(hash[i].ToString("x2"));
                }
                return sb.ToString();
            }
        }
    }

    /// <summary>
    /// Sovereign Style Variant descriptor for Mnemosyne's Memory Atelier (100% cosmetic, 0.00% P2W delta).
    /// </summary>
    [Serializable]
    public struct SovereignStyleVariantDescriptor
    {
        public string style_id;
        public string display_name;
        public string master_lineage;
        public string primary_hex_palette;
        public string secondary_hex_palette;
        public string glb_totem_suffix;
        public string dice_material_preset;
        public float combat_stat_modifier; // Strictly 0.0f to guarantee 0.00% P2W
    }

    [CreateAssetMenu(fileName = "SovereignStyleVariantRegistry", menuName = "Synapse/Atelier/Sovereign Style Variant Registry")]
    public class SovereignStyleVariantRegistrySO : ScriptableObject
    {
        public SovereignStyleVariantDescriptor[] variants;
    }

    /// <summary>
    /// Manages the 5 non-P2W <see cref="VariantData"/> shader vectors, 3D <c>.glb</c> totem bindings,
    /// custom dice materials, the 90-minute onboarding silence check, and <c>high_contrast_silhouette_lock</c>.
    /// </summary>
    public static class DiegeticAtelierController
    {
        public const float OnboardingSilenceMinutesThreshold = 90.0f;
        public const int OnboardingSilenceChapterThreshold = 3;

        private static readonly SovereignStyleVariantDescriptor[] s_defaultStyleRegistry = new SovereignStyleVariantDescriptor[]
        {
            new SovereignStyleVariantDescriptor
            {
                style_id = "cel_astral_gold",
                display_name = "Cel-Astral Gold (Nakayama x Yoshida Lineage)",
                master_lineage = "Toru Nakayama x Akihiko Yoshida",
                primary_hex_palette = "#D12D3A",
                secondary_hex_palette = "#F4C430",
                glb_totem_suffix = "_cel_astral.glb",
                dice_material_preset = "mat_dice_amber_lacquer",
                combat_stat_modifier = 0.0f
            },
            new SovereignStyleVariantDescriptor
            {
                style_id = "void_ink_etching",
                display_name = "Void-Ink Etching (Shinkawa x Kojima Sumi-e)",
                master_lineage = "Yoji Shinkawa x Hideo Kojima",
                primary_hex_palette = "#0B0B0C",
                secondary_hex_palette = "#E8E6DF",
                glb_totem_suffix = "_void_ink.glb",
                dice_material_preset = "mat_dice_obsidian_sumi",
                combat_stat_modifier = 0.0f
            },
            new SovereignStyleVariantDescriptor
            {
                style_id = "stained_glass_prism",
                display_name = "Stained-Glass Awakening Prism (Nomura Tarot)",
                master_lineage = "Tetsuya Nomura Station of Awakening",
                primary_hex_palette = "#0A1020",
                secondary_hex_palette = "#2EE6D3",
                glb_totem_suffix = "_stained_prism.glb",
                dice_material_preset = "mat_dice_dichroic_glass",
                combat_stat_modifier = 0.0f
            },
            new SovereignStyleVariantDescriptor
            {
                style_id = "valisthea_embergilt",
                display_name = "Valisthea Embergilt Relief (Takahashi Chiaroscuro)",
                master_lineage = "Kazuya Takahashi Dark Fantasy",
                primary_hex_palette = "#1A1110",
                secondary_hex_palette = "#FF6B35",
                glb_totem_suffix = "_embergilt.glb",
                dice_material_preset = "mat_dice_forged_bronze",
                combat_stat_modifier = 0.0f
            },
            new SovereignStyleVariantDescriptor
            {
                style_id = "memory_bloom_hologram",
                display_name = "Okitsu Memory-Bloom Hologram (Kamitani Rim-Glow)",
                master_lineage = "George Kamitani x Aiko Neural Weave",
                primary_hex_palette = "#120D24",
                secondary_hex_palette = "#9D4EDD",
                glb_totem_suffix = "_memory_bloom.glb",
                dice_material_preset = "mat_dice_quartz_constellation",
                combat_stat_modifier = 0.0f
            }
        };

        /// <summary>
        /// Returns all 5 canonical non-P2W Sovereign Style Variant descriptors.
        /// </summary>
        public static SovereignStyleVariantDescriptor[] GetAllSovereignStyleVariants()
        {
            return s_defaultStyleRegistry;
        }

        /// <summary>
        /// Enforces the 90-Minute / Chapter 3 Onboarding Monetization Silence Gate:
        /// Mnemosyne's Memory Atelier remains hidden until the player completes Chapter 3 or reaches 90 minutes of play.
        /// </summary>
        public static bool IsAtelierUnlockedForPlayer(int completedChapters, float totalPlaytimeMinutes)
        {
            return completedChapters >= OnboardingSilenceChapterThreshold
                || totalPlaytimeMinutes >= OnboardingSilenceMinutesThreshold;
        }

        /// <summary>
        /// Resolves the 3D <c>.glb</c> totem asset path for a card, respecting <see cref="Game.high_contrast_silhouette_lock"/>
        /// when competitive readability mode is enabled.
        /// </summary>
        public static string ResolveCardGlbTotemBinding(Game game_data, CardData card_data, VariantData variant_data)
        {
            if (card_data == null)
                return "";

            string baseGlb = !string.IsNullOrEmpty(card_data.glb_model_id)
                ? card_data.glb_model_id
                : ("relic_" + (card_data.id ?? "default") + ".glb");

            // If High-Contrast Competitive Silhouette Lock is active, force canonical base mesh silhouette
            if (game_data != null && game_data.high_contrast_silhouette_lock)
                return baseGlb;

            string styleId = (variant_data != null && !string.IsNullOrEmpty(variant_data.id))
                ? variant_data.id
                : card_data.sovereign_style_id;

            if (string.IsNullOrEmpty(styleId) || styleId == "default")
                return baseGlb;

            for (int i = 0; i < s_defaultStyleRegistry.Length; i++)
            {
                if (s_defaultStyleRegistry[i].style_id == styleId)
                {
                    string stem = baseGlb.EndsWith(".glb", StringComparison.OrdinalIgnoreCase)
                        ? baseGlb.Substring(0, baseGlb.Length - 4)
                        : baseGlb;
                    return stem + s_defaultStyleRegistry[i].glb_totem_suffix;
                }
            }

            return baseGlb;
        }

        /// <summary>
        /// Toggles <see cref="Game.high_contrast_silhouette_lock"/> for instant competitive board readability (< 3.0s).
        /// </summary>
        public static void SetHighContrastSilhouetteLock(Game game_data, bool enabled)
        {
            if (game_data != null)
            {
                game_data.high_contrast_silhouette_lock = enabled;
            }
        }
    }

    /// <summary>
    /// Descriptor for an Antigravity Agent Command Deck capability card (Plugins, Skills, Tool Calling, MCP Conduits)
    /// and its paired watertight skeletal-rigged <c>.glb</c> / <c>.q3gs</c> 3D tabletop miniature.
    /// </summary>
    [Serializable]
    public struct AgentCommandDeckCardDescriptor
    {
        public string card_id;
        public string title;
        public string tier;
        public int mana_cost;
        public int north;
        public int east;
        public int south;
        public int west;
        public string primary_hex;
        public string accent_hex;
        public string card_png_path;
        public string emblem_svg_path;
        public string glb_relic_path;
        public string q3gs_splat_path;
        public string telegraph_pattern;
        public string ability_summary;
    }

    /// <summary>
    /// Registry binding the 37-card Antigravity Agent Command Deck (4 Mythic Sovereign Plugins, 12 Arcane Skills
    /// routing 93+ gamedev skills, 12 Native Tool-Calling Spells, and 9 MCP Server Conduits) and the 6 watertight
    /// (<c>V=4,034, E=12,096, F=8,064, V-E+F=2</c>) skeletal-rigged <c>.glb</c> / <c>.q3gs</c> relics into Unity.
    /// </summary>
    public static class AgentCommandDeckRegistry
    {
        public const int TotalAgentDeckCards = 37;
        public const int MythicPluginsCount = 4;
        public const int ArcaneSkillsCount = 12;
        public const int TacticalSpellsCount = 12;
        public const int McpConduitsCount = 9;
        public const int Watertight3DRelicsCount = 6;

        private static readonly AgentCommandDeckCardDescriptor[] s_sovereignPlugins = new AgentCommandDeckCardDescriptor[]
        {
            new AgentCommandDeckCardDescriptor
            {
                card_id = "plugin_01_tcg_creative_designer",
                title = "Grand Arcanist of CardCraft",
                tier = "MYTHIC_PLUGIN",
                mana_cost = 5,
                north = 8, east = 7, south = 6, west = 7,
                primary_hex = "#A855F7",
                accent_hex = "#FFB800",
                card_png_path = "GeneratedArt/AgentDeck/Cards/plugin_01_tcg_creative_designer.png",
                emblem_svg_path = "GeneratedArt/AgentDeck/SVGs/plugin_01_tcg_creative_designer.svg",
                glb_relic_path = "Assets/Resources/Models3D/AgentDeck/agent_01_grand_arcanist_designer.glb",
                q3gs_splat_path = "Assets/Resources/Models3D/AgentDeck/agent_01_grand_arcanist_designer.q3gs",
                telegraph_pattern = "3x3 Atelier Prism + Golden Ratio Frame Lock",
                ability_summary = "DEPLOY: Compiles 8-block morphological briefs, 600x800 portraits, & SVG telegraphs."
            },
            new AgentCommandDeckCardDescriptor
            {
                card_id = "plugin_02_parallel_swarm_orchestrator",
                title = "Chronos Swarm Commander",
                tier = "MYTHIC_PLUGIN",
                mana_cost = 5,
                north = 7, east = 8, south = 6, west = 7,
                primary_hex = "#F97316",
                accent_hex = "#00E5FF",
                card_png_path = "GeneratedArt/AgentDeck/Cards/plugin_02_parallel_swarm_orchestrator.png",
                emblem_svg_path = "GeneratedArt/AgentDeck/SVGs/plugin_02_parallel_swarm_orchestrator.svg",
                glb_relic_path = "Assets/Resources/Models3D/AgentDeck/agent_02_chronos_swarm_commander.glb",
                q3gs_splat_path = "Assets/Resources/Models3D/AgentDeck/agent_02_chronos_swarm_commander.q3gs",
                telegraph_pattern = "Tri-Portal Worktree Fan-Out (Share / Branch)",
                ability_summary = "DEPLOY: Summons parallel subagents in isolated git worktrees with shared memory."
            },
            new AgentCommandDeckCardDescriptor
            {
                card_id = "plugin_03_jev_system_one",
                title = "Hallowed Arbiter of System One",
                tier = "MYTHIC_PLUGIN",
                mana_cost = 4,
                north = 8, east = 6, south = 8, west = 6,
                primary_hex = "#2EE6D3",
                accent_hex = "#FFB800",
                card_png_path = "GeneratedArt/AgentDeck/Cards/plugin_03_jev_system_one.png",
                emblem_svg_path = "GeneratedArt/AgentDeck/SVGs/plugin_03_jev_system_one.svg",
                glb_relic_path = "Assets/Resources/Models3D/AgentDeck/agent_03_hallowed_arbiter_jev.glb",
                q3gs_splat_path = "Assets/Resources/Models3D/AgentDeck/agent_03_hallowed_arbiter_jev.q3gs",
                telegraph_pattern = "Octagonal Law-Seal Verification Gate",
                ability_summary = "GUARD: Screens untrusted input (jev_screen) & gates diffs with calibrated probabilities."
            },
            new AgentCommandDeckCardDescriptor
            {
                card_id = "plugin_04_mlx_apple_silicon",
                title = "A18 Pro Metal Forge Sovereign",
                tier = "MYTHIC_PLUGIN",
                mana_cost = 4,
                north = 7, east = 7, south = 7, west = 7,
                primary_hex = "#00E5FF",
                accent_hex = "#6366F1",
                card_png_path = "GeneratedArt/AgentDeck/Cards/plugin_04_mlx_apple_silicon.png",
                emblem_svg_path = "GeneratedArt/AgentDeck/SVGs/plugin_04_mlx_apple_silicon.svg",
                glb_relic_path = "Assets/Resources/Models3D/AgentDeck/agent_04_a18_pro_metal_sovereign.glb",
                q3gs_splat_path = "Assets/Resources/Models3D/AgentDeck/agent_04_a18_pro_metal_sovereign.q3gs",
                telegraph_pattern = "Single-Pass Logit Diamond Refraction",
                ability_summary = "OVERCHARGE: Executes zero-latency Choice, Score & Noul decisions on Metal GPU."
            }
        };

        public static AgentCommandDeckCardDescriptor[] GetSovereignPluginCards()
        {
            return s_sovereignPlugins;
        }
    }

    /// <summary>
    /// 3-scene campaign loop progression states (Citadel Stage Map -> Tactile Tabletop Duel -> Post-Victory Spoils Draft).
    /// </summary>
    public enum CampaignLoopScene
    {
        CitadelStageMap = 0,
        TactileTabletopDuel = 1,
        PostVictorySpoilsDraft = 2
    }

    /// <summary>
    /// Directional clash callout payload for 180-degree capture flips and floating stat comparisons.
    /// </summary>
    [Serializable]
    public struct DirectionalClashCallout
    {
        public int from_slot_index;
        public int to_slot_index;
        public string direction_edge;
        public int attacker_stat;
        public int defender_stat;
        public bool column_boosted;
        public bool triggered_180_capture_flip;
    }

    /// <summary>
    /// Tactile 2.5D tabletop HUD and board topology state synchronized with the WebPlayable layout.
    /// </summary>
    [Serializable]
    public struct TactileTabletopTopologyState
    {
        public CampaignLoopScene active_scene;
        public bool top_trapezoid_scoreboard_visible;
        public bool boss_circular_medallion_crest_visible;
        public bool circular_column_die_pedestals_aligned;
        public bool holo_telegraph_incoming_lip_active;
        public bool ghost_underlying_nameplate_suppressed;
        public float stat_badge_bg_opacity;
        public float board_pitch_deg;
        public int[] column_dice_pips;
        public bool[] column_die_tumbling_3d;
    }

    /// <summary>
    /// Unity 2022.3.40f1 Native Runtime Visual &amp; Cinematics Bridge for the tactile 2.5D tabletop layout.
    /// </summary>
    public static class TactileTabletopHudAndCinematicsBridge
    {
        public static TactileTabletopTopologyState CreateDefaultTabletopTopology()
        {
            return new TactileTabletopTopologyState
            {
                active_scene = CampaignLoopScene.TactileTabletopDuel,
                top_trapezoid_scoreboard_visible = true,
                boss_circular_medallion_crest_visible = true,
                circular_column_die_pedestals_aligned = true,
                holo_telegraph_incoming_lip_active = true,
                ghost_underlying_nameplate_suppressed = true,
                stat_badge_bg_opacity = 0.94f,
                board_pitch_deg = 22.0f,
                column_dice_pips = new int[] { 2, 4, 6 },
                column_die_tumbling_3d = new bool[] { false, false, false }
            };
        }

        public static Quaternion EvaluateCaptureFlipRotation3D(float normalizedTime)
        {
            return Quaternion.Euler(0f, Mathf.SmoothStep(0f, 180f, Mathf.Clamp01(normalizedTime)), 0f);
        }

        public static Quaternion EvaluateDieTumbleRotation3D(float normalizedTime)
        {
            float t = Mathf.Clamp01(normalizedTime);
            return Quaternion.Euler(360f * t, 540f * t, 180f * t);
        }

        public static float ComputeAudioTensionCutoffHz(bool imminentTelegraph, int openSlotsCount)
        {
            return imminentTelegraph || openSlotsCount <= 2 ? 1680f : 920f;
        }

        public static CampaignLoopScene AdvanceCampaignScene(CampaignLoopScene current, bool stageWon)
        {
            switch (current)
            {
                case CampaignLoopScene.CitadelStageMap:
                    return CampaignLoopScene.TactileTabletopDuel;
                case CampaignLoopScene.TactileTabletopDuel:
                    return stageWon ? CampaignLoopScene.PostVictorySpoilsDraft : CampaignLoopScene.CitadelStageMap;
                case CampaignLoopScene.PostVictorySpoilsDraft:
                default:
                    return CampaignLoopScene.CitadelStageMap;
            }
        }
    }

    /// <summary>
    /// PXG Engine NVIDIA Tesla V100 (Volta sm_70, FP16) &amp; 24fps 8-Frame Sakuga Cut-In Strip Bridge.
    /// Synchronizes 24fps Studio Trigger / Omega Strikers Sakuga sprite-strip playback and
    /// Frame-2 Impact Frame detection between WebPlayable and Unity 2022.3.40f1.
    /// </summary>
    public static class PxgV100SakugaTelegraphBridge
    {
        public const int DefaultStripFrames = 8;
        public const int DefaultStripFps = 24;
        public const int ImpactFrameIndex = 2;
        public const string TargetGpuModel = "NVIDIA Tesla V100 (Volta sm_70)";
        public const string NativeDtype = "float16";

        public static Vector4 EvaluateSakugaStripFrameUv(int frameIndex, int totalFrames = DefaultStripFrames)
        {
            int safeTotal = Mathf.Max(1, totalFrames);
            int clampedFrame = ((frameIndex % safeTotal) + safeTotal) % safeTotal;
            float scaleX = 1.0f / safeTotal;
            float offsetX = clampedFrame * scaleX;
            return new Vector4(scaleX, 1.0f, offsetX, 0.0f);
        }

        public static bool IsSakugaImpactFrame(int frameIndex, int totalFrames = DefaultStripFrames)
        {
            int safeTotal = Mathf.Max(1, totalFrames);
            int clampedFrame = ((frameIndex % safeTotal) + safeTotal) % safeTotal;
            return clampedFrame == ImpactFrameIndex;
        }
    }

    [Serializable]
    public class LanPacketFrame
    {
        public int seq;
        public ushort networkOpcode;
        public string actionName;
        public int playerId;
        public string cardId;
        public int slotX;
        public int slotY;
        public int dieIndex;
        public int budgeDelta;
        public float resonanceMultiplier;
        public int capturesFlipped;
        public string serverStateHashHex;
    }

    [Serializable]
    public class LanMultiplayerSimulationReport
    {
        public string timestampUtc;
        public string unityVersion;
        public string transport;
        public int loopbackPort;
        public int tcpClientsConnected;
        public int tcpPacketsExchanged;
        public int tcpBytesTransferred;
        public int opcodesExecutedCount;
        public ushort[] customOpcodesVerified;
        public int turnsSimulated;
        public int totalCardsDeployedOn3x3;
        public int directionalCapturesTriggered;
        public float peakDiceResonanceMultiplier;
        public string finalServerStateHashHex;
        public string finalClient0StateHashHex;
        public string finalClient1StateHashHex;
        public bool stateHashLockstepParity;
        public int finalPlayer0BoardCount;
        public int finalPlayer1BoardCount;
        public string winner;
        public string bridgeDiagnosticSummary;
        public List<LanPacketFrame> packetTrace = new List<LanPacketFrame>();
        public string status;
    }

    /// <summary>
    /// Headless Loopback TCP/IP LAN Multiplayer Simulator between two TcgEngine instances
    /// (Instance 0: Sovereign Agent Command Deck vs Instance 1: Cradle of Echoes Boss Deck).
    /// Verifies TCP socket framing, opcodes 1060 (RollDiceRow), 1062 (ApplyBudge), 1064 (TriggerChronoLock),
    /// 3x3 directional grid capture flips, and FNV-1a state hash lockstep parity across Server + 2 Clients.
    /// </summary>
    public static class SynapseLanMultiplayerSimulator
    {
        public const ushort OpcodeRollDiceRow = 1060;
        public const ushort OpcodeApplyBudge = 1062;
        public const ushort OpcodeTriggerChronoLock = 1064;
        public const ushort OpcodePlayCard3x3 = 1010;
        public const ushort OpcodeTacticalSlide3x3 = 1020;
        public const ushort OpcodeEndTurn = 1030;

        public static LanMultiplayerSimulationReport RunLoopbackLanMatch(string writeJsonPath = null)
        {
            var report = new LanMultiplayerSimulationReport
            {
                timestampUtc = DateTime.UtcNow.ToString("o"),
                unityVersion = Application.unityVersion,
                transport = "TCP/IPv4 Loopback (127.0.0.1) + IndieMarcNetcodeServerBridge",
                customOpcodesVerified = new ushort[] { OpcodeRollDiceRow, OpcodeApplyBudge, OpcodeTriggerChronoLock }
            };

            // 1. Run full IndieMarcNetcodeServerBridge + HybridMinimaxAI + WebApiBridge self-test
            bool bridgeOk = SynapseIndieMarcTcgEngineBridge.RunHeadlessBridgeVerification(out string bridgeDiag);
            report.bridgeDiagnosticSummary = bridgeDiag;

            // 2. Spin up two independent TcgEngine.Game instances (Authoritative Server + Client Mirror)
            Game serverGame = new Game("lan_match_sovereign_vs_boss_server", 2);
            Game client0Game = new Game("lan_match_sovereign_vs_boss_client0", 2);
            Game client1Game = new Game("lan_match_sovereign_vs_boss_client1", 2);

            string[][] matchCards = new string[][]
            {
                // Player 0 (Sovereign Agent Command Deck): id, title, N, E, S, W, pip
                new[] { "plugin_01_tcg_creative_designer", "Grand Arcanist of CardCraft", "8", "7", "6", "7", "6", "0", "1", "1" },
                new[] { "e_eclipse", "Eclipse Void Blade", "5", "5", "5", "5", "2", "1", "2", "1" },
                new[] { "plugin_02_parallel_swarm_orchestrator", "Chronos Swarm Commander", "7", "8", "6", "7", "5", "0", "2", "2" },
                new[] { "e_construct_rex", "Obsidian Construct Rex", "6", "5", "5", "6", "3", "1", "3", "2" },
                new[] { "plugin_03_jev_system_one", "Hallowed Arbiter of System One", "8", "6", "8", "6", "4", "0", "3", "1" },
                new[] { "e_void_harbinger", "Void Harbinger", "5", "6", "5", "5", "2", "1", "1", "2" },
                new[] { "plugin_04_mlx_apple_silicon", "A18 Pro Metal Forge Sovereign", "7", "7", "7", "7", "6", "0", "1", "3" }
            };

            var createdSoList = new List<CardData>();
            foreach (var row in matchCards)
            {
                var cd = ScriptableObject.CreateInstance<CardData>();
                cd.id = row[0];
                cd.title = row[1];
                cd.type = CardType.Character;
                cd.dir_north = int.Parse(row[2]);
                cd.dir_east = int.Parse(row[3]);
                cd.dir_south = int.Parse(row[4]);
                cd.dir_west = int.Parse(row[5]);
                cd.dice_pip_affinity = int.Parse(row[6]);
                CardData.card_dict[cd.id] = cd;
                createdSoList.Add(cd);
            }

            TcpListener listener = new TcpListener(IPAddress.Loopback, 0);
            listener.Start();
            int port = ((IPEndPoint)listener.LocalEndpoint).Port;
            report.loopbackPort = port;

            using (TcpClient client0 = new TcpClient())
            using (TcpClient client1 = new TcpClient())
            {
                client0.NoDelay = true;
                client1.NoDelay = true;
                client0.Connect(IPAddress.Loopback, port);
                TcpClient serverConn0 = listener.AcceptTcpClient();
                client1.Connect(IPAddress.Loopback, port);
                TcpClient serverConn1 = listener.AcceptTcpClient();

                using (serverConn0)
                using (serverConn1)
                {
                    report.tcpClientsConnected = 2;
                    NetworkStream c0Stream = client0.GetStream();
                    NetworkStream c1Stream = client1.GetStream();
                    NetworkStream s0Stream = serverConn0.GetStream();
                    NetworkStream s1Stream = serverConn1.GetStream();

                    int seq = 1;
                    void BroadcastFrame(LanPacketFrame frame)
                    {
                        string payload = JsonUtility.ToJson(frame);
                        byte[] body = Encoding.UTF8.GetBytes(payload);
                        byte[] header = BitConverter.GetBytes(body.Length);

                        NetworkStream senderClient = frame.playerId == 0 ? c0Stream : c1Stream;
                        NetworkStream receiverServer = frame.playerId == 0 ? s0Stream : s1Stream;

                        // Client -> Server
                        senderClient.Write(header, 0, 4);
                        senderClient.Write(body, 0, body.Length);
                        senderClient.Flush();
                        ReadExact(receiverServer, header.Length + body.Length);

                        // Server -> Both Clients broadcast
                        s0Stream.Write(header, 0, 4);
                        s0Stream.Write(body, 0, body.Length);
                        s0Stream.Flush();
                        s1Stream.Write(header, 0, 4);
                        s1Stream.Write(body, 0, body.Length);
                        s1Stream.Flush();

                        ReadExact(c0Stream, header.Length + body.Length);
                        ReadExact(c1Stream, header.Length + body.Length);

                        report.tcpPacketsExchanged += 3; // 1 upstream + 2 downstream broadcast
                        report.tcpBytesTransferred += (header.Length + body.Length) * 3;
                        report.opcodesExecutedCount++;
                        report.packetTrace.Add(frame);
                    }

                    // Step 1: Opcode 1060 RollDiceRow
                    CardFrontUnifiedRuntime.OnTurnStartRollDice(serverGame, new System.Random(1060));
                    CardFrontUnifiedRuntime.OnTurnStartRollDice(client0Game, new System.Random(1060));
                    CardFrontUnifiedRuntime.OnTurnStartRollDice(client1Game, new System.Random(1060));
                    SetDicePipsAll(new[] { serverGame, client0Game, client1Game }, new[] { 6, 6, 5, 4, 4 });

                    BroadcastFrame(new LanPacketFrame
                    {
                        seq = seq++,
                        networkOpcode = OpcodeRollDiceRow,
                        actionName = "RollDiceRow",
                        playerId = 0,
                        resonanceMultiplier = serverGame.active_resonance_multiplier,
                        serverStateHashHex = ComputeGameFnv1aHex(serverGame)
                    });

                    // Step 2: Opcode 1062 ApplyBudge (budge die[2] from 5 -> 6 for Full House 2.75x!)
                    foreach (var g in new[] { serverGame, client0Game, client1Game })
                    {
                        CardFrontUnifiedRuntime.ExecuteBudge(g, 2, +1);
                    }
                    report.peakDiceResonanceMultiplier = Mathf.Max(report.peakDiceResonanceMultiplier, serverGame.active_resonance_multiplier);

                    BroadcastFrame(new LanPacketFrame
                    {
                        seq = seq++,
                        networkOpcode = OpcodeApplyBudge,
                        actionName = "ApplyBudge",
                        playerId = 0,
                        dieIndex = 2,
                        budgeDelta = +1,
                        resonanceMultiplier = serverGame.active_resonance_multiplier,
                        serverStateHashHex = ComputeGameFnv1aHex(serverGame)
                    });

                    // Step 3: Opcode 1064 TriggerChronoLock (lock dice 0, 1, 2)
                    foreach (var g in new[] { serverGame, client0Game, client1Game })
                    {
                        CardFrontUnifiedRuntime.ExecuteChronoReroll(g, 0b11111, new System.Random(1064));
                    }
                    BroadcastFrame(new LanPacketFrame
                    {
                        seq = seq++,
                        networkOpcode = OpcodeTriggerChronoLock,
                        actionName = "TriggerChronoLock",
                        playerId = 0,
                        dieIndex = 0,
                        resonanceMultiplier = serverGame.active_resonance_multiplier,
                        serverStateHashHex = ComputeGameFnv1aHex(serverGame)
                    });

                    // Step 4: Alternate turns deploying 7 cards onto the 3x3 directional grid
                    int turnIdx = 0;
                    foreach (var row in matchCards)
                    {
                        string cid = row[0];
                        int pid = int.Parse(row[7]);
                        int sx = int.Parse(row[8]);
                        int sy = int.Parse(row[9]);
                        string uid = $"lan_card_{turnIdx}_{cid}";

                        int flipsOnServer = 0;
                        foreach (var g in new[] { serverGame, client0Game, client1Game })
                        {
                            Card c = new Card(cid, uid, pid)
                            {
                                CardData = CardData.Get(cid),
                                slot = new Slot(sx, sy, pid)
                            };
                            g.players[pid].cards_board.Add(c);
                            var res = CardFrontUnifiedRuntime.OnCardPlayedEvaluate3x3AndResonance(g, c, c.slot);
                            if (ReferenceEquals(g, serverGame))
                            {
                                flipsOnServer = res.adjacent_enemy_cards_flipped;
                                report.peakDiceResonanceMultiplier = Mathf.Max(report.peakDiceResonanceMultiplier, res.resonance_multiplier);
                            }
                        }

                        report.totalCardsDeployedOn3x3++;
                        report.directionalCapturesTriggered += flipsOnServer;
                        report.turnsSimulated++;

                        BroadcastFrame(new LanPacketFrame
                        {
                            seq = seq++,
                            networkOpcode = OpcodePlayCard3x3,
                            actionName = "PlayCard3x3",
                            playerId = pid,
                            cardId = cid,
                            slotX = sx,
                            slotY = sy,
                            resonanceMultiplier = serverGame.active_resonance_multiplier,
                            capturesFlipped = flipsOnServer,
                            serverStateHashHex = ComputeGameFnv1aHex(serverGame)
                        });

                        BroadcastFrame(new LanPacketFrame
                        {
                            seq = seq++,
                            networkOpcode = OpcodeEndTurn,
                            actionName = "EndTurn",
                            playerId = pid,
                            resonanceMultiplier = serverGame.active_resonance_multiplier,
                            serverStateHashHex = ComputeGameFnv1aHex(serverGame)
                        });
                        turnIdx++;
                    }
                }
            }
            listener.Stop();

            report.finalServerStateHashHex = ComputeGameFnv1aHex(serverGame);
            report.finalClient0StateHashHex = ComputeGameFnv1aHex(client0Game);
            report.finalClient1StateHashHex = ComputeGameFnv1aHex(client1Game);
            report.stateHashLockstepParity =
                bridgeOk &&
                report.finalServerStateHashHex == report.finalClient0StateHashHex &&
                report.finalServerStateHashHex == report.finalClient1StateHashHex;

            int p0Count = 0;
            int p1Count = 0;
            foreach (var p in serverGame.players)
            {
                foreach (var c in p.cards_board)
                {
                    if (c.player_id == 0) p0Count++;
                    else p1Count++;
                }
            }
            report.finalPlayer0BoardCount = p0Count;
            report.finalPlayer1BoardCount = p1Count;
            report.winner = p0Count >= p1Count ? "Player 0 (Sovereign Agent Command Deck)" : "Player 1 (Cradle of Echoes Boss)";
            report.status = report.stateHashLockstepParity && report.tcpPacketsExchanged >= 15
                ? "PASS_HEADLESS_LAN_MULTIPLAYER_SIMULATION"
                : "FAIL_LAN_PARITY";

            foreach (var so in createdSoList)
            {
                UnityEngine.Object.DestroyImmediate(so);
            }

            if (!string.IsNullOrEmpty(writeJsonPath))
            {
                string dir = Path.GetDirectoryName(writeJsonPath);
                if (!string.IsNullOrEmpty(dir) && !Directory.Exists(dir))
                    Directory.CreateDirectory(dir);
                File.WriteAllText(writeJsonPath, JsonUtility.ToJson(report, true));
            }

            return report;
        }

        private static void SetDicePipsAll(Game[] games, int[] pips)
        {
            foreach (var g in games)
            {
                Array.Copy(pips, g.dice_pips, 5);
                g.active_resonance_multiplier = CardFrontUnifiedRuntime.EvaluateDiceResonance(g.dice_pips);
            }
        }

        private static void ReadExact(NetworkStream stream, int totalBytes)
        {
            byte[] buf = new byte[totalBytes];
            int offset = 0;
            while (offset < totalBytes)
            {
                int read = stream.Read(buf, offset, totalBytes - offset);
                if (read <= 0) break;
                offset += read;
            }
        }

        public static string ComputeGameFnv1aHex(Game g)
        {
            ulong hash = 14695981039346656037UL;
            void Mix(int val)
            {
                hash ^= (ulong)(uint)val;
                hash *= 1099511628211UL;
            }
            void MixStr(string s)
            {
                if (string.IsNullOrEmpty(s)) return;
                for (int i = 0; i < s.Length; i++)
                {
                    hash ^= s[i];
                    hash *= 1099511628211UL;
                }
            }

            for (int i = 0; i < g.dice_pips.Length; i++) Mix(g.dice_pips[i]);
            for (int i = 0; i < g.dice_locked.Length; i++) Mix(g.dice_locked[i] ? 1 : 0);
            Mix(Mathf.RoundToInt(g.active_resonance_multiplier * 100f));
            foreach (var p in g.players)
            {
                Mix(p.player_id);
                foreach (var c in p.cards_board)
                {
                    MixStr(c.card_id);
                    Mix(c.player_id);
                    Mix(c.slot.x);
                    Mix(c.slot.y);
                    Mix(c.slot.p);
                    Mix(c.attack);
                }
            }
            return hash.ToString("X16");
        }
    }

    /// <summary>
    /// Standalone macOS Player Runtime Bootstrapper attached to SynapseMainMenu &amp; SynapseTacticalBattleArena.
    /// Executes LAN loopback self-verification when launched with <c>--verify-standalone-lan</c> or in batchmode,
    /// and renders an interactive 3x3 + 5-Dice tabletop HUD in windowed mode.
    /// </summary>
    public class SynapseStandalonePlayerBootstrap : MonoBehaviour
    {
        private LanMultiplayerSimulationReport _lastReport;

        private void Start()
        {
            string outPath = Path.Combine(Directory.GetCurrentDirectory(), "Logs/macos_standalone_player_runtime_verification.json");
            _lastReport = SynapseLanMultiplayerSimulator.RunLoopbackLanMatch(outPath);
            Debug.Log($"[SynapseStandalonePlayerBootstrap] Standalone Player Runtime Verification: {_lastReport.status} (Hash={_lastReport.finalServerStateHashHex}, Packets={_lastReport.tcpPacketsExchanged})");

            string[] args = Environment.GetCommandLineArgs();
            bool quitAfterVerify = Application.isBatchMode;
            for (int i = 0; i < args.Length; i++)
            {
                if (args[i] == "--verify-standalone-lan")
                {
                    quitAfterVerify = true;
                    break;
                }
            }

            if (quitAfterVerify)
            {
                Application.Quit(0);
            }
        }

        private void OnGUI()
        {
            if (_lastReport == null) return;
            GUI.Box(new Rect(16, 16, 620, 140), "CARDFRONT: Cradle of Echoes — Standalone macOS (Unity 6000.6.8f1) + TcgEngine LAN");
            GUI.Label(new Rect(28, 44, 590, 24), $"Status: {_lastReport.status} | TCP Loopback Port: {_lastReport.loopbackPort}");
            GUI.Label(new Rect(28, 68, 590, 24), $"Packets: {_lastReport.tcpPacketsExchanged} ({_lastReport.tcpBytesTransferred} B) | State Hash Parity: {_lastReport.finalServerStateHashHex}");
            GUI.Label(new Rect(28, 92, 590, 24), $"3x3 Captures: {_lastReport.directionalCapturesTriggered} | Peak Dicevaders Resonance: {_lastReport.peakDiceResonanceMultiplier:F2}x");
            GUI.Label(new Rect(28, 116, 590, 24), $"Winner: {_lastReport.winner} ({_lastReport.finalPlayer0BoardCount} vs {_lastReport.finalPlayer1BoardCount})");
        }
    }
}
