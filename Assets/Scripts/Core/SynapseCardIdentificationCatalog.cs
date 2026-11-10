using System;
using System.Collections.Generic;
using System.Security.Cryptography;
using System.Text;
using UnityEngine;

namespace Synapse.TcgEngine.Core
{
    /// <summary>
    /// Collector Rarity Tiers modeled on Shadowverse EVOLVE & CARDFRONT: Cradle of Echoes booster sets:
    /// BR (Bronze Rare), GR (Gold Rare), SR (Silver Rare), LG (Legendary), SL (Super Legendary), UR (Ultimate Rare).
    /// </summary>
    public enum CollectorRarityTier
    {
        BR,
        GR,
        SR,
        LG,
        SL,
        UR
    }

    /// <summary>
    /// Card Evolution State tracking pre-evolution (進化前), post-evolution (進化後), and Sakuga Transcended (超進化・作画覚醒) states.
    /// </summary>
    public enum CardEvolutionState
    {
        Unevolved_ShinkaMae,
        Evolved_ShinkaGo,
        SakugaTranscended
    }

    /// <summary>
    /// Parsed components of a collector card number such as "BP05-110 SR" or "BP05-110EV SR".
    /// </summary>
    [Serializable]
    public struct ParsedCardNumber
    {
        public string setCode;
        public string collectorIndex;
        public int collectorIndexNumeric;
        public string evolutionSuffix;
        public string rarityCode;
        public CollectorRarityTier rarity;
        public bool isEvolved;
        public bool isValid;
    }

    /// <summary>
    /// Bilingual Collector Identification metadata structure modeled on the canonical 6-row specification:
    ///   original title    機構翼の少女・ローザ(進化前)
    ///   card game         Shadowverse EVOLVE
    ///   version           [BP05] Eternal omens
    ///   original version  ブースターパック第5弾 永劫なる絶傑
    ///   card number       BP05-110 SR
    ///   rarity            SR
    /// </summary>
    [Serializable]
    public struct CardCollectorIdentification
    {
        public string cardId;
        public string titleEn;
        public string originalTitleJp;
        public string cardGame;
        public string versionEn;
        public string originalVersionJp;
        public string cardNumber;
        public CollectorRarityTier rarity;
        public CardEvolutionState evolutionState;
        public string sha256CollectorHash;
    }

    /// <summary>
    /// Bilingual Card Identification & Collector Taxonomy Catalog for Unity 6 (Synapse.TcgEngine.Core).
    /// Supports parsing collector numbers, formatting 6-row bilingual specification tables,
    /// transforming unevolved (進化前) cards into evolved (進化後 / EV) states, and cryptographic hashing.
    /// </summary>
    public static class SynapseCardIdentificationCatalog
    {
        public const string DefaultCardGameSvEvolve = "Shadowverse EVOLVE";
        public const string DefaultCardGameCardFront = "CARDFRONT: Cradle of Echoes";
        public const string Bp05VersionEn = "[BP05] Eternal omens";
        public const string Bp05OriginalVersionJp = "ブースターパック第5弾 永劫なる絶傑";
        public const string Cf01VersionEn = "[BP01] Cradle of Echoes";
        public const string Cf01OriginalVersionJp = "ブースターパック第1弾 残響の揺籃";

        public const string SuffixUnevolvedJp = "(進化前)";
        public const string SuffixEvolvedJp = "(進化後)";
        public const string SuffixTranscendedJp = "(超進化)";

