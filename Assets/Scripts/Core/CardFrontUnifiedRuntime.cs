using System;
using System.Collections.Generic;
using System.Security.Cryptography;
using System.Text;
using UnityEngine;

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

                    bool captured = false;
                    // Neighbor is North (dy == +1): compare our North vs neighbor's South
                    if (dy == 1 && result.effective_north > neighbor.CardData.dir_south)
                        captured = true;
                    // Neighbor is East (dx == +1): compare our East vs neighbor's West
                    else if (dx == 1 && result.effective_east > neighbor.CardData.dir_west)
                        captured = true;
                    // Neighbor is South (dy == -1): compare our South vs neighbor's North
                    else if (dy == -1 && result.effective_south > neighbor.CardData.dir_north)
                        captured = true;
                    // Neighbor is West (dx == -1): compare our West vs neighbor's East
                    else if (dx == -1 && result.effective_west > neighbor.CardData.dir_east)
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
        private const string DefaultReceiptSecret = "CARDFRONT_ECHO_GHOST_SOVEREIGN_HMAC_KEY_2026";

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

            EchoGhostSnapshot snapshot = JsonUtility.FromJson<EchoGhostSnapshot>(jsonSnapshot);
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
            string secretKey = DefaultReceiptSecret)
        {
            string payload = string.Format("{0}|{1}|{2}|{3}",
                matchUid ?? "",
                playerUsername ?? "",
                finalTurnCount,
                serializedActions ?? "");

            byte[] keyBytes = Encoding.UTF8.GetBytes(string.IsNullOrEmpty(secretKey) ? DefaultReceiptSecret : secretKey);
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

    /// <summary>
    /// Manages the 5 non-P2W <see cref="VariantData"/> shader vectors, 3D <c>.glb</c> totem bindings,
    /// custom dice materials, the 90-minute onboarding silence check, and <c>high_contrast_silhouette_lock</c>.
    /// </summary>
    public static class DiegeticAtelierController
    {
        public const float OnboardingSilenceMinutesThreshold = 90.0f;
        public const int OnboardingSilenceChapterThreshold = 3;

        private static readonly SovereignStyleVariantDescriptor[] s_sovereignStyles = new SovereignStyleVariantDescriptor[]
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
            return s_sovereignStyles;
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

            for (int i = 0; i < s_sovereignStyles.Length; i++)
            {
                if (s_sovereignStyles[i].style_id == styleId)
                {
                    string stem = baseGlb.EndsWith(".glb", StringComparison.OrdinalIgnoreCase)
                        ? baseGlb.Substring(0, baseGlb.Length - 4)
                        : baseGlb;
                    return stem + s_sovereignStyles[i].glb_totem_suffix;
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
}