        /// <summary>
        /// Parses a collector card number (e.g. "BP05-110 SR" or "BP05-110EV SR") into its
        /// set code ("BP05"), collector index ("110"), evolution suffix ("EV" or ""), and rarity ("SR").
        /// </summary>
        public static ParsedCardNumber ParseCardNumber(string cardNumber)
        {
            ParsedCardNumber parsed = new ParsedCardNumber
            {
                setCode = string.Empty,
                collectorIndex = string.Empty,
                collectorIndexNumeric = 0,
                evolutionSuffix = string.Empty,
                rarityCode = "SR",
                rarity = CollectorRarityTier.SR,
                isEvolved = false,
                isValid = false
            };

            if (string.IsNullOrWhiteSpace(cardNumber))
            {
                return parsed;
            }

            string trimmed = cardNumber.Trim();
            string[] tokens = trimmed.Split(new char[] { ' ', '\t' }, StringSplitOptions.RemoveEmptyEntries);
            if (tokens.Length == 0)
            {
                return parsed;
            }

            string codeToken = tokens[0];
            if (tokens.Length >= 2)
            {
                parsed.rarityCode = tokens[tokens.Length - 1].Trim().ToUpperInvariant();
                if (Enum.TryParse<CollectorRarityTier>(parsed.rarityCode, true, out CollectorRarityTier parsedTier))
                {
                    parsed.rarity = parsedTier;
                }
            }

            int dashIndex = codeToken.IndexOf('-');
            if (dashIndex <= 0 || dashIndex >= codeToken.Length - 1)
            {
                parsed.setCode = codeToken;
                return parsed;
            }

            parsed.setCode = codeToken.Substring(0, dashIndex).Trim();
            string rhs = codeToken.Substring(dashIndex + 1).Trim();

            int digitEnd = 0;
            while (digitEnd < rhs.Length && char.IsDigit(rhs[digitEnd]))
            {
                digitEnd++;
            }

            if (digitEnd > 0)
            {
                parsed.collectorIndex = rhs.Substring(0, digitEnd);
                int.TryParse(parsed.collectorIndex, out parsed.collectorIndexNumeric);
                parsed.evolutionSuffix = rhs.Substring(digitEnd).Trim().ToUpperInvariant();
                parsed.isEvolved = string.Equals(parsed.evolutionSuffix, "EV", StringComparison.OrdinalIgnoreCase);
                parsed.isValid = true;
            }
            else
            {
                parsed.collectorIndex = rhs;
            }

            return parsed;
        }

        /// <summary>
        /// Overload extracting parsed card number components directly via out parameters.
        /// </summary>
        public static ParsedCardNumber ParseCardNumber(
            string cardNumber,
            out string setCode,
            out string collectorIndex,
            out string evolutionSuffix,
            out CollectorRarityTier rarity)
        {
            ParsedCardNumber res = ParseCardNumber(cardNumber);
            setCode = res.setCode;
            collectorIndex = res.collectorIndex;
            evolutionSuffix = res.evolutionSuffix;
            rarity = res.rarity;
            return res;
        }

        /// <summary>
        /// Formats the canonical 6-row bilingual collector specification table:
        ///   original title    機構翼の少女・ローザ(進化前)
        ///   card game         Shadowverse EVOLVE
        ///   version           [BP05] Eternal omens
        ///   original version  ブースターパック第5弾 永劫なる絶傑
        ///   card number       BP05-110 SR
        ///   rarity            SR
        /// </summary>
        public static string FormatCollectorTable(CardCollectorIdentification id)
        {
            StringBuilder sb = new StringBuilder(256);
            sb.Append("original title".PadRight(18)).Append(id.originalTitleJp ?? string.Empty).Append('\n');
            sb.Append("card game".PadRight(18)).Append(id.cardGame ?? string.Empty).Append('\n');
            sb.Append("version".PadRight(18)).Append(id.versionEn ?? string.Empty).Append('\n');
            sb.Append("original version".PadRight(18)).Append(id.originalVersionJp ?? string.Empty).Append('\n');
            sb.Append("card number".PadRight(18)).Append(id.cardNumber ?? string.Empty).Append('\n');
            sb.Append("rarity".PadRight(18)).Append(id.rarity.ToString());
            return sb.ToString();
        }

        /// <summary>
        /// Converts an unevolved (進化前) card identification to its evolved (進化後) state:
        /// - Replaces "(進化前)" with "(進化後)" in originalTitleJp
        /// - Appends "EV" to the collector index in cardNumber ("BP05-110 SR" -> "BP05-110EV SR")
        /// - Sets evolutionState to CardEvolutionState.Evolved_ShinkaGo
        /// - Updates sha256CollectorHash deterministically
        /// </summary>
        public static CardCollectorIdentification ToEvolvedState(CardCollectorIdentification unevolved)
        {
            CardCollectorIdentification evolved = unevolved;
            evolved.evolutionState = CardEvolutionState.Evolved_ShinkaGo;

            if (!string.IsNullOrEmpty(unevolved.cardId))
            {
                if (unevolved.cardId.EndsWith("_unevolved", StringComparison.OrdinalIgnoreCase))
                {
                    evolved.cardId = unevolved.cardId.Substring(0, unevolved.cardId.Length - "_unevolved".Length) + "_evolved";
                }
                else if (!unevolved.cardId.EndsWith("_ev", StringComparison.OrdinalIgnoreCase))
                {
                    evolved.cardId = unevolved.cardId + "_ev";
                }
            }

            if (!string.IsNullOrEmpty(unevolved.titleEn))
            {
                if (unevolved.titleEn.Contains("(Unevolved)"))
                {
                    evolved.titleEn = unevolved.titleEn.Replace("(Unevolved)", "(Evolved)");
                }
                else if (!unevolved.titleEn.Contains("(Evolved)"))
                {
                    evolved.titleEn = unevolved.titleEn + " (Evolved)";
                }
            }

            if (!string.IsNullOrEmpty(unevolved.originalTitleJp))
            {
                if (unevolved.originalTitleJp.Contains(SuffixUnevolvedJp))
                {
                    evolved.originalTitleJp = unevolved.originalTitleJp.Replace(SuffixUnevolvedJp, SuffixEvolvedJp);
                }
                else if (!unevolved.originalTitleJp.Contains(SuffixEvolvedJp))
                {
                    evolved.originalTitleJp = unevolved.originalTitleJp + SuffixEvolvedJp;
                }
            }

            ParsedCardNumber parsed = ParseCardNumber(unevolved.cardNumber);
            if (parsed.isValid)
            {
                string evSuffix = string.IsNullOrEmpty(parsed.evolutionSuffix) ? "EV" : parsed.evolutionSuffix;
                if (!evSuffix.Contains("EV"))
                {
                    evSuffix = evSuffix + "EV";
                }
                evolved.cardNumber = parsed.setCode + "-" + parsed.collectorIndex + evSuffix + " " + parsed.rarity.ToString();
            }
            else if (!string.IsNullOrEmpty(unevolved.cardNumber) && !unevolved.cardNumber.Contains("EV"))
            {
                int spaceIdx = unevolved.cardNumber.IndexOf(' ');
                if (spaceIdx > 0)
                {
                    evolved.cardNumber = unevolved.cardNumber.Substring(0, spaceIdx) + "EV" + unevolved.cardNumber.Substring(spaceIdx);
                }
                else
                {
                    evolved.cardNumber = unevolved.cardNumber + "EV";
                }
            }

            evolved.sha256CollectorHash = ComputeCollectorSha256(evolved);
            return evolved;
        }

        /// <summary>
        /// Returns the canonical reference entry for Rosa, Mechawing Maiden (Unevolved):
        ///   original title    機構翼の少女・ローザ(進化前)
        ///   card game         Shadowverse EVOLVE
        ///   version           [BP05] Eternal omens
        ///   original version  ブースターパック第5弾 永劫なる絶傑
        ///   card number       BP05-110 SR
        ///   rarity            SR
        /// </summary>
        public static CardCollectorIdentification GetReferenceRosaBp05Entry()
        {
            CardCollectorIdentification entry = new CardCollectorIdentification
            {
                cardId = "bp05_110_rosa_unevolved",
                titleEn = "Rosa, Mechawing Maiden (Unevolved)",
                originalTitleJp = "機構翼の少女・ローザ(進化前)",
                cardGame = DefaultCardGameSvEvolve,
                versionEn = Bp05VersionEn,
                originalVersionJp = Bp05OriginalVersionJp,
                cardNumber = "BP05-110 SR",
                rarity = CollectorRarityTier.SR,
                evolutionState = CardEvolutionState.Unevolved_ShinkaMae,
                sha256CollectorHash = string.Empty
            };
            entry.sha256CollectorHash = ComputeCollectorSha256(entry);
            return entry;
        }

        /// <summary>
        /// Computes a deterministic lowercase hex SHA-256 hash over the canonical bilingual fields.
        /// </summary>
        public static string ComputeCollectorSha256(CardCollectorIdentification id)
        {
            string payload = string.Join(
                "|",
                id.cardId ?? string.Empty,
                id.titleEn ?? string.Empty,
                id.originalTitleJp ?? string.Empty,
                id.cardGame ?? string.Empty,
                id.versionEn ?? string.Empty,
                id.originalVersionJp ?? string.Empty,
                id.cardNumber ?? string.Empty,
                id.rarity.ToString(),
                id.evolutionState.ToString()
            );

            using (SHA256 sha = SHA256.Create())
            {
                byte[] digest = sha.ComputeHash(Encoding.UTF8.GetBytes(payload));
                StringBuilder hex = new StringBuilder(digest.Length * 2);
                for (int i = 0; i < digest.Length; i++)
                {
                    hex.Append(digest[i].ToString("x2"));
                }
                return hex.ToString();
            }
        }

        /// <summary>
        /// Builds the complete bilingual collector catalog for the 14 canonical CARDFRONT / PROJECT CF + CardCraft cards
        /// plus the BP05-110 SR Rosa reference entry.
        /// </summary>
        public static List<CardCollectorIdentification> GetCanonicalCollectorCatalog()
        {
            List<CardCollectorIdentification> list = new List<CardCollectorIdentification>(16);
            list.Add(GetReferenceRosaBp05Entry());
            list.Add(ToEvolvedState(GetReferenceRosaBp05Entry()));

            void AddEntry(
                string cid,
                string en,
                string jp,
                string game,
                string verEn,
                string verJp,
                string num,
                CollectorRarityTier rar,
                CardEvolutionState evo)
            {
                CardCollectorIdentification item = new CardCollectorIdentification
                {
                    cardId = cid,
                    titleEn = en,
                    originalTitleJp = jp,
                    cardGame = game,
                    versionEn = verEn,
                    originalVersionJp = verJp,
                    cardNumber = num,
                    rarity = rar,
                    evolutionState = evo,
                    sha256CollectorHash = string.Empty
                };
                item.sha256CollectorHash = ComputeCollectorSha256(item);
                list.Add(item);
            }

            AddEntry("cf_01_mystic_mage", "Mystic Mage", "秘術の魔道士・ミスティック(進化前)", DefaultCardGameCardFront, Cf01VersionEn, Cf01OriginalVersionJp, "BP01-001 LG", CollectorRarityTier.LG, CardEvolutionState.Unevolved_ShinkaMae);
            AddEntry("cf_02_mech_knight", "Mech Knight", "機甲翼の騎士・ヴァンガード(進化前)", DefaultCardGameCardFront, Cf01VersionEn, Cf01OriginalVersionJp, "BP01-002 SR", CollectorRarityTier.SR, CardEvolutionState.Unevolved_ShinkaMae);
            AddEntry("cf_03_celestial_guardian", "Celestial Guardian", "天界の守護神・セレスティア(進化前)", DefaultCardGameCardFront, Cf01VersionEn, Cf01OriginalVersionJp, "BP01-003 LG", CollectorRarityTier.LG, CardEvolutionState.Unevolved_ShinkaMae);
            AddEntry("cf_04_shadow_assassin", "Shadow Assassin", "宵闇の暗殺者・エクリプス(進化前)", DefaultCardGameCardFront, Cf01VersionEn, Cf01OriginalVersionJp, "BP01-004 GR", CollectorRarityTier.GR, CardEvolutionState.Unevolved_ShinkaMae);
            AddEntry("cf_05_elemental_sprite", "Elemental Sprite", "精霊の妖精・スプライト(進化前)", DefaultCardGameCardFront, Cf01VersionEn, Cf01OriginalVersionJp, "BP01-005 BR", CollectorRarityTier.BR, CardEvolutionState.Unevolved_ShinkaMae);
            AddEntry("cf_06_galactic_explorer", "Galactic Explorer", "星海の探求者・オデッセイ(進化前)", DefaultCardGameCardFront, Cf01VersionEn, Cf01OriginalVersionJp, "BP01-006 SR", CollectorRarityTier.SR, CardEvolutionState.Unevolved_ShinkaMae);
            AddEntry("cf_07_clockwork_sorcerer", "Clockwork Sorcerer", "時空歯車の魔術師・クロノス(進化前)", DefaultCardGameCardFront, Cf01VersionEn, Cf01OriginalVersionJp, "BP01-007 GR", CollectorRarityTier.GR, CardEvolutionState.Unevolved_ShinkaMae);
            AddEntry("cf_08_phoenix_guardian", "Phoenix Guardian", "不死鳥の守護者・フェニックス(進化前)", DefaultCardGameCardFront, Cf01VersionEn, Cf01OriginalVersionJp, "BP01-008 SL", CollectorRarityTier.SL, CardEvolutionState.Unevolved_ShinkaMae);
            AddEntry("cf_09_cyber_ninja", "Cyber Ninja", "電脳の忍・サイバーシャドウ(進化前)", DefaultCardGameCardFront, Cf01VersionEn, Cf01OriginalVersionJp, "BP01-009 SR", CollectorRarityTier.SR, CardEvolutionState.Unevolved_ShinkaMae);
            AddEntry("cf_10_lunar_oracle", "Lunar Oracle", "月光の神託者・ルナオラクル(進化前)", DefaultCardGameCardFront, Cf01VersionEn, Cf01OriginalVersionJp, "BP01-010 UR", CollectorRarityTier.UR, CardEvolutionState.Unevolved_ShinkaMae);
            AddEntry("cc_01_sketching", "Sketching", "創世の素描・スケッチング(進化前)", DefaultCardGameCardFront, Cf01VersionEn, Cf01OriginalVersionJp, "BP01-011 BR", CollectorRarityTier.BR, CardEvolutionState.Unevolved_ShinkaMae);
            AddEntry("cc_02_concept_art", "Concept Art", "創世の概念画・コンセプトアート(進化後)", DefaultCardGameCardFront, Cf01VersionEn, Cf01OriginalVersionJp, "BP01-011EV SR", CollectorRarityTier.SR, CardEvolutionState.Evolved_ShinkaGo);
            AddEntry("cc_03_storyboard", "Storyboard", "創世の絵コンテ・ストーリーボード(進化前)", DefaultCardGameCardFront, Cf01VersionEn, Cf01OriginalVersionJp, "BP01-012 BR", CollectorRarityTier.BR, CardEvolutionState.Unevolved_ShinkaMae);
            AddEntry("cc_04_animatic", "Animatic", "創世の作画覚醒・アニマティック(進化後)", DefaultCardGameCardFront, Cf01VersionEn, Cf01OriginalVersionJp, "BP01-012EV LG", CollectorRarityTier.LG, CardEvolutionState.Evolved_ShinkaGo);

            return list;
        }
    }
}
